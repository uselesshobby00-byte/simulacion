"""
models/cliente.py
Clase Cliente - Entidad que genera demanda de productos
"""

from dataclasses import dataclass, field
from typing import List, Dict
import numpy as np
from models.enums import TipoCliente


@dataclass
class Cliente:
    """
    Representa un cliente que genera demanda de productos
    
    Attributes:
        id: Identificador único del cliente
        nombre: Nombre del cliente
        tipo: Tipo de cliente (MINORISTA, MAYORISTA, INTERNO, EXTERNO)
        productos_solicitados: Lista de IDs de productos que compra
        frecuencia_compra: Cada cuántos días realiza pedidos
        cantidad_promedio: Cantidad promedio que compra por producto
        prioridad: Nivel de prioridad (1-5, donde 5 es máxima prioridad)
        variabilidad: Desviación estándar relativa de la demanda (0-1)
        activo: Si el cliente está actualmente activo
    """
    
    id: str
    nombre: str
    tipo: TipoCliente
    productos_solicitados: List[str]
    frecuencia_compra: int = 7  # días
    cantidad_promedio: int = 10
    prioridad: int = 1  # 1-5
    variabilidad: float = 0.2  # 0-1
    activo: bool = True
    
    # Estadísticas del cliente
    total_compras: int = field(default=0, init=False)
    total_gastado: float = field(default=0.0, init=False)
    pedidos_realizados: int = field(default=0, init=False)
    desabastecimientos_sufridos: int = field(default=0, init=False)
    
    def __post_init__(self):
        """Validaciones después de la inicialización"""
        if not 1 <= self.prioridad <= 5:
            raise ValueError("La prioridad debe estar entre 1 y 5")
        
        if not 0 <= self.variabilidad <= 1:
            raise ValueError("La variabilidad debe estar entre 0 y 1")
        
        if self.frecuencia_compra < 1:
            raise ValueError("La frecuencia de compra debe ser al menos 1 día")
        
        if self.cantidad_promedio < 1:
            raise ValueError("La cantidad promedio debe ser al menos 1")
    
    def generar_demanda(self, producto_id: str) -> int:
        """
        Genera una demanda aleatoria para un producto específico
        
        Args:
            producto_id: ID del producto solicitado
            
        Returns:
            Cantidad de unidades demandadas (0 si no solicita ese producto)
        """
        if producto_id not in self.productos_solicitados:
            return 0
        
        if not self.activo:
            return 0
        
        # Ajustar cantidad promedio según el tipo de cliente
        cantidad_base = self._ajustar_por_tipo_cliente()
        
        # Generar demanda con variabilidad (distribución normal)
        desviacion = cantidad_base * self.variabilidad
        demanda = np.random.normal(cantidad_base, desviacion)
        
        # Asegurar que la demanda sea positiva y entera
        demanda = max(1, int(round(demanda)))
        
        return demanda
    
    def _ajustar_por_tipo_cliente(self) -> int:
        """
        Ajusta la cantidad promedio según el tipo de cliente
        
        Returns:
            Cantidad ajustada
        """
        if self.tipo == TipoCliente.MAYORISTA:
            return int(self.cantidad_promedio * 2.0)  # Mayoristas compran el doble
        elif self.tipo == TipoCliente.MINORISTA:
            return self.cantidad_promedio
        elif self.tipo == TipoCliente.INTERNO:
            return int(self.cantidad_promedio * 1.2)  # Clientes internos +20%
        else:  # EXTERNO
            return int(self.cantidad_promedio * 0.8)  # Clientes externos -20%
    
    def debe_realizar_pedido(self, dia_actual: int) -> bool:
        """
        Determina si el cliente debe realizar un pedido en el día actual
        
        Args:
            dia_actual: Día actual de la simulación
            
        Returns:
            True si debe realizar pedido
        """
        if not self.activo:
            return False
        
        return dia_actual % self.frecuencia_compra == 0
    
    def registrar_compra(self, cantidad: int, monto_gastado: float):
        """
        Registra una compra exitosa del cliente
        
        Args:
            cantidad: Cantidad de unidades compradas
            monto_gastado: Monto total de la compra
        """
        self.total_compras += cantidad
        self.total_gastado += monto_gastado
        self.pedidos_realizados += 1
    
    def registrar_desabastecimiento(self):
        """Registra un caso de desabastecimiento"""
        self.desabastecimientos_sufridos += 1
    
    def calcular_nivel_satisfaccion(self) -> float:
        """
        Calcula el nivel de satisfacción del cliente
        
        Returns:
            Porcentaje de satisfacción (0-1)
        """
        if self.pedidos_realizados == 0:
            return 1.0  # Sin pedidos, asumimos satisfacción inicial
        
        # Satisfacción = pedidos exitosos / total de pedidos
        pedidos_exitosos = self.pedidos_realizados - self.desabastecimientos_sufridos
        satisfaccion = pedidos_exitosos / self.pedidos_realizados
        
        return max(0.0, min(1.0, satisfaccion))
    
    def obtener_penalizacion_desabastecimiento(self, costo_base: float) -> float:
        """
        Calcula la penalización por desabastecimiento según prioridad
        
        Args:
            costo_base: Costo base de la penalización
            
        Returns:
            Monto de la penalización
        """
        # La penalización aumenta con la prioridad del cliente
        factor_prioridad = self.prioridad / 5.0  # Normalizar a 0-1
        return costo_base * (1 + factor_prioridad)
    
    def cambiar_estado(self, activo: bool):
        """
        Cambia el estado de actividad del cliente
        
        Args:
            activo: Nuevo estado
        """
        self.activo = activo
    
    def obtener_estadisticas(self) -> Dict:
        """
        Retorna estadísticas del cliente
        
        Returns:
            Diccionario con estadísticas
        """
        return {
            'id': self.id,
            'nombre': self.nombre,
            'tipo': self.tipo.value,
            'prioridad': self.prioridad,
            'total_compras': self.total_compras,
            'total_gastado': self.total_gastado,
            'pedidos_realizados': self.pedidos_realizados,
            'desabastecimientos': self.desabastecimientos_sufridos,
            'satisfaccion': self.calcular_nivel_satisfaccion(),
            'activo': self.activo
        }
    
    def obtener_informacion(self) -> Dict:
        """
        Retorna información general del cliente
        
        Returns:
            Diccionario con información del cliente
        """
        return {
            'id': self.id,
            'nombre': self.nombre,
            'tipo': self.tipo.value,
            'frecuencia_compra': self.frecuencia_compra,
            'cantidad_promedio': self.cantidad_promedio,
            'prioridad': self.prioridad,
            'variabilidad': self.variabilidad,
            'num_productos': len(self.productos_solicitados),
            'activo': self.activo
        }
    
    def reiniciar_estadisticas(self):
        """Reinicia las estadísticas del cliente"""
        self.total_compras = 0
        self.total_gastado = 0.0
        self.pedidos_realizados = 0
        self.desabastecimientos_sufridos = 0
    
    def __repr__(self) -> str:
        """Representación en string del cliente"""
        estado = "Activo" if self.activo else "Inactivo"
        return f"Cliente({self.id}, {self.nombre}, {self.tipo.value}, {estado})"