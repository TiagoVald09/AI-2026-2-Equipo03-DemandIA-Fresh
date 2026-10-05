"""
agents.py
Las tres formas de decidir cuánto producir ANTES de conocer la demanda del día:

    decidir_base()      -> producción fija
    decidir_reactivo()  -> reglas IF-THEN sobre el día anterior
    decidir_utilidad()  -> prueba cantidades y elige la de mayor utilidad esperada

Ninguna usa Machine Learning.
"""

from config import (AJUSTE_REACTIVO, PASO_CANDIDATOS, UMBRAL_BAJAR, UMBRAL_SUBIR,
                    VENTANA_HISTORIAL)
from metrics import calcular_resultado_dia


def limitar_produccion(cantidad, p):
    """Redondea y acota la producción al rango permitido [mínimo, máximo]."""
    return int(round(min(max(cantidad, p.min_produccion), p.max_produccion)))


# ---------------------------------------------------------------------------
# 1) MODO BASE: no es inteligente, siempre produce lo mismo
# ---------------------------------------------------------------------------
def decidir_base(p):
    return int(p.produccion_base)


# ---------------------------------------------------------------------------
# 2) AGENTE REACTIVO SIMPLE: percibe solo el día anterior
# ---------------------------------------------------------------------------
def decidir_reactivo(produccion_ayer, ventas_ayer, p):
    """Reglas condición-acción sobre el porcentaje vendido ayer.

    Si vendió >= 95% de lo producido -> produce 10% más
    Si vendió <= 75% de lo producido -> produce 10% menos
    En otro caso                     -> mantiene
    El primer día (sin "ayer") parte de la producción base.
    """
    if produccion_ayer is None:
        return limitar_produccion(p.produccion_base, p)

    porcentaje_vendido = ventas_ayer / produccion_ayer if produccion_ayer > 0 else 1.0

    if porcentaje_vendido >= UMBRAL_SUBIR:
        nueva = produccion_ayer * (1 + AJUSTE_REACTIVO)
    elif porcentaje_vendido <= UMBRAL_BAJAR:
        nueva = produccion_ayer * (1 - AJUSTE_REACTIVO)
    else:
        nueva = produccion_ayer

    return limitar_produccion(nueva, p)


# ---------------------------------------------------------------------------
# 3) AGENTE BASADO EN UTILIDAD: prueba acciones y maximiza utilidad esperada
# ---------------------------------------------------------------------------
def escenarios_de_demanda(historial_demanda, p):
    """Demandas posibles para mañana: las de los últimos 7 días observados.

    Los últimos días observados se utilizan como escenarios empíricos de
    demanda igualmente probables.
    Si aún hay menos de 7 días de historia, el agente completa los que faltan
    con la demanda promedio configurada (su creencia inicial).
    """
    recientes = list(historial_demanda)[-VENTANA_HISTORIAL:]
    faltantes = VENTANA_HISTORIAL - len(recientes)
    return [p.demanda_media] * faltantes + recientes


def utilidad_esperada(cantidad, escenarios, p):
    """Promedio de la utilidad de producir `cantidad` en cada escenario."""
    utilidades = [calcular_resultado_dia(cantidad, demanda, p)["utilidad"]
                  for demanda in escenarios]
    return sum(utilidades) / len(utilidades)


def decidir_utilidad(historial_demanda, p):
    """Elige la cantidad candidata con MAYOR utilidad esperada."""
    escenarios = escenarios_de_demanda(historial_demanda, p)

    mejor_cantidad, mejor_valor = None, float("-inf")
    for cantidad in range(p.min_produccion, p.max_produccion + 1, PASO_CANDIDATOS):
        valor = utilidad_esperada(cantidad, escenarios, p)
        if valor > mejor_valor:
            mejor_cantidad, mejor_valor = cantidad, valor
    return int(mejor_cantidad)
