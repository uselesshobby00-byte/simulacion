"""
config/__init__.py
Módulo de configuración
"""

from config.configuracion import *

__all__ = [
    'DIAS_EVALUACION_PERIODICA',
    'SALDO_INICIAL_DEFAULT',
    'COSTO_ALMACENAMIENTO_DEFAULT',
    'COSTO_DESABASTECIMIENTO_BASE',
    'VENTANA_ANCHO',
    'VENTANA_ALTO',
    'COLORES_PRODUCTOS',
    'MENSAJES',
    'AYUDA',
    'validar_rango',
    'obtener_color_producto',
    'formatear_moneda',
    'formatear_porcentaje'
]