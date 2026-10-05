# DemandIA Fresh — Equipo 03

*Inteligencia para producir lo necesario, vender más y desperdiciar menos.* Curso Agentes Inteligentes, USIL 2026-2 · Trabajo Final — Avance 1.

## Problema y quién lo sufre

Cafeterías, panaderías y pequeños negocios de alimentos perecibles deben decidir cada día cuánto producir **antes de conocer la demanda real**: si producen de más, desperdician y pierden dinero; si producen de menos, pierden ventas y clientes.

## Modo base

Produce siempre la misma cantidad: **100 unidades/día**. No usa historia ni se adapta.

## Técnicas comparadas

Las tres estrategias enfrentan **exactamente la misma demanda simulada** (sin Machine Learning).

- **Agente reactivo simple:** mira solo el día anterior. Si vendió ≥ 95 % de lo producido, produce 10 % más; si vendió ≤ 75 %, produce 10 % menos; en otro caso mantiene (límites 40–180).
- **Agente basado en utilidad:** toma la demanda de los últimos 7 días como escenarios, prueba cantidades de 40 a 180 (de 5 en 5) y elige la de mayor utilidad esperada.

## Métrica principal

**Utilidad neta acumulada** = Σ (ventas × precio − producción × costo − desperdicio × costo de desperdicio − ventas perdidas × penalización). También se miden desperdicio, ventas perdidas y nivel de servicio.

## Resultados

Simulación real con valores por defecto (30 días, semilla 42, demanda promedio 100, precio S/ 15, costo S/ 7, desperdicio S/ 2, penalización S/ 5):

| Estrategia | Utilidad neta acumulada | Desperdicio | Ventas perdidas | Nivel de servicio | Producción total |
|---|---:|---:|---:|---:|---:|
| Base | S/ 20,682 | 79 | 395 | 88.1 % | 3,000 |
| Reactivo | S/ 21,619 | 505 | 28 | 99.2 % | 3,793 |
| **Utilidad (ganador)** | **S/ 22,488** | 186 | 182 | 94.5 % | 3,320 |

Datos sintéticos; detalles, validación con 30 semillas y limitaciones en el informe y en `GUIA_DEFENSA_DEMANDIA.md`.

## Cómo ejecutar localmente

Python 3.10+. Crear y activar el entorno virtual:

```bash
python -m venv venv
```

| Terminal | Activar |
|---|---|
| Git Bash | `source venv/Scripts/activate` |
| PowerShell | `.\venv\Scripts\Activate.ps1` |
| CMD | `venv\Scripts\activate` |
| macOS / Linux | `source venv/bin/activate` |

```bash
pip install -r requirements.txt
streamlit run app.py
```

Alternativa si Streamlit no es reconocido: `python -m streamlit run app.py`

## Demo online y repositorio

- Demo: https://demandia-fresh-equipo03.streamlit.app
- Repositorio: https://github.com/TiagoVald09/AI-2026-2-Equipo03-DemandIA-Fresh

## Uso de IA

Claude Code fue utilizado como asistente para generar, integrar, revisar y depurar parte del código y la documentación del proyecto. El equipo revisó, probó y comprende la lógica implementada.

## Equipo y roles

- **Santiago Valdivia:** integración, configuración, métricas y documentación.
- **Fabian Cristobal:** interfaz Streamlit y experiencia de usuario.
- **Jesus Camargo:** simulación y generación de demanda.
- **Said Taravay:** lógica y validación de agentes.

Los cuatro integrantes realizaron aportes mediante commits y Pull Requests propios en el repositorio.
