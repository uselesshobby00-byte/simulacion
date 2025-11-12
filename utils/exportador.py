"""
utils/exportador.py
Funciones para exportar datos de la simulación a CSV
"""

import csv
import os
from datetime import datetime
from typing import List, Dict
from config.configuracion import (
    FORMATO_FECHA_EXPORTACION,
    RUTA_EXPORTACION_DEFAULT,
    COLUMNAS_PEDIDO,
    COLUMNAS_DEMANDA,
    COLUMNAS_RECEPCION,
    COLUMNAS_VENTA,
    COLUMNAS_PENALIZACION
)


class ExportadorDatos:
    """
    Clase para exportar datos de la simulación a archivos CSV
    """
    
    def __init__(self, ruta_base: str = RUTA_EXPORTACION_DEFAULT):
        """
        Inicializa el exportador
        
        Args:
            ruta_base: Ruta base para guardar archivos
        """
        self.ruta_base = ruta_base
        self._crear_directorio_si_no_existe()
    
    def _crear_directorio_si_no_existe(self):
        """Crea el directorio de exportación si no existe"""
        if not os.path.exists(self.ruta_base):
            os.makedirs(self.ruta_base)
    
    def _generar_nombre_archivo(self, prefijo: str, extension: str = "csv") -> str:
        """
        Genera un nombre de archivo único con timestamp
        
        Args:
            prefijo: Prefijo del archivo
            extension: Extensión del archivo
            
        Returns:
            Nombre completo del archivo
        """
        timestamp = datetime.now().strftime(FORMATO_FECHA_EXPORTACION)
        return f"{prefijo}_{timestamp}.{extension}"
    
    def exportar_eventos(self, eventos: List[Dict], tipo_evento: str = "todos") -> str:
        """
        Exporta eventos a un archivo CSV
        
        Args:
            eventos: Lista de eventos a exportar
            tipo_evento: Tipo de evento (pedido, demanda, recepcion, venta, penalizacion, todos)
            
        Returns:
            Ruta del archivo creado
        """
        # Filtrar eventos por tipo si se especifica
        if tipo_evento != "todos":
            eventos = [e for e in eventos if e.get('tipo', '').lower() == tipo_evento.lower()]
        
        if not eventos:
            return None
        
        # Generar nombre de archivo
        nombre_archivo = self._generar_nombre_archivo(f"eventos_{tipo_evento}")
        ruta_completa = os.path.join(self.ruta_base, nombre_archivo)
        
        # Determinar columnas según el tipo
        if tipo_evento == "todos":
            # Obtener todas las claves únicas
            columnas = set()
            for evento in eventos:
                columnas.update(evento.keys())
            columnas = sorted(list(columnas))
        else:
            columnas = self._obtener_columnas_por_tipo(tipo_evento)
        
        # Escribir CSV
        with open(ruta_completa, 'w', newline='', encoding='utf-8') as archivo:
            writer = csv.DictWriter(archivo, fieldnames=columnas)
            writer.writeheader()
            
            for evento in eventos:
                # Filtrar solo las columnas que existen en el evento
                fila = {col: evento.get(col, '') for col in columnas}
                writer.writerow(fila)
        
        return ruta_completa
    
    def _obtener_columnas_por_tipo(self, tipo: str) -> List[str]:
        """
        Obtiene las columnas según el tipo de evento
        
        Args:
            tipo: Tipo de evento
            
        Returns:
            Lista de nombres de columnas
        """
        columnas_map = {
            'pedido': COLUMNAS_PEDIDO,
            'demanda': COLUMNAS_DEMANDA,
            'recepcion': COLUMNAS_RECEPCION,
            'venta': COLUMNAS_VENTA,
            'penalizacion': COLUMNAS_PENALIZACION
        }
        return columnas_map.get(tipo.lower(), [])
    
    def exportar_resumen_simulacion(self, estado_final: Dict) -> str:
        """
        Exporta un resumen de la simulación
        
        Args:
            estado_final: Estado final de la simulación
            
        Returns:
            Ruta del archivo creado
        """
        nombre_archivo = self._generar_nombre_archivo("resumen_simulacion")
        ruta_completa = os.path.join(self.ruta_base, nombre_archivo)
        
        with open(ruta_completa, 'w', newline='', encoding='utf-8') as archivo:
            writer = csv.writer(archivo)
            
            # Encabezado
            writer.writerow(['RESUMEN DE SIMULACIÓN'])
            writer.writerow(['Fecha de generación', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
            writer.writerow([])
            
            # Información general
            writer.writerow(['INFORMACIÓN GENERAL'])
            writer.writerow(['Día final', estado_final.get('dia', 0)])
            writer.writerow(['Fecha final', estado_final.get('fecha', '')])
            writer.writerow([])
            
            # Finanzas
            finanzas = estado_final.get('finanzas', {})
            writer.writerow(['ESTADO FINANCIERO'])
            writer.writerow(['Saldo inicial', f"${finanzas.get('saldo_inicial', 0):,.2f}"])
            writer.writerow(['Saldo final', f"${finanzas.get('saldo_actual', 0):,.2f}"])
            writer.writerow(['Ingresos totales', f"${finanzas.get('ingresos_totales', 0):,.2f}"])
            writer.writerow(['Egresos totales', f"${finanzas.get('egresos_totales', 0):,.2f}"])
            writer.writerow(['Utilidad neta', f"${finanzas.get('utilidad_neta', 0):,.2f}"])
            writer.writerow(['Rentabilidad', f"{finanzas.get('rentabilidad', 0):.2f}%"])
            writer.writerow([])
            
            # Gestor
            gestor = estado_final.get('gestor', {})
            writer.writerow(['GESTOR DE PEDIDOS'])
            writer.writerow(['Política actual', gestor.get('politica_actual', 'N/A')])
            writer.writerow(['Sensibilidad', gestor.get('sensibilidad', 0)])
            writer.writerow(['Pedidos generados', gestor.get('pedidos_generados', 0)])
            writer.writerow(['Costo total pedidos', f"${gestor.get('costo_total_pedidos', 0):,.2f}"])
            writer.writerow([])
            
            # Métricas
            metricas = estado_final.get('metricas', {})
            writer.writerow(['MÉTRICAS OPERATIVAS'])
            writer.writerow(['Desabastecimientos', metricas.get('desabastecimientos', 0)])
            writer.writerow(['Ventas totales', metricas.get('ventas_totales', 0)])
            writer.writerow(['Unidades vendidas', metricas.get('unidades_vendidas', 0)])
            writer.writerow(['Pedidos pendientes', metricas.get('pedidos_pendientes', 0)])
            writer.writerow([])
            
            # Productos
            productos = estado_final.get('productos', {})
            writer.writerow(['ESTADO DE PRODUCTOS'])
            writer.writerow(['ID', 'Nombre', 'Inventario', 'Punto Pedido', 'Lotes'])
            for prod_id, datos in productos.items():
                writer.writerow([
                    prod_id,
                    datos.get('nombre', ''),
                    datos.get('inventario', 0),
                    datos.get('punto_pedido', 0),
                    datos.get('num_lotes', 0)
                ])
        
        return ruta_completa
    
    def exportar_productos(self, productos: Dict) -> str:
        """
        Exporta información detallada de productos
        
        Args:
            productos: Diccionario de productos
            
        Returns:
            Ruta del archivo creado
        """
        nombre_archivo = self._generar_nombre_archivo("productos")
        ruta_completa = os.path.join(self.ruta_base, nombre_archivo)
        
        columnas = [
            'id', 'nombre', 'nivel_inventario', 'costo_unitario',
            'precio_venta', 'punto_pedido', 'demanda_estimada',
            'tiempo_reposicion', 'capacidad_maxima', 'num_lotes'
        ]
        
        with open(ruta_completa, 'w', newline='', encoding='utf-8') as archivo:
            writer = csv.DictWriter(archivo, fieldnames=columnas)
            writer.writeheader()
            
            for producto in productos.values():
                info = producto.obtener_informacion()
                writer.writerow(info)
        
        return ruta_completa
    
    def exportar_transacciones_financieras(self, transacciones: List[Dict]) -> str:
        """
        Exporta transacciones financieras
        
        Args:
            transacciones: Lista de transacciones
            
        Returns:
            Ruta del archivo creado
        """
        if not transacciones:
            return None
        
        nombre_archivo = self._generar_nombre_archivo("transacciones_financieras")
        ruta_completa = os.path.join(self.ruta_base, nombre_archivo)
        
        columnas = ['fecha', 'tipo', 'concepto', 'monto', 'categoria']
        
        with open(ruta_completa, 'w', newline='', encoding='utf-8') as archivo:
            writer = csv.DictWriter(archivo, fieldnames=columnas)
            writer.writeheader()
            writer.writerows(transacciones)
        
        return ruta_completa
    
    def exportar_estadisticas_clientes(self, clientes: List) -> str:
        """
        Exporta estadísticas de clientes
        
        Args:
            clientes: Lista de clientes
            
        Returns:
            Ruta del archivo creado
        """
        nombre_archivo = self._generar_nombre_archivo("estadisticas_clientes")
        ruta_completa = os.path.join(self.ruta_base, nombre_archivo)
        
        columnas = [
            'id', 'nombre', 'tipo', 'prioridad', 'total_compras',
            'total_gastado', 'pedidos_realizados', 'desabastecimientos',
            'satisfaccion', 'activo'
        ]
        
        with open(ruta_completa, 'w', newline='', encoding='utf-8') as archivo:
            writer = csv.DictWriter(archivo, fieldnames=columnas)
            writer.writeheader()
            
            for cliente in clientes:
                stats = cliente.obtener_estadisticas()
                writer.writerow(stats)
        
        return ruta_completa
    
    def exportar_todo(self, simulador) -> Dict[str, str]:
        """
        Exporta todos los datos de la simulación
        
        Args:
            simulador: Instancia del simulador
            
        Returns:
            Diccionario con las rutas de todos los archivos generados
        """
        archivos = {}
        
        # Estado general
        estado = simulador.obtener_estado()
        archivos['resumen'] = self.exportar_resumen_simulacion(estado)
        
        # Eventos
        eventos = simulador.exportar_eventos()
        archivos['eventos_todos'] = self.exportar_eventos(eventos, "todos")
        
        # Eventos por tipo
        for tipo in ['pedido', 'venta', 'recepcion', 'desabastecimiento']:
            archivo = self.exportar_eventos(eventos, tipo)
            if archivo:
                archivos[f'eventos_{tipo}'] = archivo
        
        # Productos
        archivos['productos'] = self.exportar_productos(simulador.productos)
        
        # Transacciones financieras
        transacciones = simulador.finanzas.exportar_transacciones()
        archivo_trans = self.exportar_transacciones_financieras(transacciones)
        if archivo_trans:
            archivos['transacciones'] = archivo_trans
        
        # Estadísticas de clientes
        archivos['clientes'] = self.exportar_estadisticas_clientes(simulador.clientes)
        
        return archivos


# Funciones de utilidad para uso directo

def exportar_rapido(simulador, tipo: str = "resumen") -> str:
    """
    Exportación rápida de datos
    
    Args:
        simulador: Instancia del simulador
        tipo: Tipo de exportación (resumen, eventos, productos, todo)
        
    Returns:
        Ruta del archivo o mensaje de éxito
    """
    exportador = ExportadorDatos()
    
    if tipo == "resumen":
        return exportador.exportar_resumen_simulacion(simulador.obtener_estado())
    elif tipo == "eventos":
        return exportador.exportar_eventos(simulador.exportar_eventos(), "todos")
    elif tipo == "productos":
        return exportador.exportar_productos(simulador.productos)
    elif tipo == "todo":
        archivos = exportador.exportar_todo(simulador)
        return f"Se generaron {len(archivos)} archivos"
    else:
        raise ValueError(f"Tipo de exportación no válido: {tipo}")