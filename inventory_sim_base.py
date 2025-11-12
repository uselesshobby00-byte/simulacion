"""
Sistema de Simulación de Gestión de Inventario
Simulación de eventos discretos para análisis de políticas de inventario
"""

import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from enum import Enum
import csv

# ==================== ENUMERACIONES ====================

class MetodoInventario(Enum):
    """Métodos de rotación de inventario"""
    PEPS = "PEPS"  # Primero en Entrar, Primero en Salir
    UEPS = "UEPS"  # Último en Entrar, Primero en Salir
    PROMEDIO = "PROMEDIO"

class TipoCliente(Enum):
    """Tipos de cliente según volumen y frecuencia"""
    MINORISTA = "MINORISTA"
    MAYORISTA = "MAYORISTA"
    INTERNO = "INTERNO"
    EXTERNO = "EXTERNO"

class PoliticaReposicion(Enum):
    """Estrategias de reposición del gestor"""
    CONSERVADORA = "CONSERVADORA"  # Minimiza costos de almacenamiento
    AGRESIVA = "AGRESIVA"           # Minimiza desabastecimiento
    ADAPTATIVA = "ADAPTATIVA"       # Cambia según desempeño

# ==================== CLASES DE ENTIDADES ====================

@dataclass
class Producto:
    """Representa un artículo en el inventario"""
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
    
    def agregar_lote(self, cantidad: int, costo: float, fecha: datetime):
        """Agrega un nuevo lote al inventario"""
        self.lotes.append({
            'cantidad': cantidad,
            'costo': costo,
            'fecha_ingreso': fecha
        })
        self.nivel_inventario += cantidad
    
    def retirar_unidades(self, cantidad: int, metodo: MetodoInventario) -> float:
        """Retira unidades según el método de inventario"""
        if cantidad > self.nivel_inventario:
            return 0.0  # No hay suficiente inventario
        
        retiradas = 0
        costo_total = 0.0
        
        if metodo == MetodoInventario.PEPS:
            # Ordenar por fecha más antigua
            self.lotes.sort(key=lambda x: x['fecha_ingreso'])
        elif metodo == MetodoInventario.UEPS:
            # Ordenar por fecha más reciente
            self.lotes.sort(key=lambda x: x['fecha_ingreso'], reverse=True)
        elif metodo == MetodoInventario.PROMEDIO:
            # Calcular costo promedio
            if self.nivel_inventario > 0:
                costo_total = sum(l['cantidad'] * l['costo'] for l in self.lotes)
                costo_promedio = costo_total / self.nivel_inventario
                self.nivel_inventario -= cantidad
                return costo_promedio * cantidad
        
        # Para PEPS y UEPS
        for lote in self.lotes[:]:
            if retiradas >= cantidad:
                break
            
            cantidad_a_retirar = min(lote['cantidad'], cantidad - retiradas)
            costo_total += cantidad_a_retirar * lote['costo']
            lote['cantidad'] -= cantidad_a_retirar
            retiradas += cantidad_a_retirar
            
            if lote['cantidad'] == 0:
                self.lotes.remove(lote)
        
        self.nivel_inventario -= retiradas
        return costo_total


@dataclass
class Proveedor:
    """Proveedor de productos"""
    id: str
    nombre: str
    productos_ofrecidos: List[str]
    tiempo_entrega: int = 5  # días
    costo_base: float = 10.0
    fiabilidad: float = 0.95  # 0-1
    descuento_volumen: Dict[str, tuple] = field(default_factory=dict)  # {producto: (min_cantidad, descuento)}
    
    def calcular_costo(self, producto_id: str, cantidad: int) -> float:
        """Calcula el costo total considerando descuentos"""
        costo = self.costo_base * cantidad
        
        if producto_id in self.descuento_volumen:
            min_cant, descuento = self.descuento_volumen[producto_id]
            if cantidad >= min_cant:
                costo *= (1 - descuento)
        
        return costo
    
    def simular_retraso(self) -> int:
        """Simula si hay retraso en la entrega"""
        if np.random.random() > self.fiabilidad:
            # Hay retraso: 1-3 días adicionales
            return np.random.randint(1, 4)
        return 0


@dataclass
class Cliente:
    """Cliente que genera demanda"""
    id: str
    nombre: str
    tipo: TipoCliente
    productos_solicitados: List[str]
    frecuencia_compra: int = 7  # días
    cantidad_promedio: int = 10
    prioridad: int = 1  # 1-5, donde 5 es más prioritario
    variabilidad: float = 0.2  # desviación estándar relativa
    
    def generar_demanda(self, producto_id: str) -> int:
        """Genera una demanda con variabilidad"""
        if producto_id not in self.productos_solicitados:
            return 0
        
        demanda = max(1, int(np.random.normal(
            self.cantidad_promedio,
            self.cantidad_promedio * self.variabilidad
        )))
        
        return demanda


@dataclass
class Finanzas:
    """Registro financiero del sistema"""
    saldo_inicial: float = 100000.0
    saldo_actual: float = 100000.0
    ingresos_totales: float = 0.0
    egresos_totales: float = 0.0
    
    def registrar_ingreso(self, monto: float, concepto: str, fecha: datetime):
        """Registra un ingreso"""
        self.ingresos_totales += monto
        self.saldo_actual += monto
    
    def registrar_egreso(self, monto: float, concepto: str, fecha: datetime):
        """Registra un egreso"""
        self.egresos_totales += monto
        self.saldo_actual -= monto
    
    @property
    def utilidad_neta(self) -> float:
        """Calcula la utilidad neta"""
        return self.ingresos_totales - self.egresos_totales


class GestorPedidos:
    """Gestor que toma decisiones sobre pedidos"""
    
    def __init__(self, politica: PoliticaReposicion = PoliticaReposicion.CONSERVADORA):
        self.politica = politica
        self.sensibilidad = 1.0
        self.frecuencia_revision = 1  # días
        self.historial_decisiones = []
    
    def evaluar_pedido(self, producto: Producto, proveedores: List[Proveedor]) -> Optional[tuple]:
        """Evalúa si se debe generar un pedido y selecciona proveedor"""
        
        # Verificar si se alcanzó el punto de pedido
        if producto.nivel_inventario > producto.punto_pedido * self.sensibilidad:
            return None
        
        # Calcular cantidad a pedir según política
        cantidad = self._calcular_cantidad_pedido(producto)
        
        # Buscar mejor proveedor
        mejor_proveedor = None
        mejor_costo = float('inf')
        
        for proveedor in proveedores:
            if producto.id in proveedor.productos_ofrecidos:
                costo = proveedor.calcular_costo(producto.id, cantidad)
                if costo < mejor_costo and proveedor.fiabilidad > 0.7:
                    mejor_costo = costo
                    mejor_proveedor = proveedor
        
        if mejor_proveedor:
            return (mejor_proveedor, cantidad, mejor_costo)
        
        return None
    
    def _calcular_cantidad_pedido(self, producto: Producto) -> int:
        """Calcula la cantidad a pedir según la política"""
        if self.politica == PoliticaReposicion.CONSERVADORA:
            # Pedir solo lo necesario para cubrir la demanda estimada
            return int(producto.demanda_estimada * producto.tiempo_reposicion)
        
        elif self.politica == PoliticaReposicion.AGRESIVA:
            # Pedir más para evitar desabastecimiento
            return int(producto.demanda_estimada * producto.tiempo_reposicion * 1.5)
        
        else:  # ADAPTATIVA
            # Ajustar según el nivel actual
            deficit = producto.punto_pedido - producto.nivel_inventario
            return max(deficit, int(producto.demanda_estimada * producto.tiempo_reposicion))
    
    def evaluar_desempeno(self, inventario, finanzas, dias_evaluados: int):
        """Evalúa el desempeño y ajusta la política si es necesario"""
        utilidad = finanzas.utilidad_neta
        
        # Criterios simples de cambio de política
        if self.politica == PoliticaReposicion.CONSERVADORA:
            if utilidad < 0:  # Pérdidas por desabastecimiento
                self.politica = PoliticaReposicion.AGRESIVA
                self.sensibilidad = 1.2
        
        elif self.politica == PoliticaReposicion.AGRESIVA:
            if utilidad < finanzas.saldo_inicial * 0.8:  # Costos excesivos
                self.politica = PoliticaReposicion.CONSERVADORA
                self.sensibilidad = 0.8


# ==================== SIMULADOR PRINCIPAL ====================

class SimuladorInventario:
    """Motor de simulación de eventos discretos"""
    
    def __init__(self, metodo_inventario: MetodoInventario = MetodoInventario.PEPS):
        self.fecha_actual = datetime.now()
        self.dia_simulacion = 0
        self.metodo_inventario = metodo_inventario
        
        # Entidades
        self.productos: Dict[str, Producto] = {}
        self.proveedores: List[Proveedor] = []
        self.clientes: List[Cliente] = []
        self.gestor = GestorPedidos()
        self.finanzas = Finanzas()
        
        # Eventos pendientes
        self.pedidos_pendientes = []
        
        # Costos del sistema
        self.costo_almacenamiento = 0.1  # por unidad por día
        self.costo_desabastecimiento_base = 50.0
        
        # Métricas
        self.eventos_log = []
        self.desabastecimientos = 0
        
    def agregar_producto(self, producto: Producto):
        """Agrega un producto al sistema"""
        self.productos[producto.id] = producto
    
    def agregar_proveedor(self, proveedor: Proveedor):
        """Agrega un proveedor al sistema"""
        self.proveedores.append(proveedor)
    
    def agregar_cliente(self, cliente: Cliente):
        """Agrega un cliente al sistema"""
        self.clientes.append(cliente)
    
    def avanzar_dia(self):
        """Ejecuta un ciclo de simulación (un día)"""
        self.dia_simulacion += 1
        self.fecha_actual += timedelta(days=1)
        
        # 1. Generar demanda de clientes
        self._procesar_demandas()
        
        # 2. Evaluar inventario y generar pedidos
        self._evaluar_inventario()
        
        # 3. Procesar entregas pendientes
        self._procesar_entregas()
        
        # 4. Registrar costos de almacenamiento
        self._registrar_costos_almacenamiento()
        
        # 5. Evaluación periódica (cada 7 días)
        if self.dia_simulacion % 7 == 0:
            self.gestor.evaluar_desempeno(self.productos, self.finanzas, 7)
    
    def _procesar_demandas(self):
        """Procesa las demandas de los clientes activos"""
        for cliente in self.clientes:
            if self.dia_simulacion % cliente.frecuencia_compra == 0:
                for producto_id in cliente.productos_solicitados:
                    if producto_id in self.productos:
                        cantidad = cliente.generar_demanda(producto_id)
                        self._atender_demanda(cliente, producto_id, cantidad)
    
    def _atender_demanda(self, cliente: Cliente, producto_id: str, cantidad: int):
        """Intenta satisfacer una demanda"""
        producto = self.productos[producto_id]
        
        if producto.nivel_inventario >= cantidad:
            # Hay inventario suficiente
            costo = producto.retirar_unidades(cantidad, self.metodo_inventario)
            ingreso = cantidad * producto.precio_venta
            
            self.finanzas.registrar_ingreso(ingreso, f"Venta a {cliente.nombre}", self.fecha_actual)
            
            self.eventos_log.append({
                'dia': self.dia_simulacion,
                'tipo': 'VENTA',
                'cliente': cliente.nombre,
                'producto': producto_id,
                'cantidad': cantidad,
                'ingreso': ingreso
            })
        else:
            # Desabastecimiento
            self.desabastecimientos += 1
            penalizacion = self.costo_desabastecimiento_base * cliente.prioridad
            
            self.finanzas.registrar_egreso(penalizacion, f"Desabastecimiento {cliente.nombre}", self.fecha_actual)
            
            self.eventos_log.append({
                'dia': self.dia_simulacion,
                'tipo': 'DESABASTECIMIENTO',
                'cliente': cliente.nombre,
                'producto': producto_id,
                'cantidad': cantidad,
                'penalizacion': penalizacion
            })
    
    def _evaluar_inventario(self):
        """Evalúa el inventario y genera pedidos si es necesario"""
        for producto in self.productos.values():
            resultado = self.gestor.evaluar_pedido(producto, self.proveedores)
            
            if resultado:
                proveedor, cantidad, costo = resultado
                
                # Crear pedido pendiente
                dias_entrega = proveedor.tiempo_entrega + proveedor.simular_retraso()
                
                self.pedidos_pendientes.append({
                    'producto_id': producto.id,
                    'proveedor': proveedor,
                    'cantidad': cantidad,
                    'costo': costo,
                    'dia_llegada': self.dia_simulacion + dias_entrega
                })
                
                self.eventos_log.append({
                    'dia': self.dia_simulacion,
                    'tipo': 'PEDIDO',
                    'producto': producto.id,
                    'proveedor': proveedor.nombre,
                    'cantidad': cantidad,
                    'costo': costo
                })
    
    def _procesar_entregas(self):
        """Procesa pedidos que llegan en este día"""
        entregas = [p for p in self.pedidos_pendientes if p['dia_llegada'] == self.dia_simulacion]
        
        for entrega in entregas:
            producto = self.productos[entrega['producto_id']]
            producto.agregar_lote(entrega['cantidad'], entrega['costo'] / entrega['cantidad'], self.fecha_actual)
            
            self.finanzas.registrar_egreso(entrega['costo'], f"Compra a {entrega['proveedor'].nombre}", self.fecha_actual)
            
            self.pedidos_pendientes.remove(entrega)
            
            self.eventos_log.append({
                'dia': self.dia_simulacion,
                'tipo': 'RECEPCION',
                'producto': entrega['producto_id'],
                'cantidad': entrega['cantidad'],
                'egreso': entrega['costo']
            })
    
    def _registrar_costos_almacenamiento(self):
        """Registra los costos diarios de almacenamiento"""
        costo_total = 0
        for producto in self.productos.values():
            costo = producto.nivel_inventario * self.costo_almacenamiento
            costo_total += costo
        
        if costo_total > 0:
            self.finanzas.registrar_egreso(costo_total, "Almacenamiento diario", self.fecha_actual)
    
    def obtener_estado(self) -> Dict:
        """Retorna el estado actual de la simulación"""
        return {
            'dia': self.dia_simulacion,
            'productos': {pid: {
                'inventario': p.nivel_inventario,
                'punto_pedido': p.punto_pedido
            } for pid, p in self.productos.items()},
            'finanzas': {
                'saldo': self.finanzas.saldo_actual,
                'ingresos': self.finanzas.ingresos_totales,
                'egresos': self.finanzas.egresos_totales,
                'utilidad': self.finanzas.utilidad_neta
            },
            'desabastecimientos': self.desabastecimientos,
            'politica': self.gestor.politica.value
        }


# ==================== EJEMPLO DE USO ====================

if __name__ == "__main__":
    # Crear simulador
    sim = SimuladorInventario(MetodoInventario.PEPS)
    
    # Crear productos
    producto1 = Producto(
        id="PROD001",
        nombre="Tornillo M6",
        costo_unitario=0.5,
        precio_venta=1.2,
        punto_pedido=50,
        demanda_estimada=10,
        tiempo_reposicion=3
    )
    sim.agregar_producto(producto1)
    
    # Crear proveedor
    proveedor1 = Proveedor(
        id="PROV001",
        nombre="Suministros ABC",
        productos_ofrecidos=["PROD001"],
        tiempo_entrega=3,
        costo_base=0.5,
        fiabilidad=0.95,
        descuento_volumen={"PROD001": (100, 0.1)}
    )
    sim.agregar_proveedor(proveedor1)
    
    # Crear cliente
    cliente1 = Cliente(
        id="CLI001",
        nombre="Ferretería XYZ",
        tipo=TipoCliente.MINORISTA,
        productos_solicitados=["PROD001"],
        frecuencia_compra=3,
        cantidad_promedio=15,
        prioridad=3
    )
    sim.agregar_cliente(cliente1)
    
    # Simular 30 días
    print("Iniciando simulación...")
    for _ in range(30):
        sim.avanzar_dia()
    
    # Mostrar resultados
    estado = sim.obtener_estado()
    print(f"\n=== Resultados después de {estado['dia']} días ===")
    print(f"Saldo actual: ${estado['finanzas']['saldo']:.2f}")
    print(f"Utilidad neta: ${estado['finanzas']['utilidad']:.2f}")
    print(f"Desabastecimientos: {estado['desabastecimientos']}")
    print(f"Política actual: {estado['politica']}")
    
    for pid, datos in estado['productos'].items():
        print(f"\nProducto {pid}:")
        print(f"  Inventario: {datos['inventario']} unidades")
        print(f"  Punto de pedido: {datos['punto_pedido']}")
