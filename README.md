# 🌌 Jet Force Gemini - Static Recompilation Port

Este proyecto busca crear un **port nativo para PC** del clásico de Nintendo 64 **Jet Force Gemini**, utilizando tecnología de recompilación estática automatizada. Creado por hobby en mi tiempo libre y como aprendizaje para crear un entorno automatizado o semiautomatizado por IA.

El objetivo principal es lograr que el juego se ejecute de forma nativa en sistemas modernos (Windows/Linux) sin necesidad de emulación tradicional, permitiendo mejoras de rendimiento, soporte para resoluciones modernas y tasas de cuadros por segundo desbloqueadas.

---
<!-- PROGRESS:START -->

## 📊 Progreso del Proyecto

**Estado:** 🟡 `IN DEVELOPMENT`

| Área | Progreso |
|---|---:|
| Análisis de funciones | **10.14%** |
| Funciones exitosas | **10.13%** |
| Jump Tables | **98.18%** |
| Relocations | **0.00%** |

### Progreso visual

```text
Funciones analizadas [■■□□□□□□□□□□□□□□□□□□] 10.14%
Funciones exitosas   [■■□□□□□□□□□□□□□□□□□□] 10.13%
Jump Tables          [■■■■■■■■■■■■■■■■■■■■] 98.18%
Relocations          [□□□□□□□□□□□□□□□□□□□□] 0.00%
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

**Última actualización:** `2026-10-16`

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

### Ejecutar la recompilación

`config.toml` usa el formato de N64Recomp. Ajusta `input.elf_path` y `input.rom_file_path` a tus copias locales. Los overlays presentes en el ELF deben estar listados en `relocatable_sections.txt`.

```powershell
git -C N64Recomp apply ..\tools\n64recomp-jfg.patch
cmake -S N64Recomp -B build/N64Recomp
cmake --build build/N64Recomp --config Release --target N64RecompCLI
.\build\N64Recomp\Release\N64Recomp.exe config.toml
```

La tabla de saltos de `func_80074B50` ya se analiza preservando su entrada nula y su índice. `gen_anim_data` tiene un tamaño de función corregido a `0xFD0` porque el tamaño ELF (`0x468`) truncaba una rama válida a `0x8007475C`; la generación ahora incluye esa etiqueta dentro de la función. `_itoa` se renombra a `_itoa_recomp` para evitar una colisión con la función homónima del CRT de MSVC. Los blobs de microcódigo RSP incluidos en `.text` se excluyen de la recompilación de CPU. `RSPRecomp` genera los archivos de audio, arranque y F3DDKR; el perfil de arranque compila, pero audio y F3DDKR todavía no: sus perfiles actuales exceden el espacio de IMEM disponible y dejan ramas a etiquetas fuera de la imagen generada; falta identificar sus rangos de código/overlays reales. El código generado no es todavía un ejecutable jugable: faltan integrar en el build del juego los cambios del runtime, contar con un backend gráfico que procese los rangos DPC y completar el build nativo.

Los perfiles de `RSPRecomp` están en `rsp/` y esperan la ROM en `rom/JetForceGemini.z64`. El perfil de audio genera código con:

```powershell
.\build\N64Recomp\Release\RSPRecomp.exe rsp\audio.toml
```

El generador maneja las lecturas/escrituras COP2 de banderas vectoriales y emite llamadas a `ultramodern::dpc::read_register` / `write_register` para los registros DPC; antes de escribir `DPC_END`, también registra el DMEM para los rangos XBUS. La implementación de esta API y del procesamiento DPC optativo está terminada en una rama separada de `N64ModernRuntime`, con pruebas enfocadas aprobadas, pero todavía no está incorporada en este build. Los backends gráficos no soportan DPC todavía: ninguno activa esa capacidad, por lo que los microcódigos de arranque y F3DDKR no pueden procesar comandos gráficos en este estado. La configuración completa del proyecto también requiere los submódulos `thirdparty/miniz` y `N64Recomp`, ausentes en algunos checkouts. No se deben reemplazar accesos DPC por valores ficticios.

---

## ⚖️ Nota Legal

Este repositorio **no incluye** ni distribuirá archivos protegidos por derechos de autor, activos del juego (gráficos, música, niveles) ni copias de la ROM original. Para compilar y ejecutar este port, el usuario final debe proporcionar su propia copia legal de la ROM de *Jet Force Gemini*.

---

## 📌 Aviso sobre el desarrollo

Este es un proyecto **independiente y realizado por hobby**. No está afiliado, respaldado ni autorizado por Nintendo, Rare o cualquier otra entidad propietaria de los derechos de *Jet Force Gemini*.

El objetivo del proyecto es exclusivamente educativo, experimental y de preservación.
