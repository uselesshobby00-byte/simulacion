"""
models/enums.py
Enumeraciones utilizadas en el sistema de simulación
"""

from enum import Enum


class MetodoInventario(Enum):
    """Métodos de rotación de inventario"""
    PEPS = "PEPS"  # Primero en Entrar, Primero en Salir
    UEPS = "UEPS"  # Último en Entrar, Primero en Salir
    PROMEDIO = "PROMEDIO"  # Costo Promedio Ponderado


class TipoCliente(Enum):
    """Tipos de cliente según volumen y frecuencia de compra"""
    MINORISTA = "MINORISTA"  # Compra en pequeñas cantidades, alta frecuencia
    MAYORISTA = "MAYORISTA"  # Compra en grandes cantidades, menor frecuencia
    INTERNO = "INTERNO"      # Cliente dentro de la organización
    EXTERNO = "EXTERNO"      # Cliente ajeno a la organización


class PoliticaReposicion(Enum):
    """Estrategias de reposición del gestor de pedidos"""
    CONSERVADORA = "CONSERVADORA"  # Minimiza costos de almacenamiento
    AGRESIVA = "AGRESIVA"          # Minimiza riesgo de desabastecimiento
    ADAPTATIVA = "ADAPTATIVA"      # Cambia según el desempeño del sistema


class TipoEvento(Enum):
    """Tipos de eventos que ocurren en la simulación"""
    VENTA = "VENTA"
    PEDIDO = "PEDIDO"
    RECEPCION = "RECEPCION"
    DESABASTECIMIENTO = "DESABASTECIMIENTO"
    CAMBIO_POLITICA = "CAMBIO_POLITICA"
    RETRASO_ENTREGA = "RETRASO_ENTREGA"