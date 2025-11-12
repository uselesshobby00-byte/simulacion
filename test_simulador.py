"""
test_simulador.py
Script de prueba simple para verificar el funcionamiento del simulador
"""

from datetime import datetime
from models.enums import MetodoInventario, PoliticaReposicion, TipoCliente
from models.producto import Producto
from models.proveedor import Proveedor
from models.cliente import Cliente
from core.simulador import SimuladorInventario
from utils.exportador import exportar_rapido


def prueba_basica():
    """Prueba básica del simulador"""
    print("=" * 60)
    print("PRUEBA BÁSICA DEL SIMULADOR DE INVENTARIO")
    print("=" * 60)
    
    # Crear simulador
    print("\n1. Creando simulador...")
    simulador = SimuladorInventario(
        metodo_inventario=MetodoInventario.PEPS,
        politica_reposicion=PoliticaReposicion.CONSERVADORA,
        saldo_inicial=50000.0
    )
    print("   ✓ Simulador creado")
    
    # Agregar producto
    print("\n2. Agregando producto...")
    producto = Producto(
        id="PROD001",
        nombre="Tornillo M6",
        costo_unitario=0.5,
        precio_venta=1.2,
        punto_pedido=30,
        demanda_estimada=10,
        tiempo_reposicion=3
    )
    producto.agregar_lote(50, 0.5, simulador.fecha_actual)
    simulador.agregar_producto(producto)
    print(f"   ✓ Producto agregado: {producto}")
    
    # Agregar proveedor
    print("\n3. Agregando proveedor...")
    proveedor = Proveedor(
        id="PROV001",
        nombre="Suministros ABC",
        productos_ofrecidos=["PROD001"],
        tiempo_entrega=3,
        costo_base=0.5,
        fiabilidad=0.95
    )
    simulador.agregar_proveedor(proveedor)
    print(f"   ✓ Proveedor agregado: {proveedor}")
    
    # Agregar cliente
    print("\n4. Agregando cliente...")
    cliente = Cliente(
        id="CLI001",
        nombre="Ferretería XYZ",
        tipo=TipoCliente.MINORISTA,
        productos_solicitados=["PROD001"],
        frecuencia_compra=2,
        cantidad_promedio=15,
        prioridad=3
    )
    simulador.agregar_cliente(cliente)
    print(f"   ✓ Cliente agregado: {cliente}")
    
    # Simular días
    print("\n5. Ejecutando simulación de 15 días...")
    for dia in range(1, 16):
        simulador.avanzar_dia()
        if dia % 5 == 0:
            print(f"   Día {dia} completado")
    
    # Mostrar resultados
    print("\n6. Resultados de la simulación:")
    print("-" * 60)
    
    estado = simulador.obtener_estado()
    
    print(f"\n   Información General:")
    print(f"   - Días simulados: {estado['dia']}")
    print(f"   - Método de inventario: {simulador.metodo_inventario.value}")
    
    print(f"\n   Estado Financiero:")
    finanzas = estado['finanzas']
    print(f"   - Saldo inicial: ${finanzas['saldo_inicial']:,.2f}")
    print(f"   - Saldo actual: ${finanzas['saldo_actual']:,.2f}")
    print(f"   - Ingresos totales: ${finanzas['ingresos_totales']:,.2f}")
    print(f"   - Egresos totales: ${finanzas['egresos_totales']:,.2f}")
    print(f"   - Utilidad neta: ${finanzas['utilidad_neta']:,.2f}")
    print(f"   - Rentabilidad: {finanzas['rentabilidad']:.2f}%")
    
    print(f"\n   Gestor de Pedidos:")
    gestor = estado['gestor']
    print(f"   - Política actual: {gestor['politica_actual']}")
    print(f"   - Sensibilidad: {gestor['sensibilidad']}")
    print(f"   - Pedidos generados: {gestor['pedidos_generados']}")
    print(f"   - Costo total de pedidos: ${gestor['costo_total_pedidos']:,.2f}")
    
    print(f"\n   Métricas Operativas:")
    metricas = estado['metricas']
    print(f"   - Desabastecimientos: {metricas['desabastecimientos']}")
    print(f"   - Ventas totales: {metricas['ventas_totales']}")
    print(f"   - Unidades vendidas: {metricas['unidades_vendidas']}")
    print(f"   - Pedidos pendientes: {metricas['pedidos_pendientes']}")
    
    print(f"\n   Estado de Productos:")
    for prod_id, datos in estado['productos'].items():
        print(f"   - {datos['nombre']} ({prod_id}):")
        print(f"     * Inventario: {datos['inventario']} unidades")
        print(f"     * Punto de pedido: {datos['punto_pedido']}")
        print(f"     * Lotes: {datos['num_lotes']}")
    
    # Mostrar eventos recientes
    print(f"\n   Últimos 5 Eventos:")
    eventos = simulador.obtener_eventos_recientes(5)
    for evento in eventos:
        print(f"   - Día {evento['dia']}: {evento['tipo']}")
        datos = evento['datos']
        if evento['tipo'] == 'VENTA':
            print(f"     * {datos['cliente']} compró {datos['cantidad']} unidades (+${datos['ingreso']:.2f})")
        elif evento['tipo'] == 'PEDIDO':
            print(f"     * Pedido a {datos['proveedor']}: {datos['cantidad']} unidades (-${datos['costo']:.2f})")
        elif evento['tipo'] == 'RECEPCION':
            print(f"     * Recibido: {datos['cantidad']} unidades")
        elif evento['tipo'] == 'DESABASTECIMIENTO':
            print(f"     * {datos['cliente']} no pudo comprar {datos['cantidad_solicitada']} unidades")
    
    print("\n" + "=" * 60)
    print("PRUEBA COMPLETADA EXITOSAMENTE")
    print("=" * 60)
    
    return simulador


def prueba_comparacion_politicas():
    """Compara diferentes políticas de reposición"""
    print("\n\n" + "=" * 60)
    print("COMPARACIÓN DE POLÍTICAS DE REPOSICIÓN")
    print("=" * 60)
    
    resultados = {}
    
    for politica in [PoliticaReposicion.CONSERVADORA, 
                     PoliticaReposicion.AGRESIVA, 
                     PoliticaReposicion.ADAPTATIVA]:
        
        print(f"\n--- Probando política: {politica.value} ---")
        
        # Crear simulador
        simulador = SimuladorInventario(
            metodo_inventario=MetodoInventario.PEPS,
            politica_reposicion=politica,
            saldo_inicial=50000.0
        )
        
        # Configurar (mismo setup que prueba básica)
        producto = Producto(
            id="PROD001", nombre="Tornillo M6",
            costo_unitario=0.5, precio_venta=1.2,
            punto_pedido=30, demanda_estimada=10, tiempo_reposicion=3
        )
        producto.agregar_lote(50, 0.5, simulador.fecha_actual)
        simulador.agregar_producto(producto)
        
        proveedor = Proveedor(
            id="PROV001", nombre="Suministros ABC",
            productos_ofrecidos=["PROD001"],
            tiempo_entrega=3, costo_base=0.5, fiabilidad=0.95
        )
        simulador.agregar_proveedor(proveedor)
        
        cliente = Cliente(
            id="CLI001", nombre="Ferretería XYZ",
            tipo=TipoCliente.MINORISTA,
            productos_solicitados=["PROD001"],
            frecuencia_compra=2, cantidad_promedio=15, prioridad=3
        )
        simulador.agregar_cliente(cliente)
        
        # Simular 30 días
        simulador.simular_dias(30)
        
        # Guardar resultados
        estado = simulador.obtener_estado()
        resultados[politica.value] = {
            'utilidad': estado['finanzas']['utilidad_neta'],
            'desabastecimientos': estado['metricas']['desabastecimientos'],
            'ventas': estado['metricas']['ventas_totales'],
            'inventario_final': estado['productos']['PROD001']['inventario']
        }
        
        print(f"Utilidad: ${estado['finanzas']['utilidad_neta']:,.2f}")
        print(f"Desabastecimientos: {estado['metricas']['desabastecimientos']}")
        print(f"Ventas: {estado['metricas']['ventas_totales']}")
    
    # Mostrar comparación
    print("\n" + "=" * 60)
    print("RESUMEN COMPARATIVO")
    print("=" * 60)
    print(f"\n{'Política':<20} {'Utilidad':<15} {'Desabast.':<12} {'Ventas':<10}")
    print("-" * 60)
    
    for politica, datos in resultados.items():
        print(f"{politica:<20} ${datos['utilidad']:>10,.2f}   {datos['desabastecimientos']:>8}   {datos['ventas']:>8}")
    
    # Encontrar mejor política
    mejor_politica = max(resultados.items(), key=lambda x: x[1]['utilidad'])
    print(f"\n✓ Mejor política: {mejor_politica[0]} (Utilidad: ${mejor_politica[1]['utilidad']:,.2f})")


if __name__ == "__main__":
    # Ejecutar pruebas
    try:
        # Prueba básica
        simulador = prueba_basica()
        
        # Prueba de comparación
        prueba_comparacion_politicas()
        
        print("\n\n¡Todas las pruebas completadas exitosamente! ✓")
        
    except Exception as e:
        print(f"\n❌ Error durante las pruebas: {str(e)}")
        import traceback
        traceback.print_exc()