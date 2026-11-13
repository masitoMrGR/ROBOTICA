"""Tests de check_reglamento.py con reglamentos y robots ficticios en una carpeta temporal.
Los números de aquí son de prueba, no de ningún reglamento real.
Correr: .venv\\Scripts\\python.exe -m pytest tools\\tests -q
"""
import sys
from pathlib import Path

import pytest
import trimesh
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import check_reglamento as cr  # noqa: E402


def _reg(root, cid, estado="verificado", **lim):
    d = root / "reglamentos" / cid
    d.mkdir(parents=True)
    cat = {k: {"valor": v, "fuente": "test p.1"} for k, v in lim.items()}
    (d / "reglamento.yaml").write_text(yaml.safe_dump(
        {"competencia": cid, "estado": estado, "categorias": {"cat": cat}}), encoding="utf-8")


def _robot(root, comps, masas=None, caja=None):
    r = root / "RobotTest"
    (r / "spec").mkdir(parents=True)
    (r / "build").mkdir()
    spec = {"nombre": "RobotTest", "competencias": [{"id": c, "categoria": "cat"} for c in comps],
            "variante_activa": "v1" if caja else None, "masas": masas or {}}
    (r / "spec" / "robot.yaml").write_text(yaml.safe_dump(spec), encoding="utf-8")
    if caja:
        trimesh.creation.box(extents=caja).export(r / "build" / "v1.stl")
    return r


def _estados(inf):
    return {n: e for n, e, _ in inf.chequeos}


def test_cumple(tmp_path):
    _reg(tmp_path, "A", largo_max_mm=100, ancho_max_mm=100, masa_max_g=500)
    r = _robot(tmp_path, ["A"], {"medida_g": 480}, caja=(98, 95, 40))
    inf = cr.revisar(r, tmp_path)
    assert inf.estado == cr.CUMPLE
    assert _estados(inf) == {"largo": cr.CUMPLE, "ancho": cr.CUMPLE, "masa": cr.CUMPLE}  # alto sin límite


def test_toma_el_limite_mas_estricto(tmp_path):
    _reg(tmp_path, "A", largo_max_mm=200, masa_max_g=500)
    _reg(tmp_path, "B", largo_max_mm=100, masa_max_g=1000)
    r = _robot(tmp_path, ["A", "B"], {"medida_g": 600}, caja=(150, 50, 30))
    inf = cr.revisar(r, tmp_path)
    assert inf.limites["largo_max_mm"].valor == 100 and inf.limites["largo_max_mm"].origen.startswith("B/")
    assert inf.limites["masa_max_g"].valor == 500 and inf.limites["masa_max_g"].origen.startswith("A/")
    assert _estados(inf) == {"largo": cr.NO_CUMPLE, "masa": cr.NO_CUMPLE}
    assert inf.estado == cr.NO_CUMPLE


def test_huella_independiente_de_orientacion(tmp_path):
    _reg(tmp_path, "A", largo_max_mm=100, ancho_max_mm=60)
    r = _robot(tmp_path, ["A"], caja=(55, 99, 20))  # girado 90° en XY
    assert _estados(cr.revisar(r, tmp_path)) == {"largo": cr.CUMPLE, "ancho": cr.CUMPLE}


def test_reglamento_pendiente_nunca_cumple(tmp_path):
    _reg(tmp_path, "A", estado="pendiente", largo_max_mm=100)
    r = _robot(tmp_path, ["A"], {"medida_g": 1}, caja=(10, 10, 10))
    inf = cr.revisar(r, tmp_path)
    assert inf.estado == cr.INDETERMINADO
    assert any("pendiente" in a for a in inf.avisos)
    assert cr.CUMPLE not in _estados(inf).values()


def test_pendiente_mas_verificado_sigue_indeterminado(tmp_path):
    _reg(tmp_path, "A", largo_max_mm=100)
    _reg(tmp_path, "B", estado="pendiente")
    r = _robot(tmp_path, ["A", "B"], caja=(50, 50, 50))
    assert cr.revisar(r, tmp_path).estado == cr.INDETERMINADO


def test_pendiente_no_oculta_un_incumplimiento(tmp_path):
    _reg(tmp_path, "A", largo_max_mm=100)
    _reg(tmp_path, "B", estado="pendiente")
    r = _robot(tmp_path, ["A", "B"], caja=(120, 50, 50))
    assert cr.revisar(r, tmp_path).estado == cr.NO_CUMPLE


def test_sin_competencias_es_indeterminado(tmp_path):
    r = _robot(tmp_path, [])
    inf = cr.revisar(r, tmp_path)
    assert inf.estado == cr.INDETERMINADO and inf.avisos


def test_falta_stl_o_masa_es_indeterminado(tmp_path):
    _reg(tmp_path, "A", largo_max_mm=100, masa_max_g=500)
    r = _robot(tmp_path, ["A"])  # sin STL ni masa
    inf = cr.revisar(r, tmp_path)
    assert inf.estado == cr.INDETERMINADO
    assert _estados(inf) == {"largo": cr.INDETERMINADO, "masa": cr.INDETERMINADO}


def test_masa_estimada_se_marca(tmp_path):
    _reg(tmp_path, "A", masa_max_g=500)
    r = _robot(tmp_path, ["A"], {"estimada_g": 450})
    inf = cr.revisar(r, tmp_path)
    assert inf.estado == cr.CUMPLE
    assert "ESTIMADA" in inf.chequeos[0][2]


def test_categoria_inexistente_avisa(tmp_path):
    _reg(tmp_path, "A", largo_max_mm=100)
    r = _robot(tmp_path, ["A"], caja=(50, 50, 50))
    spec = yaml.safe_load((r / "spec" / "robot.yaml").read_text(encoding="utf-8"))
    spec["competencias"][0]["categoria"] = "otra"
    (r / "spec" / "robot.yaml").write_text(yaml.safe_dump(spec), encoding="utf-8")
    inf = cr.revisar(r, tmp_path)
    assert inf.estado == cr.INDETERMINADO and any("otra" in a for a in inf.avisos)


@pytest.mark.parametrize("robot", sorted(p.name for p in cr.ROOT.iterdir() if p.is_dir() and p.name.startswith("Robot")))
def test_robots_reales_no_dan_cumple_con_reglamentos_pendientes(robot):
    """Mientras ningún reglamento real esté verificado, ningún robot del repo puede salir CUMPLE."""
    regs = list((cr.ROOT / "reglamentos").glob("*/reglamento.yaml"))
    if any(yaml.safe_load(p.read_text(encoding="utf-8")).get("estado") == "verificado" for p in regs):
        pytest.skip("ya hay reglamentos verificados")
    assert cr.revisar(cr.ROOT / robot).estado != cr.CUMPLE
