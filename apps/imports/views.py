import json
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, ListView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from .models import ImportLog, ImportError
from .services.products import ProductImporter
from .services.clients import ClientImporter
from .services.categories import CategoryImporter
from .services.abrazaderas import AbrazaderaImporter


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin que requiere ser admin."""
    
    def test_func(self):
        return self.request.user.es_admin


IMPORTERS = {
    'productos': {
        'class': ProductImporter,
        'nombre': 'Productos',
        'icono': '📦',
        'descripcion': 'Importar productos desde Excel o CSV. Columnas: SKU, Nombre, Precio, Stock, filtro_1..5'
    },
    'clientes': {
        'class': ClientImporter,
        'nombre': 'Clientes',
        'icono': '👥',
        'descripcion': 'Importar clientes desde Excel o CSV. Columnas: Usuario, Nombre, Email, Descuento, etc.'
    },
    'categorias': {
        'class': CategoryImporter,
        'nombre': 'Categorías',
        'icono': '📁',
        'descripcion': 'Importar categorías desde Excel o CSV. Columna: Nombre'
    },
    'abrazaderas': {
        'class': AbrazaderaImporter,
        'nombre': 'Abrazaderas',
        'icono': '🔩',
        'descripcion': 'Importar abrazaderas con atributos específicos. Columnas: SKU, Nombre, Tipo, Medida, Material, etc.'
    },
}


class ImportSelectView(AdminRequiredMixin, TemplateView):
    """Vista para seleccionar tipo de importación."""
    template_name = 'imports/select.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['importadores'] = IMPORTERS
        return context


class ImportUploadView(AdminRequiredMixin, View):
    """Vista para subir archivo."""
    template_name = 'imports/upload.html'
    
    def get(self, request, tipo):
        if tipo not in IMPORTERS:
            messages.error(request, 'Tipo de importación inválido')
            return redirect('imports:select')
        
        return render(request, self.template_name, {
            'tipo': tipo,
            'info': IMPORTERS[tipo]
        })
    
    def post(self, request, tipo):
        if tipo not in IMPORTERS:
            messages.error(request, 'Tipo de importación inválido')
            return redirect('imports:select')
        
        archivo = request.FILES.get('archivo')
        if not archivo:
            messages.error(request, 'Debe seleccionar un archivo')
            return redirect('imports:upload', tipo=tipo)
        
        # Validar extensión
        nombre = archivo.name.lower()
        if not (nombre.endswith('.xlsx') or nombre.endswith('.csv')):
            messages.error(request, 'Formato no válido. Use .xlsx o .csv')
            return redirect('imports:upload', tipo=tipo)
        
        # Guardar archivo temporalmente
        path = f'imports/temp/{request.user.id}_{tipo}_{archivo.name}'
        saved_path = default_storage.save(path, ContentFile(archivo.read()))
        
        # Guardar path en sesión
        request.session[f'import_{tipo}_file'] = saved_path
        request.session[f'import_{tipo}_filename'] = archivo.name
        
        return redirect('imports:preview', tipo=tipo)


class ImportPreviewView(AdminRequiredMixin, View):
    """Vista de preview antes de importar."""
    template_name = 'imports/preview.html'
    
    def get(self, request, tipo):
        if tipo not in IMPORTERS:
            messages.error(request, 'Tipo de importación inválido')
            return redirect('imports:select')
        
        file_path = request.session.get(f'import_{tipo}_file')
        filename = request.session.get(f'import_{tipo}_filename')
        
        if not file_path or not default_storage.exists(file_path):
            messages.error(request, 'Archivo no encontrado. Suba el archivo nuevamente.')
            return redirect('imports:upload', tipo=tipo)
        
        try:
            # Obtener el path completo
            full_path = default_storage.path(file_path)
            
            # Crear importador y hacer preview
            importer_class = IMPORTERS[tipo]['class']
            importer = importer_class(full_path, request.user)
            preview = importer.preview()
            
            # Guardar datos en sesión para ejecución
            request.session[f'import_{tipo}_preview'] = {
                'a_crear': preview['a_crear'],
                'a_actualizar': preview['a_actualizar'],
                'total': preview['total'],
                'errores_count': len(preview['errores'])
            }
            
            return render(request, self.template_name, {
                'tipo': tipo,
                'info': IMPORTERS[tipo],
                'filename': filename,
                'preview': preview,
                'columnas': list(preview['filas'][0].keys()) if preview['filas'] else []
            })
            
        except Exception as e:
            messages.error(request, f'Error al procesar archivo: {str(e)}')
            return redirect('imports:upload', tipo=tipo)


class ImportExecuteView(AdminRequiredMixin, View):
    """Vista para ejecutar la importación."""
    
    def post(self, request, tipo):
        if tipo not in IMPORTERS:
            return JsonResponse({'error': 'Tipo inválido'}, status=400)
        
        file_path = request.session.get(f'import_{tipo}_file')
        
        if not file_path or not default_storage.exists(file_path):
            return JsonResponse({'error': 'Archivo no encontrado'}, status=400)
        
        try:
            # Obtener opciones
            opciones = {}
            if tipo == 'clientes':
                opciones['actualizar_passwords'] = request.POST.get('actualizar_passwords') == 'on'
            
            # Crear importador y ejecutar
            full_path = default_storage.path(file_path)
            importer_class = IMPORTERS[tipo]['class']
            importer = importer_class(full_path, request.user, opciones)
            importer.preview()  # Cargar datos primero
            log = importer.ejecutar()
            
            # Limpiar sesión
            del request.session[f'import_{tipo}_file']
            del request.session[f'import_{tipo}_filename']
            if f'import_{tipo}_preview' in request.session:
                del request.session[f'import_{tipo}_preview']
            
            # Eliminar archivo temporal
            default_storage.delete(file_path)
            
            return JsonResponse({
                'success': True,
                'log_id': log.id,
                'creados': log.creados,
                'actualizados': log.actualizados,
                'errores': log.errores
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


def import_progress(request, log_id):
    """Retorna el progreso de una importación."""
    try:
        log = ImportLog.objects.get(id=log_id)
        return JsonResponse({
            'estado': log.estado,
            'progreso': log.progreso,
            'procesados': log.procesados,
            'total': log.total_filas,
            'creados': log.creados,
            'actualizados': log.actualizados,
            'errores': log.errores
        })
    except ImportLog.DoesNotExist:
        return JsonResponse({'error': 'Log no encontrado'}, status=404)


def active_import_status(request):
    """Retorna el estado de la importación activa más reciente del usuario."""
    log = ImportLog.objects.filter(
        usuario=request.user, 
        estado='procesando'
    ).order_by('-created_at').first()
    
    if not log:
        return JsonResponse({'active': False})
    
    return JsonResponse({
        'active': True,
        'log_id': log.id,
        'progreso': log.procesados,
        'total': log.total_filas,
        'estado': log.estado
    })


class ImportLogListView(AdminRequiredMixin, ListView):
    """Lista de logs de importación."""
    model = ImportLog
    template_name = 'imports/logs.html'
    context_object_name = 'logs'
    paginate_by = 20


def download_errors(request, log_id):
    """Descarga CSV con errores de importación."""
    log = get_object_or_404(ImportLog, id=log_id)
    
    import csv
    import io
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Fila', 'Columna', 'Valor', 'Error'])
    
    for error in log.errores_detalle.all():
        writer.writerow([error.fila, error.columna, error.valor, error.mensaje])
    
    response = HttpResponse(output.getvalue(), content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="errores_importacion_{log.id}.csv"'
    return response


def cancel_import(request, log_id):
    """Cancela una importación en proceso."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        log = ImportLog.objects.get(id=log_id)
        
        if log.estado != 'procesando':
            return JsonResponse({'error': 'Solo se pueden cancelar importaciones en proceso'}, status=400)
        
        log.estado = 'cancelado'
        log.save(update_fields=['estado'])
        
        return JsonResponse({
            'success': True,
            'message': 'Importación cancelada'
        })
    except ImportLog.DoesNotExist:
        return JsonResponse({'error': 'Log no encontrado'}, status=404)
