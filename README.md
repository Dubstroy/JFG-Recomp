# 🌌 Jet Force Gemini - Static Recompilation Port

Este proyecto busca crear un **port nativo para PC** del clásico de Nintendo 64 **Jet Force Gemini**, utilizando tecnología de recompilación estática automatizada. Creado por hobby en mi tiempo libre y como aprendizaje para crear un entorno automatizado o semiautomatizado por IA.

El objetivo principal es lograr que el juego se ejecute de forma nativa en sistemas modernos (Windows/Linux) sin necesidad de emulación tradicional, permitiendo mejoras de rendimiento, soporte para resoluciones modernas y tasas de cuadros por segundo desbloqueadas.

---
<!-- PROGRESS:START -->

## 📊 Progreso del Proyecto

**Estado:** 🟡 `IN DEVELOPMENT`

| Área | Progreso |
|---|---:|
| Decompilación | **15.60%** |
| Análisis de funciones | **10.14%** |
| Funciones exitosas | **10.13%** |
| Jump Tables | **98.18%** |
| Relocations | **0.00%** |

### Progreso visual

```text
Decompilación        [███░░░░░░░░░░░░░░░░░] 15.60%
Funciones analizadas [██░░░░░░░░░░░░░░░░░░] 10.14%
Funciones exitosas   [██░░░░░░░░░░░░░░░░░░] 10.13%
Jump Tables          [████████████████████] 98.18%
Relocations          [░░░░░░░░░░░░░░░░░░░░] 0.00%
```

### Funciones

- **Total:** 11,253
- **Analizadas:** 1,141
- **Exitosas:** 1,140
- **Errores:** 1

### Jump Tables

- **Detectadas:** 55
- **Resueltas:** 54

### Relocations

- **Total:** 0
- **Resueltas:** 0

### Componentes

| Componente | Progreso |
|---|---:|
| ELF Analysis | **100.00%** |
| MIPS Analysis | **0.00%** |
| C Generation | **0.00%** |
| Native Build | **0.00%** |
| Runtime | **0.00%** |

**Última actualización:** `2026-09-11`

<!-- PROGRESS:END -->

## 🛠️ Tecnologías Utilizadas

Este repositorio se apoya fuertemente en las herramientas desarrolladas por la comunidad de preservación:

* **[N64Recomp](https://github.com/N64Recomp/N64Recomp):** Herramienta central para la traducción estática de binarios MIPS a código nativo en C++.
* **RT64:** Renderizador moderno utilizado de fondo para traducir los gráficos originales a APIs modernas como DirectX 12 y Vulkan.
* **MIPS / MIPS III:** Arquitectura utilizada por el hardware original de Nintendo 64.
* **C/C++:** Lenguajes utilizados durante la generación y compilación del código recompilado.
* **Python:** Utilizado para automatización, procesamiento de datos y seguimiento del progreso.

---

## 📂 Estructura del Proyecto

* `/N64Recomp`: Submódulo con las herramientas de recompilación.
* `/src`: Código fuente en C++ generado automáticamente y parches manuales.
* `/patches`: Configuraciones específicas para solucionar errores lógicos del juego.
* `/rom`: Carpeta local para colocar la ROM legal (excluida de Git por razones legales).
* `/progress.json`: Estado y métricas del progreso del proyecto.
* `/update_progress.py`: Script utilizado para actualizar las métricas del proyecto.
* `/N64Recomp/progress_stats.json`: Estadísticas generadas directamente durante el análisis de N64Recomp.

---

## 🧪 Estado Técnico

El proyecto se encuentra actualmente en la fase de **análisis y recompilación del binario original**.

El ELF original de *Jet Force Gemini* ya ha sido analizado y el proceso de recompilación está avanzando mediante el procesamiento individual de sus funciones MIPS.

El proyecto también incorpora soporte específico para las estructuras de relocación utilizadas por los overlays de *Jet Force Gemini*, permitiendo que N64Recomp pueda interpretar información que no está representada mediante las relocaciones ELF estándar.

---

## ⚖️ Nota Legal

Este repositorio **no incluye** ni distribuirá archivos protegidos por derechos de autor, activos del juego (gráficos, música, niveles) ni copias de la ROM original. Para compilar y ejecutar este port, el usuario final debe proporcionar su propia copia legal de la ROM de *Jet Force Gemini*.

---

## 📌 Aviso sobre el desarrollo

Este es un proyecto **independiente y realizado por hobby**. No está afiliado, respaldado ni autorizado por Nintendo, Rare o cualquier otra entidad propietaria de los derechos de *Jet Force Gemini*.

El objetivo del proyecto es exclusivamente educativo, experimental y de preservación.
