from django.urls import path
from . import views

app_name = 'imports'

urlpatterns = [
    # Selección de tipo de importación
    path('', views.ImportSelectView.as_view(), name='select'),
    
    # Upload de archivo
    path('<str:tipo>/upload/', views.ImportUploadView.as_view(), name='upload'),
    
    # Preview antes de importar
    path('<str:tipo>/preview/', views.ImportPreviewView.as_view(), name='preview'),
    
    # Ejecutar importación
    path('<str:tipo>/execute/', views.ImportExecuteView.as_view(), name='execute'),
    
    # Progreso (AJAX)
    path('progress/<int:log_id>/', views.import_progress, name='progress'),
    path('active-status/', views.active_import_status, name='active_status'),
    
    # Historial de importaciones
    path('logs/', views.ImportLogListView.as_view(), name='logs'),
    
    # Descargar errores
    path('errors/<int:log_id>/', views.download_errors, name='download_errors'),
    
    # Cancelar importación
    path('cancel/<int:log_id>/', views.cancel_import, name='cancel'),
]
