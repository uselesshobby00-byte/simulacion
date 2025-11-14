"""
gui/interfaz_principal.py
Ventana principal de la aplicación
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional

from core.simulador import SimuladorInventario
from gui.panel_configuracion import PanelConfiguracion
from gui.panel_productos import PanelProductos
from gui.panel_graficas import PanelGraficas
from utils.exportador import ExportadorDatos
from config.configuracion import VENTANA_ANCHO, VENTANA_ALTO, VENTANA_TITULO


class InterfazPrincipal:
    """
    Ventana principal que coordina todos los componentes de la interfaz
    
    Attributes:
        root: Ventana raíz de Tkinter
        simulador: Instancia del simulador de inventario
    """
    
    def __init__(self, root: tk.Tk, simulador: Optional[SimuladorInventario] = None):
        """
        Inicializa la interfaz principal
        
        Args:
            root: Ventana raíz de Tkinter
            simulador: Simulador pre-configurado (opcional)
        """
        self.root = root
        self.simulador = simulador
        self.exportador = ExportadorDatos()
        
        # Configurar ventana principal
        self._configurar_ventana()
        
        # Crear componentes de la interfaz
        self._crear_menu()
        self._crear_interfaz()
        
        # Si hay simulador, actualizar interfaz
        if self.simulador:
            self._actualizar_interfaz_completa()
    
    def _configurar_ventana(self):
        """Configura las propiedades de la ventana principal"""
        self.root.title(VENTANA_TITULO)
        self.root.geometry(f"{VENTANA_ANCHO}x{VENTANA_ALTO}")
        
        # Configurar redimensionamiento
        self.root.rowconfigure(1, weight=1)
        self.root.columnconfigure(0, weight=1)
        
        # Centrar ventana en la pantalla
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (VENTANA_ANCHO // 2)
        y = (self.root.winfo_screenheight() // 2) - (VENTANA_ALTO // 2)
        self.root.geometry(f"{VENTANA_ANCHO}x{VENTANA_ALTO}+{x}+{y}")
    
    def _crear_menu(self):
        """Crea la barra de menú"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menú Archivo
        menu_archivo = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Archivo", menu=menu_archivo)
        menu_archivo.add_command(label="Nueva Simulación", command=self._nueva_simulacion)
        menu_archivo.add_command(label="Reiniciar", command=self._reiniciar_simulacion)
        menu_archivo.add_separator()
        menu_archivo.add_command(label="Exportar Resumen", command=self._exportar_resumen)
        menu_archivo.add_command(label="Exportar Todo", command=self._exportar_todo)
        menu_archivo.add_separator()
        menu_archivo.add_command(label="Salir", command=self._salir)
        
        # Menú Simulación
        menu_simulacion = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Simulación", menu=menu_simulacion)
        menu_simulacion.add_command(label="Avanzar 1 Día", command=self._avanzar_un_dia)
        menu_simulacion.add_command(label="Simular 7 Días", command=lambda: self._simular_dias(7))
        menu_simulacion.add_command(label="Simular 30 Días", command=lambda: self._simular_dias(30))
        menu_simulacion.add_command(label="Simular 90 Días", command=lambda: self._simular_dias(90))
        
        # Menú Ayuda
        menu_ayuda = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ayuda", menu=menu_ayuda)
        menu_ayuda.add_command(label="Acerca de", command=self._mostrar_acerca_de)
        menu_ayuda.add_command(label="Manual de Usuario", command=self._mostrar_manual)
    
    def _crear_interfaz(self):
        """Crea todos los componentes de la interfaz"""
        
        # Panel de configuración (superior)
        self.panel_config = PanelConfiguracion(
            self.root,
            on_inicializar=self._inicializar_desde_panel,
            on_avanzar=self._avanzar_un_dia,
            on_simular=lambda: self._simular_dias(30),
            on_reiniciar=self._reiniciar_simulacion
        )
        self.panel_config.frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        # Frame contenedor para paneles izquierdo y derecho
        frame_contenedor = ttk.Frame(self.root)
        frame_contenedor.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        frame_contenedor.rowconfigure(0, weight=1)
        frame_contenedor.columnconfigure(0, weight=0)  # Panel izquierdo fijo
        frame_contenedor.columnconfigure(1, weight=1)  # Panel derecho expandible
        
        # Panel de productos (izquierdo)
        self.panel_productos = PanelProductos(
            frame_contenedor,
            on_aplicar_config=self._aplicar_configuracion_producto
        )
        self.panel_productos.frame.grid(row=0, column=0, sticky="ns", padx=5, pady=5)
        
        # Panel de gráficas (derecho)
        self.panel_graficas = PanelGraficas(frame_contenedor)
        self.panel_graficas.frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        
        # Barra de estado (inferior)
        self._crear_barra_estado()
    
    def _crear_barra_estado(self):
        """Crea la barra de estado en la parte inferior"""
        self.barra_estado = ttk.Label(
            self.root,
            text="Listo para iniciar simulación",
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.barra_estado.grid(row=2, column=0, sticky="ew")
    
    # ==================== CALLBACKS DE PANELES ====================
    
    def _inicializar_desde_panel(self, metodo: str, politica: str):
        """
        Callback cuando se inicializa desde el panel de configuración
        
        Args:
            metodo: Método de inventario seleccionado
            politica: Política de reposición seleccionada
        """
        if self.simulador is None:
            messagebox.showwarning(
                "Advertencia",
                "No hay simulador cargado. Use 'Archivo > Nueva Simulación' primero."
            )
            return
        
        # Actualizar configuración del simulador existente
        from models.enums import MetodoInventario, PoliticaReposicion
        self.simulador.metodo_inventario = MetodoInventario[metodo]
        self.simulador.gestor.politica = PoliticaReposicion[politica]
        
        self._actualizar_interfaz_completa()
        self._actualizar_barra_estado("Configuración actualizada")
        messagebox.showinfo("Éxito", "Configuración aplicada correctamente")
    
    def _aplicar_configuracion_producto(self, producto_id: str, punto_pedido: int, demanda: float):
        """
        Callback cuando se aplica configuración a un producto
        
        Args:
            producto_id: ID del producto
            punto_pedido: Nuevo punto de pedido
            demanda: Nueva demanda estimada
        """
        if not self.simulador or producto_id not in self.simulador.productos:
            messagebox.showerror("Error", "Producto no encontrado")
            return
        
        producto = self.simulador.productos[producto_id]
        producto.punto_pedido = punto_pedido
        producto.demanda_estimada = demanda
        
        self._actualizar_interfaz_completa()
        self._actualizar_barra_estado(f"Producto {producto_id} actualizado")
        messagebox.showinfo("Éxito", "Configuración del producto actualizada")
    
    # ==================== ACCIONES DE SIMULACIÓN ====================
    
    def _avanzar_un_dia(self):
        """Avanza un día en la simulación"""
        if not self.simulador:
            messagebox.showwarning("Advertencia", "Primero inicialice la simulación")
            return
        
        self.simulador.avanzar_dia()
        self._actualizar_interfaz_completa()
        self._actualizar_barra_estado(f"Día {self.simulador.dia_simulacion} completado")
    
    def _simular_dias(self, num_dias: int):
        """
        Simula múltiples días
        
        Args:
            num_dias: Número de días a simular
        """
        if not self.simulador:
            messagebox.showwarning("Advertencia", "Primero inicialice la simulación")
            return
        
        # Mostrar ventana de progreso
        ventana_progreso = tk.Toplevel(self.root)
        ventana_progreso.title("Simulando...")
        ventana_progreso.geometry("300x100")
        ventana_progreso.transient(self.root)
        ventana_progreso.grab_set()
        
        ttk.Label(ventana_progreso, text=f"Simulando {num_dias} días...").pack(pady=10)
        progreso = ttk.Progressbar(ventana_progreso, length=250, mode='determinate')
        progreso.pack(pady=10)
        
        # Simular día por día con actualización de progreso
        for i in range(num_dias):
            self.simulador.avanzar_dia()
            progreso['value'] = ((i + 1) / num_dias) * 100
            ventana_progreso.update()
        
        ventana_progreso.destroy()
        
        self._actualizar_interfaz_completa()
        self._actualizar_barra_estado(f"Simulación de {num_dias} días completada")
        messagebox.showinfo("Completado", f"Simulación de {num_dias} días completada exitosamente")
    
    def _reiniciar_simulacion(self):
        """Reinicia la simulación actual"""
        if not self.simulador:
            return
        
        respuesta = messagebox.askyesno(
            "Confirmar",
            "¿Está seguro de que desea reiniciar la simulación?\nSe perderán todos los datos actuales."
        )
        
        if respuesta:
            self.simulador.reiniciar()
            self._actualizar_interfaz_completa()
            self._actualizar_barra_estado("Simulación reiniciada")
    
    def _nueva_simulacion(self):
        """Crea una nueva simulación"""
        # Esta función se llama desde el menú
        # El simulador ya viene configurado desde main.py
        messagebox.showinfo(
            "Nueva Simulación",
            "Para crear una nueva simulación, reinicie la aplicación.\n\n"
            "Próximamente: diálogo para configurar nueva simulación."
        )
    
    # ==================== ACTUALIZACIÓN DE INTERFAZ ====================
    
    def _actualizar_interfaz_completa(self):
        """Actualiza todos los componentes de la interfaz"""
        if not self.simulador:
            return
        
        estado = self.simulador.obtener_estado()
        
        # Actualizar panel de productos
        self.panel_productos.actualizar_estado(estado)
        
        # Actualizar gráficas
        self.panel_graficas.actualizar_graficas(self.simulador)
        
        # Actualizar eventos
        eventos_recientes = self.simulador.obtener_eventos_recientes(20)
        self.panel_graficas.actualizar_eventos(eventos_recientes)
    
    def _actualizar_barra_estado(self, mensaje: str):
        """
        Actualiza el mensaje de la barra de estado
        
        Args:
            mensaje: Mensaje a mostrar
        """
        self.barra_estado.config(text=mensaje)
        self.root.update_idletasks()
    
    # ==================== EXPORTACIÓN ====================
    
    def _exportar_resumen(self):
        """Exporta un resumen de la simulación"""
        if not self.simulador:
            messagebox.showwarning("Advertencia", "No hay simulación para exportar")
            return
        
        try:
            estado = self.simulador.obtener_estado()
            archivo = self.exportador.exportar_resumen_simulacion(estado)
            messagebox.showinfo("Éxito", f"Resumen exportado a:\n{archivo}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar: {str(e)}")
    
    def _exportar_todo(self):
        """Exporta todos los datos de la simulación"""
        if not self.simulador:
            messagebox.showwarning("Advertencia", "No hay simulación para exportar")
            return
        
        try:
            archivos = self.exportador.exportar_todo(self.simulador)
            mensaje = f"Se exportaron {len(archivos)} archivos:\n\n"
            for tipo, ruta in archivos.items():
                mensaje += f"• {tipo}\n"
            messagebox.showinfo("Éxito", mensaje)
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar: {str(e)}")
    
    # ==================== MENÚ AYUDA ====================
    
    def _mostrar_acerca_de(self):
        """Muestra información sobre la aplicación"""
        ventana = tk.Toplevel(self.root)
        ventana.title("Acerca de")
        ventana.geometry("400x300")
        ventana.transient(self.root)
        ventana.grab_set()
        
        texto = """
        Simulador de Gestión de Inventario
        Versión 1.0
        
        Sistema de simulación de eventos discretos para
        análisis y optimización de políticas de inventario.
        
        Características:
        • Simulación de eventos discretos
        • Múltiples políticas de reposición
        • Métodos PEPS, UEPS y Promedio
        • Análisis financiero completo
        • Exportación de datos
        
        Desarrollado como proyecto educativo de
        simulación de sistemas de inventario.
        """
        
        ttk.Label(ventana, text=texto, justify=tk.LEFT, padding=20).pack()
        ttk.Button(ventana, text="Cerrar", command=ventana.destroy).pack(pady=10)
    
    def _mostrar_manual(self):
        """Muestra el manual de usuario"""
        ventana = tk.Toplevel(self.root)
        ventana.title("Manual de Usuario")
        ventana.geometry("600x400")
        ventana.transient(self.root)
        
        # Crear frame con scrollbar
        frame = ttk.Frame(ventana)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        texto = tk.Text(frame, wrap=tk.WORD, yscrollcommand=scrollbar.set)
        texto.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=texto.yview)
        
        manual = """
MANUAL DE USUARIO - SIMULADOR DE INVENTARIO

1. INICIO RÁPIDO
   • La simulación ya está inicializada con datos de ejemplo
   • Use el panel superior para controlar la simulación
   • Observe las gráficas actualizarse en tiempo real

2. CONFIGURACIÓN
   • Método de Inventario: PEPS, UEPS o Promedio
   • Política de Reposición: Conservadora, Agresiva o Adaptativa

3. CONTROLES
   • Avanzar 1 Día: Simula un solo día
   • Simular 30 Días: Ejecuta una simulación completa
   • Reiniciar: Vuelve al estado inicial

4. PANEL DE PRODUCTOS
   • Ver inventario actual de cada producto
   • Configurar punto de pedido y demanda estimada
   • Seleccione un producto y modifique los valores

5. GRÁFICAS
   • Pestaña Inventario: Evolución de niveles
   • Pestaña Finanzas: Ingresos, egresos y saldo
   • Pestaña Eventos: Registro de todas las operaciones

6. EXPORTACIÓN
   • Archivo > Exportar Resumen: Resume la simulación
   • Archivo > Exportar Todo: Todos los datos en CSV

7. INTERPRETACIÓN DE RESULTADOS
   • Utilidad Neta: Debe ser positiva y creciente
   • Desabastecimientos: Menos es mejor
   • Inventario: Debe mantenerse estable

8. POLÍTICAS DE REPOSICIÓN
   • CONSERVADORA: Minimiza costos de almacenamiento
   • AGRESIVA: Minimiza desabastecimiento
   • ADAPTATIVA: Se ajusta automáticamente

9. MÉTODOS DE INVENTARIO
   • PEPS: Primero en Entrar, Primero en Salir
   • UEPS: Último en Entrar, Primero en Salir
   • PROMEDIO: Costo Promedio Ponderado

Para más información, consulte el archivo README.md
        """
        
        texto.insert(1.0, manual)
        texto.config(state=tk.DISABLED)
        
        ttk.Button(ventana, text="Cerrar", command=ventana.destroy).pack(pady=10)
    
    def _salir(self):
        """Cierra la aplicación"""
        if messagebox.askokcancel("Salir", "¿Desea salir de la aplicación?"):
            self.root.quit()