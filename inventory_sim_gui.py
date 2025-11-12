"""
Interfaz Gráfica para el Sistema de Simulación de Inventario
Usando Tkinter y Matplotlib para visualización
"""

import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np

# Importar las clases del simulador
# from inventory_sim_base import *


class InterfazSimulador:
    """Interfaz gráfica principal del simulador"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Gestión de Inventario")
        self.root.geometry("1400x900")
        
        # Simulador (se inicializa después)
        self.simulador = None
        self.running = False
        
        # Datos para gráficas
        self.historia_inventario = {}
        self.historia_financiera = {
            'dias': [],
            'saldo': [],
            'ingresos': [],
            'egresos': []
        }
        
        self._crear_interfaz()
    
    def _crear_interfaz(self):
        """Crea todos los componentes de la interfaz"""
        
        # ===== PANEL SUPERIOR: CONFIGURACIÓN =====
        frame_config = ttk.LabelFrame(self.root, text="Configuración Inicial", padding=10)
        frame_config.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
        
        # Método de inventario
        ttk.Label(frame_config, text="Método de Inventario:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.metodo_var = tk.StringVar(value="PEPS")
        ttk.Combobox(frame_config, textvariable=self.metodo_var, 
                     values=["PEPS", "UEPS", "PROMEDIO"], width=15).grid(row=0, column=1, padx=5)
        
        # Política de reposición
        ttk.Label(frame_config, text="Política de Reposición:").grid(row=0, column=2, sticky=tk.W, padx=5)
        self.politica_var = tk.StringVar(value="CONSERVADORA")
        ttk.Combobox(frame_config, textvariable=self.politica_var,
                     values=["CONSERVADORA", "AGRESIVA", "ADAPTATIVA"], width=15).grid(row=0, column=3, padx=5)
        
        # Botones de control
        ttk.Button(frame_config, text="Inicializar Simulación", 
                   command=self._inicializar_simulacion).grid(row=0, column=4, padx=10)
        ttk.Button(frame_config, text="Avanzar 1 Día", 
                   command=self._avanzar_dia).grid(row=0, column=5, padx=5)
        ttk.Button(frame_config, text="Simular 30 Días", 
                   command=self._simular_periodo).grid(row=0, column=6, padx=5)
        ttk.Button(frame_config, text="Reiniciar", 
                   command=self._reiniciar).grid(row=0, column=7, padx=5)
        
        # ===== PANEL IZQUIERDO: PRODUCTOS Y ESTADO =====
        frame_izq = ttk.Frame(self.root)
        frame_izq.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=10, pady=5)
        
        # Estado general
        frame_estado = ttk.LabelFrame(frame_izq, text="Estado General", padding=10)
        frame_estado.pack(fill=tk.X, pady=5)
        
        self.lbl_dia = ttk.Label(frame_estado, text="Día: 0", font=("Arial", 12, "bold"))
        self.lbl_dia.pack(anchor=tk.W)
        
        self.lbl_saldo = ttk.Label(frame_estado, text="Saldo: $0.00", font=("Arial", 11))
        self.lbl_saldo.pack(anchor=tk.W)
        
        self.lbl_utilidad = ttk.Label(frame_estado, text="Utilidad Neta: $0.00", font=("Arial", 11))
        self.lbl_utilidad.pack(anchor=tk.W)
        
        self.lbl_desabastecimientos = ttk.Label(frame_estado, text="Desabastecimientos: 0")
        self.lbl_desabastecimientos.pack(anchor=tk.W)
        
        self.lbl_politica = ttk.Label(frame_estado, text="Política: N/A")
        self.lbl_politica.pack(anchor=tk.W)
        
        # Lista de productos
        frame_productos = ttk.LabelFrame(frame_izq, text="Productos", padding=10)
        frame_productos.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Tabla de productos
        columnas = ("ID", "Inventario", "Punto Pedido")
        self.tree_productos = ttk.Treeview(frame_productos, columns=columnas, 
                                           show="tree headings", height=10)
        
        self.tree_productos.heading("#0", text="Nombre")
        self.tree_productos.column("#0", width=100)
        
        for col in columnas:
            self.tree_productos.heading(col, text=col)
            self.tree_productos.column(col, width=80)
        
        scrollbar = ttk.Scrollbar(frame_productos, orient=tk.VERTICAL, 
                                  command=self.tree_productos.yview)
        self.tree_productos.configure(yscrollcommand=scrollbar.set)
        
        self.tree_productos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Configuración de producto
        frame_config_prod = ttk.LabelFrame(frame_izq, text="Configurar Producto", padding=10)
        frame_config_prod.pack(fill=tk.X, pady=5)
        
        ttk.Label(frame_config_prod, text="Punto de Pedido:").grid(row=0, column=0, sticky=tk.W)
        self.entry_punto_pedido = ttk.Entry(frame_config_prod, width=10)
        self.entry_punto_pedido.grid(row=0, column=1, padx=5)
        
        ttk.Label(frame_config_prod, text="Demanda Est.:").grid(row=1, column=0, sticky=tk.W)
        self.entry_demanda = ttk.Entry(frame_config_prod, width=10)
        self.entry_demanda.grid(row=1, column=1, padx=5)
        
        ttk.Button(frame_config_prod, text="Aplicar", 
                   command=self._aplicar_config_producto).grid(row=2, column=0, columnspan=2, pady=5)
        
        # ===== PANEL CENTRAL: GRÁFICAS =====
        frame_graficas = ttk.Frame(self.root)
        frame_graficas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Notebook para múltiples gráficas
        self.notebook = ttk.Notebook(frame_graficas)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Pestaña 1: Inventario
        self.tab_inventario = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_inventario, text="Niveles de Inventario")
        
        self.fig_inventario = Figure(figsize=(8, 6))
        self.ax_inventario = self.fig_inventario.add_subplot(111)
        self.canvas_inventario = FigureCanvasTkAgg(self.fig_inventario, self.tab_inventario)
        self.canvas_inventario.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Pestaña 2: Finanzas
        self.tab_finanzas = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_finanzas, text="Estado Financiero")
        
        self.fig_finanzas = Figure(figsize=(8, 6))
        self.ax_finanzas = self.fig_finanzas.add_subplot(111)
        self.canvas_finanzas = FigureCanvasTkAgg(self.fig_finanzas, self.tab_finanzas)
        self.canvas_finanzas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Pestaña 3: Eventos
        self.tab_eventos = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_eventos, text="Registro de Eventos")
        
        self.text_eventos = tk.Text(self.tab_eventos, height=20, width=60)
        scrollbar_eventos = ttk.Scrollbar(self.tab_eventos, command=self.text_eventos.yview)
        self.text_eventos.configure(yscrollcommand=scrollbar_eventos.set)
        
        self.text_eventos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_eventos.pack(side=tk.RIGHT, fill=tk.Y)
    
    def _inicializar_simulacion(self):
        """Inicializa una nueva simulación con datos de ejemplo"""
        from inventory_sim_base import (
            SimuladorInventario, MetodoInventario, Producto, 
            Proveedor, Cliente, TipoCliente, PoliticaReposicion
        )
        
        # Convertir strings a enums
        metodo = MetodoInventario[self.metodo_var.get()]
        
        # Crear simulador
        self.simulador = SimuladorInventario(metodo)
        
        # Configurar política
        politica = PoliticaReposicion[self.politica_var.get()]
        self.simulador.gestor.politica = politica
        
        # Crear productos de ejemplo
        productos_ejemplo = [
            Producto("PROD001", "Tornillo M6", costo_unitario=0.5, precio_venta=1.2, 
                     punto_pedido=50, demanda_estimada=10, tiempo_reposicion=3),
            Producto("PROD002", "Tuerca M6", costo_unitario=0.3, precio_venta=0.9,
                     punto_pedido=60, demanda_estimada=12, tiempo_reposicion=3),
            Producto("PROD003", "Arandela", costo_unitario=0.1, precio_venta=0.4,
                     punto_pedido=100, demanda_estimada=20, tiempo_reposicion=2)
        ]
        
        for prod in productos_ejemplo:
            # Agregar inventario inicial
            prod.agregar_lote(100, prod.costo_unitario, self.simulador.fecha_actual)
            self.simulador.agregar_producto(prod)
            self.historia_inventario[prod.id] = []
        
        # Crear proveedores
        proveedores_ejemplo = [
            Proveedor("PROV001", "Suministros ABC", 
                      productos_ofrecidos=["PROD001", "PROD002", "PROD003"],
                      tiempo_entrega=3, costo_base=0.5, fiabilidad=0.95,
                      descuento_volumen={"PROD001": (100, 0.1), "PROD002": (150, 0.15)}),
            Proveedor("PROV002", "Distribuidora XYZ",
                      productos_ofrecidos=["PROD001", "PROD003"],
                      tiempo_entrega=2, costo_base=0.55, fiabilidad=0.98)
        ]
        
        for prov in proveedores_ejemplo:
            self.simulador.agregar_proveedor(prov)
        
        # Crear clientes
        clientes_ejemplo = [
            Cliente("CLI001", "Ferretería XYZ", TipoCliente.MINORISTA,
                    productos_solicitados=["PROD001", "PROD002"],
                    frecuencia_compra=3, cantidad_promedio=15, prioridad=3),
            Cliente("CLI002", "Construcciones ABC", TipoCliente.MAYORISTA,
                    productos_solicitados=["PROD001", "PROD003"],
                    frecuencia_compra=7, cantidad_promedio=50, prioridad=4),
            Cliente("CLI003", "Taller Local", TipoCliente.MINORISTA,
                    productos_solicitados=["PROD002", "PROD003"],
                    frecuencia_compra=2, cantidad_promedio=10, prioridad=2)
        ]
        
        for cli in clientes_ejemplo:
            self.simulador.agregar_cliente(cli)
        
        # Limpiar historia
        self.historia_financiera = {'dias': [], 'saldo': [], 'ingresos': [], 'egresos': []}
        
        # Actualizar interfaz
        self._actualizar_interfaz()
        
        messagebox.showinfo("Éxito", "Simulación inicializada correctamente")
    
    def _avanzar_dia(self):
        """Avanza un día en la simulación"""
        if not self.simulador:
            messagebox.showwarning("Advertencia", "Primero inicialice la simulación")
            return
        
        self.simulador.avanzar_dia()
        self._actualizar_interfaz()
        self._agregar_eventos_recientes()
    
    def _simular_periodo(self):
        """Simula 30 días"""
        if not self.simulador:
            messagebox.showwarning("Advertencia", "Primero inicialice la simulación")
            return
        
        for _ in range(30):
            self.simulador.avanzar_dia()
            self._actualizar_historia()
        
        self._actualizar_interfaz()
        self._actualizar_graficas()
        
        messagebox.showinfo("Completado", "Simulación de 30 días completada")
    
    def _reiniciar(self):
        """Reinicia la simulación"""
        self.simulador = None
        self.historia_inventario = {}
        self.historia_financiera = {'dias': [], 'saldo': [], 'ingresos': [], 'egresos': []}
        
        # Limpiar interfaz
        for item in self.tree_productos.get_children():
            self.tree_productos.delete(item)
        
        self.text_eventos.delete(1.0, tk.END)
        
        self.ax_inventario.clear()
        self.canvas_inventario.draw()
        
        self.ax_finanzas.clear()
        self.canvas_finanzas.draw()
        
        messagebox.showinfo("Reinicio", "Simulación reiniciada")
    
    def _actualizar_interfaz(self):
        """Actualiza todos los elementos de la interfaz"""
        if not self.simulador:
            return
        
        estado = self.simulador.obtener_estado()
        
        # Actualizar etiquetas
        self.lbl_dia.config(text=f"Día: {estado['dia']}")
        self.lbl_saldo.config(text=f"Saldo: ${estado['finanzas']['saldo']:.2f}")
        self.lbl_utilidad.config(text=f"Utilidad Neta: ${estado['finanzas']['utilidad']:.2f}")
        self.lbl_desabastecimientos.config(text=f"Desabastecimientos: {estado['desabastecimientos']}")
        self.lbl_politica.config(text=f"Política: {estado['politica']}")
        
        # Actualizar tabla de productos
        for item in self.tree_productos.get_children():
            self.tree_productos.delete(item)
        
        for prod_id, producto in self.simulador.productos.items():
            self.tree_productos.insert("", tk.END, text=producto.nombre,
                                       values=(prod_id, producto.nivel_inventario, 
                                               producto.punto_pedido))
        
        # Actualizar historia
        self._actualizar_historia()
        self._actualizar_graficas()
    
    def _actualizar_historia(self):
        """Actualiza el historial de datos"""
        if not self.simulador:
            return
        
        estado = self.simulador.obtener_estado()
        
        # Historia financiera
        self.historia_financiera['dias'].append(estado['dia'])
        self.historia_financiera['saldo'].append(estado['finanzas']['saldo'])
        self.historia_financiera['ingresos'].append(estado['finanzas']['ingresos'])
        self.historia_financiera['egresos'].append(estado['finanzas']['egresos'])
        
        # Historia de inventario
        for prod_id, datos in estado['productos'].items():
            if prod_id not in self.historia_inventario:
                self.historia_inventario[prod_id] = []
            self.historia_inventario[prod_id].append(datos['inventario'])
    
    def _actualizar_graficas(self):
        """Actualiza las gráficas"""
        if not self.simulador or not self.historia_financiera['dias']:
            return
        
        # Gráfica de inventario
        self.ax_inventario.clear()
        self.ax_inventario.set_title("Evolución del Inventario")
        self.ax_inventario.set_xlabel("Día")
        self.ax_inventario.set_ylabel("Unidades")
        self.ax_inventario.grid(True, alpha=0.3)
        
        for prod_id, historia in self.historia_inventario.items():
            if historia:
                producto = self.simulador.productos[prod_id]
                dias = range(len(historia))
                self.ax_inventario.plot(dias, historia, marker='o', 
                                        label=f"{producto.nombre}", linewidth=2)
                # Línea de punto de pedido
                self.ax_inventario.axhline(y=producto.punto_pedido, 
                                           linestyle='--', alpha=0.5)
        
        self.ax_inventario.legend()
        self.canvas_inventario.draw()
        
        # Gráfica financiera
        self.ax_finanzas.clear()
        self.ax_finanzas.set_title("Estado Financiero")
        self.ax_finanzas.set_xlabel("Día")
        self.ax_finanzas.set_ylabel("Monto ($)")
        self.ax_finanzas.grid(True, alpha=0.3)
        
        dias = self.historia_financiera['dias']
        self.ax_finanzas.plot(dias, self.historia_financiera['saldo'], 
                              marker='o', label='Saldo', linewidth=2, color='green')
        self.ax_finanzas.plot(dias, self.historia_financiera['ingresos'], 
                              marker='s', label='Ingresos Acumulados', linewidth=2, color='blue')
        self.ax_finanzas.plot(dias, self.historia_financiera['egresos'], 
                              marker='^', label='Egresos Acumulados', linewidth=2, color='red')
        
        self.ax_finanzas.legend()
        self.canvas_finanzas.draw()
    
    def _agregar_eventos_recientes(self):
        """Agrega los eventos más recientes al log"""
        if not self.simulador or not self.simulador.eventos_log:
            return
        
        # Obtener últimos 5 eventos
        eventos_recientes = self.simulador.eventos_log[-5:]
        
        for evento in eventos_recientes:
            texto = f"Día {evento['dia']} - {evento['tipo']}: "
            
            if evento['tipo'] == 'VENTA':
                texto += f"{evento['cliente']} compró {evento['cantidad']} de {evento['producto']} (+${evento['ingreso']:.2f})"
            elif evento['tipo'] == 'DESABASTECIMIENTO':
                texto += f"{evento['cliente']} no pudo comprar {evento['cantidad']} de {evento['producto']} (-${evento['penalizacion']:.2f})"
            elif evento['tipo'] == 'PEDIDO':
                texto += f"Pedido a {evento['proveedor']}: {evento['cantidad']} de {evento['producto']} (-${evento['costo']:.2f})"
            elif evento['tipo'] == 'RECEPCION':
                texto += f"Recibido: {evento['cantidad']} de {evento['producto']}"
            
            self.text_eventos.insert(tk.END, texto + "\n")
            self.text_eventos.see(tk.END)
    
    def _aplicar_config_producto(self):
        """Aplica configuración al producto seleccionado"""
        seleccion = self.tree_productos.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione un producto")
            return
        
        item = self.tree_productos.item(seleccion[0])
        prod_id = item['values'][0]
        
        try:
            nuevo_punto = int(self.entry_punto_pedido.get())
            nueva_demanda = float(self.entry_demanda.get())
            
            producto = self.simulador.productos[prod_id]
            producto.punto_pedido = nuevo_punto
            producto.demanda_estimada = nueva_demanda
            
            self._actualizar_interfaz()
            messagebox.showinfo("Éxito", "Configuración aplicada")
        except ValueError:
            messagebox.showerror("Error", "Valores inválidos")


def main():
    """Función principal"""
    root = tk.Tk()
    app = InterfazSimulador(root)
    root.mainloop()


if __name__ == "__main__":
    main()
