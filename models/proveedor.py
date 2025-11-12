"""
models/proveedor.py
Clase Proveedor - Entidad que suministra productos
"""

from dataclasses import dataclass, field
from typing import List, Dict, Tuple
import numpy as np


@dataclass
class Proveedor:
    """
    Representa un proveedor de productos
    
    Attributes:
        id: Identificador único del proveedor
        nombre: Nombre del proveedor
        productos_ofrecidos: Lista de IDs de productos que suministra
        tiempo_entrega: Días promedio de entrega
        costo_base: Costo base por unidad (puede variar por producto)
        fiabilidad: Probabilidad de cumplir con el tiempo de entrega (0-1)
        descuento_volumen: Dict con condiciones de descuento por producto
        minimo_pedido: Cantidad mínima para realizar un pedido
        frecuencia_envios: Cada cuántos días acepta pedidos
    """
    
    id: str
    nombre: str
    productos_ofrecidos: List[str]
    tiempo_entrega: int = 5  # días
    costo_base: float = 10.0
    fiabilidad: float = 0.95  # 0-1
    descuento_volumen: Dict[str, Tuple[int, float]] = field(default_factory=dict)
    minimo_pedido: int = 10
    frecuencia_envios: int = 1  # días
    
    def __post_init__(self):
        """Validaciones después de la inicialización"""
        if not 0 <= self.fiabilidad <= 1:
            raise ValueError("La fiabilidad debe estar entre 0 y 1")
        
        if self.tiempo_entrega < 1:
            raise ValueError("El tiempo de entrega debe ser al menos 1 día")
        
        if self.costo_base < 0:
            raise ValueError("El costo base no puede ser negativo")
    
    def calcular_costo_total(self, producto_id: str, cantidad: int, 
                            costo_unitario_producto: float = None) -> float:
        """
        Calcula el costo total de un pedido considerando descuentos
        
        Args:
            producto_id: ID del producto
            cantidad: Cantidad a pedir
            costo_unitario_producto: Costo base del producto (opcional)
            
        Returns:
            Costo total del pedido
        """
        if cantidad < 0:
            raise ValueError("La cantidad no puede ser negativa")
        
        if producto_id not in self.productos_ofrecidos:
            raise ValueError(f"El proveedor no ofrece el producto {producto_id}")
        
        # Usar el costo del producto si se proporciona, sino usar el costo_base
        costo = costo_unitario_producto if costo_unitario_producto else self.costo_base
        costo_total = costo * cantidad
        
        # Aplicar descuento por volumen si aplica
        if producto_id in self.descuento_volumen:
            min_cantidad, porcentaje_descuento = self.descuento_volumen[producto_id]
            if cantidad >= min_cantidad:
                costo_total *= (1 - porcentaje_descuento)
        
        return costo_total
    
    def puede_atender_pedido(self, producto_id: str, cantidad: int) -> bool:
        """
        Verifica si el proveedor puede atender un pedido
        
        Args:
            producto_id: ID del producto
            cantidad: Cantidad solicitada
            
        Returns:
            True si puede atender el pedido
        """
        if producto_id not in self.productos_ofrecidos:
            return False
        
        if cantidad < self.minimo_pedido:
            return False
        
        return True
    
    def simular_retraso(self) -> int:
        """
        Simula si habrá retraso en la entrega basado en fiabilidad
        
        Returns:
            Días de retraso adicional (0 si no hay retraso)
        """
        # Probabilidad de retraso = 1 - fiabilidad
        if np.random.random() > self.fiabilidad:
            # Hay retraso: entre 1 y 3 días adicionales
            return np.random.randint(1, 4)
        return 0
    
    def calcular_tiempo_entrega_real(self) -> int:
        """
        Calcula el tiempo de entrega real incluyendo posibles retrasos
        
        Returns:
            Días totales hasta la entrega
        """
        return self.tiempo_entrega + self.simular_retraso()
    
    def obtener_descuento_aplicable(self, producto_id: str, cantidad: int) -> float:
        """
        Obtiene el porcentaje de descuento aplicable
        
        Args:
            producto_id: ID del producto
            cantidad: Cantidad a pedir
            
        Returns:
            Porcentaje de descuento (0 si no aplica)
        """
        if producto_id not in self.descuento_volumen:
            return 0.0
        
        min_cantidad, porcentaje_descuento = self.descuento_volumen[producto_id]
        if cantidad >= min_cantidad:
            return porcentaje_descuento
        
        return 0.0
    
    def agregar_descuento_volumen(self, producto_id: str, 
                                  cantidad_minima: int, 
                                  porcentaje_descuento: float):
        """
        Agrega o actualiza un descuento por volumen
        
        Args:
            producto_id: ID del producto
            cantidad_minima: Cantidad mínima para aplicar descuento
            porcentaje_descuento: Porcentaje de descuento (0-1)
        """
        if producto_id not in self.productos_ofrecidos:
            raise ValueError(f"El proveedor no ofrece el producto {producto_id}")
        
        if not 0 <= porcentaje_descuento <= 1:
            raise ValueError("El descuento debe estar entre 0 y 1")
        
        if cantidad_minima < 1:
            raise ValueError("La cantidad mínima debe ser al menos 1")
        
        self.descuento_volumen[producto_id] = (cantidad_minima, porcentaje_descuento)
    
    def obtener_informacion(self) -> Dict:
        """
        Retorna un diccionario con la información del proveedor
        
        Returns:
            Diccionario con todos los atributos relevantes
        """
        return {
            'id': self.id,
            'nombre': self.nombre,
            'num_productos': len(self.productos_ofrecidos),
            'tiempo_entrega': self.tiempo_entrega,
            'fiabilidad': self.fiabilidad,
            'costo_base': self.costo_base,
            'minimo_pedido': self.minimo_pedido,
            'frecuencia_envios': self.frecuencia_envios,
            'tiene_descuentos': len(self.descuento_volumen) > 0
        }
    
    def comparar_con(self, otro_proveedor: 'Proveedor', 
                     producto_id: str, cantidad: int) -> Dict:
        """
        Compara este proveedor con otro para un pedido específico
        
        Args:
            otro_proveedor: Otro proveedor a comparar
            producto_id: ID del producto
            cantidad: Cantidad a pedir
            
        Returns:
            Diccionario con la comparación
        """
        if not self.puede_atender_pedido(producto_id, cantidad):
            return {'puede_atender': False, 'razon': 'Este proveedor no puede atender'}
        
        if not otro_proveedor.puede_atender_pedido(producto_id, cantidad):
            return {'puede_atender': True, 'mejor_opcion': True, 
                   'razon': 'El otro proveedor no puede atender'}
        
        costo_este = self.calcular_costo_total(producto_id, cantidad)
        costo_otro = otro_proveedor.calcular_costo_total(producto_id, cantidad)
        
        return {
            'puede_atender': True,
            'costo_este': costo_este,
            'costo_otro': costo_otro,
            'mejor_precio': costo_este < costo_otro,
            'diferencia_costo': abs(costo_este - costo_otro),
            'mas_fiable': self.fiabilidad > otro_proveedor.fiabilidad,
            'mas_rapido': self.tiempo_entrega < otro_proveedor.tiempo_entrega
        }
    
    def __repr__(self) -> str:
        """Representación en string del proveedor"""
        return f"Proveedor({self.id}, {self.nombre}, Productos: {len(self.productos_ofrecidos)})"