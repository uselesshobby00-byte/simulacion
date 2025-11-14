"""
gui/panel_graficas.py
Panel derecho con gráficas y visualizaciones
"""

import tkinter as tk
from tkinter import ttk
from typing import List, Dict
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from config.configuracion import (
    COLORES_PRODUCTOS,
    GRAFICA_ANCHO,
    GRAFICA_ALTO,
    obtener_color_producto
)


class PanelGraficas:
    """
    Panel de gráficas y visualizaciones
    
    Attributes:
        frame: Frame contenedor del panel
        notebook: Notebook con múltiples pestañas
    """
    
    def __init__(self, parent):
        """
        Inicializa el panel de gráficas
        
        Args:
            parent: Widget padre
        """
        # Frame principal
        self.frame = ttk.Frame(parent)
        
        # Datos históricos para gráficas
        self.historia_inventario = {}
        self.historia_finanzas = {
            'dias': [],
            'saldo': [],
            'ingresos': [],
            'egresos': [],
            'utilidad': []
        }
        
        self._crear_widgets()
    
    def _crear_widgets(self):
        """Crea todos los widgets del panel"""
        
        # Notebook con pestañas
        self.notebook = ttk.Notebook(self.frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Pestaña 1: Inventario
        self._crear_pestaña_inventario()
        
        # Pestaña 2: Finanzas
        self._crear_pestaña_finanzas()
        
        # Pestaña 3: Eventos
        self._crear_pestaña_eventos()
        
        # Pestaña 4: Métricas
        self._crear_pestaña_metricas()
    
    def _crear_pestaña_inventario(self):
        """Crea la pestaña de inventario"""
        tab_inventario = ttk.Frame(self.notebook)
        self.notebook.add(tab_inventario, text="📊 Niveles de Inventario")
        
        # Frame para la gráfica
        frame_grafica = ttk.Frame(tab_inventario)
        frame_grafica.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Crear figura de matplotlib
        self.fig_inventario = Figure(figsize=(GRAFICA_ANCHO, GRAFICA_ALTO), dpi=100)
        self.ax_inventario = self.fig_inventario.add_subplot(111)
        
        # Canvas para mostrar la figura
        self.canvas_inventario = FigureCanvasTkAgg(self.fig_inventario, frame_grafica)
        self.canvas_inventario.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Configurar gráfica inicial
        self.ax_inventario.set_title("Evolución de Niveles de Inventario", fontsize=12, fontweight='bold')
        self.ax_inventario.set_xlabel("Día de Simulación")
        self.ax_inventario.set_ylabel("Unidades en Inventario")
        self.ax_inventario.grid(True, alpha=0.3)
        self.ax_inventario.text(0.5, 0.5, 'Esperando datos...', 
                               horizontalalignment='center',
                               verticalalignment='center',
                               transform=self.ax_inventario.transAxes,
                               fontsize=14, color='gray')
        
        self.canvas_inventario.draw()
    
    def _crear_pestaña_finanzas(self):
        """Crea la pestaña de finanzas"""
        tab_finanzas = ttk.Frame(self.notebook)
        self.notebook.add(tab_finanzas, text="💰 Estado Financiero")
        
        # Frame para la gráfica
        frame_grafica = ttk.Frame(tab_finanzas)
        frame_grafica.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Crear figura de matplotlib
        self.fig_finanzas = Figure(figsize=(GRAFICA_ANCHO, GRAFICA_ALTO), dpi=100)
        self.ax_finanzas = self.fig_finanzas.add_subplot(111)
        
        # Canvas para mostrar la figura
        self.canvas_finanzas = FigureCanvasTkAgg(self.fig_finanzas, frame_grafica)
        self.canvas_finanzas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Configurar gráfica inicial
        self.ax_finanzas.set_title("Evolución Financiera", fontsize=12, fontweight='bold')
        self.ax_finanzas.set_xlabel("Día de Simulación")
        self.ax_finanzas.set_ylabel("Monto ($)")
        self.ax_finanzas.grid(True, alpha=0.3)
        self.ax_finanzas.text(0.5, 0.5, 'Esperando datos...', 
                             horizontalalignment='center',
                             verticalalignment='center',
                             transform=self.ax_finanzas.transAxes,
                             fontsize=14, color='gray')
        
        self.canvas_finanzas.draw()
    
    def _crear_pestaña_eventos(self):
        """Crea la pestaña de eventos"""
        tab_eventos = ttk.Frame(self.notebook)
        self.notebook.add(tab_eventos, text="📝 Registro de Eventos")
        
        # Frame contenedor
        frame_contenedor = ttk.Frame(tab_eventos)
        frame_contenedor.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Barra de herramientas
        frame_toolbar = ttk.Frame(frame_contenedor)
        frame_toolbar.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(frame_toolbar, text="Filtrar por tipo:").pack(side=tk.LEFT, padx=5)
        
        self.filtro_eventos = tk.StringVar(value="TODOS")
        combo_filtro = ttk.Combobox(
            frame_toolbar,
            textvariable=self.filtro_eventos,
            values=["TODOS", "VENTA", "PEDIDO", "RECEPCION", "DESABASTECIMIENTO", "CAMBIO_POLITICA"],
            width=20,
            state="readonly"
        )
        combo_filtro.pack(side=tk.LEFT, padx=5)
        combo_filtro.bind("<<ComboboxSelected>>", lambda e: self._filtrar_eventos())
        
        ttk.Button(frame_toolbar, text="🔄 Actualizar", 
                  command=self._actualizar_eventos).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(frame_toolbar, text="🗑️ Limpiar", 
                  command=self._limpiar_eventos).pack(side=tk.LEFT, padx=5)
        
        # Text widget con scrollbar
        frame_text = ttk.Frame(frame_contenedor)
        frame_text.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(frame_text)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.text_eventos = tk.Text(
            frame_text,
            wrap=tk.WORD,
            yscrollcommand=scrollbar.set,
            font=("Consolas", 9)
        )
        self.text_eventos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.text_eventos.yview)
        
        # Configurar tags para colores
        self.text_eventos.tag_configure("VENTA", foreground="green")
        self.text_eventos.tag_configure("PEDIDO", foreground="blue")
        self.text_eventos.tag_configure("RECEPCION", foreground="purple")
        self.text_eventos.tag_configure("DESABASTECIMIENTO", foreground="red")
        self.text_eventos.tag_configure("CAMBIO_POLITICA", foreground="orange")
        self.text_eventos.tag_configure("header", font=("Consolas", 9, "bold"))
        
        # Almacenar eventos completos para filtrado
        self.eventos_completos = []
    
    def _crear_pestaña_metricas(self):
        """Crea la pestaña de métricas"""
        tab_metricas = ttk.Frame(self.notebook)
        self.notebook.add(tab_metricas, text="📈 Métricas y KPIs")
        
        # Frame principal con dos columnas
        frame_principal = ttk.Frame(tab_metricas)
        frame_principal.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Columna izquierda: Métricas financieras
        frame_izq = ttk.LabelFrame(frame_principal, text="💰 Métricas Financieras", padding=10)
        frame_izq.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.lbl_metricas_fin = tk.Text(frame_izq, height=15, width=40, 
                                        relief=tk.FLAT, font=("Arial", 10))
        self.lbl_metricas_fin.pack(fill=tk.BOTH, expand=True)
        
        # Columna derecha: Métricas operativas
        frame_der = ttk.LabelFrame(frame_principal, text="📦 Métricas Operativas", padding=10)
        frame_der.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        self.lbl_metricas_op = tk.Text(frame_der, height=15, width=40, 
                                       relief=tk.FLAT, font=("Arial", 10))
        self.lbl_metricas_op.pack(fill=tk.BOTH, expand=True)
        
        # Gráfica de pastel (parte inferior)
        frame_grafica_pie = ttk.LabelFrame(tab_metricas, text="📊 Distribución de Costos", padding=10)
        frame_grafica_pie.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        self.fig_pie = Figure(figsize=(8, 3), dpi=100)
        self.ax_pie = self.fig_pie.add_subplot(111)
        self.canvas_pie = FigureCanvasTkAgg(self.fig_pie, frame_grafica_pie)
        self.canvas_pie.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    # ===== MÉTODOS DE ACTUALIZACIÓN =====
    
    def actualizar_graficas(self, simulador):
        """
        Actualiza todas las gráficas con datos del simulador
        
        Args:
            simulador: Instancia del simulador
        """
        estado = simulador.obtener_estado()
        
        # Actualizar historia
        self._actualizar_historia(estado)
        
        # Actualizar gráfica de inventario
        self._actualizar_grafica_inventario(simulador)
        
        # Actualizar gráfica financiera
        self._actualizar_grafica_finanzas()
        
        # Actualizar métricas
        self._actualizar_metricas(simulador)
    
    def _actualizar_historia(self, estado: Dict):
        """Actualiza los datos históricos"""
        dia = estado['dia']
        
        # Historia financiera
        if dia not in self.historia_finanzas['dias']:
            finanzas = estado['finanzas']
            self.historia_finanzas['dias'].append(dia)
            self.historia_finanzas['saldo'].append(finanzas['saldo_actual'])
            self.historia_finanzas['ingresos'].append(finanzas['ingresos_totales'])
            self.historia_finanzas['egresos'].append(finanzas['egresos_totales'])
            self.historia_finanzas['utilidad'].append(finanzas['utilidad_neta'])
        
        # Historia de inventario
        for prod_id, datos in estado['productos'].items():
            if prod_id not in self.historia_inventario:
                self.historia_inventario[prod_id] = {
                    'nombre': datos['nombre'],
                    'niveles': [],
                    'punto_pedido': datos['punto_pedido']
                }
            
            if len(self.historia_inventario[prod_id]['niveles']) < dia:
                self.historia_inventario[prod_id]['niveles'].append(datos['inventario'])
    
    def _actualizar_grafica_inventario(self, simulador):
        """Actualiza la gráfica de inventario"""
        self.ax_inventario.clear()
        
        if not self.historia_inventario:
            self.ax_inventario.text(0.5, 0.5, 'Sin datos de inventario', 
                                   horizontalalignment='center',
                                   verticalalignment='center',
                                   transform=self.ax_inventario.transAxes,
                                   fontsize=14, color='gray')
        else:
            # Graficar cada producto
            for i, (prod_id, datos) in enumerate(self.historia_inventario.items()):
                if datos['niveles']:
                    dias = list(range(1, len(datos['niveles']) + 1))
                    color = obtener_color_producto(i)
                    
                    # Línea de inventario
                    self.ax_inventario.plot(dias, datos['niveles'], 
                                           marker='o', label=datos['nombre'],
                                           color=color, linewidth=2, markersize=4)
                    
                    # Línea de punto de pedido
                    self.ax_inventario.axhline(y=datos['punto_pedido'], 
                                              color=color, linestyle='--', 
                                              alpha=0.5, linewidth=1)
            
            self.ax_inventario.set_title("Evolución de Niveles de Inventario", 
                                        fontsize=12, fontweight='bold')
            self.ax_inventario.set_xlabel("Día de Simulación")
            self.ax_inventario.set_ylabel("Unidades en Inventario")
            self.ax_inventario.grid(True, alpha=0.3)
            self.ax_inventario.legend(loc='best', fontsize=8)
        
        self.canvas_inventario.draw()
    
    def _actualizar_grafica_finanzas(self):
        """Actualiza la gráfica financiera"""
        self.ax_finanzas.clear()
        
        if not self.historia_finanzas['dias']:
            self.ax_finanzas.text(0.5, 0.5, 'Sin datos financieros', 
                                 horizontalalignment='center',
                                 verticalalignment='center',
                                 transform=self.ax_finanzas.transAxes,
                                 fontsize=14, color='gray')
        else:
            dias = self.historia_finanzas['dias']
            
            # Gráfica de saldo
            self.ax_finanzas.plot(dias, self.historia_finanzas['saldo'], 
                                 marker='o', label='Saldo', 
                                 color='green', linewidth=2, markersize=4)
            
            # Gráfica de ingresos
            self.ax_finanzas.plot(dias, self.historia_finanzas['ingresos'], 
                                 marker='s', label='Ingresos Acum.', 
                                 color='blue', linewidth=2, markersize=4)
            
            # Gráfica de egresos
            self.ax_finanzas.plot(dias, self.historia_finanzas['egresos'], 
                                 marker='^', label='Egresos Acum.', 
                                 color='red', linewidth=2, markersize=4)
            
            # Gráfica de utilidad
            self.ax_finanzas.plot(dias, self.historia_finanzas['utilidad'], 
                                 marker='D', label='Utilidad Neta', 
                                 color='purple', linewidth=2, markersize=4)
            
            self.ax_finanzas.set_title("Evolución Financiera", 
                                      fontsize=12, fontweight='bold')
            self.ax_finanzas.set_xlabel("Día de Simulación")
            self.ax_finanzas.set_ylabel("Monto ($)")
            self.ax_finanzas.grid(True, alpha=0.3)
            self.ax_finanzas.legend(loc='best', fontsize=8)
            
            # Formato de eje Y en miles
            self.ax_finanzas.yaxis.set_major_formatter(
                plt.FuncFormatter(lambda x, p: f'${x/1000:.1f}K')
            )
        
        self.canvas_finanzas.draw()
    
    def _actualizar_metricas(self, simulador):
        """Actualiza el panel de métricas"""
        estado = simulador.obtener_estado()
        finanzas = estado['finanzas']
        metricas = estado['metricas']
        
        # Métricas financieras
        texto_fin = f"""
📊 Resumen Financiero (Día {estado['dia']})
{'='*40}

💰 Saldo Actual:      ${finanzas['saldo_actual']:,.2f}
💵 Saldo Inicial:     ${finanzas['saldo_inicial']:,.2f}

📈 Ingresos Totales:  ${finanzas['ingresos_totales']:,.2f}
📉 Egresos Totales:   ${finanzas['egresos_totales']:,.2f}

{'='*40}
💎 UTILIDAD NETA:     ${finanzas['utilidad_neta']:,.2f}
📊 Rentabilidad:      {finanzas['rentabilidad']:.2f}%

📝 Transacciones:     {finanzas['num_transacciones']}
        """
        
        self.lbl_metricas_fin.delete(1.0, tk.END)
        self.lbl_metricas_fin.insert(1.0, texto_fin)
        
        # Métricas operativas
        gestor = estado['gestor']
        
        texto_op = f"""
📦 Métricas Operativas
{'='*40}

❌ Desabastecimientos: {metricas['desabastecimientos']}
✅ Ventas Totales:     {metricas['ventas_totales']}
📦 Unidades Vendidas:  {metricas['unidades_vendidas']}
⏳ Pedidos Pendientes: {metricas['pedidos_pendientes']}

{'='*40}
🎯 Política Actual:    {gestor['politica_actual']}
🎚️  Sensibilidad:      {gestor['sensibilidad']:.2f}

📋 Pedidos Generados:  {gestor['pedidos_generados']}
💵 Costo Pedidos:      ${gestor['costo_total_pedidos']:,.2f}
        """
        
        if gestor['pedidos_generados'] > 0:
            texto_op += f"\n💰 Costo Prom/Pedido:  ${gestor['costo_promedio_pedido']:,.2f}"
        
        self.lbl_metricas_op.delete(1.0, tk.END)
        self.lbl_metricas_op.insert(1.0, texto_op)
        
        # Gráfica de pastel de costos
        self._actualizar_grafica_costos(simulador)
    
    def _actualizar_grafica_costos(self, simulador):
        """Actualiza la gráfica de pastel de costos"""
        self.ax_pie.clear()
        
        desglose = simulador.finanzas.obtener_desglose_egresos()
        
        # Filtrar valores > 0
        labels = []
        sizes = []
        colors = []
        
        color_map = {
            'compras': '#2196F3',
            'almacenamiento': '#FF9800',
            'penalizaciones': '#F44336',
            'otros': '#9E9E9E'
        }
        
        for categoria, monto in desglose.items():
            if monto > 0:
                labels.append(categoria.capitalize())
                sizes.append(monto)
                colors.append(color_map.get(categoria, '#9E9E9E'))
        
        if sizes:
            self.ax_pie.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                           startangle=90)
            self.ax_pie.set_title("Distribución de Costos")
        else:
            self.ax_pie.text(0.5, 0.5, 'Sin datos de costos', 
                           horizontalalignment='center',
                           verticalalignment='center',
                           transform=self.ax_pie.transAxes,
                           fontsize=12, color='gray')
        
        self.canvas_pie.draw()
    
    def actualizar_eventos(self, eventos: List[Dict]):
        """
        Actualiza la lista de eventos
        
        Args:
            eventos: Lista de eventos recientes
        """
        self.eventos_completos = eventos
        self._mostrar_eventos(eventos)
    
    def _mostrar_eventos(self, eventos: List[Dict]):
        """Muestra eventos en el text widget"""
        self.text_eventos.delete(1.0, tk.END)
        
        if not eventos:
            self.text_eventos.insert(tk.END, "No hay eventos registrados aún.\n")
            return
        
        for evento in reversed(eventos):  # Más recientes primero
            dia = evento['dia']
            tipo = evento['tipo']
            datos = evento['datos']
            
            # Header del evento
            header = f"[Día {dia}] {tipo}\n"
            self.text_eventos.insert(tk.END, header, ("header", tipo))
            
            # Detalles según tipo
            if tipo == "VENTA":
                detalle = f"  ✓ {datos['cliente']} compró {datos['cantidad']} de {datos['producto']}\n"
                detalle += f"    Ingreso: ${datos['ingreso']:.2f}\n\n"
            elif tipo == "PEDIDO":
                detalle = f"  📋 Pedido a {datos['proveedor']}: {datos['cantidad']} de {datos['producto']}\n"
                detalle += f"    Costo: ${datos['costo']:.2f}, Entrega en {datos.get('dias_entrega', '?')} días\n\n"
            elif tipo == "RECEPCION":
                detalle = f"  📦 Recibido: {datos['cantidad']} de {datos['producto']}\n"
                detalle += f"    Egreso: ${datos['egreso']:.2f}\n\n"
            elif tipo == "DESABASTECIMIENTO":
                detalle = f"  ❌ {datos['cliente']} no pudo comprar {datos['cantidad_solicitada']} de {datos['producto']}\n"
                detalle += f"    Disponible: {datos['inventario_disponible']}, Penalización: ${datos['penalizacion']:.2f}\n\n"
            elif tipo == "CAMBIO_POLITICA":
                detalle = f"  🔄 Cambio de política: {datos.get('politica_anterior', '?')} → {datos.get('politica_nueva', '?')}\n"
                detalle += f"    Razón: {datos.get('razon', 'No especificada')}\n\n"
            else:
                detalle = f"  {datos}\n\n"
            
            self.text_eventos.insert(tk.END, detalle)
        
        self.text_eventos.see(1.0)  # Scroll al inicio
    
    def _filtrar_eventos(self):
        """Filtra eventos según el tipo seleccionado"""
        filtro = self.filtro_eventos.get()
        
        if filtro == "TODOS":
            eventos_filtrados = self.eventos_completos
        else:
            eventos_filtrados = [e for e in self.eventos_completos if e['tipo'] == filtro]
        
        self._mostrar_eventos(eventos_filtrados)
    
    def _actualizar_eventos(self):
        """Actualiza la lista de eventos"""
        self._filtrar_eventos()
    
    def _limpiar_eventos(self):
        """Limpia la lista de eventos"""
        self.text_eventos.delete(1.0, tk.END)
        self.text_eventos.insert(tk.END, "Eventos limpiados.\n")
    
    def limpiar(self):
        """Limpia todas las gráficas y datos"""
        self.historia_inventario = {}
        self.historia_finanzas = {
            'dias': [],
            'saldo': [],
            'ingresos': [],
            'egresos': [],
            'utilidad': []
        }
        self.eventos_completos = []
        
        # Limpiar gráficas
        self.ax_inventario.clear()
        self.ax_finanzas.clear()
        self.ax_pie.clear()
        
        self.canvas_inventario.draw()
        self.canvas_finanzas.draw()
        self.canvas_pie.draw()
        
        # Limpiar eventos
        self.text_eventos.delete(1.0, tk.END)
        
        # Limpiar métricas
        self.lbl_metricas_fin.delete(1.0, tk.END)
        self.lbl_metricas_op.delete(1.0, tk.END)