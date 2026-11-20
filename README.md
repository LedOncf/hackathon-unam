# 🏈 NFL Tactical Coach Simulator

![NFL Big Data Bowl](https://img.shields.io/badge/NFL-Big_Data_Bowl-013369?style=for-the-badge)
![Tracking Data](https://img.shields.io/badge/Tracking-122_Games_%7C_8%2C522_Plays-D50A0A?style=for-the-badge)
![Stack](https://img.shields.io/badge/Stack-FastAPI_%2B_React_%2B_Recharts-0F172A?style=for-the-badge)

> **¿Qué construimos?**
> Construimos **NFL Tactical Coach Simulator**, un motor de analítica avanzada y una aplicación web interactiva que procesan **8,522 jugadas válidas y 122 partidos** de *player tracking* (10 Hz) para transformar millones de coordenadas en métricas físicas como la mordida de los *linebackers* (`lb_bite_yards`), el tiempo al lanzamiento (`time_to_throw`) y la ventaja numérica en la línea (`protection_advantage`).

### 📊 ¿Qué revela el análisis?
* **El mito del Play Action:** El análisis revela que el *Play Action* es significativamente más efectivo contra coberturas en **Zona** (**+7.53 puntos porcentuales** de éxito, y hasta **+12.35 pp** contra *Cover-2*) que contra Hombre a Hombre, pero fracasa en **Red Zone** donde pierde **1.80 yardas** por jugada.
* **El espejismo del Blitz:** Asimismo, descubre el espejismo del *blitz*: enviar cinco o más *rushers* incrementa la presión (**+13.5 pp**) pero no mejora el éxito defensivo global salvo que exista desventaja numérica en la línea o se enfrente una formación *Singleback*, mientras que las ofensivas en *Empty* lo castigan con un **50.9% de éxito**.

### 🎯 ¿Quién lo usaría?
Esta herramienta está diseñada para **coordinadores ofensivos, coordinadores defensivos y equipos de estrategia de la NFL** que buscan optimizar su plan de juego semanal y tomar mejores decisiones situacionales durante el partido respaldadas por intervalos de confianza al 95%.
