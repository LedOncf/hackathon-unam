# VERIFICATION_RUN

Archivos de tracking: 122. Muestra detallada: 10 archivos (2021090900, 2021091212, 2021091910, 2021092607, 2021100305, 2021101002, 2021101700, 2021102100, 2021103100, 2021110100).

## 1. Formato crudo de `time` (los archivos completos, un archivo a la vez)

- Archivos leídos: 122; con error: 0.
- Filas: 8,314,178; frames distintos (jugada, frameId): 361,486; jugadas: 8,557.
- Ejemplos de valores crudos: ['2021-09-10T00:26:31Z', '2021-09-10T00:26:32Z', '2021-09-10T00:26:33Z'].
- Cadenas `time` distintas: 43,828. Sin fracción de segundo: 43,828 (100.00%). Con fracción: 0. No parseables: 0.
- Frames cuyo `time` cae en segundo entero: 361,486 de 361,486 (100.00%).
- Pares de frames consecutivos: 352,929. Con dt = 0 s: 317,665 (90.01%). Con dt < 0: 0.
- Valores de dt entre frames consecutivos (s: pares): 0.0: 317665, 1.0: 35264.
- Saltos de `frameId` entre frames consecutivos (salto: pares): 1: 352929.
- Frames por marca de tiempo distinta dentro de una jugada (frames: casos): 10: 28438, 8: 1789, 9: 1754, 1: 1752, 3: 1744, 2: 1726, 7: 1707, 6: 1680, 5: 1619, 4: 1612.

**Conclusión sobre `time`:** 
el formato es homogéneo (`YYYY-MM-DDTHH:MM:SSZ`, sin fracciones) y el parseo no pierde información. La columna `time` tiene resolución real de 1 s: cada marca de tiempo se repite en varios frames consecutivos (ver frames por marca). No es un problema de parseo; es una propiedad de los datos. Por eso `time_to_throw` se calcula con `frameId` a 10 Hz ((res − snap)/10) y `frame_dt_ok` exige `frameId` sin saltos de 1 y `time` no decreciente (D12).

## 2. Valores de `team` (muestra)

- Valores: TB: 79948, NYG: 71060, CIN: 66968, CLE: 62216, DEN: 62029, ATL: 59774, DAL: 44308, JAX: 38577, MIA: 38577, KC: 36498, GB: 35090, MIN: 34749, PIT: 31878, football: 31173, CAR: 24134.
- Resultado: abreviaturas de equipo (D8 usa los valores tal cual).
- Eventos distintos por frame (muestra): nan: 28710, ball_snap: 757, pass_forward: 683, autoevent_passforward: 341, autoevent_ballsnap: 324, play_action: 181, run: 36, pass_arrived: 29, qb_sack: 27, autoevent_passinterrupted: 25, first_contact: 12, line_set: 10, pass_tipped: 10, man_in_motion: 7, shift: 7.

## 3. Rol PFF `Pass` frente a `officialPosition == QB` (todas las jugadas PFF)

- Registros con `pff_role == Pass`: 8,557 en 8,557 jugadas.
- Proporción con `officialPosition == QB`: 0.9999.
- Posiciones de esos jugadores: QB: 8556, WR: 1.
- Jugadas con más de un `Pass`: 0.

## 4. `frame_dt_ok`, `time_to_throw` (muestra procesada con `process_tracking_frame`)

- Jugadas en la muestra: 757.
- `frame_dt_ok == 1`: 100.0%.
- `time_to_throw` no nulo: 723. Valores enteros: 10.8%. Mín/mediana/máx: 1.00 / 2.70 / 16.60.
- `time_to_throw` coincide con (res − snap)/10 en el 100.0% de las jugadas (valores enteros: 10.8%).
- `mean_dt_time` (diagnóstico, dt medio por `time`): media 0.0998 s, mín/máx 0.069 / 0.136 s.

## 5. Rendimiento

- Tiempo por archivo (lectura + proceso, muestra): media 0.42 s, máx 0.51 s. Extrapolado a 122 archivos: ≈ 0.8 min.
- Pico de memoria (`ru_maxrss`, proceso completo, incluye tablas base y el escaneo de `time`): 177 MB.
- Pico tras la muestra, archivo a archivo (MB): 162, 171, 172, 172, 172, 172, 174, 174, 174, 177.
- Tiempo total de esta verificación: 20.7 s.


## 6. Corrida completa `python -m src.analyze` (122 archivos, tras la corrección D12)

- Tiempo total: 52.7 s (reloj de pared). Pico de RAM (`/usr/bin/time -v`, RSS máximo): 190.7 MB.
- Archivos de tracking ok / con error: 122 / 0. Tabla maestra: 8,522 jugadas, 52 columnas, 0 duplicados por (`gameId`, `playId`), `has_tracking` verdadero en todas. Formato: csv (sin pyarrow).
- `frame_dt_ok == 1`: 8,522 de 8,522 (100%; antes 63.1% con `time`).
- `time_to_throw` no nulo: 8,036 (94.3%); mín/mediana/máx 1.00 / 2.80 / 19.20 s. Los 486 nulos son 462 jugadas con snap sin evento de resolución (en su mayoría scrambles y carreras, `passResult` R) y 24 sin snap.
- `min_rusher_dist_at_throw` no nulo: 8,057 (mediana 2.80 yd, máx 16.43). `lb_bite_yards` no nulo: 8,498 (rango -3.40 a 3.72, media 0.66).
- Signo de `lb_bite_yards`: con `x_norm` la defensa queda en mayor X (media al snap: defensa 67.8, ofensiva 61.9). Cambio snap→snap+10 en el archivo 2021090900: DT/DE/NT +1.7 a +1.9 yd (avanzan hacia la línea), CB/FS/SS -0.4 a -0.7 yd (retroceden). Convención positiva = avance hacia la línea de golpeo confirmada.
- Sin avisos en el Log. `n_speed_outliers` = 0 en todas las jugadas (máx `s` observada 11.18 yd/s).
