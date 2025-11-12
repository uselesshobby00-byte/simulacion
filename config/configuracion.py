"""
config/configuracion.py
Parámetros de configuración global del sistema
"""

# ==================== CONFIGURACIÓN DE SIMULACIÓN ====================

# Parámetros temporales
DIAS_EVALUACION_PERIODICA = 7  # Cada cuántos días se evalúa el desempeño
DIAS_MINIMOS_CAMBIO_POLITICA = 7  # Días mínimos entre cambios de política

# Parámetros financieros
SALDO_INICIAL_DEFAULT = 100000.0  # Capital inicial por defecto
COSTO_ALMACENAMIENTO_DEFAULT = 0.1  # Costo por unidad por día
COSTO_DESABASTECIMIENTO_BASE = 50.0  # Penalización base por desabastecimiento

# Parámetros de inventario
FACTOR_STOCK_SEGURIDAD = 1.5  # Factor para calcular stock de seguridad
CAPACIDAD_MAXIMA_DEFAULT = 1000  # Capacidad máxima por defecto

# ==================== CONFIGURACIÓN DE INTERFAZ ====================

# Ventana principal
VENTANA_ANCHO = 1400
VENTANA_ALTO = 900
VENTANA_TITULO = "Simulador de Gestión de Inventario"

# Colores
COLOR_FONDO = "#F5F5F5"
COLOR_PRIMARY = "#1976D2"
COLOR_SECONDARY = "#424242"
COLOR_SUCCESS = "#4CAF50"
COLOR_WARNING = "#FF9800"
COLOR_DANGER = "#F44336"
COLOR_INFO = "#2196F3"

# Gráficas
GRAFICA_ANCHO = 8
GRAFICA_ALTO = 6
GRAFICA_DPI = 100

# Estilos de líneas para gráficas
ESTILO_LINEA_INVENTARIO = {'linewidth': 2, 'marker': 'o', 'markersize': 4}
ESTILO_LINEA_FINANZAS = {'linewidth': 2, 'marker': 's', 'markersize': 4}
ESTILO_LINEA_PUNTO_PEDIDO = {'linestyle': '--', 'linewidth': 1, 'alpha': 0.6}

# Colores para productos (gráficas)
COLORES_PRODUCTOS = [
    '#1f77b4',  # azul
    '#ff7f0e',  # naranja
    '#2ca02c',  # verde
    '#d62728',  # rojo
    '#9467bd',  # púrpura
    '#8c564b',  # café
    '#e377c2',  # rosa
    '#7f7f7f',  # gris
    '#bcbd22',  # verde oliva
    '#17becf'   # cian
]

# ==================== CONFIGURACIÓN DE EXPORTACIÓN ====================

# Formatos de archivo
FORMATO_FECHA_EXPORTACION = "%Y-%m-%d_%H-%M-%S"
RUTA_EXPORTACION_DEFAULT = "data/resultados/"

# Nombres de archivos
ARCHIVO_EVENTOS_PEDIDO = "eventos_pedido.csv"
ARCHIVO_EVENTOS_DEMANDA = "eventos_demanda.csv"
ARCHIVO_EVENTOS_RECEPCION = "eventos_recepcion.csv"
ARCHIVO_EVENTOS_VENTA = "eventos_venta.csv"
ARCHIVO_EVENTOS_PENALIZACION = "eventos_penalizacion.csv"
ARCHIVO_RESUMEN = "resumen_simulacion.csv"

# Columnas de archivos CSV
COLUMNAS_PEDIDO = [
    'dia', 'producto_id', 'proveedor', 'cantidad', 
    'costo_total', 'dias_entrega'
]

COLUMNAS_DEMANDA = [
    'dia', 'cliente', 'producto_id', 'cantidad', 
    'tipo_cliente', 'prioridad'
]

COLUMNAS_RECEPCION = [
    'dia', 'producto_id', 'cantidad', 'costo_total', 
    'proveedor'
]

COLUMNAS_VENTA = [
    'dia', 'cliente', 'producto_id', 'cantidad', 
    'ingreso', 'costo'
]

COLUMNAS_PENALIZACION = [
    'dia', 'cliente', 'producto_id', 'cantidad_solicitada',
    'inventario_disponible', 'penalizacion'
]

# ==================== CONFIGURACIÓN DE POLÍTICAS ====================

# Factores de política conservadora
CONSERVADORA_FACTOR_PEDIDO = 1.0
CONSERVADORA_SENSIBILIDAD = 1.0

# Factores de política agresiva
AGRESIVA_FACTOR_PEDIDO = 1.5
AGRESIVA_SENSIBILIDAD = 1.2

# Factores de política adaptativa
ADAPTATIVA_SENSIBILIDAD_MIN = 0.5
ADAPTATIVA_SENSIBILIDAD_MAX = 2.0
ADAPTATIVA_AJUSTE_PASO = 0.2

# ==================== MENSAJES Y TEXTOS ====================

MENSAJES = {
    'bienvenida': "Bienvenido al Simulador de Gestión de Inventario",
    'simulacion_iniciada': "Simulación inicializada correctamente",
    'simulacion_completada': "Simulación completada",
    'error_general': "Ha ocurrido un error en el sistema",
    'exportacion_exitosa': "Datos exportados correctamente",
    'sin_datos': "No hay datos para mostrar",
    'configuracion_guardada': "Configuración guardada correctamente"
}

AYUDA = {
    'metodo_peps': "PEPS (Primero en Entrar, Primero en Salir): Los productos más antiguos se venden primero. Útil para productos perecederos.",
    'metodo_ueps': "UEPS (Último en Entrar, Primero en Salir): Los productos más recientes se venden primero.",
    'metodo_promedio': "Promedio Ponderado: Se calcula un costo promedio de todas las unidades en inventario.",
    'politica_conservadora': "Minimiza costos de almacenamiento pidiendo solo lo necesario.",
    'politica_agresiva': "Minimiza riesgo de desabastecimiento manteniendo más inventario.",
    'politica_adaptativa': "Ajusta dinámicamente según el desempeño del sistema."
}

# ==================== LÍMITES Y VALIDACIONES ====================

# Límites para productos
PRODUCTO_CANTIDAD_MIN = 0
PRODUCTO_CANTIDAD_MAX = 100000
PRODUCTO_COSTO_MIN = 0.01
PRODUCTO_COSTO_MAX = 10000
PRODUCTO_PUNTO_PEDIDO_MIN = 1
PRODUCTO_PUNTO_PEDIDO_MAX = 10000

# Límites para proveedores
PROVEEDOR_TIEMPO_ENTREGA_MIN = 1
PROVEEDOR_TIEMPO_ENTREGA_MAX = 30
PROVEEDOR_FIABILIDAD_MIN = 0.0
PROVEEDOR_FIABILIDAD_MAX = 1.0

# Límites para clientes
CLIENTE_FRECUENCIA_MIN = 1
CLIENTE_FRECUENCIA_MAX = 365
CLIENTE_CANTIDAD_MIN = 1
CLIENTE_CANTIDAD_MAX = 10000
CLIENTE_PRIORIDAD_MIN = 1
CLIENTE_PRIORIDAD_MAX = 5

# Límites para simulación
SIMULACION_DIAS_MIN = 1
SIMULACION_DIAS_MAX = 365

# ==================== FUNCIONES DE UTILIDAD ====================

def validar_rango(valor, minimo, maximo, nombre_campo="valor"):
    """
    Valida que un valor esté dentro de un rango
    
    Args:
        valor: Valor a validar
        minimo: Valor mínimo permitido
        maximo: Valor máximo permitido
        nombre_campo: Nombre del campo para el mensaje de error
        
    Returns:
        True si es válido
        
    Raises:
        ValueError si está fuera del rango
    """
    if not minimo <= valor <= maximo:
        raise ValueError(
            f"{nombre_campo} debe estar entre {minimo} y {maximo}"
        )
    return True


def obtener_color_producto(indice):
    """
    Obtiene un color para un producto según su índice
    
    Args:
        indice: Índice del producto
        
    Returns:
        Color en formato hexadecimal
    """
    return COLORES_PRODUCTOS[indice % len(COLORES_PRODUCTOS)]


def formatear_moneda(monto):
    """
    Formatea un monto como moneda
    
    Args:
        monto: Cantidad a formatear
        
    Returns:
        String formateado
    """
    return f"${monto:,.2f}"


def formatear_porcentaje(valor):
    """
    Formatea un valor como porcentaje
    
    Args:
        valor: Valor a formatear (0-1 o 0-100)
        
    Returns:
        String formateado
    """
    if valor <= 1.0:
        valor *= 100
    return f"{valor:.2f}%"