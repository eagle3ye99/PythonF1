# 🏎️ Análisis de Datos de Fórmula 1 con OpenF1 API

Este repositorio permite realizar análisis de datos de Fórmula 1 utilizando la [API OpenF1](https://api.openf1.org/v1/). El análisis se centra principalmente en la sesión de **Carrera (Race)**.

---

## 📊 Descripción de los Datos

**Fuente:** [OpenF1 API](https://api.openf1.org/v1/)  
**Cobertura temporal:** 2023–2025  
**Actualización:** Tiempo real durante sesiones activas  
**Formato original:** JSON → Convertido a CSV para análisis  

### 🧱 Estructura de los Datos

#### 👤 Pilotos (`drivers`)
- `driver_number`: Número identificador (1–99)
- `full_name`: Nombre completo
- `team_name`: Nombre del equipo
- `team_colour`: Color hexadecimal
- `session_key`: ID de sesión

#### 🕒 Vueltas (`laps`)
- `lap_number`: Número de vuelta
- `lap_duration`: Duración (segundos)
- `st_speed`: Velocidad en recta principal (km/h)
- `date_start`: Timestamp de inicio (ISO 8601)
- `driver_number`: Referencia al piloto

#### 🏁 Posiciones (`position`)
- `position`: Posición en carrera
- `date`: Timestamp
- `driver_number`: Referencia al piloto

---

## ⚠️ Calidad y Limitaciones

- **Completitud:** ~95% de los datos por sesión
- **Latencia:** 1–3 segundos en sesiones en vivo
- **Precisión temporal:** Milisegundos
- **Limitación:** Solo datos desde 2023. Actualmente limitado a sesiones de tipo **Race**.

---

## 🛠️ Requisitos Previos

- Python **3.8+**
- Librerías: `pandas`, `matplotlib`, `numpy`
- Archivo `Circuits.csv` en el mismo directorio (se puede generar con `Circuits.py`)

---

## ▶️ Ejecución del Análisis

1. Correr el script principal.
2. En consola, seleccionar:
   - Número de circuito (1–23)
   - Año (2023–2025) *(recomendado: 2023–2024)*
   - Tipo de sesión (`Practice` / `Qualifying` / `Race` / `Sprint`)
3. Procesamiento automático:
   - Extracción de datos
   - Limpieza y validación
   - Generación de resultados

### 📦 Resultados generados
- 6 archivos **CSV**
- 2 gráficos **PNG**
- Estadísticas en consola

---

## 📈 Análisis Realizados

### 1. Vueltas Más Rápidas

- 🔍 **Datos:** tiempo más rápido por piloto y diferencias relativas
- 🎯 **Importancia:** indicador de rendimiento puro
- 🧮 **Metodología:**
  - Filtrado de vueltas inválidas
  - Selección de tiempo mínimo por piloto
  - Cálculo de deltas

### 2. Evolución de Posiciones

- 🔍 **Datos:** comparación entre posición inicial y final
- 🎯 **Importancia:** indica efectividad de estrategias y maniobras
- 🧮 **Metodología:**
  - Correlación entre datos de posición y vuelta
  - Cálculo de cambios netos
  - Visualización por color de equipo

---

## 📊 Interpretación de Resultados

- **Gráfico de vueltas rápidas:** valores cercanos a 0.0s = alto rendimiento.
- **Gráfico de posiciones:** líneas ascendentes = ganancia de posiciones.
- **CSV:** compatibles con Excel / R / Python.

---

## 📌 Conclusiones

### 🧑‍✈️ Rendimiento de Pilotos
- Pilotos con la vuelta más rápida suelen obtener mejores resultados.
- Vueltas lentas → posiciones bajas.

### 🏎️ Equipos y Constructores
- Equipos de punta → mejor rendimiento y posiciones.
- Mejora visible a lo largo del fin de semana (de práctica a carrera).

---

## 💡 Posibles Mejoras

- Ampliar el menú interactivo y permitir tipos de análisis según la sesión.
- Comparar vuelta rápida de clasificación vs. carrera por piloto.
- Generar más tipos de gráficos automáticamente.

---

## 📚 Recursos Adicionales

- **[OpenF1 API](https://api.openf1.org/v1/):** documentación de endpoints
- **Pandas:** manipulación de datos
- **Matplotlib:** visualización
- **FIA:** resultados oficiales
- **Pirelli:** datos de neumáticos
- **APIs meteorológicas:** datos climáticos históricos
