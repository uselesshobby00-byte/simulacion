"""
models/finanzas.py
Clase Finanzas - Gestión financiera del sistema
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict


@dataclass
class TransaccionFinanciera:
    """
    Representa una transacción financiera individual
    
    Attributes:
        fecha: Fecha de la transacción
        tipo: Tipo de transacción (INGRESO o EGRESO)
        concepto: Descripción de la transacción
        monto: Monto de la transacción
        categoria: Categoría (VENTA, COMPRA, ALMACENAMIENTO, PENALIZACION)
    """
    fecha: datetime
    tipo: str  # INGRESO o EGRESO
    concepto: str
    monto: float
    categoria: str


@dataclass
class Finanzas:
    """
    Gestiona el estado financiero del sistema de inventario
    
    Attributes:
        saldo_inicial: Capital inicial del sistema
        saldo_actual: Saldo disponible actual
        ingresos_totales: Total acumulado de ingresos
        egresos_totales: Total acumulado de egresos
        transacciones: Historial de todas las transacciones
    """
    
    saldo_inicial: float = 100000.0
    saldo_actual: float = 100000.0
    ingresos_totales: float = 0.0
    egresos_totales: float = 0.0
    
    transacciones: List[TransaccionFinanciera] = field(default_factory=list)
    
    # Contadores por categoría
    ingresos_venta: float = field(default=0.0, init=False)
    egresos_compra: float = field(default=0.0, init=False)
    egresos_almacenamiento: float = field(default=0.0, init=False)
    egresos_penalizacion: float = field(default=0.0, init=False)
    
    def __post_init__(self):
        """Validaciones después de la inicialización"""
        if self.saldo_inicial < 0:
            raise ValueError("El saldo inicial no puede ser negativo")
        
        self.saldo_actual = self.saldo_inicial
    
    def registrar_ingreso(self, monto: float, concepto: str, fecha: datetime, 
                         categoria: str = "VENTA"):
        """
        Registra un ingreso en el sistema
        
        Args:
            monto: Cantidad de dinero ingresada
            concepto: Descripción del ingreso
            fecha: Fecha del ingreso
            categoria: Categoría del ingreso
        """
        if monto < 0:
            raise ValueError("El monto de ingreso no puede ser negativo")
        
        self.ingresos_totales += monto
        self.saldo_actual += monto
        
        # Actualizar contador por categoría
        if categoria == "VENTA":
            self.ingresos_venta += monto
        
        # Registrar transacción
        transaccion = TransaccionFinanciera(
            fecha=fecha,
            tipo="INGRESO",
            concepto=concepto,
            monto=monto,
            categoria=categoria
        )
        self.transacciones.append(transaccion)
    
    def registrar_egreso(self, monto: float, concepto: str, fecha: datetime, 
                        categoria: str = "COMPRA"):
        """
        Registra un egreso en el sistema
        
        Args:
            monto: Cantidad de dinero egresada
            concepto: Descripción del egreso
            fecha: Fecha del egreso
            categoria: Categoría del egreso (COMPRA, ALMACENAMIENTO, PENALIZACION)
        """
        if monto < 0:
            raise ValueError("El monto de egreso no puede ser negativo")
        
        self.egresos_totales += monto
        self.saldo_actual -= monto
        
        # Actualizar contadores por categoría
        if categoria == "COMPRA":
            self.egresos_compra += monto
        elif categoria == "ALMACENAMIENTO":
            self.egresos_almacenamiento += monto
        elif categoria == "PENALIZACION":
            self.egresos_penalizacion += monto
        
        # Registrar transacción
        transaccion = TransaccionFinanciera(
            fecha=fecha,
            tipo="EGRESO",
            concepto=concepto,
            monto=monto,
            categoria=categoria
        )
        self.transacciones.append(transaccion)
    
    @property
    def utilidad_neta(self) -> float:
        """
        Calcula la utilidad neta del sistema
        
        Returns:
            Utilidad neta (ingresos - egresos)
        """
        return self.ingresos_totales - self.egresos_totales
    
    @property
    def rentabilidad(self) -> float:
        """
        Calcula el porcentaje de rentabilidad
        
        Returns:
            Rentabilidad como porcentaje
        """
        if self.saldo_inicial == 0:
            return 0.0
        
        return (self.utilidad_neta / self.saldo_inicial) * 100
    
    def tiene_saldo_suficiente(self, monto: float) -> bool:
        """
        Verifica si hay saldo suficiente para un egreso
        
        Args:
            monto: Monto a verificar
            
        Returns:
            True si hay saldo suficiente
        """
        return self.saldo_actual >= monto
    
    def obtener_balance(self) -> Dict:
        """
        Obtiene un resumen del balance financiero
        
        Returns:
            Diccionario con el balance
        """
        return {
            'saldo_inicial': self.saldo_inicial,
            'saldo_actual': self.saldo_actual,
            'ingresos_totales': self.ingresos_totales,
            'egresos_totales': self.egresos_totales,
            'utilidad_neta': self.utilidad_neta,
            'rentabilidad': self.rentabilidad,
            'num_transacciones': len(self.transacciones)
        }
    
    def obtener_desglose_egresos(self) -> Dict:
        """
        Obtiene un desglose detallado de los egresos
        
        Returns:
            Diccionario con el desglose por categoría
        """
        return {
            'compras': self.egresos_compra,
            'almacenamiento': self.egresos_almacenamiento,
            'penalizaciones': self.egresos_penalizacion,
            'otros': self.egresos_totales - (
                self.egresos_compra + 
                self.egresos_almacenamiento + 
                self.egresos_penalizacion
            )
        }
    
    def obtener_transacciones_periodo(self, fecha_inicio: datetime, 
                                     fecha_fin: datetime) -> List[TransaccionFinanciera]:
        """
        Obtiene las transacciones en un periodo específico
        
        Args:
            fecha_inicio: Fecha inicial del periodo
            fecha_fin: Fecha final del periodo
            
        Returns:
            Lista de transacciones en el periodo
        """
        return [
            t for t in self.transacciones 
            if fecha_inicio <= t.fecha <= fecha_fin
        ]
    
    def calcular_flujo_caja_neto(self) -> float:
        """
        Calcula el flujo de caja neto (cambio en el saldo)
        
        Returns:
            Flujo de caja neto
        """
        return self.saldo_actual - self.saldo_inicial
    
    def calcular_margen_bruto(self) -> float:
        """
        Calcula el margen bruto de ganancia
        
        Returns:
            Margen bruto como porcentaje
        """
        if self.ingresos_totales == 0:
            return 0.0
        
        utilidad_bruta = self.ingresos_totales - self.egresos_compra
        return (utilidad_bruta / self.ingresos_totales) * 100
    
    def obtener_estadisticas_completas(self) -> Dict:
        """
        Obtiene estadísticas financieras completas
        
        Returns:
            Diccionario con todas las estadísticas
        """
        return {
            'balance': self.obtener_balance(),
            'desglose_egresos': self.obtener_desglose_egresos(),
            'margen_bruto': self.calcular_margen_bruto(),
            'flujo_caja_neto': self.calcular_flujo_caja_neto(),
            'ingresos_venta': self.ingresos_venta,
            'relacion_ingreso_egreso': (
                self.ingresos_totales / self.egresos_totales 
                if self.egresos_totales > 0 else 0
            )
        }
    
    def exportar_transacciones(self) -> List[Dict]:
        """
        Exporta las transacciones en formato lista de diccionarios
        
        Returns:
            Lista de transacciones como diccionarios
        """
        return [
            {
                'fecha': t.fecha.isoformat(),
                'tipo': t.tipo,
                'concepto': t.concepto,
                'monto': t.monto,
                'categoria': t.categoria
            }
            for t in self.transacciones
        ]
    
    def reiniciar(self, nuevo_saldo_inicial: float = None):
        """
        Reinicia el sistema financiero
        
        Args:
            nuevo_saldo_inicial: Nuevo saldo inicial (opcional)
        """
        if nuevo_saldo_inicial is not None:
            if nuevo_saldo_inicial < 0:
                raise ValueError("El saldo inicial no puede ser negativo")
            self.saldo_inicial = nuevo_saldo_inicial
        
        self.saldo_actual = self.saldo_inicial
        self.ingresos_totales = 0.0
        self.egresos_totales = 0.0
        self.ingresos_venta = 0.0
        self.egresos_compra = 0.0
        self.egresos_almacenamiento = 0.0
        self.egresos_penalizacion = 0.0
        self.transacciones = []
    
    def __repr__(self) -> str:
        """Representación en string de las finanzas"""
        return f"Finanzas(Saldo: ${self.saldo_actual:.2f}, Utilidad: ${self.utilidad_neta:.2f})"