Lee y sigue `AGENTS.md` (reglas compartidas del proyecto).

## Específico de Antigravity (Gemini)
- Rol: leer, extraer y auditar (ver la tabla "Quién edita qué" de `AGENTS.md`).
- Extraes a `reglamentos/*/reglamento.yaml`, `componentes/componentes.yaml` y `RobotXxx/spec/robot.yaml`, siempre con fuente (archivo + página). Nunca cambies `estado` a `verificado`: eso lo hace el usuario.
- Al auditar busca números que violen la física y saltos lógicos. No edites `cad/`, `sim/`, `firmware/`, `pcb/` ni `tools/`: deja la auditoría en `RobotXxx/reports/auditoria-<fecha>.md`.
- Trabaja solo en el robot que te indiquen.
