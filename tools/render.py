"""Plan B sin MCP: renderiza un .scad a PNG (cámara fija) y exporta STL con OpenSCAD CLI.

Uso: .venv\\Scripts\\python.exe tools\\render.py RobotXxx\\cad\\pieza.scad [--vista iso|top|front|right] [-D var=valor ...]
Salida: RobotXxx\\build\\<nombre>_<vista>.png y RobotXxx\\build\\<nombre>.stl
(Un .scad de componentes\\scad\\ sale en componentes\\build\\.)
"""
import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OPENSCAD = shutil.which("openscad") or os.path.expandvars(r"%LOCALAPPDATA%\Programs\OpenSCAD\openscad.com")
# --camera=rotx,roty,rotz,dist ignorado con --viewall; solo fija la orientación
VISTAS = {"iso": "0,0,0,55,0,25,0", "top": "0,0,0,0,0,0,0", "front": "0,0,0,90,0,0,0", "right": "0,0,0,90,0,90,0"}


def carpeta_build(scad: Path, root: Path = ROOT) -> Path:
    """build/ del robot (o de componentes/) que contiene el .scad."""
    try:
        top = scad.resolve().relative_to(root.resolve()).parts[0]
    except (ValueError, IndexError):
        sys.exit(f"{scad} está fuera de {root}")
    if top.startswith("Robot") or top == "componentes":
        return root / top / "build"
    sys.exit(f"{scad} no está dentro de una carpeta RobotXxx/ ni de componentes/")


def run(args):
    r = subprocess.run([OPENSCAD, "--backend=manifold", *args], capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"OpenSCAD falló:\n{r.stderr}")
    return r.stderr


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scad")
    ap.add_argument("--vista", default="iso", choices=VISTAS)
    ap.add_argument("-D", action="append", default=[], help="override de variable, p.ej. -D ancho=98")
    a = ap.parse_args()
    scad = Path(a.scad).resolve()
    out = carpeta_build(scad)
    out.mkdir(exist_ok=True)
    defs = [x for d in a.D for x in ("-D", d)]
    png = out / f"{scad.stem}_{a.vista}.png"
    stl = out / f"{scad.stem}.stl"
    run([*defs, "--autocenter", "--viewall", "--imgsize=1024,768", "--colorscheme=Tomorrow",
         "--projection=o", "--view=axes,scales", f"--camera={VISTAS[a.vista]}", "-o", str(png), str(scad)])
    log = run([*defs, "-o", str(stl), str(scad)])
    for line in log.splitlines():
        if any(k in line for k in ("WARNING", "ERROR", "ECHO", "Status")):
            print(line)
    print(f"PNG: {png}\nSTL: {stl}")


if __name__ == "__main__":
    main()
