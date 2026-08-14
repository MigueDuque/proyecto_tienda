# Mockup GUI — Granero Home Dashboard

## 🧭 Descripción general
Este mockup representa la interfaz principal del sistema **Granero**, diseñada para ofrecer una experiencia moderna, clara y corporativa.  
El objetivo es transmitir **eficiencia, tecnología y control visual** sobre las operaciones del negocio (ventas, inventario y contabilidad).

La composición se basa en un **layout de tres zonas**:
1. **Sidebar vertical** con navegación principal.
2. **Zona superior de KPIs** con métricas clave.
3. **Panel inferior dividido** entre “Stock Bajo” y “Ventas Recientes”.

---

## 🎨 Estilo visual
- **Tema:** Futurista corporativo, con estética de “centro de comando financiero”.
- **Fondo:** Azul espacial profundo (`#050816`) con gradientes suaves hacia azul marino (`#0B1023`).
- **Superficies:** Tarjetas flotantes con sombras difusas y bordes redondeados.
- **Tipografía:** Inter o Space Grotesk — geométrica, ligera y legible.
- **Iconografía:** Minimalista, con íconos lineales en tonos verdes, azules y grises.

---

## 🌈 Paleta de colores
| Elemento | Color | Hex | Uso |
|-----------|--------|-----|-----|
| Fondo principal | Deep Space Navy | `#050816` | Base del dashboard |
| Superficies / Cards | Midnight Blue | `#0B1023` | Paneles y tarjetas |
| Acento principal | Electric Blue | `#2F80FF` | Métricas y botones activos |
| Éxito / positivo | Mint AI Green | `#56F2C1` | Ventas, saldo positivo |
| Advertencia | Warning Orange | `#FFB020` | Stock bajo o alertas |
| Error / crítico | Critical Red | `#FF4D6D` | Stock agotado |
| Texto principal | Soft White | `#F5F7FA` | Labels y títulos |
| Texto secundario | Muted Gray | `#94A3B8` | Subtítulos y valores menores |

---

## 🧩 Componentes principales

### 1. Sidebar
- Fondo sólido azul oscuro.
- Íconos blancos con hover en Electric Blue.
- Sección activa con **glow verde** y fondo suavemente iluminado.
- Pie con email del usuario y botón “Cerrar sesión”.

### 2. Tarjetas KPI
- Tres tarjetas flotantes con ícono + valor + etiqueta:
  - 💵 **Ventas de hoy:** texto verde brillante.
  - 📅 **Ventas del mes:** texto azul eléctrico.
  - 👛 **Saldo en caja:** texto turquesa.
- Animación de entrada tipo *fade-in* y hover con leve escala.

### 3. Stock Bajo
- Tabla con columnas: Producto | Stock | Mínimo.
- Cada fila incluye:
  - Badge de alerta (rojo, naranja o amarillo).
  - Barra de progreso horizontal mostrando nivel de stock.
  - Fondo de fila con gradiente sutil según severidad.

### 4. Ventas Recientes
- Tabla con columnas: Fecha | Total | Pago.
- Íconos de método de pago (💳 crédito, 💵 contado).
- Animación *slide-up* para nuevas entradas.
- Enlace “Ver ventas” arriba a la derecha.

---

## ✨ Animaciones y microinteracciones
- **Hover:** escala leve + sombra difusa.
- **Carga inicial:** fade-in secuencial de tarjetas y tablas.
- **Transiciones:** suaves entre secciones