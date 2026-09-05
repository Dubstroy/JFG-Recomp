# 🌌 Jet Force Gemini - Static Recompilation Port

Este proyecto busca crear un **port nativo para PC** del clásico de Nintendo 64 **Jet Force Gemini**, utilizando tecnología de recompilación estática automatizada.

El objetivo principal es lograr que el juego se ejecute de forma nativa en sistemas modernos (Windows/Linux) sin necesidad de emulación tradicional, permitiendo mejoras de rendimiento, soporte para resoluciones modernas y tasas de cuadros por segundo desbloqueadas.

---

## 🛠️ Tecnologías Utilizadas

Este repositorio se apoya fuertemente en las herramientas desarrolladas por la comunidad de preservación:
*   **[N64Recomp](https://github.com):** Herramienta central para la traducción estática de binarios MIPS a código nativo en C++.
*   **RT64:** Renderizador moderno utilizado de fondo para traducir los gráficos originales a APIs modernas como DirectX 12 y Vulkan.

---

## 📂 Estructura del Proyecto

*   `/N64Recomp`: Submódulo con las herramientas de recompilación.
*   `/src`: Código fuente en C++ generado automáticamente y parches manuales.
*   `/patches`: Configuraciones específicas para solucionar errores lógicos del juego.
*   `/rom`: Carpeta local para colocar la ROM legal (excluida de Git por razones legales).

---

## ⚖️ Nota Legal

Este repositorio **no incluye** ni distribuirá archivos protegidos por derechos de autor, activos del juego (gráficos, música, niveles) ni copias de la ROM original. Para compilar y ejecutar este port, el usuario final debe proporcionar su propia copia legal de la ROM de *Jet Force Gemini*.
