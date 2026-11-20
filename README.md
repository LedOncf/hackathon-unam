# 🏈 NFL Tactical Coach

![NFL Big Data Bowl](https://img.shields.io/badge/NFL-Big_Data_Bowl-013369?style=for-the-badge)
![Tracking Data](https://img.shields.io/badge/Tracking-122_Games_%7C_8%2C522_Plays-D50A0A?style=for-the-badge)
![Stack](https://img.shields.io/badge/Stack-Python_%2B_pandas_%7C_FastAPI_%2B_React_en_desarrollo-0F172A?style=for-the-badge)

> **¿Qué construimos?**
> Un pipeline de analítica en Python que procesa **8,522 jugadas de pase válidas y 122 partidos** (semanas 1 a 8 de 2021) de *player tracking* (~8.3 millones de filas, un archivo a la vez, 191 MB de RAM pico) y las combina con las etiquetas de PFF. Calcula métricas como la mordida de los *linebackers* (`lb_bite_yards`), el tiempo al lanzamiento (`time_to_throw`, a 10 cuadros por segundo), la distancia del rusher más cercano al QB (`min_rusher_dist_at_throw`) y la ventaja numérica en la línea (`protection_advantage`). Los resultados salen con intervalos de confianza al 95% en `outputs/COACH_INSIGHTS.md`. El dashboard (FastAPI + React) todavía no está construido.

### 📊 ¿Qué revela el análisis?
Todas las cifras son diferencias en la tasa de éxito (por down y distancia, sin EPA) con su IC95. Solo hay jugadas de pase y 8 semanas, así que las celdas con menos de 30 jugadas se marcan como no concluyentes.

* **Play Action:** mejora la tasa de éxito en **+6.8 pp** [4.3, 9.3] y rinde **+1.6 yardas** [1.1, 2.2] frente al mismo tipo de jugada sin él. El efecto se concentra en **Zona** (**+7.5 pp** [4.6, 10.5]); contra Hombre a Hombre es **+3.5 pp** [-1.6, 8.7], no distinguible de cero. Por cobertura destacan **Cover-2** (**+12.3 pp** [5.4, 19.1]), **Cover-0** (**+23.0 pp** [7.6, 36.6], con solo 50 jugadas de play action) y **Cover-3** (**+7.9 pp** [3.8, 11.9]). En **Red Zone** pierde **1.8 yardas** por jugada [-2.9, -0.7], aunque su tasa de éxito no cambia de forma detectable (-0.8 pp [-12.3, 11.5]).
* **Mordida de los linebackers:** el efecto del play action no crece de forma lineal con la mordida. Es mayor cuando los linebackers casi no avanzaron (menos de 0.10 yardas, **+13.8 pp** [6.0, 21.1]) o avanzaron mucho (1.16 yardas o más, **+10.4 pp** [4.1, 16.7]), y menor en los rangos intermedios.
* **Blitz:** enviar cinco o más *rushers* aumenta la presión en **+13.5 pp** [11.0, 15.9] (47.3% frente a 33.8%) y acorta el tiempo al lanzamiento en 0.21 s, pero **no mejora el éxito defensivo de forma detectable** (-1.8 pp [-4.2, 0.7] de éxito ofensivo). La excepción es la formación **Singleback**, donde el blitz reduce el éxito ofensivo en **9.4 pp** [3.2, 15.5] (45.6% frente a 55.0%). Contra **Empty** el blitz no castiga a la ofensiva: su éxito es de **50.9%** frente a 46.6% sin blitz (+4.3 pp [-2.3, 11.0], no concluyente).
* **Protección:** cuando los bloqueadores están en desventaja numérica (`protection_advantage` de -2 a -1, 122 jugadas) la presión llega a **61.5%** y el éxito ofensivo baja a **39.3%** [31.1, 48.2], frente a 47% o más en las demás categorías. Los intervalos se traslapan, así que es una señal y no una conclusión firme.

### 🎯 ¿Quién lo usaría?
Está pensado para **coordinadores ofensivos, coordinadores defensivos y equipos de estrategia** que quieran revisar decisiones situacionales (cuándo llamar play action, cuándo conviene el blitz) con intervalos de confianza y tamaños de muestra a la vista.
