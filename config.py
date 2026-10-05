"""
config.py
Parámetros y constantes de DemandIA Fresh.

Aquí vive TODO valor que se menciona en el README y en el informe
(umbrales del agente reactivo, ventana del agente de utilidad, etc.).
Si algo cambia, se cambia solo en este archivo.
"""

from dataclasses import dataclass

# Nombres de las tres estrategias (se usan en tablas y gráficos)
BASE = "Base"
REACTIVO = "Reactivo"
UTILIDAD = "Utilidad"
ESTRATEGIAS = (BASE, REACTIVO, UTILIDAD)

# --- Agente reactivo simple (reglas IF-THEN sobre el día anterior) ---
UMBRAL_SUBIR = 0.95    # vendió >= 95% de lo producido  -> produce 10% más
UMBRAL_BAJAR = 0.75    # vendió <= 75% de lo producido  -> produce 10% menos
AJUSTE_REACTIVO = 0.10

# --- Agente basado en utilidad ---
VENTANA_HISTORIAL = 7  # días recientes de demanda observada que usa el agente
PASO_CANDIDATOS = 5    # cantidades candidatas: mínimo, mínimo+5, ..., máximo

# --- Límites de producción (proporción de la demanda promedio) ---
# Con demanda promedio 100 equivalen a 40 y 180 unidades.
MIN_PRODUCCION_REL = 0.40
MAX_PRODUCCION_REL = 1.80

# --- Demanda sintética ---
# Efecto del día de la semana (el día 1 es lunes). Los factores suman 7.
FACTOR_DIA_SEMANA = (0.90, 0.95, 0.95, 1.00, 1.10, 1.20, 0.90)
RUIDO_DIARIO = 0.10        # variación aleatoria: desviación estándar de 10%
PROB_DIA_ALTO = 0.10       # probabilidad de que un día sea de demanda alta
FACTOR_DIA_ALTO = 1.30     # un día de demanda alta vende 30% más
# Cambio de nivel: desde la mitad del periodo la demanda sube 20% (p. ej. cambio
# de temporada o promoción sostenida). Una regla fija no se adapta a esto.
CAMBIO_NIVEL = 0.20


@dataclass(frozen=True)
class Parametros:
    """Parámetros editables desde la barra lateral de la app."""

    demanda_media: int = 100                  # demanda promedio (unidades/día)
    precio_venta: float = 15.0                # S/ por unidad vendida
    costo_produccion: float = 7.0             # S/ por unidad producida
    costo_desperdicio: float = 2.0            # S/ extra por unidad desperdiciada
    penalizacion_venta_perdida: float = 5.0   # S/ por unidad no vendida (quiebre)
    produccion_base: int = 100                # producción fija del modo base
    dias: int = 30                            # días simulados
    seed: int = 42                            # semilla aleatoria

    @property
    def min_produccion(self):
        """Producción mínima permitida a los agentes (nunca menos de 1)."""
        return max(1, round(MIN_PRODUCCION_REL * self.demanda_media))

    @property
    def max_produccion(self):
        """Producción máxima permitida a los agentes."""
        return max(self.min_produccion, round(MAX_PRODUCCION_REL * self.demanda_media))
