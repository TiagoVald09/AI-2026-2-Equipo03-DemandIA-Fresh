"""
simulation.py
Genera la demanda sintética y enfrenta las tres estrategias a la MISMA demanda.
"""

from dataclasses import replace

import numpy as np
import pandas as pd

from agents import decidir_base, decidir_reactivo, decidir_utilidad
from config import (BASE, CAMBIO_NIVEL, ESTRATEGIAS, FACTOR_DIA_ALTO,
                    FACTOR_DIA_SEMANA, PROB_DIA_ALTO, REACTIVO, RUIDO_DIARIO,
                    UTILIDAD)
from metrics import calcular_resultado_dia, resumir_corridas


def generar_demanda(p):
    """Demanda real de `p.dias` días (sin Machine Learning).

    demanda = demanda_media * efecto_día_semana * ruido * (día alto: +30%)
    y desde la mitad del periodo un cambio de nivel de +20%.
    La semilla hace que el resultado sea reproducible.
    """
    rng = np.random.default_rng(p.seed)
    dias = np.arange(p.dias)

    efecto_dia = np.array(FACTOR_DIA_SEMANA)[dias % 7]
    ruido = rng.normal(1.0, RUIDO_DIARIO, p.dias)
    es_dia_alto = rng.random(p.dias) < PROB_DIA_ALTO
    factor_alto = np.where(es_dia_alto, FACTOR_DIA_ALTO, 1.0)
    nivel = np.where(dias >= p.dias // 2, 1 + CAMBIO_NIVEL, 1.0)

    demanda = p.demanda_media * efecto_dia * ruido * factor_alto * nivel
    return np.clip(np.round(demanda), 0, None).astype(int)  # nunca negativa


def ejecutar_simulacion(p, demanda=None):
    """Simula `p.dias` días con las tres estrategias y devuelve un DataFrame
    con una fila por (estrategia, día).

    Las tres usan EXACTAMENTE la misma demanda. Cada una decide la producción
    ANTES de ver la demanda del día; después el entorno revela la demanda y se
    calculan los resultados.
    """
    if demanda is None:
        demanda = generar_demanda(p)

    ultima = {e: {"produccion": None, "ventas": None} for e in ESTRATEGIAS}
    demanda_observada = []   # demandas de días anteriores (las ve el agente de utilidad)
    filas = []

    for dia, demanda_real in enumerate(demanda, start=1):
        # --- 1) Cada estrategia decide sin conocer la demanda de hoy ---
        produccion = {
            BASE: decidir_base(p),
            REACTIVO: decidir_reactivo(ultima[REACTIVO]["produccion"],
                                       ultima[REACTIVO]["ventas"], p),
            UTILIDAD: decidir_utilidad(demanda_observada, p),
        }

        # --- 2) Se revela la demanda y se calcula el resultado del día ---
        for estrategia in ESTRATEGIAS:
            r = calcular_resultado_dia(produccion[estrategia], int(demanda_real), p)
            ultima[estrategia] = {"produccion": r["produccion"], "ventas": r["ventas"]}
            filas.append({"dia": dia, "estrategia": estrategia, **r})

        demanda_observada.append(int(demanda_real))

    df = pd.DataFrame(filas)
    df["utilidad_acumulada"] = df.groupby("estrategia")["utilidad"].cumsum()
    return df

    # Mantener este orden de generación aleatoria permite reproducir
    # exactamente el mismo escenario cuando se utiliza la misma semilla.
def ejecutar_multiples_corridas(p, n_corridas=30):
    """Repite la comparación con semillas consecutivas (seed, seed+1, ...).

    Sirve para ver si el resultado depende de una sola secuencia de demanda.
    Devuelve la tabla resumen por estrategia.
    """
      if n_corridas < 1:
        raise ValueError("El número de corridas debe ser al menos 1.")
          
    filas = []
    for i in range(n_corridas):
        p_i = replace(p, seed=p.seed + i)
        df = ejecutar_simulacion(p_i)
        totales = df.groupby("estrategia")["utilidad"].sum()
        for estrategia in ESTRATEGIAS:
            filas.append({"seed": p_i.seed, "estrategia": estrategia,
                          "utilidad_total": totales[estrategia]})
    return resumir_corridas(pd.DataFrame(filas))
