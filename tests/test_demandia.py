"""
Pruebas de DemandIA Fresh. Se pueden ejecutar de dos formas:

    python tests/test_demandia.py      (sin instalar nada extra)
    pytest                             (si tienes pytest)
"""

import sys
from dataclasses import replace
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agents import decidir_base, decidir_reactivo, decidir_utilidad  # noqa: E402
from config import ESTRATEGIAS, Parametros  # noqa: E402
from metrics import calcular_metricas_finales, calcular_resultado_dia  # noqa: E402
from simulation import (ejecutar_multiples_corridas, ejecutar_simulacion,  # noqa: E402
                        generar_demanda)

P = Parametros()


def test_formula_de_utilidad_a_mano():
    # produce 120, demanda 100: vende 100, desperdicia 20, no pierde ventas
    r = calcular_resultado_dia(120, 100, P)
    assert r["ventas"] == 100 and r["desperdicio"] == 20 and r["ventas_perdidas"] == 0
    assert r["utilidad"] == 100 * 15 - 120 * 7 - 20 * 2 - 0
    # produce 80, demanda 100: vende 80, pierde 20 ventas, no desperdicia
    r = calcular_resultado_dia(80, 100, P)
    assert r["ventas"] == 80 and r["desperdicio"] == 0 and r["ventas_perdidas"] == 20
    assert r["utilidad"] == 80 * 15 - 80 * 7 - 0 - 20 * 5


def test_misma_semilla_misma_demanda():
    assert np.array_equal(generar_demanda(P), generar_demanda(P))


def test_distinta_semilla_distinta_demanda():
    assert not np.array_equal(generar_demanda(P), generar_demanda(replace(P, seed=7)))


def test_demanda_valida():
    for seed in range(50):
        d = generar_demanda(replace(P, seed=seed))
        assert len(d) == P.dias and (d >= 0).all()


def test_misma_semilla_mismo_resultado():
    a = ejecutar_simulacion(P)
    b = ejecutar_simulacion(P)
    assert a.equals(b)


def test_las_tres_estrategias_ven_la_misma_demanda():
    df = ejecutar_simulacion(P)
    demandas = [df[df["estrategia"] == e]["demanda"].tolist() for e in ESTRATEGIAS]
    assert demandas[0] == demandas[1] == demandas[2] == generar_demanda(P).tolist()


def test_base_produce_siempre_lo_mismo():
    df = ejecutar_simulacion(P)
    assert (df[df["estrategia"] == "Base"]["produccion"] == P.produccion_base).all()
    assert decidir_base(P) == 100


def test_reglas_del_reactivo():
    assert decidir_reactivo(None, None, P) == 100          # primer día
    assert decidir_reactivo(100, 100, P) == 110            # 100% >= 95% -> sube
    assert decidir_reactivo(100, 95, P) == 110             # justo 95%   -> sube
    assert decidir_reactivo(100, 94, P) == 100             # 94%         -> mantiene
    assert decidir_reactivo(100, 76, P) == 100             # 76%         -> mantiene
    assert decidir_reactivo(100, 75, P) == 90              # justo 75%   -> baja
    assert decidir_reactivo(100, 50, P) == 90              # 50%         -> baja
    assert decidir_reactivo(180, 180, P) == 180            # respeta el máximo
    assert decidir_reactivo(40, 10, P) == 40               # respeta el mínimo
    assert decidir_reactivo(0, 0, P) >= 1                  # sin división entre cero


def test_utilidad_elige_el_maximo_esperado():
    historial = [90, 110, 100, 95, 105, 120, 100]
    elegida = decidir_utilidad(historial, P)
    assert P.min_produccion <= elegida <= P.max_produccion
    # ninguna otra cantidad candidata debe tener mayor utilidad esperada
    from agents import escenarios_de_demanda, utilidad_esperada
    esc = escenarios_de_demanda(historial, P)
    mejor = utilidad_esperada(elegida, esc, P)
    for q in range(P.min_produccion, P.max_produccion + 1, 5):
        assert utilidad_esperada(q, esc, P) <= mejor + 1e-9


def test_utilidad_sin_historia_no_falla():
    assert P.min_produccion <= decidir_utilidad([], P) <= P.max_produccion


def test_mas_costo_de_desperdicio_produce_menos():
    hist = [80, 120, 100, 90, 110, 130, 95]
    barato = decidir_utilidad(hist, P)
    caro = decidir_utilidad(hist, replace(P, costo_desperdicio=20.0))
    assert caro <= barato


def test_mas_penalizacion_produce_mas():
    hist = [80, 120, 100, 90, 110, 130, 95]
    normal = decidir_utilidad(hist, P)
    alta = decidir_utilidad(hist, replace(P, penalizacion_venta_perdida=20.0))
    assert alta >= normal


def test_sin_valores_negativos_ni_divisiones_por_cero():
    casos = [P, replace(P, demanda_media=20), replace(P, demanda_media=300),
             replace(P, produccion_base=0), replace(P, costo_produccion=0.0,
                                                    costo_desperdicio=0.0,
                                                    penalizacion_venta_perdida=0.0),
             replace(P, dias=7), replace(P, dias=90)]
    for caso in casos:
        df = ejecutar_simulacion(caso)
        columnas = ["demanda", "produccion", "ventas", "desperdicio", "ventas_perdidas"]
        assert (df[columnas] >= 0).all().all()
        assert (df["ventas"] <= df["demanda"]).all()
        assert (df["ventas"] <= df["produccion"]).all()
        m = calcular_metricas_finales(df)
        assert m["Nivel de servicio (%)"].between(0, 100).all()
        assert not m.isna().any().any()


def test_metricas_finales_cuadran_con_el_diario():
    df = ejecutar_simulacion(P)
    m = calcular_metricas_finales(df)
    for e in ESTRATEGIAS:
        d = df[df["estrategia"] == e]
        assert m.loc[e, "Utilidad neta acumulada"] == d["utilidad"].sum()
        assert d["utilidad_acumulada"].iloc[-1] == d["utilidad"].sum()
        assert m.loc[e, "Producción total"] == m.loc[e, "Unidades vendidas"] + m.loc[e, "Desperdicio total"]


def test_corridas_multiples():
    t = ejecutar_multiples_corridas(P, 5)
    assert abs(t["Corridas ganadas (%)"].sum() - 100) < 1e-9


if __name__ == "__main__":
    pruebas = [f for n, f in sorted(globals().items()) if n.startswith("test_")]
    for prueba in pruebas:
        prueba()
        print(f"OK  {prueba.__name__}")
    print(f"\n{len(pruebas)} pruebas pasaron.")
