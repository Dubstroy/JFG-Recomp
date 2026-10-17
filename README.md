# 🌌 Jet Force Gemini - Static Recompilation Port

Este proyecto busca crear un **port nativo para PC** del clásico de Nintendo 64 **Jet Force Gemini**, utilizando tecnología de recompilación estática automatizada. Creado por hobby en mi tiempo libre y como aprendizaje para crear un entorno automatizado o semiautomatizado por IA.

El objetivo principal es lograr que el juego se ejecute de forma nativa en sistemas modernos (Windows/Linux) sin necesidad de emulación tradicional, permitiendo mejoras de rendimiento, soporte para resoluciones modernas y tasas de cuadros por segundo desbloqueadas.

---
<!-- PROGRESS:START -->

## 📊 Estado del Proyecto

**Estado general:** 🟡 `IN DEVELOPMENT`

| Área | Estado | Detalle |
|---|---|---|
| Recompilación CPU | **VALIDADO** | Código generado para 11,253 funciones y compilado como biblioteca estática contra el runtime fijado. |
| Microcódigo RSP de arranque | **VALIDADO** | La salida generada compila. |
| Microcódigo RSP de audio | **VALIDADO** | La imagen base y el overlay se describen a partir de los descriptores DMEM del juego; la salida generada compila contra los headers del runtime. |
| Microcódigo RSP F3DDKR | **EN PROGRESO** | Los descriptores DMEM identifican varios rangos de código y overlays que el perfil aún no representa correctamente. |
| Integración de DPC y RT64 | **EN RAMA SEPARADA** | La API DPC del runtime y el consumidor RT64 se compilaron en ramas separadas; aún no están integrados al inicio del juego en este repositorio. |
| Build nativo jugable | **NO DISPONIBLE** | Todavía no hay un ejecutable integrado ni un arranque verificado del juego. |

**Última actualización:** `2026-10-17`

<!-- PROGRESS:END -->

## 🛠️ Tecnologías Utilizadas

Este repositorio se apoya fuertemente en las herramientas desarrolladas por la comunidad de preservación:

* **[N64Recomp](https://github.com/N64Recomp/N64Recomp):** Herramienta central para la traducción estática de binarios MIPS a código nativo en C++.
* **RT64:** Renderizador existente que se está evaluando como consumidor de DPC; todavía no forma parte de un ejecutable integrado de este proyecto.
* **MIPS / MIPS III:** Arquitectura utilizada por el hardware original de Nintendo 64.
* **C/C++:** Lenguajes utilizados durante la generación y compilación del código recompilado.
* **Python:** Utilizado para automatización, procesamiento de datos y seguimiento del progreso.

---

## 📂 Estructura del Proyecto

* `/N64Recomp`: Submódulo con N64Recomp y RSPRecomp; `tools/n64recomp-jfg.patch` contiene los cambios específicos del generador.
* `/rsp`: Perfiles de recompilación de los microcódigos de audio, arranque y F3DDKR.
* `/tools`: Scripts de análisis y el parche reproducible para N64Recomp.
* `/rom`: Ubicación local esperada para la ROM legal (excluida de Git).
* `/build` y `/src`: Salidas locales de compilación y código generado (excluidas de Git).
* `/progress.json`: Estado por hitos; `update_progress.py` actualiza la fecha y `update_readme.py` refleja esos datos en este README.

---

## 🧪 Estado Técnico

El proyecto ya superó la etapa de análisis inicial: N64Recomp generó código para 11,253 funciones y ese código CPU se compiló como biblioteca estática contra el runtime fijado. Las salidas generadas y los archivos del juego son artefactos locales y no se distribuyen en este repositorio.

El generador también incluye soporte específico para las estructuras de relocación de overlays de *Jet Force Gemini*, que no están representadas por relocaciones ELF estándar.

### Ejecutar la recompilación

`config.toml` usa el formato de N64Recomp. Ajusta `input.elf_path` y `input.rom_file_path` a tus copias locales. Los overlays presentes en el ELF deben estar listados en `relocatable_sections.txt`.

```powershell
git -C N64Recomp apply ..\tools\n64recomp-jfg.patch
cmake -S N64Recomp -B build/N64Recomp
cmake --build build/N64Recomp --config Release --target N64RecompCLI
.\build\N64Recomp\Release\N64Recomp.exe config.toml
```

La tabla de saltos de `func_80074B50` preserva su entrada nula y su índice. El tamaño de `gen_anim_data` está corregido a `0xFD0` para incluir una rama válida que el tamaño ELF (`0x468`) truncaba; `_itoa` se renombra para evitar una colisión con el CRT de MSVC. Los blobs RSP se excluyen de la recompilación CPU.

El perfil de arranque genera código que compila. El perfil de audio refleja la imagen base (`0xF80` bytes), el overlay (`0x8B8` bytes en `0x1238`) y los destinos indirectos descritos por los datos DMEM del juego; la salida también compila contra los headers del runtime fijado. Estos microcódigos han sido validados al generar/compilar, pero no se han probado en ejecución. F3DDKR sigue en investigación: sus datos DMEM describen varios rangos y overlays que aún no están representados fielmente en el perfil.

**No hay todavía un ejecutable jugable ni un arranque del juego verificado.** La API DPC del runtime y el consumidor RT64 LLE se compilaron en ramas de trabajo separadas, pero no están integrados aquí con el inicio del juego. El trabajo pendiente incluye completar el perfil F3DDKR, integrar el runtime y el adaptador en el ciclo de vida del juego, y verificar el procesamiento gráfico/DPC de extremo a extremo.

Los perfiles de `RSPRecomp` están en `rsp/` y esperan la ROM en `rom/JetForceGemini.z64`. El perfil de audio genera código con:

```powershell
.\build\N64Recomp\Release\RSPRecomp.exe rsp\audio.toml
```

El generador maneja las lecturas/escrituras COP2 de banderas vectoriales y emite llamadas a `ultramodern::dpc::read_register` / `write_register` para los registros DPC; antes de escribir `DPC_END`, registra el DMEM para los rangos XBUS. El soporte de runtime/backend desarrollado aparte no implica que el juego arranque: la integración y validación de extremo a extremo siguen pendientes. No se deben reemplazar accesos DPC por valores ficticios.

---

## ⚖️ Nota Legal

Este repositorio **no incluye** ni distribuirá archivos protegidos por derechos de autor, activos del juego (gráficos, música, niveles) ni copias de la ROM original. Para compilar y ejecutar este port, el usuario final debe proporcionar su propia copia legal de la ROM de *Jet Force Gemini*.

---

## 📌 Aviso sobre el desarrollo

Este es un proyecto **independiente y realizado por hobby**. No está afiliado, respaldado ni autorizado por Nintendo, Rare o cualquier otra entidad propietaria de los derechos de *Jet Force Gemini*.

El objetivo del proyecto es exclusivamente educativo, experimental y de preservación.
