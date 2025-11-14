"""
gui/__init__.py
Módulo de interfaz gráfica de usuario
"""

from gui.interfaz_principal import InterfazPrincipal
from gui.panel_configuracion import PanelConfiguracion
from gui.panel_productos import PanelProductos
from gui.panel_graficas import PanelGraficas

__all__ = [
    'InterfazPrincipal',
    'PanelConfiguracion',
    'PanelProductos',
    'PanelGraficas'
]