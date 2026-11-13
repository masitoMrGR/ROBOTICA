# Plan de trabajo: Claude Code + Antigravity (Gemini) para CAD, simulación y minisumo RC

Documento de traspaso para Claude (plan Pro). Fecha: 2026-11-13.
Lo redactó otra instancia de Claude durante una conversación larga con el usuario. Léelo completo antes de actuar.

**Convención:** lo marcado con **(NO VERIFICADO)** no se confirmó en fuentes durante la conversación. Compruébalo antes de darlo por cierto. Lo demás salió de documentación oficial, de foros o de salidas reales de la laptop del usuario, y las fuentes están al final (sección 10).

---

## 0. Instrucciones para ti (Claude que recibe este documento)

1. No asumas que todo lo de aquí es correcto. La sección 8 lista errores que ya se corrigieron, y la sección 9 lo que sigue sin verificar.
2. Antes de proponer instalaciones o crear archivos, pregunta lo que falta (sección 7).
3. Entrega, en este orden:
   1. Revisión del entorno del usuario (comandos de comprobación, sin instalar nada todavía).
   2. Plan de instalación paso a paso (sección 3), confirmando antes de instalar cualquier cosa pesada.
   3. Plantilla del proyecto (sección 2.4): `CLAUDE.md`, `GEMINI.md`/`AGENTS.md`, `CONTEXTO_PROYECTO.md`, carpetas, `git init` y scripts de verificación.
   4. Prueba de los MCP candidatos con el protocolo de la sección 4.5, y el plan B (sección 4.6) si ninguno pasa.
   5. Primera simulación de minisumo con parámetros genéricos marcados como de ejemplo, y el esqueleto del reporte HTML.
4. Restricciones del usuario:
   - Debe usar sus suscripciones, **sin consumo por API** (sección 5).
   - Prefiere **open source**, porque quiere facturar (las licencias estudiantiles no sirven para eso, sección 3.2).
   - Los números finales deben salir de **scripts con tests**, no de lo que diga cualquier IA.
   - No ejecutes comandos destructivos ni edites el registro de Windows sin confirmación explícita.

---

## 1. Contexto de la persona

- Es de **CS (Computer Science)**. Usaba Tinkercad como "bloc geométrico" (sumar y restar sólidos). Busca el equivalente por código.
- Está en Perú. Pregunta por licencias gratuitas para estudiantes universitarios, y si valen para estudiantes peruanos.
- **Quiere facturar** con sus suscripciones de IA.
- Suscripciones: **Claude Pro anual** y **Google AI Pro**. El usuario cree que su Google AI Pro es una promoción de 4 años. Lo más probable es que sea un **descuento** hasta por 4 años (no 4 años gratis), pero **hay que comprobarlo en Google One** (precio y fecha de renovación). Importa porque Antigravity solo da acceso a los modelos de Claude con una suscripción Pro que no sea de prueba (sección 5).
- Laptop con Windows. Dato observado en el log de un instalador: edición `CoreSingleLanguage` (Home), versión `10.0.26300`, x64. **RAM, CPU y GPU: desconocidos.**
- Discos: tenía C, D y E, y los unificó en C y D (esto causó el problema de la sección 6.2).
- Ya tiene instalados: **Antigravity IDE** y la **app de Antigravity** (ambas con su cuenta Gemini Pro) y **Claude Code CLI**.
- Existe además un proyecto web suyo en `D:\ProyectoNexo\nexopro-mejorado-v2-scroll-fix`. **No mezclar** con el proyecto de CAD; usar una carpeta nueva (por ejemplo `D:\ProyectoCAD\minisumo`).

**Proyecto principal:** diseñar en 3D un minisumo RC, **calcular** correctamente (empuje, tracción, vuelco), **simular combates** y generar un **reporte HTML** detallado, como lo haría un ingeniero que sabe comunicar los datos y las mejoras prioritarias.

---

## 2. Arquitectura de uso de Claude y Gemini

### 2.1 Principio

**Claude Code construye y valida; Antigravity (Gemini) lee, extrae y audita.** Ambos trabajan sobre **la misma carpeta**, y la integración es un **repositorio git local**, no pasarse datos por chat. Los MCP son una ayuda opcional para el ciclo de verificación (sección 4), no la integración.

Los modelos razonan sobre código y números. No "ven" el espacio 3D de forma nativa. Lo que da confiabilidad es el **ciclo de verificación** (generar, renderizar, mirar, medir, corregir), y ese ciclo exige trabajar en la laptop con archivos y comandos, no en un chat web.

### 2.2 Dónde corre cada una

| Pieza | Dónde | Notas |
|---|---|---|
| Antigravity IDE | Editor único (fork de VS Code) | Gemini en su panel. Cuota compartida con la app y el CLI de Antigravity |
| Claude Code | **CLI** en la terminal integrada del Antigravity IDE | Es el mismo motor que la pestaña Code de la app de escritorio; todas las "puertas" (CLI, app, extensión) usan la misma cuenta y comparten límites con el chat de Claude |
| Visor 3D | Ventana de **OpenSCAD** con recarga automática | Independiente del IDE: cada cambio que una IA guarda en el `.scad` se ve al instante |
| App de escritorio de Claude | Opcional | Hoy no funciona (sección 6.2). No es necesaria |
| Antigravity CLI (`agy`) | Opcional | Es el reemplazo de Gemini CLI. Lee `GEMINI.md` y `AGENTS.md` |

Alternativa dentro de Antigravity IDE: la extensión de Claude Code. Hubo reportes de que se instala a mano desde el Marketplace, y un bug de arranque en forks de VS Code (el CLI buscaba el comando `code`) fue marcado como resuelto el 24-mar-2026. **(NO VERIFICADO hoy en la máquina del usuario.)**

### 2.3 Reparto de roles (hipótesis de trabajo)

| Tarea | Quién | Motivo |
|---|---|---|
| Leer datasheets, fotos, videos, reglamento y llenar `spec/robot.yaml` | Antigravity (modelos Gemini) | Entrada multimodal y mucho contexto. **Hipótesis, no medida.** Las medidas sacadas de fotos son estimaciones: verificar con calibre |
| Modelar (OpenSCAD/FreeCAD), simulación, tests, firmware, reporte | Claude Code | Edita archivos y ejecuta comandos con verificación |
| Auditar reporte y cálculos | Antigravity | Segunda opinión de otro modelo |
| Decidir qué se fabrica | El usuario | |

Nadie midió cuál modelo es mejor en cada tarea. Las afirmaciones de que "Claude razona mejor el espacio" o "Gemini mide mejor sobre fotos" **no están verificadas**. Se decide con el test A/B de la sección 2.8.

En Antigravity usa por defecto modelos Gemini y deja a Claude para Claude Code, porque en Antigravity los modelos de terceros gastan la cuota más rápido (sección 5).

### 2.4 Estructura de la carpeta

```
minisumo/
├─ CONTEXTO_PROYECTO.md      memoria compartida (unidades, medidas, reglas) que leen ambas IA
├─ CLAUDE.md                 reglas para Claude Code (apunta a CONTEXTO_PROYECTO.md)
├─ GEMINI.md                 reglas para Antigravity (apunta a CONTEXTO_PROYECTO.md)
├─ inputs/                   datasheets, fotos con regla o calibre, videos, reglamento
├─ spec/                     robot.yaml, tabla de cotas             ← Antigravity
├─ cad/                      parametros.scad, chasis.scad, STL      ← Claude Code
├─ sim/                      simulación MuJoCo + tests              ← Claude Code
├─ firmware/                 PlatformIO (si aplica)                 ← Claude Code
├─ tools/                    scripts de render y verificación       ← Claude Code
└─ reports/                  reporte HTML + auditorías              ← Claude genera, Antigravity audita
```

Las medidas físicas viven como **variables** en `cad/parametros.scad`, para poder cambiarlas sin pedirle nada a la IA.

### 2.5 Reglas de coordinación

1. `git init` en la carpeta, con un commit entre turnos de cada IA.
2. Zonas separadas (tabla de 2.3). **Nunca dos agentes editando el mismo archivo a la vez.**
3. Un solo `CONTEXTO_PROYECTO.md` como fuente de verdad. `CLAUDE.md` y `GEMINI.md` solo lo referencian.
4. Cada cambio de geometría pasa por el ciclo de verificación antes del commit.

### 2.6 Flujo por fases

- **Fase 1, ingesta (Antigravity):** extrae a `spec/robot.yaml` masa, motores (torque de bloqueo, corriente, velocidad), reducción, ruedas, batería, dimensiones y reglamento. Cada valor lleva su fuente.
- **Fase 2, construcción (Claude Code):** modela con módulos y variables, y corre la simulación.
- **Fase 3, ciclo de verificación:**
  1. Renderizar una imagen del modelo (con MCP, sección 4, o con el script de la sección 4.6).
  2. Que el agente la mire y compare con la especificación. **(NO VERIFICADO: que ambos agentes abran imágenes en esta configuración; probarlo.)**
  3. Exportar STL y medir con un script: caja envolvente, volumen, malla cerrada, colisiones entre piezas.
  4. Correr los tests de la simulación. Invariantes mínimos: el empuje nunca supera el menor entre la fuerza máxima del motor y μ·N (tracción), y el umbral de vuelco usa la altura del centro de masa.
- **Fase 4, auditoría cruzada (Antigravity):** revisa el reporte buscando saltos lógicos y números que violen la física. Claude corrige.
- **Fase 5, calibración con el robot real:** medir el coeficiente de fricción de las llantas sobre el dohyo y la fuerza de empuje con balanza o dinamómetro, y ajustar el modelo antes de confiar en el resto.

### 2.7 Simulador de minisumo: capas y reporte

Capas:
1. **Analítico (Python/NumPy):** curva torque-velocidad de un motor DC con caída de voltaje de la batería, tracción μ·N, transferencia de carga, umbral de vuelco, efecto de la cuña, aceleración y tiempo hasta sacar al rival.
2. **Simulación física (MuJoCo):** cientos o miles de combates con variación aleatoria (fricción, posición inicial, masa y estrategia del rival), para obtener **tasa de victoria con intervalo de confianza**, no una anécdota.
3. **Datos crudos:** `results.json`.
4. **Reporte HTML** (por ejemplo con Plotly): resumen ejecutivo (veredicto y 3 hallazgos), ficha técnica y supuestos, gráficas de motor/tracción/empuje, análisis de sensibilidad (gráfico tornado), mapa de calor por posición y estrategia, comparativa de variantes (cuña, reducción, centro de masa) y **lista priorizada de mejoras** con impacto estimado.
5. **Opcional:** replay 3D de los mejores y peores combates (Three.js).

Reglamento típico de minisumo: robot de hasta 10×10 cm y 500 g, dohyo de 77 cm de diámetro. **(NO VERIFICADO: confirmar con el reglamento de la competencia concreta.)**

Limitaciones: la fricción del caucho adherente es lo más difícil de modelar, y el simulador solo es tan bueno como sus parámetros (de ahí la Fase 5). PyBullet como alternativa a MuJoCo: **(NO VERIFICADO: licencia y encaje).**

### 2.8 Test A/B para decidir quién hace qué

Darle la misma tarea a ambos y comparar resultados:
- Extraer parámetros del mismo datasheet.
- Generar la misma pieza en OpenSCAD con las mismas medidas.
- Auditar el mismo reporte con un error plantado a propósito.

Medir: errores encontrados, número de iteraciones y cuota gastada.

---

## 3. Programas

### 3.1 Tabla principal

| Software | Para qué | Licencia | Peso (instalador / instalado) | Prioridad y estado |
|---|---|---|---|---|
| Antigravity IDE | Editor único, Gemini | Propietario; gratis con límites, más cuota con Google AI Pro | ~0.23 GB / ~0.7 GB (cifra de un tutorial del lanzamiento) | **Ya instalado** (actualizador roto, sección 6.3) |
| Claude Code CLI | Claude en terminal | Propietario; requiere Pro, Max, Team, Enterprise o Console | ~0.5 GB (fuente de terceros) | **Ya instalado** (v2.1.316) |
| OpenSCAD | Modelado 3D por código | GPL | ~0.02 GB (instalador de la versión 2021.01) | **1. Ahora** |
| Git for Windows | Control de versiones y shell de Claude Code | Open source | ~0.06 GB / ~0.3 GB **(NO VERIFICADO, estimación)** | **1. Ahora** |
| Python + MuJoCo (+ numpy, plotly) | Simulación y gráficas del reporte | MuJoCo: Apache 2.0 | MuJoCo: decenas de MB como máximo por paquete; Python, numpy y plotly **(NO VERIFICADO)** | **1. Ahora** (si Python no está ya) |
| FreeCAD | CAD paramétrico con interfaz, STEP, ensamblajes | LGPL-2.0-or-later (según el manifiesto de WinGet) | ~0.52 GB / ~2.3 GB (cifra de la 1.0.2) | **2. Después**, si se necesitan ensamblajes |
| PlatformIO | Firmware ESP32/Arduino | Apache 2.0; libre para uso comercial | 1.5 a 2 GB, casi todo compiladores | **3. Solo si programa el robot** |
| KiCad | Esquemáticos y PCB | GPL-3.0 | ~1 GB; hasta ~5 GB o más con librerías (fuente de terceros) | **3. Solo si diseña placas** |
| Blender | Renders para clientes | Open source (versión de licencia **NO VERIFICADA**) | ~1 GB mínimo | **3. Solo si lo necesita** |
| OrcaSlicer o PrusaSlicer | Cortar piezas para imprimir en 3D | Open source | ~0.3 GB (cifra de Gemini, **NO VERIFICADA**) | **3. Solo si imprime** |
| App de escritorio de Claude | Interfaz gráfica de Claude Code | Propietario | 0.28 GB (instalador, según el log del usuario) | Opcional; hoy bloqueada (6.2) |
| build123d / CadQuery + OCP CAD Viewer | Alternativa de CAD en Python | Gemini dijo Apache 2.0 **(NO VERIFICADO)** | ~0.6 GB según Gemini **(NO VERIFICADO)** | Opcional |
| Wokwi para VS Code | Simular ESP32 | Gratis para open source; **uso comercial requiere licencia** | Pequeño **(NO VERIFICADO)** | **No recomendado para trabajo con clientes** |

Espacio total: **menos de 1 GB nuevo** para arrancar; con todo lo opcional, entre **6 y 11 GB**.

Requisitos de sistema:
- **Claude Code** (oficial): Windows 10 1809+, 4 GB de RAM, x64 o ARM64.
- **Antigravity:** Windows 10 o superior; una reseña de terceros indica 8 GB de RAM (16 recomendados) y 2 GB de disco.
- **FreeCAD** (terceros): entre 2 y 4 GB de RAM mínimo según la fuente, 8 GB recomendados.
- **Blender:** 4 núcleos, 8 GB de RAM mínimo, GPU con OpenGL 4.3. Desde la 5.0 se exige NVIDIA GeForce 900+, AMD GCN 4ª generación+ o Intel Kaby Lake+.
- **KiCad:** 4 GB de RAM mínimo, 8 GB recomendados (tercero). Versión estable 10.0.6 (29-ago-2026).

Las licencias open source (GPL/LGPL/Apache) permiten usar el programa para trabajo comercial. Si algún día se redistribuye el programa en sí, hay matices. **(Conocimiento general, no verificado en las fuentes de esta sesión.)**

### 3.2 Licencias de estudiante: NO sirven para facturar

- **Autodesk (Fusion, etc.):** solo fines educativos, nunca comerciales. La verificación va por SheerID con documentos; un correo institucional no basta ni es requisito. Autodesk dice que casi todas las instituciones del mundo califican, salvo países bajo embargo de EE. UU. Perú no está en esa excepción, pero **no hay confirmación explícita para Perú**. Verificación de un año, renovable. El plan "Personal Use" gratuito es no comercial y solo para menos de US$1,000 de ingresos al año.
- **Onshape Education:** solo uso no comercial.
- **SolidWorks Student Edition:** unos US$86 a 139 por 12 meses; el uso comercial está prohibido.
- **GitHub Student Developer Pack:** disponible en la mayoría de países, para estudiantes verificados, con reverificación periódica (la documentación de GitHub dice 2 años).
- **Wokwi:** la promoción de "3 meses de Pro" es para aulas (docentes), no una licencia estudiantil.
- **Google AI Pro estudiantil:** para Perú hubo un año gratis con registro hasta el 9-dic-2025. Hoy la oferta de AI Pro gratis es solo para EE. UU. (quien ya la reclamó en Perú la conserva hasta que termine su periodo). Fuera de EE. UU. se ofrece AI Plus gratis un año (canje hasta el 31-dic-2026). Además existe AI Pro con descuento hasta por 4 años, que probablemente es lo que tiene el usuario.

### 3.3 Orden de instalación

1. Comprobar el entorno: `claude --version`, `claude doctor`, `git --version`, `python --version`, y RAM/CPU/GPU del equipo.
2. Instalar **OpenSCAD**, **Git for Windows** y **Python** (si falta). Confirmar los IDs con `winget search` antes de `winget install`. Ya verificados: `Anthropic.ClaudeCode` y `FreeCAD.FreeCAD`. El de OpenSCAD y el de Git **(NO VERIFICADOS)**.
3. En un entorno virtual: `pip install mujoco numpy plotly`.
4. Probar el ciclo de verificación sin MCP (sección 4.6).
5. Añadir MCP (sección 4).
6. FreeCAD, PlatformIO, KiCad, Blender y slicer, solo cuando haga falta.

### 3.4 Dónde instalar

Todo en `C:` con rutas por defecto. Los usuarios que instalaron Antigravity fuera de la ruta por defecto reportan fallos del actualizador, y el usuario ya tuvo un problema de volumen en `D:` (6.2). Si `C:` queda justo, se puede redirigir la carpeta de PlatformIO a otra unidad con la variable `PLATFORMIO_CORE_DIR`. Los proyectos pueden vivir en `D:`.

---

## 4. MCP (Model Context Protocol)

### 4.1 Qué aportan y qué no

- Un MCP es un **programa local** que le da herramientas a un agente. **No consume créditos por sí mismo.** El costo depende de la cuenta con la que el modelo que lo llama esté autenticado (sección 5).
- **Claude Code y Antigravity soportan MCP.** Ambos pueden apuntar al mismo servidor, cada uno con su archivo de configuración y su propia instancia.
- Valor principal: el **ciclo de verificación**, es decir, que el agente vea lo que construyó (por ejemplo, el MCP de FreeCAD devuelve una captura tras cada operación; los de OpenSCAD generan PNG).
- **No hacen que las dos IA trabajen juntas.** Eso lo hace la carpeta compartida con git.
- Cada MCP activo añade herramientas al contexto del agente y algo de consumo de cuota. Activar solo los que se usen. **(Afirmación general, NO VERIFICADA con cifras.)**
- Con MCP que controlan un programa abierto (FreeCAD, Blender), conectar **un solo agente a la vez**. El de Blender advierte que solo debe correr una instancia. Además, el de Blender y uno de FreeCAD (theosib) usan por defecto el mismo puerto, el 9876.

### 4.2 Seguridad

Los MCP son proyectos de la comunidad, no verificados. Ejecutan código con los permisos del usuario. Los de Blender y FreeCAD pueden ejecutar **Python arbitrario** dentro del programa. Antes de instalar: revisar el repositorio, su licencia y sus dependencias; no pegar claves ni credenciales en ninguna configuración; y no usarlos con archivos de terceros no confiables.

### 4.3 Candidatos

**OpenSCAD (prioridad 1; elegir uno tras probarlos):**

| MCP | Cómo funciona (según su descripción) | Notas |
|---|---|---|
| `petrijr/openscad-mcp` | Envoltorio del CLI de OpenSCAD: valida, renderiza PNG y exporta STL/3MF/OFF. Requiere `openscad` en el PATH. Transporte stdio, con script opcional para Docker | **(NO VERIFICADO si trabaja con archivos de la carpeta del proyecto)** |
| `jkoets/OpenSCAD-MCP` | Crea, actualiza y lee modelos; `render_preview` (PNG) y `render_code`. Guarda los modelos en `./workspace` relativo al servidor | Ojo: no necesariamente en la carpeta del proyecto. Espera OpenSCAD en `C:\Program Files\OpenSCAD\openscad.exe` |
| `dkpoulsen/openscad-mcp` (npm `openscad-mcp`) | Herramientas `render`, `preview`, `validate`, `info`. Recibe el **código como texto** | Obliga a reenviar el código en cada llamada: más cuota y riesgo de desincronizarse de los archivos reales |
| `devaclark/mcp-3d-tools` | 30 herramientas: render con vista previa en el chat, medición, análisis y reparación de mallas, exportación 3MF, estimación de impresión. `openscad_render` recibe `scad_file` y `variables`. **Corre en Docker** | Docker no es liviano **(NO VERIFICADO)**. No se sabe cómo monta la carpeta del usuario. Dejar para después |

Mi orden de prueba (juicio mío, hipótesis a validar con 4.5): `petrijr`, luego `jkoets`, luego `dkpoulsen`, y `mcp-3d-tools` al final por el Docker.

**FreeCAD (prioridad 2, solo si hay ensamblajes o STEP):**
- `neka-nat/freecad-mcp` (MIT). Se registra con `claude mcp add freecad -- uvx freecad-mcp` (requiere `uv`). Hay que copiar el addon `FreeCADMCP` a la carpeta de módulos de FreeCAD, reiniciar, elegir el banco de trabajo "MCP Addon" y pulsar **Start RPC Server**. La ruta en Windows de esa carpeta **(NO VERIFICADA)**.
- Alternativas: `spkane/freecad-robust-mcp` (83 herramientas, `pip install freecad-robust-mcp`), `theosib/FreeCAD-MCP-Server` (puerto TCP 9876). **Evitar** `proximile/freecad-mcp`: 57 herramientas con Docker y componentes de visión y generación 3D con servicios externos.

**Blender (prioridad 3, solo para visuales de clientes):** `ahujasid/blender-mcp`. Requiere Blender 3.0+ y Python 3.10+. Se registra con `claude mcp add blender uvx blender-mcp`. Se instala el `addon.py` y se pulsa "Connect to Claude" en la barra lateral de Blender. Puerto por defecto 9876. Telemetría desactivable con `DISABLE_TELEMETRY=true`. No activar integraciones que pidan claves de API.

**KiCad (prioridad 3, solo si diseña PCB):** `lamaalrajih/kicad-mcp` (análisis, BOM, DRC por `kicad-cli`, visualización), `mixelpixx/KiCAD-MCP-Server` (KiCad 9+), `obhox/kicad-mcp` "Konnect" (plugin para KiCad 10), `ProductOfAmerica/mcp-server-kicad` (100+ herramientas). KiCad actual es la 10.x y algunos MCP apuntan a la 9.

**Sin MCP:** PlatformIO, Git y MuJoCo se manejan con comandos de terminal.

### 4.4 Cómo registrarlos

- **Claude Code:** `claude mcp add <nombre> -- <comando> <argumentos>`, o un archivo `.mcp.json` en la raíz del proyecto. Para ver el listado y las opciones: `claude mcp --help` **(NO VERIFICADO el subcomando exacto)**.
- **Antigravity CLI (`agy`):** archivo `mcp_config.json`. Global en `~/.gemini/antigravity-cli/mcp_config.json`, y por proyecto en `.agents/mcp_config.json`. En la primera ejecución `agy` ofrece importar la configuración vieja de Gemini CLI (`~/.gemini`). Guía oficial de migración: `antigravity.google/docs/gcli-migration`.
- **Antigravity IDE:** dónde se configuran los MCP en el IDE **(NO VERIFICADO)**; mirar en sus ajustes.
- Instrucciones por proyecto: Claude Code lee `CLAUDE.md`; `agy` lee `GEMINI.md` y `AGENTS.md`.

### 4.5 Protocolo de prueba de un MCP

1. Instalar y registrar el MCP en **un** agente. Listar sus herramientas.
2. Crear en la **carpeta del proyecto** un `.scad` trivial (un cubo con un agujero) y pedir una vista previa PNG.
3. Comprobar que el archivo que lee o escribe está en la carpeta del proyecto y no en una carpeta propia del servidor.
4. Que el agente describa la imagen y confirme que coincide con lo pedido.
5. Exportar STL y pasarlo por el script de verificación (caja envolvente y volumen conocidos).
6. Confirmar que **no hay consumo de API**: sin claves en variables de entorno, y consumo normal en `/usage`.
7. Repetir con el segundo agente, **sin** tener el primero conectado al mismo programa abierto.
8. Si falla cualquier paso: pasar al plan B.

### 4.6 Plan B sin MCP (siempre disponible)

Un script en `tools/` que llame a `openscad` por línea de comandos para exportar un PNG (con cámara y tamaño fijos) y el STL, y otro en Python que mida el STL. Los dos agentes lo ejecutan por terminal y abren la imagen resultante. OpenSCAD puede exportar PNG desde la línea de comandos; **(NO VERIFICADO en la máquina del usuario, probarlo)**. Elegir al implementarlo la librería de Python para la malla y revisar su licencia.

---

## 5. Evitar cobros por API

**Claude Code:**
- Iniciar sesión con `claude auth login` o simplemente `claude`, y elegir la **cuenta de Claude con suscripción** (claude.ai), no la opción de Console (facturación por API).
- Si existe la variable de entorno `ANTHROPIC_API_KEY`, Claude Code usa esa clave y **cobra por API** en lugar de la suscripción. En el equipo del usuario salió **vacía** (comprobado el 2026-11-01). Si Claude Code pregunta si usar una clave de API, responder que no.
- Comprobar con `/usage` (algunas fuentes dicen `/status`) y con `claude doctor` que la suscripción de claude.ai esté activa.
- Dejar apagado el "extra usage" (en claude.ai: Settings > Usage). Si al agotar el límite Claude Code ofrece seguir con créditos de API, rechazar.
- El uso se **comparte** entre el chat de Claude y Claude Code.

**Antigravity:**
- Plan individual gratis con límite semanal. Google AI Pro/Ultra suben la cuota, y la cuota es la misma en la app y en el CLI.
- Dejar desactivado el interruptor **"Enable AI Credit Overages"**: en "Always" gasta créditos comprados al agotarse la cuota.
- Los modelos de Claude dentro de Antigravity salen de la **cuota de Google**, no de la cuenta de Claude del usuario. Según la documentación de Google (revisada el 3-oct-2026 por un medio), Claude Sonnet 5.5 y Opus 5.5 están para Google AI Pro y Ultra **con suscripción que no sea de prueba**, y se programó retirar los Claude 4.6 y GPT-OSS-120B el 2-nov-2026. Los modelos de terceros gastan la cuota más rápido que los Gemini.
- No usar proxies de terceros que redirijan una suscripción hacia otra herramienta: mezclan credenciales y pueden arriesgar la cuenta. **(Sus términos no se verificaron.)**

---

## 6. Estado actual y pendientes

### 6.1 Claude Code CLI

Instalado (v2.1.316) en `C:\Users\mgian\.local\bin\claude.exe`. El PATH ya está corregido y `claude doctor` dice "No installation issues found". `ANTHROPIC_API_KEY` está vacía. **Pendiente:** iniciar sesión con la cuenta Pro (**no confirmado**), comprobar `/usage` y abrir `claude` dentro de la terminal de Antigravity IDE en la carpeta del proyecto. La primera vez en una carpeta pide confiar en ella: leer el aviso antes de aceptar.

### 6.2 App de escritorio de Claude (instalación fallida)

- Error: `AddPackage failed with HRESULT 0x80073D0D`. Según Microsoft, ese código significa que el volumen está desconectado.
- Diagnóstico confirmado: el paquete `Claude_1.30096.5.0_x64__pzs8sxrjxfjjc` está registrado en un volumen de aplicaciones en `D:\WindowsApps` que figura **desconectado** (`IsOffline: True`), con estado `PackageOffline, DataOffline, NotAvailable`. Casi seguro quedó huérfano al unificar los discos C, D y E.
- `Mount-AppxVolume` y `Remove-AppxVolume` fallan con `0x80070490` ("no se ha encontrado el elemento"). El volumen por defecto ya es `C:`.
- Otras apps rotas por lo mismo: `OpenAI.Codex` y `Microsoft.Office.OneNoteVirtualPrinter`.
- El log también muestra que el instalador no pudo quitar el servicio `CoworkVMService` (acceso denegado). Hay reportes públicos de ese problema bloqueando reinstalaciones.
- **Siguiente paso, aún no hecho:** en PowerShell como administrador, `Remove-AppxPackage -Package "Claude_1.30096.5.0_x64__pzs8sxrjxfjjc"`, comprobar con `Get-AppxPackage *Claude*` que ya no aparece, y volver a ejecutar `Claude Setup.exe`. Si falla de nuevo, no editar el registro por cuenta propia: revisar con el usuario.
- **Es opcional.** El CLI cubre la necesidad. La pestaña Code de la app es el mismo Claude Code con interfaz gráfica; la app exige Git for Windows para sesiones locales.

### 6.3 Actualizador de Antigravity IDE

- Errores: "Failed to install Visual Studio Code update" y "CreateProcess falló; código 2" al intentar ejecutar `C:\Users\mgian\AppData\Local\Programs\Antigravity IDE\Antigravity IDE.exe`.
- Es un bug **conocido** del actualizador, con varios reportes en el foro de Google. Los logs muestran "Code path doesn't seem to exist". Se relaciona sobre todo con instalaciones fuera de la ruta por defecto. El texto sobre antivirus es un aviso genérico de VS Code.
- Diagnóstico pendiente: leer `C:\Users\mgian\AppData\Local\Temp\vscode-inno-updater-1793588938.log`, ver dónde está instalado realmente el IDE (clic derecho en el acceso directo, "Abrir ubicación del archivo") y revisar si Malwarebytes puso algo en cuarentena.
- Arreglo propuesto: cerrar el IDE, descargar el instalador nuevo de `antigravity.google/download` e instalarlo **sin cambiar la ruta por defecto**. Mientras tanto, el IDE probablemente sigue abriendo con la versión actual.

---

## 7. Información que falta (preguntar al usuario)

1. RAM, CPU y GPU de la laptop (y espacio libre en C: y D:).
2. ¿Python está instalado? ¿Qué versión?
3. ¿Ya inició sesión en Claude Code con la cuenta Pro? ¿Qué muestra `/usage`?
4. Especificaciones del robot: motores, ruedas, reducción, batería, masa, dimensiones, y el reglamento de la competencia.
5. ¿Imprimirá piezas en 3D, programará el firmware o diseñará placas? (decide si se instalan slicer, PlatformIO y KiCad).
6. ¿Su Google AI Pro es una suscripción de pago con descuento o una promoción de prueba?
7. ¿Qué mostró el log del actualizador de Antigravity y dónde está instalado el IDE?

---

## 8. Errores corregidos durante la conversación

1. **Gemini CLI ya no existe para su plan.** El acceso gratuito por cuenta de Google se apagó el 18-jun-2026 y los planes AI Pro pasaron a **Antigravity CLI (`agy`)**. Cualquier mención previa a Gemini CLI está desactualizada, incluida la de la página que generó Gemini.
2. **Claude dentro de Antigravity:** una reseña afirmaba que exigía una clave de API propia. No coincide con la documentación de Google ni con su foro: viene de la cuota de Google, con la condición de suscripción Pro que no sea de prueba.
3. **Las licencias estudiantiles no valen para facturar** (Autodesk, Onshape, SolidWorks, Fusion personal).
4. **Afirmaciones de Gemini sin respaldo o incorrectas:** que Autodesk "reconoce dominios `.edu.pe`" (no encontré tal lista y Autodesk dice que el correo institucional no es suficiente ni requisito); que Wokwi tiene "licencia académica válida en Perú" (lo que hay es una promoción para aulas, y el uso comercial es de pago); KiCad "v8/v9" (la actual es la 10.x); cifras de peso (FreeCAD instalado es ~2.3 GB, no 1.2 a 1.5 GB). Los puntajes y porcentajes de su página comparativa no tienen metodología.
5. **Su demostración de torreta (Three.js/OpenSCAD/Wokwi) tiene errores que no hay que copiar:** el `.scad` usa Z hacia arriba y la escena y el HUD usan Y hacia arriba sin conversión; el firmware se anuncia como "no bloqueante" pero el `loop()` usa `delay(50)`; alimenta un MG996R y un SG90 desde el VIN del ESP32 (el MG996R puede pedir mucha corriente en bloqueo: estimación mía); el ECHO del HC-SR04 saca 5 V a un GPIO de 3.3 V sin divisor; el atributo `angle` en el `diagram.json` de Wokwi **(NO VERIFICADO)**; y "listo para impresión 3D" es exagerado porque falta el alojamiento de los servos.
6. **Lo de "4 años" de Google AI Pro:** lo más probable es un descuento, no 4 años gratis.
7. **La app de escritorio de Claude** no es un producto distinto: incluye Claude Code en la pestaña Code. El CLI no es una versión recortada. Se dijo antes que su instalación previa estaba "probablemente intacta"; el diagnóstico real mostró que el paquete está desconectado.
8. **Los MCP de OpenSCAD no son equivalentes:** algunos reciben el código como texto y otros guardan los modelos en su propia carpeta. Hay que probarlos con 4.5. Wokwi, que se mencionó antes como reemplazo de Tinkercad Circuits, requiere licencia de pago para uso comercial.

---

## 9. Lo que sigue sin verificar (resumen)

- Pesos de Git, Python, numpy, plotly, slicers, OpenSCAD instalado y Wokwi.
- Requisitos mínimos de FreeCAD y KiCad (solo fuentes de terceros) y de RAM de Antigravity.
- Reglamento de minisumo (10×10 cm, 500 g, dohyo de 77 cm).
- Que ambos agentes abran imágenes en este flujo, y que OpenSCAD exporte PNG por CLI en su equipo.
- Qué MCP de OpenSCAD trabaja con archivos de la carpeta del proyecto, y cómo monta carpetas `mcp-3d-tools`.
- Dónde se configuran los MCP en Antigravity IDE; compatibilidad de extensiones (Claude Code, Wokwi, PlatformIO) en ese IDE.
- Ruta de módulos de FreeCAD en Windows para el addon del MCP.
- Licencias de Blender (versión), build123d/CadQuery y PyBullet.
- Si el Google AI Pro del usuario cuenta como "no de prueba" para acceder a Claude en Antigravity.
- Subcomando exacto para listar MCP en Claude Code; términos de los proxies de terceros.

---

## 10. Fuentes

- Claude Code, instalación y autenticación: https://code.claude.com/docs/en/install
- Claude Code con plan Pro o Max: https://support.claude.com/en/articles/11145838
- Claude Code Desktop (pestañas Chat, Cowork y Code): https://code.claude.com/docs/en/desktop
- Límites de uso de Claude Code: https://www.morphllm.com/claude-code-usage-limits
- Gemini CLI a Antigravity CLI: https://computingforgeeks.com/install-configure-gemini-cli/
- Antigravity CLI y MCP: https://mem.nowledge.co/docs/integrations/antigravity-cli
- Antigravity en Windows y cuota compartida: https://viniensina.com.br/?p=4209
- Antigravity, Claude 5.5 en planes de pago: https://letsdatascience.com/news/google-antigravity-adds-claude-55-to-paid-tiers-6a3e78f1
- Antigravity, límites y créditos de sobreuso: https://vibecodehq.pages.dev/blog/google-antigravity-rate-limits-ai-credits-pro-ultra-backlash
- Foro de Google: Claude y GPT incluidos en AI Pro: https://discuss.ai.google.dev/t/google-ai-pro-subscription-not-recognized-in-antigravity-ide-claude-gpt-models-showing-warning/169203
- Claude Code dentro de Antigravity (bug resuelto): https://claudeissues.com/issue/22360-bug-cli-fails-to-start-in-google-antigravity-error-installing-vs-code-extension
- Actualizador de Antigravity: https://discuss.ai.google.dev/t/antigravity-ide-updater-fails-when-installed-on-d-drive/179097 y https://discuss.ai.google.dev/t/bug-failed-to-update-inno-updater-fails-with-code-path-doesnt-seem-to-exist/178799
- Oferta estudiantil de Google: https://support.google.com/gemini/answer/16417758 y https://www.tiempo.com.mx/tecnologia/eres-estudiante-asi-podrias-tener-gemini-gratis-por-un-ano-22-agosto-2026/
- Descuento de AI Pro hasta 4 años: https://www.xatakamovil.com/movil-y-sociedad/gemini-pago-ahora-gratis-durante-ano-google-trae-a-espana-su-promocion-vuelta-al-cole-esperada/amp
- Autodesk, educación: https://www-pt.autodesk.com/support/account/education/admin/available-products
- Autodesk, tipos de suscripción: https://www.autodesk.com/products/fusion-360/blog/subscription-types/
- Onshape Education: https://www.onshape.com/es/education/sign-up
- SolidWorks Student: https://solidprofessor.com/blog/what-is-the-solidworks-student-edition/
- GitHub Student Pack, términos: https://docs.github.com/en/education/about-github-education/github-education-for-students/github-terms-and-conditions-for-the-student-developer-pack
- Wokwi, licencia y precios: https://wokwi.com/license y https://wokwi.com/pricing
- PlatformIO, uso comercial: https://community.platformio.org/t/platformio-commercial-use-solved/12726
- PlatformIO, espacio y carpeta: https://community.platformio.org/t/how-to-get-platformio-to-work-through-wsl-getting-no-files-found-in-ui/13008/4 y https://community.platformio.org/t/can-i-move-platformio-folder-to-another-partition-drive/6502
- MuJoCo: https://pypi.org/project/mujoco/
- FreeCAD, descargas: https://sourceforge.net/projects/free-cad/files/1.1.0 ; tamaño instalado: https://portableapps.com/node/62854 ; licencia (WinGet): https://app.silentinstallhq.com/installer/1a37e156064113c069f58e40966bc1efdcc870a5471781a5322dfbb70697be73
- FreeCAD MCP: https://mcp.directory/blog/freecad-mcp-complete-guide-2026
- Blender, requisitos 5.0: https://blenderartists.org/t/system-requirements-for-blender-5-0/1602460
- Blender MCP: https://github.com/kiuber/blender-mcp
- OpenSCAD MCP: https://github.com/jkoets/OpenSCAD-MCP ; https://glama.ai/mcp/servers/dkpoulsen/openscad-mcp/tree ; https://lobehub.com/mcp/petrijr-openscad-mcp ; https://github.com/devaclark/mcp-3d-tools
- OpenSCAD, tamaño del instalador: https://www.filehorse.com/download-openscad-64/
- KiCad: https://en.wikipedia.org/wiki/KiCad ; MCP: https://forum.kicad.info/t/i-built-an-mcp-server-that-lets-ai-assistants-help-with-kicad-pcb-design/66451
- Error de despliegue 0x80073D0D (Microsoft): https://learn.microsoft.com/windows/win32/appxpkg/troubleshooting
- Volúmenes de paquetes y cmdlets (Microsoft): https://learn.microsoft.com/en-us/windows/msix/package/package-volumes y https://learn.microsoft.com/windows/msix/desktop/powershell-msix-cmdlets
- Reporte público de `CoworkVMService` bloqueado: https://github.com/anthropics/claude-code/issues/78873
