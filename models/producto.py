"""
models/producto.py
Clase Producto - Representa un artículo en el inventario
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict
from models.enums import MetodoInventario


@dataclass
class Producto:
    """
    Representa un producto almacenado en la bodega
    
    Attributes:
        id: Identificador único del producto
        nombre: Nombre descriptivo del producto
        nivel_inventario: Cantidad actual en bodega
        costo_unitario: Precio de compra por unidad
        precio_venta: Precio de venta por unidad
        punto_pedido: Umbral para generar orden de reposición
        demanda_estimada: Demanda promedio esperada
        tiempo_reposicion: Días que tarda en llegar un pedido
        capacidad_maxima: Límite de almacenamiento
        lotes: Lista de lotes con fecha de ingreso para rotación
    """
    
    id: str
    nombre: str
    nivel_inventario: int = 0
    costo_unitario: float = 0.0
    precio_venta: float = 0.0
    punto_pedido: int = 10
    demanda_estimada: float = 5.0
    tiempo_reposicion: int = 3  # días
    capacidad_maxima: int = 1000
    
    # Registro de lotes con fecha de ingreso
    lotes: List[Dict] = field(default_factory=list)
    
    def __post_init__(self):
        """Validaciones después de la inicialización"""
        if self.precio_venta <= self.costo_unitario:
            raise ValueError("El precio de venta debe ser mayor al costo unitario")
        
        if self.punto_pedido < 0:
            raise ValueError("El punto de pedido no puede ser negativo")
    
    def agregar_lote(self, cantidad: int, costo: float, fecha: datetime) -> bool:
        """
        Agrega un nuevo lote al inventario
        
        Args:
            cantidad: Número de unidades a agregar
            costo: Costo unitario del lote
            fecha: Fecha de ingreso del lote
            
        Returns:
            True si se agregó exitosamente, False si excede capacidad
        """
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser positiva")
        
        if self.nivel_inventario + cantidad > self.capacidad_maxima:
            return False  # Excede capacidad máxima
        
        self.lotes.append({
            'cantidad': cantidad,
            'costo': costo,
            'fecha_ingreso': fecha
        })
        self.nivel_inventario += cantidad
        return True
    
    def retirar_unidades(self, cantidad: int, metodo: MetodoInventario) -> tuple[float, bool]:
        """
        Retira unidades según el método de inventario
        
        Args:
            cantidad: Número de unidades a retirar
            metodo: Método de rotación (PEPS, UEPS, PROMEDIO)
            
        Returns:
            Tupla (costo_total, exito) donde:
                - costo_total: Costo de las unidades retiradas
                - exito: True si se pudo retirar toda la cantidad
        """
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser positiva")
        
        if cantidad > self.nivel_inventario:
            return 0.0, False  # No hay suficiente inventario
        
        retiradas = 0
        costo_total = 0.0
        
        if metodo == MetodoInventario.PROMEDIO:
            # Calcular costo promedio ponderado
            if self.nivel_inventario > 0:
                costo_total_inventario = sum(l['cantidad'] * l['costo'] for l in self.lotes)
                costo_promedio = costo_total_inventario / self.nivel_inventario
                self.nivel_inventario -= cantidad
                
                # Restar proporcionalmente de todos los lotes
                factor = cantidad / (self.nivel_inventario + cantidad)
                for lote in self.lotes:
                    lote['cantidad'] = int(lote['cantidad'] * (1 - factor))
                
                # Limpiar lotes vacíos
                self.lotes = [l for l in self.lotes if l['cantidad'] > 0]
                
                return costo_promedio * cantidad, True
        
        # Para PEPS y UEPS, ordenar lotes
        if metodo == MetodoInventario.PEPS:
            # Ordenar por fecha más antigua primero
            self.lotes.sort(key=lambda x: x['fecha_ingreso'])
        elif metodo == MetodoInventario.UEPS:
            # Ordenar por fecha más reciente primero
            self.lotes.sort(key=lambda x: x['fecha_ingreso'], reverse=True)
        
        # Retirar de los lotes según el orden
        lotes_a_eliminar = []
        for i, lote in enumerate(self.lotes):
            if retiradas >= cantidad:
                break
            
            cantidad_a_retirar = min(lote['cantidad'], cantidad - retiradas)
            costo_total += cantidad_a_retirar * lote['costo']
            lote['cantidad'] -= cantidad_a_retirar
            retiradas += cantidad_a_retirar
            
            if lote['cantidad'] == 0:
                lotes_a_eliminar.append(i)
        
        # Eliminar lotes vacíos
        for i in reversed(lotes_a_eliminar):
            self.lotes.pop(i)
        
        self.nivel_inventario -= retiradas
        return costo_total, True
    
    def necesita_reposicion(self, factor_sensibilidad: float = 1.0) -> bool:
        """
        Determina si el producto necesita reposición
        
        Args:
            factor_sensibilidad: Factor para ajustar el punto de pedido
            
        Returns:
            True si el nivel está por debajo del punto de pedido ajustado
        """
        return self.nivel_inventario <= (self.punto_pedido * factor_sensibilidad)
    
    def calcular_stock_seguridad(self) -> int:
        """
        Calcula el stock de seguridad recomendado
        
        Returns:
            Unidades de stock de seguridad
        """
        # Stock de seguridad = demanda durante tiempo de reposición * factor de seguridad
        return int(self.demanda_estimada * self.tiempo_reposicion * 1.5)
    
    def obtener_informacion(self) -> Dict:
        """
        Retorna un diccionario con la información del producto
        
        Returns:
            Diccionario con todos los atributos relevantes
        """
        return {
            'id': self.id,
            'nombre': self.nombre,
            'nivel_inventario': self.nivel_inventario,
            'costo_unitario': self.costo_unitario,
            'precio_venta': self.precio_venta,
            'punto_pedido': self.punto_pedido,
            'demanda_estimada': self.demanda_estimada,
            'tiempo_reposicion': self.tiempo_reposicion,
            'capacidad_maxima': self.capacidad_maxima,
            'num_lotes': len(self.lotes),
            'stock_seguridad': self.calcular_stock_seguridad()
        }
    
    def __repr__(self) -> str:
        """Representación en string del producto"""
        return f"Producto({self.id}, {self.nombre}, Inventario: {self.nivel_inventario})"