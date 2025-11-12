"""
core/simulador.py
Motor principal de simulación de eventos discretos
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass

from models.producto import Producto
from models.proveedor import Proveedor
from models.cliente import Cliente
from models.finanzas import Finanzas
from models.enums import MetodoInventario, TipoEvento, PoliticaReposicion
from core.gestor_pedidos import GestorPedidos


@dataclass
class PedidoPendiente:
    """Representa un pedido en tránsito"""
    producto_id: str
    proveedor: Proveedor
    cantidad: int
    costo: float
    dia_pedido: int
    dia_llegada: int


@dataclass
class Evento:
    """Representa un evento en la simulación"""
    dia: int
    tipo: TipoEvento
    datos: Dict


class SimuladorInventario:
    """
    Motor de simulación de eventos discretos para gestión de inventario
    
    Simula el comportamiento del inventario considerando:
    - Demanda de clientes
    - Pedidos a proveedores
    - Políticas de reposición
    - Costos de almacenamiento y desabastecimiento
    - Rotación de inventario (PEPS, UEPS, PROMEDIO)
    
    Attributes:
        metodo_inventario: Método de rotación de inventario
        fecha_actual: Fecha actual de la simulación
        dia_simulacion: Contador de días simulados
        productos: Diccionario de productos del sistema
        proveedores: Lista de proveedores disponibles
        clientes: Lista de clientes que generan demanda
        gestor: Gestor de pedidos
        finanzas: Sistema financiero
    """
    
    def __init__(self, metodo_inventario: MetodoInventario = MetodoInventario.PEPS,
                 politica_reposicion: PoliticaReposicion = PoliticaReposicion.CONSERVADORA,
                 saldo_inicial: float = 100000.0):
        """
        Inicializa el simulador
        
        Args:
            metodo_inventario: Método de rotación de inventario
            politica_reposicion: Política inicial de reposición
            saldo_inicial: Capital inicial del sistema
        """
        self.metodo_inventario = metodo_inventario
        self.fecha_actual = datetime.now()
        self.dia_simulacion = 0
        
        # Entidades del sistema
        self.productos: Dict[str, Producto] = {}
        self.proveedores: List[Proveedor] = []
        self.clientes: List[Cliente] = []
        self.gestor = GestorPedidos(politica_reposicion)
        self.finanzas = Finanzas(saldo_inicial=saldo_inicial)
        
        # Estado de la simulación
        self.pedidos_pendientes: List[PedidoPendiente] = []
        self.eventos_log: List[Evento] = []
        
        # Costos del sistema
        self.costo_almacenamiento = 0.1  # por unidad por día
        self.costo_desabastecimiento_base = 50.0
        
        # Métricas
        self.desabastecimientos = 0
        self.ventas_totales = 0
        self.unidades_vendidas = 0
    
    # ==================== GESTIÓN DE ENTIDADES ====================
    
    def agregar_producto(self, producto: Producto) -> bool:
        """
        Agrega un producto al sistema
        
        Args:
            producto: Producto a agregar
            
        Returns:
            True si se agregó exitosamente
        """
        if producto.id in self.productos:
            return False
        
        self.productos[producto.id] = producto
        return True
    
    def agregar_proveedor(self, proveedor: Proveedor):
        """Agrega un proveedor al sistema"""
        self.proveedores.append(proveedor)
    
    def agregar_cliente(self, cliente: Cliente):
        """Agrega un cliente al sistema"""
        self.clientes.append(cliente)
    
    # ==================== CICLO DE SIMULACIÓN ====================
    
    def avanzar_dia(self):
        """
        Ejecuta un ciclo completo de simulación (un día)
        
        Secuencia de eventos:
        1. Generar demanda de clientes
        2. Evaluar inventario y generar pedidos
        3. Procesar entregas pendientes
        4. Registrar costos de almacenamiento
        5. Evaluación periódica del sistema
        """
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
            self._evaluar_sistema()
    
    def simular_dias(self, num_dias: int) -> Dict:
        """
        Simula múltiples días
        
        Args:
            num_dias: Número de días a simular
            
        Returns:
            Resumen de la simulación
        """
        for _ in range(num_dias):
            self.avanzar_dia()
        
        return self.obtener_estado()
    
    # ==================== PROCESAMIENTO DE EVENTOS ====================
    
    def _procesar_demandas(self):
        """Procesa las demandas de todos los clientes activos"""
        for cliente in self.clientes:
            if cliente.debe_realizar_pedido(self.dia_simulacion):
                for producto_id in cliente.productos_solicitados:
                    if producto_id in self.productos:
                        cantidad = cliente.generar_demanda(producto_id)
                        if cantidad > 0:
                            self._atender_demanda(cliente, producto_id, cantidad)
    
    def _atender_demanda(self, cliente: Cliente, producto_id: str, cantidad: int):
        """
        Intenta satisfacer una demanda de un cliente
        
        Args:
            cliente: Cliente que solicita
            producto_id: ID del producto solicitado
            cantidad: Cantidad solicitada
        """
        producto = self.productos[producto_id]
        
        if producto.nivel_inventario >= cantidad:
            # Hay inventario suficiente - VENTA EXITOSA
            costo, exito = producto.retirar_unidades(cantidad, self.metodo_inventario)
            
            if exito:
                ingreso = cantidad * producto.precio_venta
                
                self.finanzas.registrar_ingreso(
                    ingreso, 
                    f"Venta a {cliente.nombre}", 
                    self.fecha_actual,
                    "VENTA"
                )
                
                cliente.registrar_compra(cantidad, ingreso)
                self.ventas_totales += 1
                self.unidades_vendidas += cantidad
                
                # Registrar evento
                self.eventos_log.append(Evento(
                    dia=self.dia_simulacion,
                    tipo=TipoEvento.VENTA,
                    datos={
                        'cliente': cliente.nombre,
                        'producto': producto_id,
                        'cantidad': cantidad,
                        'ingreso': ingreso,
                        'costo': costo
                    }
                ))
        else:
            # DESABASTECIMIENTO
            self.desabastecimientos += 1
            penalizacion = cliente.obtener_penalizacion_desabastecimiento(
                self.costo_desabastecimiento_base
            )
            
            self.finanzas.registrar_egreso(
                penalizacion,
                f"Desabastecimiento {cliente.nombre}",
                self.fecha_actual,
                "PENALIZACION"
            )
            
            cliente.registrar_desabastecimiento()
            
            # Registrar evento
            self.eventos_log.append(Evento(
                dia=self.dia_simulacion,
                tipo=TipoEvento.DESABASTECIMIENTO,
                datos={
                    'cliente': cliente.nombre,
                    'producto': producto_id,
                    'cantidad_solicitada': cantidad,
                    'inventario_disponible': producto.nivel_inventario,
                    'penalizacion': penalizacion
                }
            ))
    
    def _evaluar_inventario(self):
        """Evalúa el inventario y genera pedidos si es necesario"""
        for producto in self.productos.values():
            decision = self.gestor.evaluar_pedido(
                producto, 
                self.proveedores, 
                self.dia_simulacion
            )
            
            if decision:
                # Verificar que hay saldo suficiente
                if not self.finanzas.tiene_saldo_suficiente(decision.costo_total):
                    continue
                
                # Crear pedido pendiente
                dias_entrega = decision.proveedor.calcular_tiempo_entrega_real()
                
                pedido = PedidoPendiente(
                    producto_id=decision.producto_id,
                    proveedor=decision.proveedor,
                    cantidad=decision.cantidad,
                    costo=decision.costo_total,
                    dia_pedido=self.dia_simulacion,
                    dia_llegada=self.dia_simulacion + dias_entrega
                )
                
                self.pedidos_pendientes.append(pedido)
                
                # Registrar evento
                self.eventos_log.append(Evento(
                    dia=self.dia_simulacion,
                    tipo=TipoEvento.PEDIDO,
                    datos={
                        'producto': decision.producto_id,
                        'proveedor': decision.proveedor.nombre,
                        'cantidad': decision.cantidad,
                        'costo': decision.costo_total,
                        'dias_entrega': dias_entrega
                    }
                ))
    
    def _procesar_entregas(self):
        """Procesa pedidos que llegan en este día"""
        entregas = [p for p in self.pedidos_pendientes 
                   if p.dia_llegada == self.dia_simulacion]
        
        for entrega in entregas:
            producto = self.productos[entrega.producto_id]
            
            # Agregar lote al inventario
            exito = producto.agregar_lote(
                entrega.cantidad,
                entrega.costo / entrega.cantidad,
                self.fecha_actual
            )
            
            if exito:
                # Registrar egreso financiero
                self.finanzas.registrar_egreso(
                    entrega.costo,
                    f"Compra a {entrega.proveedor.nombre}",
                    self.fecha_actual,
                    "COMPRA"
                )
                
                # Registrar evento
                self.eventos_log.append(Evento(
                    dia=self.dia_simulacion,
                    tipo=TipoEvento.RECEPCION,
                    datos={
                        'producto': entrega.producto_id,
                        'cantidad': entrega.cantidad,
                        'egreso': entrega.costo,
                        'proveedor': entrega.proveedor.nombre
                    }
                ))
            
            # Remover de pendientes
            self.pedidos_pendientes.remove(entrega)
    
    def _registrar_costos_almacenamiento(self):
        """Registra los costos diarios de almacenamiento"""
        costo_total = 0
        for producto in self.productos.values():
            costo = producto.nivel_inventario * self.costo_almacenamiento
            costo_total += costo
        
        if costo_total > 0:
            self.finanzas.registrar_egreso(
                costo_total,
                "Almacenamiento diario",
                self.fecha_actual,
                "ALMACENAMIENTO"
            )
    
    def _evaluar_sistema(self):
        """Evaluación periódica del desempeño del sistema"""
        # Calcular inventario promedio
        inventario_total = sum(p.nivel_inventario for p in self.productos.values())
        num_productos = len(self.productos)
        inventario_promedio = inventario_total / num_productos if num_productos > 0 else 0
        
        # Preparar métricas para el gestor
        metricas = {
            'utilidad_neta': self.finanzas.utilidad_neta,
            'desabastecimientos': self.desabastecimientos,
            'inventario_promedio': inventario_promedio,
            'saldo_inicial': self.finanzas.saldo_inicial
        }
        
        # Evaluar y ajustar política si es necesario
        politica_anterior = self.gestor.politica
        self.gestor.evaluar_desempeno(metricas, self.dia_simulacion)
        
        # Registrar cambio de política si ocurrió
        if self.gestor.politica != politica_anterior:
            self.eventos_log.append(Evento(
                dia=self.dia_simulacion,
                tipo=TipoEvento.CAMBIO_POLITICA,
                datos={
                    'politica_anterior': politica_anterior.value,
                    'politica_nueva': self.gestor.politica.value,
                    'razon': 'Evaluación periódica de desempeño'
                }
            ))
    
    # ==================== OBTENCIÓN DE ESTADO ====================
    
    def obtener_estado(self) -> Dict:
        """
        Retorna el estado actual completo de la simulación
        
        Returns:
            Diccionario con el estado del sistema
        """
        return {
            'dia': self.dia_simulacion,
            'fecha': self.fecha_actual.isoformat(),
            'productos': {
                pid: {
                    'nombre': p.nombre,
                    'inventario': p.nivel_inventario,
                    'punto_pedido': p.punto_pedido,
                    'num_lotes': len(p.lotes)
                } 
                for pid, p in self.productos.items()
            },
            'finanzas': self.finanzas.obtener_balance(),
            'gestor': self.gestor.obtener_estadisticas(),
            'metricas': {
                'desabastecimientos': self.desabastecimientos,
                'ventas_totales': self.ventas_totales,
                'unidades_vendidas': self.unidades_vendidas,
                'pedidos_pendientes': len(self.pedidos_pendientes)
            }
        }
    
    def obtener_eventos_recientes(self, cantidad: int = 10) -> List[Dict]:
        """
        Obtiene los eventos más recientes
        
        Args:
            cantidad: Número de eventos a retornar
            
        Returns:
            Lista de eventos recientes
        """
        eventos_recientes = self.eventos_log[-cantidad:]
        return [
            {
                'dia': e.dia,
                'tipo': e.tipo.value,
                'datos': e.datos
            }
            for e in eventos_recientes
        ]
    
    def exportar_eventos(self) -> List[Dict]:
        """Exporta todos los eventos registrados"""
        return [
            {
                'dia': e.dia,
                'tipo': e.tipo.value,
                **e.datos
            }
            for e in self.eventos_log
        ]
    
    # ==================== UTILIDADES ====================
    
    def reiniciar(self):
        """Reinicia la simulación a su estado inicial"""
        self.dia_simulacion = 0
        self.fecha_actual = datetime.now()
        
        # Reiniciar productos
        for producto in self.productos.values():
            producto.nivel_inventario = 0
            producto.lotes = []
        
        # Reiniciar clientes
        for cliente in self.clientes:
            cliente.reiniciar_estadisticas()
        
        # Reiniciar sistemas
        self.gestor.reiniciar()
        self.finanzas.reiniciar()
        
        # Limpiar estado
        self.pedidos_pendientes = []
        self.eventos_log = []
        self.desabastecimientos = 0
        self.ventas_totales = 0
        self.unidades_vendidas = 0
    
    def __repr__(self) -> str:
        """Representación en string del simulador"""
        return (f"SimuladorInventario(Día: {self.dia_simulacion}, "
                f"Productos: {len(self.productos)}, "
                f"Clientes: {len(self.clientes)})")