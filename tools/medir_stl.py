"""Mide un STL: caja envolvente, volumen, malla cerrada y masa estimada.

Uso: .venv\\Scripts\\python.exe tools\\medir_stl.py build\\pieza.stl [--densidad 1.24]   (g/cm³; PLA≈1.24, PETG≈1.27)
Sale con código 1 si la malla no es cerrada (sirve como check en scripts y tests).
"""
import argparse
import json
import sys

import trimesh


def medir(path, densidad=1.24):
    m = trimesh.load(path, force="mesh")
    partes = m.split(only_watertight=False)
    return {
        "archivo": str(path),
        "bbox_mm": [round(float(v), 3) for v in m.extents],
        "bbox_min": [round(float(v), 3) for v in m.bounds[0]],
        "bbox_max": [round(float(v), 3) for v in m.bounds[1]],
        "volumen_mm3": round(float(m.volume), 2),
        "area_mm2": round(float(m.area), 2),
        "cerrada": bool(m.is_watertight),
        "piezas_sueltas": len(partes),
        "centro_masa_mm": [round(float(v), 3) for v in m.center_mass],
        "masa_g_relleno_100": round(float(m.volume) / 1000 * densidad, 2),
    }


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("stl")
    ap.add_argument("--densidad", type=float, default=1.24)
    a = ap.parse_args()
    r = medir(a.stl, a.densidad)
    print(json.dumps(r, indent=2, ensure_ascii=False))
    sys.exit(0 if r["cerrada"] else 1)
