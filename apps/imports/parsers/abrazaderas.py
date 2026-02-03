"""
Parser de descripción para Abrazaderas.
Extrae atributos automáticamente del nombre/descripción del producto.
"""
import re


class AbrazaderaParser:
    """
    Parser para extraer atributos de abrazaderas desde texto.
    Detecta tipo de fabricación, medidas y material del texto.
    """
    
    # Palabras clave para tipo de fabricación
    TIPOS_FABRICACION = {
        'TREFILADA': ['TREFILADA', 'TREFILADO', 'TREFIL', 'TREFI'],
        'LAMINADA': ['LAMINADA', 'LAMINADO', 'LAMIN', 'LAMI'],
        'FORJADA': ['FORJADA', 'FORJADO', 'FORJ'],
    }
    
    # Patrones de materiales
    MATERIALES = {
        'ACERO': ['ACERO', 'AC.', 'AC '],
        'INOX': ['INOX', 'INOXIDABLE', 'ACERO INOX'],
        'GALVANIZADO': ['GALVANIZADO', 'GALV', 'GALVANIZADA', 'GALV.'],
        'BRONCE': ['BRONCE'],
        'ZINC': ['ZINC', 'ZINCADO'],
    }
    
    # Medidas estándar en pulgadas
    MEDIDAS_ESTANDAR = [
        '1/4', '5/16', '3/8', '7/16', '1/2', '9/16', '5/8', '11/16',
        '3/4', '13/16', '7/8', '15/16', '1', '1-1/8', '1-1/4', '1-3/8',
        '1-1/2', '1-5/8', '1-3/4', '2', '2-1/4', '2-1/2', '3', '4'
    ]
    
    # Regex estricta para el formato: "ABRAZADERA [TIPO] DE [MEDIDA] X [ANCHO] X [LARGO] [FORMA]"
    # Ejemplo: ABRAZADERA TREFILADA DE 1/2 X 85 X 260 CURVA
    REGEX_ESTRICTA = re.compile(
        r'ABRAZADERA\s+(?P<tipo>TREFILADA|LAMINADA|FORJADA)\s+(?:DE\s+)?(?P<medida>[^X]+?)\s+X\s+(?P<ancho>\d+)\s+X\s+(?P<largo>\d+)\s+(?P<forma>.*)',
        re.IGNORECASE
    )

    @classmethod
    def parsear(cls, texto):
        """
        Parsea un texto (nombre o descripción) y extrae atributos.
        Intenta primero con el formato estricto, luego fallback a búsqueda por palabras clave.
        """
        if not texto:
            return {'atributos': {}, 'warnings': []}
        
        texto = texto.strip()
        texto_upper = texto.upper()
        atributos = {}
        warnings = []
        
        # 1. Intentar Regex Estricta
        match = cls.REGEX_ESTRICTA.search(texto_upper)
        if match:
            datos = match.groupdict()
            
            atributos['tipo_fabricacion'] = datos['tipo']
            atributos['medida_pulgadas'] = cls.normalizar_medida(datos['medida'])
            atributos['ancho'] = datos['ancho']
            atributos['largo'] = datos['largo']
            atributos['forma'] = datos['forma'].strip()
            
            # Normalizar forma si es necesario (ej: /S/CURVA -> SEMICURVA si se desea, o dejar como está)
            return {
                'atributos': atributos,
                'warnings': []
            }
            
        # 2. Fallback: Búsqueda por palabras clave (Lógica anterior mejorada)
        
        # Detectar tipo de fabricación
        tipo_encontrado = None
        for tipo, palabras in cls.TIPOS_FABRICACION.items():
            for palabra in palabras:
                if palabra in texto_upper:
                    tipo_encontrado = tipo
                    break
            if tipo_encontrado:
                break
        
        if tipo_encontrado:
            atributos['tipo_fabricacion'] = tipo_encontrado
        else:
            warnings.append('No se detectó tipo de fabricación (TREFILADA/LAMINADA)')
        
        # Detectar medidas (pulgadas)
        medida = cls._extraer_medida(texto_upper)
        if medida:
            atributos['medida_pulgadas'] = medida
        else:
            warnings.append('No se detectó medida en pulgadas')
            
        # Detectar ancho y largo si aparecen con formato "X numero" pero sin estructura fija
        # Buscamos patrones como "X 85" o "X85"
        dimensiones = re.findall(r'\s*X\s*(\d+)', texto_upper)
        if len(dimensiones) >= 1:
            atributos['ancho'] = dimensiones[0]
        if len(dimensiones) >= 2:
            atributos['largo'] = dimensiones[1]
        
        # Detectar material
        material_encontrado = None
        for material, palabras in cls.MATERIALES.items():
            for palabra in palabras:
                if palabra in texto_upper:
                    material_encontrado = material
                    break
            if material_encontrado:
                break
        
        if material_encontrado:
            atributos['material'] = material_encontrado
            
        # Detectar forma (búsqueda simple al final si no matcheo regex)
        formas_comunes = ['CURVA', 'PLANA', 'SEMICURVA', '/S/CURVA', 'RECTA']
        for forma in formas_comunes:
            if forma in texto_upper:
                atributos['forma'] = forma
                break
        
        return {
            'atributos': atributos,
            'warnings': warnings
        }
    
    @classmethod
    def _extraer_medida(cls, texto):
        """Extrae la medida del texto."""
        # Primero buscar medidas estándar conocidas
        for medida in cls.MEDIDAS_ESTANDAR:
            # Buscar la medida con contexto (espacio o DE antes)
            if f' {medida}' in texto or f'DE {medida}' in texto or f'DE{medida}' in texto:
                return medida
            # Buscar al final del texto
            if texto.endswith(medida) or texto.endswith(f' {medida}"') or texto.endswith(f' {medida}'):
                return medida
        
        # Buscar patrones de fracciones: X/Y o X-Y/Z
        patron_fraccion = r'\b(\d+(?:-\d+)?/\d+)\b'
        fracciones = re.findall(patron_fraccion, texto)
        if fracciones:
            return fracciones[0]
        
        # Buscar números enteros que puedan ser medidas (1, 2, 3, 4)
        patron_entero = r'\b(1|2|3|4)\b(?!\d)'
        enteros = re.findall(patron_entero, texto)
        # Evitar falsos positivos - solo si está cerca de palabras clave
        for entero in enteros:
            if f' {entero}"' in texto or f' {entero} ' in texto:
                return entero
        
        return None
    
    @classmethod
    def normalizar_medida(cls, medida):
        """Normaliza una medida a formato estándar."""
        if not medida:
            return ''
        
        medida = str(medida).strip()
        
        # Si ya es una fracción conocida, retornar
        if medida in cls.MEDIDAS_ESTANDAR:
            return medida
        
        # Limpiar comillas
        medida = medida.replace('"', '').replace("'", '').strip()
        
        return medida
