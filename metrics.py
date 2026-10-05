"""
metrics.py
Cálculo de resultados diarios, métricas finales y validación con varias semillas.
"""

import pandas as pd

from config import ESTRATEGIAS


def calcular_resultado_dia(produccion, demanda, p):
    """Resultado económico de UN día para una producción y una demanda dadas.

    >>> AQUÍ ESTÁ LA FUNCIÓN DE UTILIDAD (la usan la simulación y el agente) <<<
    """
    ventas = min(produccion, demanda)
    desperdicio = max(produccion - demanda, 0)
    ventas_perdidas = max(demanda - produccion, 0)

    ingresos = ventas * p.precio_venta
    costo_produccion = produccion * p.costo_produccion
    costo_desperdicio_total = desperdicio * p.costo_desperdicio
    penalizacion_stockout = ventas_perdidas * p.penalizacion_venta_perdida

    # utilidad = ingresos - costo de producción - costo de desperdicio - penalización
    utilidad = (ingresos
                - costo_produccion
                - costo_desperdicio_total
                - penalizacion_stockout)

    return {
        "demanda": demanda,
        "produccion": produccion,
        "ventas": ventas,
        "desperdicio": desperdicio,
        "ventas_perdidas": ventas_perdidas,
        "ingresos": ingresos,
        "costo_produccion": costo_produccion,
        "costo_desperdicio_total": costo_desperdicio_total,
        "penalizacion_stockout": penalizacion_stockout,
        "utilidad": utilidad,
    }


def calcular_metricas_finales(df):
    """Tabla con una fila por estrategia a partir del DataFrame diario.

    Métrica principal: Utilidad neta acumulada.
    Nivel de servicio = ventas totales / demanda total * 100.
    """
    filas = []
    for estrategia in ESTRATEGIAS:
        d = df[df["estrategia"] == estrategia]
        demanda_total = d["demanda"].sum()
        ventas_totales = d["ventas"].sum()
        # Si no hubiera demanda, no hubo clientes sin atender: servicio 100%
        servicio = ventas_totales / demanda_total * 100 if demanda_total > 0 else 100.0
        filas.append({
            "Estrategia": estrategia,
            "Utilidad neta acumulada": d["utilidad"].sum(),
            "Unidades vendidas": ventas_totales,
            "Producción total": d["produccion"].sum(),
            "Desperdicio total": d["desperdicio"].sum(),
            "Ventas perdidas": d["ventas_perdidas"].sum(),
            "Nivel de servicio (%)": servicio,
        })
    return pd.DataFrame(filas).set_index("Estrategia")


def estrategia_ganadora(metricas):
    """La estrategia ganadora es la de mayor utilidad neta acumulada."""
    return metricas["Utilidad neta acumulada"].idxmax()


def resumir_corridas(df_corridas):
    """Resume varias corridas (una por semilla): utilidad media, desviación,
    mínimo, máximo y porcentaje de corridas ganadas por cada estrategia."""
    por_estrategia = df_corridas.groupby("estrategia")["utilidad_total"]
    tabla = pd.DataFrame({
        "Utilidad media": por_estrategia.mean(),
        "Desviación": por_estrategia.std(),
        "Mínima": por_estrategia.min(),
        "Máxima": por_estrategia.max(),
    }).reindex(list(ESTRATEGIAS))

    # Ganador de cada semilla = estrategia con mayor utilidad total
    ganadores = df_corridas.loc[
        df_corridas.groupby("seed")["utilidad_total"].idxmax(), "estrategia"]
    n_corridas = df_corridas["seed"].nunique()
    victorias = ganadores.value_counts().reindex(list(ESTRATEGIAS), fill_value=0)
    tabla["Corridas ganadas (%)"] = victorias / n_corridas * 100
    tabla.index.name = "Estrategia"
    return tabla
