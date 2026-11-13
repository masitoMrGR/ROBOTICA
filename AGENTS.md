# Reglas compartidas para agentes (Claude Code y Antigravity/Gemini)

Fuente de verdad del proyecto. `CLAUDE.md` y `GEMINI.md` solo apuntan aquí.
Pendientes abiertos: `PENDIENTES.md`. Plan original (histórico, puede estar desactualizado): `docs/historial/`.

## Principios

1. **Nunca des por buena una geometría o un número sin verificarlo.** Toda pieza pasa por el ciclo:
   generar → renderizar → mirar la imagen → medir (bbox, volumen, malla cerrada) → corregir.
2. Los números finales salen de **scripts con tests** (`pytest`), no de lo que diga una IA.
3. Medidas físicas como **variables** (`parametros.scad`, `spec/robot.yaml`), en **mm**, **Z hacia arriba**, origen en el centro de la base.
4. **No inventar límites ni datos.** Todo valor lleva su fuente (PDF + página, datasheet, medición con calibre y fecha) o se marca `estimado`. Si no hay dato, se deja `null`.
5. Un solo agente edita un archivo a la vez. Commit de git entre turnos de cada agente.

## Estructura

```
ROBOTICA/
├─ AGENTS.md  CLAUDE.md  GEMINI.md  PENDIENTES.md  .mcp.json
├─ .venv/  .venv-cadquery/             entornos Python (no se versionan)
├─ tools/                              COMPARTIDO: scripts de render, medición y chequeos
│  ├─ render.py  medir_stl.py  check_reglamento.py
│  ├─ fisica/                          modelos físicos reutilizables (motor DC, tracción, vuelco…)
│  └─ tests/                           pytest de tools/
├─ reglamentos/                        COMPARTIDO: una carpeta por competencia
│  ├─ XRobo7s-2026/reglamento.yaml (+ PDF oficial)
│  └─ CNR_UNI_2026/reglamento.yaml (+ PDF oficial)
├─ componentes/                        COMPARTIDO: catálogo de piezas compradas
│  ├─ componentes.yaml  datasheets/  scad/  kicad/
├─ docs/historial/                     documentos viejos, solo referencia
└─ RobotXxx/                           uno por robot (BugRace, Combate, MinisumoAutonomo,
   ├─ spec/robot.yaml                   MinisumoBTRC, SeguidorLineaVelocista, WalkingRace)
   ├─ inputs/   fotos, notas, videos propios del robot
   ├─ cad/      .scad / build123d
   ├─ sim/      analítico + MuJoCo + tests
   ├─ firmware/ PlatformIO
   ├─ pcb/      proyecto KiCad
   ├─ reports/  reporte HTML + auditorías
   └─ build/    salidas generadas (STL, PNG); fuera de git
```

**Regla de independencia:** cada `RobotXxx/` es independiente. Un agente que trabaja en un robot **no lee ni edita otro robot** salvo que el usuario lo pida. Lo único compartido es `componentes/`, `reglamentos/` y `tools/`; cambiar algo ahí afecta a todos los robots, así que se avisa al usuario y se corren los tests de `tools/`.

**Versiones:** se marcan con **tags de git** (`RobotMinisumoBTRC/v1.0`, `RobotCombate/v0.3-pruebas`), **nunca con carpetas** (`v2/`, `final/`, `copia/`). Las variantes de diseño en desarrollo van como parámetros y se elige una con `variante_activa` en `robot.yaml`.

## Quién edita qué

| Ruta | Usuario | Gemini (Antigravity) | Claude Code |
|---|---|---|---|
| `reglamentos/*/` PDF | sube | lee | lee |
| `reglamentos/*/reglamento.yaml` | **único que pasa `estado` a `verificado`** | extrae límites del PDF con fuente (deja `pendiente`) | lee; no edita límites |
| `componentes/datasheets/` | sube | lee | lee |
| `componentes/componentes.yaml` | revisa | extrae datos con fuente | lee; puede añadir medidas propias con fuente |
| `componentes/scad/`, `componentes/kicad/` | revisa | audita | modela |
| `RobotXxx/inputs/` | sube | lee | lee |
| `RobotXxx/spec/robot.yaml` | decide `competencias` y `variante_activa` | llena datos con fuente | lee; actualiza `masas.estimada_g` desde CAD |
| `RobotXxx/cad, sim, firmware, pcb` | decide | audita (no edita) | construye |
| `RobotXxx/reports/` | lee | escribe `auditoria-*.md` | genera el reporte |
| `tools/` | aprueba cambios | audita | construye y mantiene tests |
| `AGENTS.md`, `PENDIENTES.md` | aprueba | propone | propone |

## Reparto Claude / Gemini y coordinación

- **Claude Code construye y valida**: CAD, simulación, tests, firmware, PCB, reportes.
- **Gemini lee, extrae y audita**: datasheets, PDFs de reglamentos, fotos y videos → YAML con fuentes; auditoría de reportes y cálculos.
- Que uno sea "mejor" que otro en algo **no está medido**. Se decide con pruebas A/B (misma tarea a ambos, comparar errores, iteraciones y cuota).
- **Cómo se coordinan:** comparten esta carpeta, estas reglas y los mismos MCP. No se hablan directamente.
  - Modo manual: el usuario reparte tareas a cada uno.
  - Modo coordinado: Claude delega en Gemini por terminal con
    `agy -p "<tarea>" --mode plan` (solo lectura) o `--mode accept-edits` (si debe escribir en su zona).
    Verificado el 2026-11-13: responde desde la cuenta Google AI Pro y ve los 4 MCP.
    Para auditar, a Gemini se le pasan los archivos, **no el razonamiento de Claude**, para que la revisión sea independiente.
- Antigravity puede usar modelos Claude, pero gastan su cuota más rápido: allí usar Gemini por defecto.

## Fases de trabajo de un robot

1. **Reglamento:** el usuario sube el PDF → Gemini llena `reglamento.yaml` → el usuario lo revisa y pasa `estado: verificado`.
2. **Ingesta:** Gemini extrae componentes y specs a `componentes.yaml` y `robot.yaml`, con fuente.
3. **Construcción (Claude):** CAD paramétrico → ciclo de verificación → simulación (analítico + MuJoCo) con tests.
   Invariantes mínimos: el empuje nunca supera `min(fuerza del motor, μ·N)`; el vuelco usa la altura real del centro de masa.
4. **Chequeo de reglamento:** `tools/check_reglamento.py RobotXxx`. Solo `CUMPLE` cuenta; `INDETERMINADO` no es aprobado.
5. **Auditoría cruzada (Gemini):** busca números que violen la física y saltos lógicos → `reports/auditoria-*.md`; Claude corrige.
6. **Calibración con el robot real:** medir fricción de llantas, fuerza de empuje y masa; ajustar el modelo antes de confiar en el resto.
7. **Versión:** tag de git cuando el usuario aprueba.

## Comandos de verificación

```
.venv\Scripts\python.exe tools\render.py RobotXxx\cad\pieza.scad [--vista iso|top|front|right]   # → RobotXxx\build\ PNG + STL
.venv\Scripts\python.exe tools\medir_stl.py RobotXxx\build\pieza.stl                             # bbox, volumen, malla cerrada, masa
.venv\Scripts\python.exe tools\check_reglamento.py RobotXxx [--stl ruta]                          # 0 CUMPLE · 1 NO_CUMPLE · 2 INDETERMINADO
.venv\Scripts\python.exe -m pytest tools\tests -q
```
Después de renderizar, **abre el PNG y descríbelo** antes de afirmar que la pieza está bien.
`check_reglamento.py` toma el límite más estricto entre todas las competencias del robot y **nunca da CUMPLE si algún reglamento está pendiente**.

## Herramientas instaladas (verificadas el 2026-11-13)

| Herramienta | Ruta / comando | Uso |
|---|---|---|
| OpenSCAD 2026.11.12 (nightly, Manifold) | `openscad` → `%LOCALAPPDATA%\Programs\OpenSCAD\openscad.com` | CAD por código. Portable: el paquete nightly de winget falla por hash; actualizar bajando el zip oficial |
| FreeCAD 1.1.4 | `%LOCALAPPDATA%\Programs\FreeCAD 1.1\bin\freecad.exe` (`freecadcmd.exe` sin GUI) | CAD paramétrico, STEP, ensamblajes, FEM |
| KiCad 10.0.8 | `%LOCALAPPDATA%\Programs\KiCad\10.0\bin\kicad-cli.exe` | Esquemáticos, PCB, ERC/DRC, Gerbers |
| Blender 5.3 | `C:\Program Files\Blender Foundation\Blender 5.3\blender.exe` | Renders para clientes |
| PrusaSlicer 2.9.7 / OrcaSlicer 2.5.0 | menú Inicio | Laminar para impresión 3D |
| MeshLab, Inkscape | menú Inicio | Inspección de mallas; SVG |
| PlatformIO 6.2 | `pio` (+ extensión en Antigravity) | Firmware ESP32/Arduino |
| Python 3.12 `.venv` | `.venv\Scripts\python.exe` | numpy, scipy, pandas, plotly, kaleido, mujoco 4.0, trimesh, manifold3d, build123d 0.13, ocp_vscode, pytest, pyyaml, jupyterlab |
| CadQuery 2.8 `.venv-cadquery` | `.venv-cadquery\Scripts\python.exe` | **No mezclar con build123d** en el mismo venv (OCP choca) |
| uv / agy / git / Docker | en PATH | Gestor Python; CLI de Antigravity; versiones; solo si un MCP lo pide |

Hardware: Ryzen 7 7735HS, 15 GB RAM, RTX 3050 6 GB, Windows 11 Home.

## MCP configurados

Claude Code: `.mcp.json`. Antigravity IDE y `agy`: `~/.gemini/config/mcp_config.json`. Misma configuración en ambos, versiones fijas.

| MCP | Qué da | Requisito |
|---|---|---|
| `openscad` (openscad-mcp 0.6.1) | `render` (vistas, cortes, antes/después, `annotate=true` da escala mm/px), `measure`, `validate`, `export_model` | Solo accede a `D:\DiscoE\ROBOTICA` (probado: rechaza rutas fuera) |
| `freecad` (freecad-mcp 0.1.31) | Crear/editar objetos, `get_view`, FEM | FreeCAD abierto → banco **MCP Addon** → **Start RPC Server** |
| `kicad` (kicad-mcp-pro 4.14) | 25 herramientas **solo lectura** (ERC, DRC, QA visual, BOM, DFM) | Llamar `kicad_set_project` con el proyecto de `RobotXxx/pcb/` |
| `blender` (mcp-for-blender 2.2.9) | Escena, `look`, ejecutar Python | Blender abierto (N → MCP for Blender → Start). Telemetría off, safe mode on |

- **FreeCAD y Blender: un solo agente conectado a la vez.**
- No usar `generate_3d`, `search_assets`, `import_asset` ni integraciones que pidan claves o créditos (Sketchfab, Meshy, Hyper3D…).
- Si un MCP falla, usar los comandos de verificación de arriba.

## No pagar API

- Solo suscripciones: **Claude Pro** (Claude Code) y **Google AI Pro** (Antigravity, `agy`). El uso de Claude se comparte entre el chat y Claude Code.
- Sin `ANTHROPIC_API_KEY`, `GEMINI_API_KEY` ni `GOOGLE_API_KEY` en el entorno (comprobado vacío el 2026-11-13). Si Claude Code ofrece usar una clave o créditos de API al agotar el límite: **no**.
- claude.ai → Settings → Usage: "extra usage" apagado. Antigravity: **"Enable AI Credit Overages" apagado**.
- Nada de proxies que redirijan una suscripción a otra herramienta. Ninguna clave en archivos del repo.

## Licencias (para poder facturar)

- **Open source = se puede usar para trabajo comercial:** OpenSCAD (GPL-2), FreeCAD (LGPL), KiCad (GPL-3), Blender (GPL), PrusaSlicer y OrcaSlicer (AGPL-3), MuJoCo, build123d, CadQuery y PlatformIO (Apache-2.0), MCP usados (MIT). Matices solo si se **redistribuye** el programa mismo.
- **Licencias de estudiante NO sirven para facturar:** Autodesk/Fusion (educativa y Personal Use, no comerciales), Onshape Education, SolidWorks Student.
- **Wokwi:** uso comercial requiere licencia de pago. No usar en trabajos para clientes.
- Antes de agregar una librería o un MCP nuevo: revisar su licencia y anotarla aquí.
