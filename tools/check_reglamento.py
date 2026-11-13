"""Compara un robot con los reglamentos de sus competencias.

Uso: .venv\\Scripts\\python.exe tools\\check_reglamento.py RobotXxx [--stl ruta.stl]

- Lee RobotXxx/spec/robot.yaml (competencias, variante_activa, masas).
- Carga reglamentos/<id>/reglamento.yaml de cada competencia y su categoría.
- Para cada límite toma el MÁS ESTRICTO (el menor) entre las competencias.
- Compara con el bbox del STL (por defecto RobotXxx/build/<variante_activa>.stl) y con la masa.

Resultado por chequeo y global: CUMPLE | NO_CUMPLE | INDETERMINADO.
Un reglamento con estado distinto de "verificado" NUNCA da CUMPLE: se avisa y el resultado es INDETERMINADO.
En un reglamento verificado, un límite null significa "no lo limita".
La huella (largo × ancho) se compara sin importar la orientación en XY; el alto es Z.

Código de salida: 0 CUMPLE, 1 NO_CUMPLE, 2 INDETERMINADO.
"""
from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
CUMPLE, NO_CUMPLE, INDETERMINADO = "CUMPLE", "NO_CUMPLE", "INDETERMINADO"
LIMITES = ("largo_max_mm", "ancho_max_mm", "alto_max_mm", "masa_max_g")


@dataclass
class Limite:
    valor: float | None = None
    origen: str | None = None  # "XRobo7s-2026/minisumo (fuente)"


@dataclass
class Informe:
    robot: str
    limites: dict[str, Limite] = field(default_factory=dict)
    chequeos: list[tuple[str, str, str]] = field(default_factory=list)  # (nombre, estado, detalle)
    avisos: list[str] = field(default_factory=list)

    @property
    def estado(self) -> str:
        estados = [c[1] for c in self.chequeos]
        if NO_CUMPLE in estados:
            return NO_CUMPLE
        if self.avisos or not estados or INDETERMINADO in estados:
            return INDETERMINADO
        return CUMPLE


def _leer_yaml(p: Path) -> dict:
    with open(p, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _valor(entrada) -> tuple[float | None, str | None]:
    if isinstance(entrada, dict):
        return entrada.get("valor"), entrada.get("fuente")
    return entrada, None


def limites_mas_estrictos(competencias: list[dict], root: Path, informe: Informe) -> dict[str, Limite]:
    lim = {k: Limite() for k in LIMITES}
    for comp in competencias:
        cid, cat = comp.get("id"), comp.get("categoria")
        ruta = root / "reglamentos" / str(cid) / "reglamento.yaml"
        if not ruta.exists():
            informe.avisos.append(f"{cid}: no existe {ruta.relative_to(root)}")
            continue
        reg = _leer_yaml(ruta)
        if reg.get("estado") != "verificado":
            informe.avisos.append(f"{cid}: reglamento con estado '{reg.get('estado')}', no se puede dar por cumplido")
            continue
        categoria = (reg.get("categorias") or {}).get(cat)
        if categoria is None:
            informe.avisos.append(f"{cid}: la categoría '{cat}' no está en el reglamento")
            continue
        for k in LIMITES:
            v, fuente = _valor(categoria.get(k))
            if v is not None and (lim[k].valor is None or v < lim[k].valor):
                lim[k] = Limite(float(v), f"{cid}/{cat}" + (f" ({fuente})" if fuente else ""))
    return lim


def _cmp(nombre: str, medido: float | None, limite: Limite, unidad: str, informe: Informe, nota: str = ""):
    if limite.valor is None:
        return  # sin límite en los reglamentos verificados
    if medido is None:
        informe.chequeos.append((nombre, INDETERMINADO, f"falta el dato medido (límite {limite.valor:g} {unidad}, {limite.origen})"))
        return
    estado = CUMPLE if medido <= limite.valor else NO_CUMPLE
    informe.chequeos.append((nombre, estado, f"{medido:.2f} {unidad} vs máx {limite.valor:g} {unidad} [{limite.origen}]{nota}"))


def bbox_stl(stl: Path) -> tuple[float, float, float]:
    import trimesh

    m = trimesh.load(stl, force="mesh")
    x, y, z = (float(v) for v in m.extents)
    return x, y, z


def revisar(robot_dir: Path, root: Path = ROOT, stl: Path | None = None) -> Informe:
    spec = _leer_yaml(robot_dir / "spec" / "robot.yaml")
    inf = Informe(robot=spec.get("nombre") or robot_dir.name)
    comps = spec.get("competencias") or []
    if not comps:
        inf.avisos.append("robot.yaml no tiene competencias asignadas")
        return inf
    inf.limites = limites_mas_estrictos(comps, root, inf)

    # Dimensiones
    if stl is None and spec.get("variante_activa"):
        stl = robot_dir / "build" / f"{spec['variante_activa']}.stl"
    dims = None
    hay_limite_dim = any(inf.limites[k].valor is not None for k in LIMITES[:3])
    if not hay_limite_dim:
        pass  # nada que comparar; si el STL falta, _cmp no se queja
    elif stl is None:
        inf.avisos.append("sin variante_activa ni --stl: no se pueden revisar dimensiones")
    elif not Path(stl).exists():
        inf.avisos.append(f"no existe el STL {stl}")
    else:
        dims = bbox_stl(Path(stl))
    huella = sorted(dims[:2], reverse=True) if dims else [None, None]
    _cmp("largo", huella[0], inf.limites["largo_max_mm"], "mm", inf)
    _cmp("ancho", huella[1], inf.limites["ancho_max_mm"], "mm", inf)
    _cmp("alto", dims[2] if dims else None, inf.limites["alto_max_mm"], "mm", inf)

    # Masa: manda la medida; si solo hay estimada se avisa
    masas = spec.get("masas") or {}
    masa, nota = masas.get("medida_g"), " (medida)"
    if masa is None and masas.get("estimada_g") is not None:
        masa, nota = masas["estimada_g"], " (ESTIMADA, confirmar con balanza)"
    _cmp("masa", float(masa) if masa is not None else None, inf.limites["masa_max_g"], "g", inf, nota)
    return inf


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("robot", help="carpeta del robot, p.ej. RobotMinisumoBTRC")
    ap.add_argument("--stl", type=Path)
    a = ap.parse_args(argv)
    robot_dir = Path(a.robot)
    if not robot_dir.is_absolute():
        robot_dir = ROOT / robot_dir
    inf = revisar(robot_dir, ROOT, a.stl)
    print(f"Robot: {inf.robot}")
    for av in inf.avisos:
        print(f"  AVISO: {av}")
    for nombre, estado, detalle in inf.chequeos:
        print(f"  {estado:<13} {nombre:<6} {detalle}")
    print(f"RESULTADO: {inf.estado}")
    return {CUMPLE: 0, NO_CUMPLE: 1, INDETERMINADO: 2}[inf.estado]


if __name__ == "__main__":
    sys.exit(main())
