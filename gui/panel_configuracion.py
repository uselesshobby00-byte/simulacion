"""
gui/panel_configuracion.py
Panel superior de configuración y control de la simulación
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable


class PanelConfiguracion:
    """
    Panel de configuración inicial y controles de simulación
    
    Attributes:
        frame: Frame contenedor del panel
        metodo_var: Variable para el método de inventario
        politica_var: Variable para la política de reposición
    """
    
    def __init__(self, parent, 
                 on_inicializar: Callable = None,
                 on_avanzar: Callable = None,
                 on_simular: Callable = None,
                 on_reiniciar: Callable = None):
        """
        Inicializa el panel de configuración
        
        Args:
            parent: Widget padre
            on_inicializar: Callback al inicializar
            on_avanzar: Callback al avanzar un día
            on_simular: Callback al simular periodo
            on_reiniciar: Callback al reiniciar
        """
        self.on_inicializar = on_inicializar
        self.on_avanzar = on_avanzar
        self.on_simular = on_simular
        self.on_reiniciar = on_reiniciar
        
        # Frame principal
        self.frame = ttk.LabelFrame(parent, text="⚙️ Configuración y Control", padding=10)
        
        # Variables
        self.metodo_var = tk.StringVar(value="PEPS")
        self.politica_var = tk.StringVar(value="CONSERVADORA")
        
        self._crear_widgets()
    
    def _crear_widgets(self):
        """Crea todos los widgets del panel"""
        
        # ===== SECCIÓN DE CONFIGURACIÓN =====
        frame_config = ttk.Frame(self.frame)
        frame_config.pack(side=tk.LEFT, padx=10)
        
        # Método de inventario
        ttk.Label(frame_config, text="📦 Método de Inventario:", 
                 font=("Arial", 9, "bold")).grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        
        combo_metodo = ttk.Combobox(
            frame_config,
            textvariable=self.metodo_var,
            values=["PEPS", "UEPS", "PROMEDIO"],
            width=15,
            state="readonly"
        )
        combo_metodo.grid(row=0, column=1, padx=5, pady=2)
        
        # Tooltip para método
        self._crear_tooltip(combo_metodo, 
            "PEPS: Primero en Entrar, Primero en Salir\n"
            "UEPS: Último en Entrar, Primero en Salir\n"
            "PROMEDIO: Costo Promedio Ponderado")
        
        # Política de reposición
        ttk.Label(frame_config, text="📊 Política de Reposición:", 
                 font=("Arial", 9, "bold")).grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        
        combo_politica = ttk.Combobox(
            frame_config,
            textvariable=self.politica_var,
            values=["CONSERVADORA", "AGRESIVA", "ADAPTATIVA"],
            width=15,
            state="readonly"
        )
        combo_politica.grid(row=1, column=1, padx=5, pady=2)
        
        # Tooltip para política
        self._crear_tooltip(combo_politica,
            "CONSERVADORA: Minimiza costos de almacenamiento\n"
            "AGRESIVA: Minimiza desabastecimientos\n"
            "ADAPTATIVA: Se ajusta según desempeño")
        
        # ===== SEPARADOR =====
        ttk.Separator(self.frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # ===== BOTONES DE CONTROL =====
        frame_botones = ttk.Frame(self.frame)
        frame_botones.pack(side=tk.LEFT, padx=10)
        
        # Fila 1: Inicializar y Avanzar
        frame_fila1 = ttk.Frame(frame_botones)
        frame_fila1.pack(pady=2)
        
        btn_inicializar = ttk.Button(
            frame_fila1,
            text="🚀 Aplicar Configuración",
            command=self._on_inicializar_click,
            width=20
        )
        btn_inicializar.pack(side=tk.LEFT, padx=5)
        
        btn_avanzar = ttk.Button(
            frame_fila1,
            text="▶️ Avanzar 1 Día",
            command=self._on_avanzar_click,
            width=15
        )
        btn_avanzar.pack(side=tk.LEFT, padx=5)
        
        # Fila 2: Simular y Reiniciar
        frame_fila2 = ttk.Frame(frame_botones)
        frame_fila2.pack(pady=2)
        
        btn_simular = ttk.Button(
            frame_fila2,
            text="⏩ Simular 30 Días",
            command=self._on_simular_click,
            width=20
        )
        btn_simular.pack(side=tk.LEFT, padx=5)
        
        btn_reiniciar = ttk.Button(
            frame_fila2,
            text="🔄 Reiniciar",
            command=self._on_reiniciar_click,
            width=15
        )
        btn_reiniciar.pack(side=tk.LEFT, padx=5)
        
        # ===== SEPARADOR =====
        ttk.Separator(self.frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # ===== INFORMACIÓN RÁPIDA =====
        frame_info = ttk.Frame(self.frame)
        frame_info.pack(side=tk.LEFT, padx=10)
        
        ttk.Label(frame_info, text="ℹ️ Información Rápida", 
                 font=("Arial", 9, "bold")).pack(anchor=tk.W)
        
        info_texto = tk.Text(frame_info, width=35, height=2, 
                            relief=tk.FLAT, background="#f0f0f0", 
                            font=("Arial", 8))
        info_texto.pack()
        info_texto.insert(1.0, 
            "• Use el menú Simulación para más opciones\n"
            "• Configure productos en el panel izquierdo\n"
            "• Exporte datos desde el menú Archivo")
        info_texto.config(state=tk.DISABLED)
    
    def _crear_tooltip(self, widget, texto):
        """
        Crea un tooltip para un widget
        
        Args:
            widget: Widget al que agregar el tooltip
            texto: Texto del tooltip
        """
        def mostrar_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            label = ttk.Label(tooltip, text=texto, background="#ffffe0", 
                            relief=tk.SOLID, borderwidth=1, padding=5)
            label.pack()
            
            def ocultar():
                tooltip.destroy()
            
            widget.tooltip = tooltip
            widget.bind("<Leave>", lambda e: ocultar())
            tooltip.after(3000, ocultar)
        
        widget.bind("<Enter>", mostrar_tooltip)
    
    # ===== CALLBACKS =====
    
    def _on_inicializar_click(self):
        """Callback al hacer clic en inicializar"""
        if self.on_inicializar:
            metodo = self.metodo_var.get()
            politica = self.politica_var.get()
            self.on_inicializar(metodo, politica)
    
    def _on_avanzar_click(self):
        """Callback al hacer clic en avanzar"""
        if self.on_avanzar:
            self.on_avanzar()
    
    def _on_simular_click(self):
        """Callback al hacer clic en simular"""
        if self.on_simular:
            self.on_simular()
    
    def _on_reiniciar_click(self):
        """Callback al hacer clic en reiniciar"""
        if self.on_reiniciar:
            self.on_reiniciar()
    
    # ===== MÉTODOS PÚBLICOS =====
    
    def obtener_configuracion(self) -> dict:
        """
        Obtiene la configuración actual
        
        Returns:
            Diccionario con método y política seleccionados
        """
        return {
            'metodo': self.metodo_var.get(),
            'politica': self.politica_var.get()
        }
    
    def establecer_configuracion(self, metodo: str, politica: str):
        """
        Establece la configuración
        
        Args:
            metodo: Método de inventario
            politica: Política de reposición
        """
        self.metodo_var.set(metodo)
        self.politica_var.set(politica)
    
    def habilitar_controles(self, habilitado: bool):
        """
        Habilita o deshabilita los controles
        
        Args:
            habilitado: True para habilitar, False para deshabilitar
        """
        estado = "normal" if habilitado else "disabled"
        
        for widget in self.frame.winfo_children():
            if isinstance(widget, ttk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, (ttk.Button, ttk.Combobox)):
                        child.config(state=estado)