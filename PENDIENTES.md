# Pendientes

Estado al 2026-11-13. Al cerrar uno, anotar la fecha y moverlo a "Resueltos".

## Abiertos

### Cuentas y cuota
- [ ] En Claude Code, `/status`: confirmar que usa la **cuenta Claude Pro** (no Console/API).
- [ ] Antigravity: confirmar **"Enable AI Credit Overages" apagado**.
- [ ] Google One: ver si Google AI Pro es **pago con descuento** o **prueba**. Antigravity solo da modelos Claude con suscripción que no sea de prueba.

### MCP
- [ ] Probar **FreeCAD MCP** con FreeCAD abierto (Start RPC Server) y `get_view`.
- [ ] Probar **Blender MCP** con Blender abierto (Start MCP Server) y `look`.
- [ ] Confirmar que **Gemini abre imágenes** generadas (render de OpenSCAD) en Antigravity.

### Reglamentos
- [ ] Subir PDF de **XRobo7s-2026** y **CNR_UNI_2026**, que Gemini extraiga los límites y que el usuario los verifique.
- [ ] Definir `competencias` y `variante_activa` de cada robot.

### Antigravity IDE: actualizador roto
- Error: "Failed to install Visual Studio Code update" / "CreateProcess falló; código 2".
- **Corrección de hoy:** el IDE **sí está en la ruta por defecto** (`%LOCALAPPDATA%\Programs\Antigravity IDE`), así que la causa no es "instalado fuera de la ruta" como suponía el plan viejo.
- winget ve: `Google.AntigravityIDE` 2.6.0 y `Google.Antigravity` (app) 2.29.0 → 2.31.2 disponible.
- [ ] Leer `%TEMP%\vscode-inno-updater-1793588938.log` y revisar la cuarentena de Malwarebytes.
- [ ] Si sigue: cerrar el IDE y reinstalar desde `antigravity.google/download` sin cambiar la ruta. (No urgente: el IDE funciona.)

### App de escritorio de Claude (opcional; el CLI cubre la necesidad)
- Error `0x80073D0D`: el paquete `Claude_1.30096.5.0_x64__pzs8sxrjxfjjc` quedó registrado en un volumen `D:\WindowsApps` desconectado tras unificar discos. Afecta también a `OpenAI.Codex` y `Microsoft.Office.OneNoteVirtualPrinter`.
- [ ] PowerShell como administrador: `Remove-AppxPackage -Package "Claude_1.30096.5.0_x64__pzs8sxrjxfjjc"`, comprobar con `Get-AppxPackage *Claude*` y reinstalar. Si falla, **no tocar el registro**: revisar juntos.
- Nota: el instalador no pudo quitar el servicio `CoworkVMService` (acceso denegado), un bloqueo reportado públicamente.

## Resueltos (2026-11-13)
- Claude Code CLI instalado y funcionando (v2.1.323); `ANTHROPIC_API_KEY` vacía.
- Software completo instalado (ver tabla en `AGENTS.md`).
- OpenSCAD exporta PNG y STL por CLI; Claude abre y describe las imágenes.
- Configuración MCP de Antigravity IDE: `~/.gemini/config/mcp_config.json` (era "no verificado").
- Los 4 MCP aprobados en Claude Code; OpenSCAD y KiCad probados de punta a punta.
- `agy -p` funciona desde la terminal y ve los 4 MCP.
- Extensión Claude Code instalada en Antigravity IDE (era "no verificado").
- Ruta del addon de FreeCAD 1.1: `%APPDATA%\FreeCAD\v1-1\Mod\FreeCADMCP` (era "no verificado").
