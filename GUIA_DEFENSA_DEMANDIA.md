# Guía de defensa — DemandIA Fresh

Guía para la sustentación oral. Los números son los de la simulación por defecto (30 días, semilla 42).

## 1. Explicación sencilla del proyecto

Un negocio de alimentos perecibles tiene que decidir cuánto producir **antes** de saber cuánta gente va a comprar. Si produce de más, bota producto; si produce de menos, pierde ventas. Hicimos un simulador donde tres formas de decidir (base, reactivo, utilidad) se enfrentan a la **misma demanda** y vemos cuál gana más dinero.

## 2. Qué es el modo base
Produce siempre lo mismo (100 unidades). No percibe nada ni se adapta. Es la referencia.

## 3. Qué es el agente reactivo
Un agente de reglas condición-acción (IF-THEN). Solo mira el día anterior: si vendió ≥ 95 % de lo producido, sube 10 %; si vendió ≤ 75 %, baja 10 %; si no, mantiene.

## 4. Qué es el agente de utilidad
Un agente que prueba varias cantidades posibles (40, 45, …, 180), estima cuánto ganaría con cada una y elige la de mayor utilidad esperada.

## 5. Qué percibe cada uno
| Estrategia | Percepción |
|---|---|
| Base | Nada |
| Reactivo | Producción y ventas del día anterior |
| Utilidad | Demandas de los últimos 7 días (y los parámetros económicos) |

## 6. Qué acción realiza
Los tres hacen lo mismo: **decidir cuántas unidades producir mañana**.

## 7. Función de utilidad
```
Utilidad = ventas × precio − producción × costo_producción
           − desperdicio × costo_desperdicio − ventas_perdidas × penalización
```
Está en `calcular_resultado_dia()` (`metrics.py:11`). El agente la usa para estimar y la simulación para medir.

## 8. Por qué la misma demanda para todos
`generar_demanda()` se llama **una sola vez** en `ejecutar_simulacion()` y la lista resultante se recorre día a día para los tres métodos.

## 9. Por qué la comparación es justa
La comparación es justa porque los tres métodos enfrentan exactamente la misma secuencia de demanda y los mismos parámetros económicos. Cada estrategia decide sin conocer la demanda del día y la única diferencia es su mecanismo de decisión.

## 10. Qué métrica determina al ganador
La **utilidad neta acumulada**. Desperdicio, ventas perdidas y nivel de servicio explican el resultado, pero no deciden.

## 11. Si aumenta el costo de desperdicio
El agente de utilidad produce menos. Con costo S/ 2 → S/ 8, su producción media bajó de 110.7 a 105.7 unidades.

## 12. Si aumenta la penalización por venta perdida
Produce más. Con penalización S/ 5 → S/ 15, subió de 110.7 a 116.8. En ese caso el reactivo termina ganando (S/ 21,339 vs S/ 20,635).

## 13. Si cambia la semilla
Cambia la secuencia de demanda y por tanto los números, pero no la lógica. Misma semilla = mismo resultado exacto. En 30 semillas (42–71) el agente de utilidad ganó 93.3 %.

## 14. Por qué no usamos ML todavía
El Avance 1 pide comparar un modo base con técnicas del Bloque 1 (reglas y utilidad). El ML se incorporará en la Parte 2 para predecir la demanda y alimentar al agente de utilidad.

## 15. Qué código fue generado con IA
Claude Code ayudó a generar, integrar, revisar y depurar el código y el informe; el equipo lo revisó y probó. [PENDIENTE: el equipo debe precisar qué partes escribió o modificó cada integrante.]

## 16. Dónde está cada función importante
| Qué | Archivo | Línea |
|---|---|---|
| Modo base: `decidir_base()` | `agents.py` | 25 |
| Reactivo: `decidir_reactivo()` | `agents.py` | 32 |
| Utilidad: `decidir_utilidad()` | `agents.py` | 78 |
| Escenarios de demanda del agente | `agents.py` | 58 |
| Utilidad esperada de una cantidad | `agents.py` | 71 |
| **Función de utilidad** `calcular_resultado_dia()` | `metrics.py` | 11 |
| Métricas finales `calcular_metricas_finales()` | `metrics.py` | 45 |
| Demanda: `generar_demanda()` | `simulation.py` | 18 |
| Simulación: `ejecutar_simulacion()` | `simulation.py` | 38 |
| Umbrales 95 % / 75 %, ventana de 7 días, cambio de nivel | `config.py` | `UMBRAL_*`, `VENTANA_HISTORIAL`, `CAMBIO_NIVEL` |
| Interfaz | `app.py` | — |

(Las líneas pueden moverse si se edita el código; buscar por nombre de función.)

---

## 15 preguntas posibles del profesor

1. **¿Dónde percibe el agente?** En los argumentos de su función: el reactivo recibe producción y ventas de ayer; el de utilidad, el historial de demanda.
2. **¿Dónde actúa?** Decide la cantidad a producir del día; la simulación la aplica.
3. **¿Por qué el reactivo es "simple"?** Solo asocia una condición actual (porcentaje vendido de ayer) con una acción; no proyecta ni compara alternativas.
4. **¿Por qué el de utilidad es distinto?** Compara muchas acciones con una medida numérica y elige la que maximiza el resultado esperado.
5. **¿Cuál es la métrica principal?** Utilidad neta acumulada.
6. **¿Quién ganó y por qué?** El agente de utilidad (S/ 22,488 vs S/ 21,619 reactivo y S/ 20,682 base). Equilibra desperdicio (186) y ventas perdidas (182); el base pierde ventas (395) y el reactivo desperdicia mucho (505).
7. **¿El reactivo tiene mejor servicio, por qué no gana?** Sí, 99.2 %, pero a costa de 505 unidades desperdiciadas y mayor costo de producción. La utilidad pondera todo.
8. **¿Cuándo ganaría el modo base?** Cuando la demanda es estable cerca de su producción fija. Sin el cambio de nivel, el base ganó 76.7 % de las corridas.
9. **¿Los datos son reales?** No, son sintéticos: demanda promedio × día de la semana × ruido × días altos × cambio de nivel de +20 % a mitad del periodo.
10. **¿Cómo evitan que la demanda sea negativa?** Se redondea y se recorta en 0 en `generar_demanda()`; hay pruebas automáticas.
11. **¿Qué pasa el primer día?** El reactivo parte de la producción base; el de utilidad usa la demanda promedio configurada como creencia inicial.
12. **¿Por qué ventana de 7 días?** Cubre una semana completa de efecto por día y reacciona rápido a cambios; es un parámetro en `config.py`.
13. **¿Por qué 95 % y 75 %?** Son umbrales de diseño simples: vender casi todo sugiere producir más; vender poco sugiere producir menos. Se pueden cambiar en `config.py`.
14. **¿Cómo comprueban que es reproducible?** Con `np.random.default_rng(semilla)`; hay una prueba que corre dos veces y compara los DataFrames.
15. **¿Qué viene en la Parte 2?** Machine Learning (regresión, KNN, árboles) para predecir la demanda y que el agente de utilidad la use, midiendo MAE e impacto económico. No está implementado.

## Cambios en vivo para practicar
- Costo de desperdicio S/ 2 → S/ 8: el agente de utilidad produce menos.
- Penalización S/ 5 → S/ 15: produce más (y el reactivo pasa a ganar).
- Demanda promedio 100 → 130 con producción base 100: el base pierde muchas ventas (servicio ≈ 70 %).
- Cambiar la semilla: cambian los números, no la lógica.
- Producción base 100 → 120: probar y explicar qué ocurre con desperdicio y ventas perdidas.

Recuerden pulsar **🚀 Ejecutar simulación** tras cambiar parámetros.
