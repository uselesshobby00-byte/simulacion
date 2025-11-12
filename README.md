# 📦 Simulador de Gestión de Inventario

Sistema de simulación de eventos discretos para análisis y optimización de políticas de inventario en bodegas de suministros técnicos.

## 🎯 Objetivo del Proyecto

Desarrollar una herramienta interactiva que permita:
- Simular el comportamiento de un sistema de inventario
- Comparar diferentes políticas de reposición
- Analizar costos de almacenamiento y desabastecimiento
- Optimizar niveles de inventario y puntos de pedido
- Visualizar el desempeño financiero y operativo

## 🏗️ Arquitectura del Sistema

```
simulador_inventario/
│
├── models/                 # Modelos de datos
│   ├── enums.py           # Enumeraciones
│   ├── producto.py        # Clase Producto
│   ├── proveedor.py       # Clase Proveedor
│   ├── cliente.py         # Clase Cliente
│   └── finanzas.py        # Sistema financiero
│
├── core/                   # Lógica de negocio
│   ├── gestor_pedidos.py  # Gestor de decisiones
│   └── simulador.py       # Motor de simulación
│
├── gui/                    # Interfaz gráfica
│   ├── interfaz_principal.py
│   ├── panel_configuracion.py
│   ├── panel_productos.py
│   └── panel_graficas.py
│
├── config/                 # Configuración
│   └── configuracion.py
│
├── utils/                  # Utilidades
│   ├── exportador.py      # Exportación de datos
│   └── validaciones.py    # Validaciones
│
├── data/                   # Datos y resultados
│   └── resultados/
│
├── main.py                 # Punto de entrada
├── requirements.txt        # Dependencias
└── README.md              # Documentación
```

## 🚀 Instalación

### Requisitos Previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Pasos de Instalación

1. **Clonar o descargar el proyecto**

```bash
cd simulador_inventario
```

2. **Crear entorno virtual (recomendado)**

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Instalar dependencias**

```bash
pip install -r requirements.txt
```

4. **Ejecutar la aplicación**

```bash
python main.py
```

## 📚 Conceptos Principales

### Entidades del Sistema

#### 1. **Producto**
Representa un artículo almacenado con:
- Nivel de inventario actual
- Punto de pedido (umbral de reposición)
- Costos y precios
- Lotes con fechas de ingreso

#### 2. **Proveedor**
Suministra productos con:
- Tiempo de entrega
- Fiabilidad
- Descuentos por volumen
- Condiciones de pedido

#### 3. **Cliente**
Genera demanda con:
- Tipo (minorista, mayorista, interno, externo)
- Frecuencia de compra
- Cantidad promedio
- Prioridad de atención

#### 4. **Gestor de Pedidos**
Toma decisiones sobre:
- Cuándo pedir (punto de pedido)
- Cuánto pedir (cantidad de reposición)
- A qué proveedor (selección óptima)

### Métodos de Inventario

#### **PEPS (Primero en Entrar, Primero en Salir)**
- Los productos más antiguos se venden primero
- Útil para productos perecederos o con vencimiento
- Refleja mejor el flujo físico del inventario

#### **UEPS (Último en Entrar, Primero en Salir)**
- Los productos más recientes se venden primero
- Útil en contextos de inflación
- Puede representar costos actuales

#### **Promedio Ponderado**
- Se calcula un costo promedio de todas las unidades
- Más simple administrativamente
- Suaviza fluctuaciones de precios

### Políticas de Reposición

#### **Conservadora**
- Minimiza costos de almacenamiento
- Pide solo lo necesario para cubrir demanda
- Mayor riesgo de desabastecimiento
- **Ideal para**: Productos de bajo costo, demanda estable

#### **Agresiva**
- Minimiza riesgo de desabastecimiento
- Mantiene niveles altos de inventario
- Mayores costos de almacenamiento
- **Ideal para**: Productos críticos, demanda variable

#### **Adaptativa**
- Ajusta dinámicamente según desempeño
- Cambia entre conservadora y agresiva
- Responde a cambios en la demanda
- **Ideal para**: Sistemas con alta variabilidad

## 💻 Uso de la Aplicación

### 1. Inicializar Simulación

1. Seleccione el **método de inventario** (PEPS, UEPS, Promedio)
2. Elija la **política de reposición** (Conservadora, Agresiva, Adaptativa)
3. Haga clic en **"Inicializar Simulación"**

### 2. Ejecutar Simulación

- **Avanzar 1 Día**: Simula un día individual
- **Simular 30 Días**: Ejecuta una simulación completa
- Observe las gráficas actualizarse en tiempo real

### 3. Analizar Resultados

#### Panel de Estado General
- Día actual de simulación
- Saldo y utilidad neta
- Número de desabastecimientos
- Política activa

#### Pestaña de Inventario
- Niveles de inventario por producto
- Líneas de punto de pedido
- Evolución temporal

#### Pestaña Financiera
- Saldo actual
- Ingresos acumulados
- Egresos acumulados
- Utilidad neta

#### Registro de Eventos
- Ventas realizadas
- Pedidos generados
- Recepciones de mercancía
- Desabastecimientos

### 4. Configurar Productos

1. Seleccione un producto de la lista
2. Ajuste el **punto de pedido**
3. Modifique la **demanda estimada**
4. Haga clic en **"Aplicar"**

### 5. Exportar Datos

Los datos se pueden exportar automáticamente a CSV incluyendo:
- Resumen de simulación
- Eventos por tipo
- Transacciones financieras
- Estadísticas de clientes

## 📊 Métricas de Evaluación

### Métricas Financieras

- **Utilidad Neta**: Ingresos totales - Egresos totales
- **Rentabilidad**: (Utilidad / Saldo Inicial) × 100
- **Margen Bruto**: (Ingresos - Costos de Compra) / Ingresos
- **Flujo de Caja**: Cambio en el saldo

### Métricas Operativas

- **Tasa de Desabastecimiento**: Pedidos no satisfechos / Total de pedidos
- **Rotación de Inventario**: Ventas / Inventario Promedio
- **Nivel de Servicio**: Pedidos satisfechos / Total de pedidos
- **Cobertura de Inventario**: Inventario / Demanda Promedio Diaria

### Métricas de Costos

- **Costo de Almacenamiento**: Unidades × Días × Costo Unitario
- **Costo de Pedido**: Suma de todos los pedidos
- **Costo de Desabastecimiento**: Penalizaciones acumuladas
- **Costo Total**: Suma de todos los costos

## 🔧 Configuración Avanzada

### Modificar Parámetros Globales

Edite `config/configuracion.py`:

```python
# Costos del sistema
COSTO_ALMACENAMIENTO_DEFAULT = 0.1
COSTO_DESABASTECIMIENTO_BASE = 50.0

# Evaluación
DIAS_EVALUACION_PERIODICA = 7
```

### Agregar Nuevos Productos

```python
producto = Producto(
    id="PROD006",
    nombre="Nuevo Producto",
    costo_unitario=1.0,
    precio_venta=2.5,
    punto_pedido=30,
    demanda_estimada=8,
    tiempo_reposicion=4
)

simulador.agregar_producto(producto)
```

### Personalizar Proveedores

```python
proveedor = Proveedor(
    id="PROV004",
    nombre="Proveedor Especial",
    productos_ofrecidos=["PROD001", "PROD002"],
    tiempo_entrega=2,
    fiabilidad=0.98,
    descuento_volumen={
        "PROD001": (100, 0.15)  # 15% si pide 100+
    }
)
```

## 🧪 Escenarios de Prueba

### Escenario 1: Alta Demanda
- Aumentar frecuencia de compra de clientes
- Reducir tiempo de entrega de proveedores
- Probar política AGRESIVA

### Escenario 2: Recursos Limitados
- Reducir saldo inicial
- Aumentar costos de almacenamiento
- Probar política CONSERVADORA

### Escenario 3: Demanda Variable
- Aumentar variabilidad de clientes
- Simular retrasos en proveedores
- Probar política ADAPTATIVA

### Escenario 4: Comparación de Métodos
- Ejecutar 90 días con PEPS
- Reiniciar y ejecutar 90 días con UEPS
- Comparar utilidad neta final

## 📈 Interpretación de Resultados

### Señales de Buen Desempeño

✅ Utilidad neta positiva y creciente
✅ Desabastecimientos < 5% de pedidos
✅ Inventario estable cerca del punto de pedido
✅ Saldo positivo y sostenible

### Señales de Problemas

❌ Utilidad neta negativa
❌ Desabastecimientos frecuentes (>10%)
❌ Inventario excesivo o en cero
❌ Saldo decreciente rápidamente

### Ajustes Recomendados

| Problema | Solución |
|----------|----------|
| Muchos desabastecimientos | Política más agresiva o aumentar punto de pedido |
| Inventario excesivo | Política más conservadora o reducir punto de pedido |
| Costos altos | Reducir cantidad de pedido o negociar descuentos |
| Utilidad baja | Revisar precios de venta o cambiar proveedores |

## 🛠️ Desarrollo y Extensiones

### Agregar Nueva Funcionalidad

1. **Nuevas métricas**: Agregar en `core/simulador.py`
2. **Nuevos eventos**: Definir en `models/enums.py`
3. **Nuevas visualizaciones**: Crear en `gui/panel_graficas.py`

### Próximas Características

- [ ] Múltiples bodegas
- [ ] Transferencias entre bodegas
- [ ] Productos con vencimiento
- [ ] Promociones y descuentos a clientes
- [ ] Optimización automática de parámetros
- [ ] Reportes PDF
- [ ] Integración con bases de datos

## 🐛 Solución de Problemas

### La aplicación no inicia

```bash
# Verificar instalación de dependencias
pip install -r requirements.txt

# Verificar versión de Python
python --version  # Debe ser 3.8+
```

### Error en gráficas

```bash
# Reinstalar matplotlib
pip install --upgrade matplotlib
```

### Error de permisos al exportar

```bash
# Crear directorio manualmente
mkdir -p data/resultados
```

## 📝 Licencia

Este proyecto es de código abierto y está disponible para fines educativos.

## 👥 Contribuciones

Las contribuciones son bienvenidas. Por favor:
1. Fork el proyecto
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

## 📧 Contacto

Para preguntas o sugerencias sobre el proyecto, por favor abre un issue en el repositorio.

---

**Desarrollado como proyecto de simulación de sistemas de inventario**