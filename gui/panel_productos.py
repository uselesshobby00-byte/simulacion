"""
gui/panel_productos.py
Panel izquierdo con información de productos y estado general
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Dict
from config.configuracion import formatear_moneda, formatear_porcentaje


class PanelProductos:
    """
    Panel de productos y estado general del sistema
    
    Attributes:
        frame: Frame contenedor del panel
        tree_productos: TreeView con la lista de productos
    """
    
    def __init__(self, parent, on_aplicar_config: Callable = None):
        """
        Inicializa el panel de productos
        
        Args:
            parent: Widget padre
            on_aplicar_config: Callback al aplicar configuración de producto
        """
        self.on_aplicar_config = on_aplicar_config
        self.producto_seleccionado = None
        
        # Frame principal
        self.frame = ttk.Frame(parent, width=350)
        
        self._crear_widgets()
    
    def _crear_widgets(self):
        """Crea todos los widgets del panel"""
        
        # ===== ESTADO GENERAL =====
        frame_estado = ttk.LabelFrame(self.frame, text="📊 Estado General", padding=10)
        frame_estado.pack(fill=tk.X, pady=(0, 10))
        
        # Labels de estado
        self.lbl_dia = ttk.Label(frame_estado, text="Día: 0", 
                                 font=("Arial", 11, "bold"))
        self.lbl_dia.pack(anchor=tk.W, pady=2)
        
        self.lbl_saldo = ttk.Label(frame_estado, text="Saldo: $0.00", 
                                   font=("Arial", 10))
        self.lbl_saldo.pack(anchor=tk.W, pady=2)
        
        self.lbl_utilidad = ttk.Label(frame_estado, text="Utilidad Neta: $0.00", 
                                      font=("Arial", 10))
        self.lbl_utilidad.pack(anchor=tk.W, pady=2)
        
        self.lbl_rentabilidad = ttk.Label(frame_estado, text="Rentabilidad: 0.00%", 
                                         font=("Arial", 10))
        self.lbl_rentabilidad.pack(anchor=tk.W, pady=2)
        
        ttk.Separator(frame_estado, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)
        
        self.lbl_desabastecimientos = ttk.Label(frame_estado, 
                                               text="Desabastecimientos: 0")
        self.lbl_desabastecimientos.pack(anchor=tk.W, pady=2)
        
        self.lbl_ventas = ttk.Label(frame_estado, text="Ventas Totales: 0")
        self.lbl_ventas.pack(anchor=tk.W, pady=2)
        
        self.lbl_politica = ttk.Label(frame_estado, text="Política: N/A", 
                                     font=("Arial", 9, "italic"))
        self.lbl_politica.pack(anchor=tk.W, pady=2)
        
        # ===== LISTA DE PRODUCTOS =====
        frame_productos = ttk.LabelFrame(self.frame, text="📦 Productos", padding=10)
        frame_productos.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Crear TreeView
        columnas = ("inventario", "punto_pedido", "estado")
        self.tree_productos = ttk.Treeview(
            frame_productos,
            columns=columnas,
            show="tree headings",
            height=10,
            selectmode="browse"
        )
        
        # Configurar columnas
        self.tree_productos.heading("#0", text="Producto")
        self.tree_productos.column("#0", width=120, minwidth=100)
        
        self.tree_productos.heading("inventario", text="Inventario")
        self.tree_productos.column("inventario", width=70, anchor=tk.CENTER)
        
        self.tree_productos.heading("punto_pedido", text="Punto Ped.")
        self.tree_productos.column("punto_pedido", width=70, anchor=tk.CENTER)
        
        self.tree_productos.heading("estado", text="Estado")
        self.tree_productos.column("estado", width=60, anchor=tk.CENTER)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(frame_productos, orient=tk.VERTICAL, 
                                 command=self.tree_productos.yview)
        self.tree_productos.configure(yscrollcommand=scrollbar.set)
        
        # Empacar
        self.tree_productos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind de selección
        self.tree_productos.bind("<<TreeviewSelect>>", self._on_seleccionar_producto)
        
        # ===== CONFIGURACIÓN DE PRODUCTO =====
        frame_config = ttk.LabelFrame(self.frame, text="⚙️ Configurar Producto", padding=10)
        frame_config.pack(fill=tk.X)
        
        # Nombre del producto seleccionado
        self.lbl_producto_sel = ttk.Label(frame_config, text="Seleccione un producto", 
                                         font=("Arial", 9, "italic"))
        self.lbl_producto_sel.pack(anchor=tk.W, pady=(0, 5))
        
        # Punto de pedido
        frame_punto = ttk.Frame(frame_config)
        frame_punto.pack(fill=tk.X, pady=2)
        
        ttk.Label(frame_punto, text="Punto de Pedido:", width=15).pack(side=tk.LEFT)
        self.entry_punto_pedido = ttk.Entry(frame_punto, width=10)
        self.entry_punto_pedido.pack(side=tk.LEFT, padx=5)
        ttk.Label(frame_punto, text="unidades").pack(side=tk.LEFT)
        
        # Demanda estimada
        frame_demanda = ttk.Frame(frame_config)
        frame_demanda.pack(fill=tk.X, pady=2)
        
        ttk.Label(frame_demanda, text="Demanda Estimada:", width=15).pack(side=tk.LEFT)
        self.entry_demanda = ttk.Entry(frame_demanda, width=10)
        self.entry_demanda.pack(side=tk.LEFT, padx=5)
        ttk.Label(frame_demanda, text="unid/día").pack(side=tk.LEFT)
        
        # Botón aplicar
        self.btn_aplicar = ttk.Button(
            frame_config,
            text="✓ Aplicar Cambios",
            command=self._on_aplicar_click,
            state="disabled"
        )
        self.btn_aplicar.pack(pady=(10, 0))
    
    # ===== CALLBACKS =====
    
    def _on_seleccionar_producto(self, event):
        """Callback al seleccionar un producto en la lista"""
        seleccion = self.tree_productos.selection()
        if not seleccion:
            return
        
        # Obtener ID del producto
        item = self.tree_productos.item(seleccion[0])
        self.producto_seleccionado = item['values'][3] if len(item['values']) > 3 else None
        
        if self.producto_seleccionado:
            # Actualizar label
            nombre_producto = item['text']
            self.lbl_producto_sel.config(text=f"Producto: {nombre_producto}")
            
            # Cargar valores actuales
            inventario = item['values'][0]
            punto_pedido = item['values'][1]
            
            self.entry_punto_pedido.delete(0, tk.END)
            self.entry_punto_pedido.insert(0, str(punto_pedido))
            
            # La demanda se cargará desde el estado completo
            self.entry_demanda.delete(0, tk.END)
            
            # Habilitar botón
            self.btn_aplicar.config(state="normal")
    
    def _on_aplicar_click(self):
        """Callback al hacer clic en aplicar"""
        if not self.producto_seleccionado:
            messagebox.showwarning("Advertencia", "Seleccione un producto primero")
            return
        
        try:
            punto_pedido = int(self.entry_punto_pedido.get())
            demanda = float(self.entry_demanda.get())
            
            if punto_pedido < 0 or demanda < 0:
                raise ValueError("Los valores no pueden ser negativos")
            
            if self.on_aplicar_config:
                self.on_aplicar_config(self.producto_seleccionado, punto_pedido, demanda)
        
        except ValueError as e:
            messagebox.showerror("Error", f"Valores inválidos: {str(e)}")
    
    # ===== MÉTODOS PÚBLICOS =====
    
    def actualizar_estado(self, estado: Dict):
        """
        Actualiza el estado general y la lista de productos
        
        Args:
            estado: Diccionario con el estado del simulador
        """
        # Actualizar estado general
        self.lbl_dia.config(text=f"Día: {estado['dia']}")
        
        finanzas = estado.get('finanzas', {})
        saldo = finanzas.get('saldo_actual', 0)
        utilidad = finanzas.get('utilidad_neta', 0)
        rentabilidad = finanzas.get('rentabilidad', 0)
        
        # Colorear saldo según valor
        color_saldo = "green" if saldo > 0 else "red"
        self.lbl_saldo.config(
            text=formatear_moneda(saldo),
            foreground=color_saldo
        )
        
        # Colorear utilidad según valor
        color_utilidad = "green" if utilidad > 0 else "red"
        self.lbl_utilidad.config(
            text=f"Utilidad Neta: {formatear_moneda(utilidad)}",
            foreground=color_utilidad
        )
        
        self.lbl_rentabilidad.config(text=f"Rentabilidad: {formatear_porcentaje(rentabilidad)}")
        
        # Métricas
        metricas = estado.get('metricas', {})
        desabast = metricas.get('desabastecimientos', 0)
        ventas = metricas.get('ventas_totales', 0)
        
        # Colorear desabastecimientos
        color_desabast = "red" if desabast > 5 else "orange" if desabast > 0 else "green"
        self.lbl_desabastecimientos.config(
            text=f"Desabastecimientos: {desabast}",
            foreground=color_desabast
        )
        
        self.lbl_ventas.config(text=f"Ventas Totales: {ventas}")
        
        # Política
        gestor = estado.get('gestor', {})
        politica = gestor.get('politica_actual', 'N/A')
        sensibilidad = gestor.get('sensibilidad', 1.0)
        self.lbl_politica.config(
            text=f"Política: {politica} (Sens: {sensibilidad:.2f})"
        )
        
        # Actualizar lista de productos
        self._actualizar_lista_productos(estado.get('productos', {}))
    
    def _actualizar_lista_productos(self, productos: Dict):
        """
        Actualiza la lista de productos en el TreeView
        
        Args:
            productos: Diccionario de productos
        """
        # Guardar selección actual
        seleccion_actual = self.tree_productos.selection()
        producto_sel_id = None
        if seleccion_actual:
            item = self.tree_productos.item(seleccion_actual[0])
            if len(item['values']) > 3:
                producto_sel_id = item['values'][3]
        
        # Limpiar tree
        for item in self.tree_productos.get_children():
            self.tree_productos.delete(item)
        
        # Agregar productos
        for prod_id, datos in productos.items():
            nombre = datos.get('nombre', prod_id)
            inventario = datos.get('inventario', 0)
            punto_pedido = datos.get('punto_pedido', 0)
            
            # Determinar estado
            if inventario == 0:
                estado = "❌"
                tags = ("critico",)
            elif inventario <= punto_pedido:
                estado = "⚠️"
                tags = ("bajo",)
            else:
                estado = "✓"
                tags = ("normal",)
            
            # Insertar item
            item_id = self.tree_productos.insert(
                "",
                tk.END,
                text=nombre,
                values=(inventario, punto_pedido, estado, prod_id),
                tags=tags
            )
            
            # Restaurar selección
            if producto_sel_id == prod_id:
                self.tree_productos.selection_set(item_id)
        
        # Configurar tags
        self.tree_productos.tag_configure("critico", foreground="red")
        self.tree_productos.tag_configure("bajo", foreground="orange")
        self.tree_productos.tag_configure("normal", foreground="green")
    
    def limpiar(self):
        """Limpia el panel"""
        self.lbl_dia.config(text="Día: 0")
        self.lbl_saldo.config(text="Saldo: $0.00", foreground="black")
        self.lbl_utilidad.config(text="Utilidad Neta: $0.00", foreground="black")
        self.lbl_rentabilidad.config(text="Rentabilidad: 0.00%")
        self.lbl_desabastecimientos.config(text="Desabastecimientos: 0", foreground="black")
        self.lbl_ventas.config(text="Ventas Totales: 0")
        self.lbl_politica.config(text="Política: N/A")
        
        for item in self.tree_productos.get_children():
            self.tree_productos.delete(item)
        
        self.lbl_producto_sel.config(text="Seleccione un producto")
        self.entry_punto_pedido.delete(0, tk.END)
        self.entry_demanda.delete(0, tk.END)
        self.btn_aplicar.config(state="disabled")
        self.producto_seleccionado = None