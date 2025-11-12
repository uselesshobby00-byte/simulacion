"""
main.py
Punto de entrada de la aplicación
"""

import sys
import tkinter as tk
from tkinter import messagebox

# Importar módulos del proyecto
from models.enums import MetodoInventario, PoliticaReposicion, TipoCliente
from models.producto import Producto
from models.proveedor import Proveedor
from models.cliente import Cliente
from core.simulador import SimuladorInventario
from gui.interfaz_principal import InterfazPrincipal


def inicializar_simulacion_ejemplo():
    """
    Crea una simulación con datos de ejemplo
    
    Returns:
        Simulador configurado con datos de prueba
    """
    # Crear simulador
    simulador = SimuladorInventario(
        metodo_inventario=MetodoInventario.PEPS,
        politica_reposicion=PoliticaReposicion.CONSERVADORA,
        saldo_inicial=100000.0
    )
    
    # ===== PRODUCTOS =====
    productos = [
        Producto(
            id="PROD001",
            nombre="Tornillo M6",
            costo_unitario=0.5,
            precio_venta=1.2,
            punto_pedido=50,
            demanda_estimada=10,
            tiempo_reposicion=3,
            capacidad_maxima=500
        ),
        Producto(
            id="PROD002",
            nombre="Tuerca M6",
            costo_unitario=0.3,
            precio_venta=0.9,
            punto_pedido=60,
            demanda_estimada=12,
            tiempo_reposicion=3,
            capacidad_maxima=600
        ),
        Producto(
            id="PROD003",
            nombre="Arandela",
            costo_unitario=0.1,
            precio_venta=0.4,
            punto_pedido=100,
            demanda_estimada=20,
            tiempo_reposicion=2,
            capacidad_maxima=1000
        ),
        Producto(
            id="PROD004",
            nombre="Perno 1/4",
            costo_unitario=0.8,
            precio_venta=2.0,
            punto_pedido=40,
            demanda_estimada=8,
            tiempo_reposicion=4,
            capacidad_maxima=400
        ),
        Producto(
            id="PROD005",
            nombre="Clavo 3 pulgadas",
            costo_unitario=0.05,
            precio_venta=0.15,
            punto_pedido=200,
            demanda_estimada=50,
            tiempo_reposicion=2,
            capacidad_maxima=2000
        )
    ]
    
    # Agregar productos con inventario inicial
    for producto in productos:
        producto.agregar_lote(
            cantidad=100,
            costo=producto.costo_unitario,
            fecha=simulador.fecha_actual
        )
        simulador.agregar_producto(producto)
    
    # ===== PROVEEDORES =====
    proveedores = [
        Proveedor(
            id="PROV001",
            nombre="Suministros ABC",
            productos_ofrecidos=["PROD001", "PROD002", "PROD003"],
            tiempo_entrega=3,
            costo_base=0.5,
            fiabilidad=0.95,
            minimo_pedido=20,
            descuento_volumen={
                "PROD001": (100, 0.10),  # 10% descuento si pide 100+
                "PROD002": (150, 0.15)   # 15% descuento si pide 150+
            }
        ),
        Proveedor(
            id="PROV002",
            nombre="Distribuidora XYZ",
            productos_ofrecidos=["PROD001", "PROD003", "PROD004"],
            tiempo_entrega=2,
            costo_base=0.55,
            fiabilidad=0.98,
            minimo_pedido=15,
            descuento_volumen={
                "PROD004": (80, 0.12)
            }
        ),
        Proveedor(
            id="PROV003",
            nombre="Ferretería Industrial",
            productos_ofrecidos=["PROD002", "PROD004", "PROD005"],
            tiempo_entrega=4,
            costo_base=0.48,
            fiabilidad=0.90,
            minimo_pedido=30,
            descuento_volumen={
                "PROD005": (500, 0.20)  # 20% descuento en volumen alto
            }
        )
    ]
    
    for proveedor in proveedores:
        simulador.agregar_proveedor(proveedor)
    
    # ===== CLIENTES =====
    clientes = [
        Cliente(
            id="CLI001",
            nombre="Ferretería El Tornillo",
            tipo=TipoCliente.MINORISTA,
            productos_solicitados=["PROD001", "PROD002", "PROD003"],
            frecuencia_compra=3,
            cantidad_promedio=15,
            prioridad=3,
            variabilidad=0.3
        ),
        Cliente(
            id="CLI002",
            nombre="Construcciones Pérez",
            tipo=TipoCliente.MAYORISTA,
            productos_solicitados=["PROD001", "PROD003", "PROD004", "PROD005"],
            frecuencia_compra=7,
            cantidad_promedio=50,
            prioridad=4,
            variabilidad=0.4
        ),
        Cliente(
            id="CLI003",
            nombre="Taller Mecánico López",
            tipo=TipoCliente.MINORISTA,
            productos_solicitados=["PROD002", "PROD004"],
            frecuencia_compra=2,
            cantidad_promedio=10,
            prioridad=2,
            variabilidad=0.2
        ),
        Cliente(
            id="CLI004",
            nombre="Almacén Central (Interno)",
            tipo=TipoCliente.INTERNO,
            productos_solicitados=["PROD001", "PROD002", "PROD005"],
            frecuencia_compra=5,
            cantidad_promedio=25,
            prioridad=5,
            variabilidad=0.15
        ),
        Cliente(
            id="CLI005",
            nombre="Ferreterías del Norte",
            tipo=TipoCliente.MAYORISTA,
            productos_solicitados=["PROD003", "PROD005"],
            frecuencia_compra=10,
            cantidad_promedio=100,
            prioridad=3,
            variabilidad=0.5
        )
    ]
    
    for cliente in clientes:
        simulador.agregar_cliente(cliente)
    
    return simulador


def main():
    """Función principal de la aplicación"""
    try:
        # Crear ventana principal
        root = tk.Tk()
        
        # Crear simulador de ejemplo
        simulador = inicializar_simulacion_ejemplo()
        
        # Crear interfaz gráfica
        app = InterfazPrincipal(root, simulador)
        
        # Configurar cierre de ventana
        def on_closing():
            if messagebox.askokcancel("Salir", "¿Desea salir de la aplicación?"):
                root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Iniciar aplicación
        root.mainloop()
        
    except Exception as e:
        messagebox.showerror("Error", f"Error al iniciar la aplicación: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()