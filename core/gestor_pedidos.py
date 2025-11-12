"""
core/gestor_pedidos.py
Clase GestorPedidos - Lógica de decisiones de reposición de inventario
"""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict
from models.producto import Producto
from models.proveedor import Proveedor
from models.enums import PoliticaReposicion


@dataclass
class DecisionPedido:
    """
    Representa una decisión de pedido tomada por el gestor
    
    Attributes:
        producto_id: ID del producto
        proveedor: Proveedor seleccionado
        cantidad: Cantidad a pedir
        costo_total: Costo total del pedido
        razon: Razón de la decisión
        dia: Día en que se tomó la decisión
    """
    producto_id: str
    proveedor: Proveedor
    cantidad: int
    costo_total: float
    razon: str
    dia: int


class GestorPedidos:
    """
    Gestor que toma decisiones sobre cuándo y cuánto pedir a los proveedores
    
    El gestor monitorea el inventario, evalúa la demanda y decide cuándo
    generar órdenes de reposición según la política configurada.
    
    Attributes:
        politica: Estrategia de reposición (CONSERVADORA, AGRESIVA, ADAPTATIVA)
        sensibilidad: Factor de ajuste del punto de pedido (0.5-2.0)
        frecuencia_revision: Cada cuántos días revisa el inventario
        historial_decisiones: Lista de decisiones tomadas
    """
    
    def __init__(self, politica: PoliticaReposicion = PoliticaReposicion.CONSERVADORA):
        self.politica = politica
        self.sensibilidad = 1.0
        self.frecuencia_revision = 1  # días
        self.historial_decisiones: List[DecisionPedido] = []
        
        # Métricas de desempeño
        self.pedidos_generados = 0
        self.costo_total_pedidos = 0.0
        self.ultimo_cambio_politica = 0
    
    def evaluar_pedido(self, producto: Producto, proveedores: List[Proveedor], 
                      dia_actual: int) -> Optional[DecisionPedido]:
        """
        Evalúa si se debe generar un pedido para un producto
        
        Args:
            producto: Producto a evaluar
            proveedores: Lista de proveedores disponibles
            dia_actual: Día actual de la simulación
            
        Returns:
            DecisionPedido si se debe pedir, None si no
        """
        # Verificar si se alcanzó el punto de pedido
        if not producto.necesita_reposicion(self.sensibilidad):
            return None
        
        # Calcular cantidad a pedir según política
        cantidad = self._calcular_cantidad_pedido(producto)
        
        if cantidad <= 0:
            return None
        
        # Buscar mejor proveedor
        mejor_proveedor = self._seleccionar_proveedor(
            producto, proveedores, cantidad
        )
        
        if mejor_proveedor is None:
            return None
        
        # Calcular costo total
        costo_total = mejor_proveedor.calcular_costo_total(
            producto.id, cantidad, producto.costo_unitario
        )
        
        # Crear decisión
        decision = DecisionPedido(
            producto_id=producto.id,
            proveedor=mejor_proveedor,
            cantidad=cantidad,
            costo_total=costo_total,
            razon=f"Política: {self.politica.value}, Nivel: {producto.nivel_inventario}",
            dia=dia_actual
        )
        
        # Registrar decisión
        self.historial_decisiones.append(decision)
        self.pedidos_generados += 1
        self.costo_total_pedidos += costo_total
        
        return decision
    
    def _calcular_cantidad_pedido(self, producto: Producto) -> int:
        """
        Calcula la cantidad a pedir según la política activa
        
        Args:
            producto: Producto para el cual calcular la cantidad
            
        Returns:
            Cantidad a pedir
        """
        if self.politica == PoliticaReposicion.CONSERVADORA:
            # Pedir solo lo necesario para cubrir demanda durante tiempo de reposición
            cantidad = int(producto.demanda_estimada * producto.tiempo_reposicion)
            
            # No exceder el déficit actual
            deficit = max(0, producto.punto_pedido - producto.nivel_inventario)
            cantidad = min(cantidad, deficit + int(producto.demanda_estimada))
        
        elif self.politica == PoliticaReposicion.AGRESIVA:
            # Pedir más para evitar desabastecimiento
            # Cubrir demanda + stock de seguridad
            cantidad = int(
                producto.demanda_estimada * producto.tiempo_reposicion * 1.5 +
                producto.calcular_stock_seguridad()
            )
        
        else:  # ADAPTATIVA
            # Ajustar según el nivel actual y la capacidad
            deficit = producto.punto_pedido - producto.nivel_inventario
            cantidad_base = int(producto.demanda_estimada * producto.tiempo_reposicion)
            
            # Si el déficit es grande, pedir más
            if deficit > producto.punto_pedido * 0.5:
                cantidad = max(deficit, cantidad_base * 1.3)
            else:
                cantidad = cantidad_base
        
        # Asegurar que no exceda la capacidad máxima
        espacio_disponible = producto.capacidad_maxima - producto.nivel_inventario
        cantidad = min(int(cantidad), espacio_disponible)
        
        return max(0, cantidad)
    
    def _seleccionar_proveedor(self, producto: Producto, 
                              proveedores: List[Proveedor], 
                              cantidad: int) -> Optional[Proveedor]:
        """
        Selecciona el mejor proveedor para un pedido
        
        Args:
            producto: Producto a pedir
            proveedores: Lista de proveedores disponibles
            cantidad: Cantidad a pedir
            
        Returns:
            Mejor proveedor o None si ninguno puede atender
        """
        proveedores_validos = []
        
        # Filtrar proveedores que pueden atender el pedido
        for proveedor in proveedores:
            if proveedor.puede_atender_pedido(producto.id, cantidad):
                costo = proveedor.calcular_costo_total(
                    producto.id, cantidad, producto.costo_unitario
                )
                
                # Calcular score del proveedor
                # Menor costo y mayor fiabilidad es mejor
                score = costo * (2 - proveedor.fiabilidad)  # Penalizar baja fiabilidad
                
                proveedores_validos.append({
                    'proveedor': proveedor,
                    'costo': costo,
                    'score': score
                })
        
        if not proveedores_validos:
            return None
        
        # Seleccionar el proveedor con mejor score (menor es mejor)
        mejor = min(proveedores_validos, key=lambda x: x['score'])
        return mejor['proveedor']
    
    def evaluar_desempeno(self, metricas: Dict, dia_actual: int):
        """
        Evalúa el desempeño del sistema y ajusta la política si es necesario
        
        Args:
            metricas: Diccionario con métricas del sistema
                - utilidad_neta: Utilidad neta actual
                - desabastecimientos: Número de desabastecimientos
                - inventario_promedio: Nivel promedio de inventario
                - saldo_inicial: Saldo inicial del sistema
            dia_actual: Día actual de la simulación
        """
        # Solo evaluar si han pasado al menos 7 días desde el último cambio
        if dia_actual - self.ultimo_cambio_politica < 7:
            return
        
        utilidad = metricas.get('utilidad_neta', 0)
        desabastecimientos = metricas.get('desabastecimientos', 0)
        inventario_promedio = metricas.get('inventario_promedio', 0)
        saldo_inicial = metricas.get('saldo_inicial', 100000)
        
        # Evaluar según la política actual
        if self.politica == PoliticaReposicion.CONSERVADORA:
            # Si hay muchos desabastecimientos, cambiar a agresiva
            if desabastecimientos > 5:
                self._cambiar_politica(PoliticaReposicion.AGRESIVA, dia_actual)
                self.sensibilidad = 1.2
            # Si la utilidad es muy negativa, mantener pero ajustar sensibilidad
            elif utilidad < -saldo_inicial * 0.2:
                self.sensibilidad = max(0.5, self.sensibilidad - 0.1)
        
        elif self.politica == PoliticaReposicion.AGRESIVA:
            # Si la utilidad es muy negativa (exceso de costos), cambiar a conservadora
            if utilidad < -saldo_inicial * 0.3:
                self._cambiar_politica(PoliticaReposicion.CONSERVADORA, dia_actual)
                self.sensibilidad = 0.8
            # Si hay pocos desabastecimientos y buena utilidad, considerar conservadora
            elif desabastecimientos < 2 and utilidad > 0:
                self._cambiar_politica(PoliticaReposicion.CONSERVADORA, dia_actual)
                self.sensibilidad = 1.0
        
        else:  # ADAPTATIVA
            # La política adaptativa cambia dinámicamente
            if desabastecimientos > 3:
                self.sensibilidad = min(2.0, self.sensibilidad + 0.2)
            elif desabastecimientos == 0 and utilidad > 0:
                self.sensibilidad = max(0.5, self.sensibilidad - 0.1)
    
    def _cambiar_politica(self, nueva_politica: PoliticaReposicion, dia_actual: int):
        """
        Cambia la política de reposición
        
        Args:
            nueva_politica: Nueva política a aplicar
            dia_actual: Día actual
        """
        if nueva_politica != self.politica:
            self.politica = nueva_politica
            self.ultimo_cambio_politica = dia_actual
    
    def obtener_estadisticas(self) -> Dict:
        """
        Obtiene estadísticas del gestor
        
        Returns:
            Diccionario con estadísticas
        """
        return {
            'politica_actual': self.politica.value,
            'sensibilidad': self.sensibilidad,
            'pedidos_generados': self.pedidos_generados,
            'costo_total_pedidos': self.costo_total_pedidos,
            'costo_promedio_pedido': (
                self.costo_total_pedidos / self.pedidos_generados 
                if self.pedidos_generados > 0 else 0
            ),
            'ultimo_cambio_politica': self.ultimo_cambio_politica
        }
    
    def exportar_historial(self) -> List[Dict]:
        """
        Exporta el historial de decisiones
        
        Returns:
            Lista de decisiones como diccionarios
        """
        return [
            {
                'dia': d.dia,
                'producto_id': d.producto_id,
                'proveedor': d.proveedor.nombre,
                'cantidad': d.cantidad,
                'costo_total': d.costo_total,
                'razon': d.razon
            }
            for d in self.historial_decisiones
        ]
    
    def reiniciar(self):
        """Reinicia el gestor a su estado inicial"""
        self.sensibilidad = 1.0
        self.historial_decisiones = []
        self.pedidos_generados = 0
        self.costo_total_pedidos = 0.0
        self.ultimo_cambio_politica = 0
    
    def __repr__(self) -> str:
        """Representación en string del gestor"""
        return f"GestorPedidos(Política: {self.politica.value}, Sensibilidad: {self.sensibilidad})"