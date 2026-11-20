# Requirements Document

## Introduction

Pipeline modular en Python para el perfil Coach del Hackathon NFL Big Data Bowl (UNAM). El pipeline construye una tabla maestra a nivel jugada (`gameId`, `playId`) combinando `plays.csv`, `games.csv`, `players.csv`, `pffScoutingData.csv` y métricas derivadas de los 122 archivos de tracking, y genera un reporte cuantitativo en Markdown con intervalos de confianza al 95%. Consta de tres módulos: `src/features.py`, `src/tracking_metrics.py` y `src/analyze.py`. Restricciones: stack fijo (Python 3.12 en `.venv`, pandas 2.2.3, numpy 2.1.3, sin dependencias nuevas), `data/` de solo lectura, rutas relativas a la raíz del proyecto y nunca cargar un archivo de tracking completo en memoria junto con otro.

## Glossary

- **Pipeline**: Conjunto de los tres módulos `Features_Module`, `Tracking_Module` y `Analysis_Module`.
- **Features_Module**: Módulo `src/features.py`.
- **Tracking_Module**: Módulo `src/tracking_metrics.py`.
- **Analysis_Module**: Módulo `src/analyze.py`.
- **Jugada**: Fila identificada por la llave (`gameId`, `playId`).
- **Jugada_Valida**: Jugada de `plays.csv` con `down` en {1, 2, 3, 4}.
- **Jugada_Sin_Castigo**: Jugada de `plays.csv` cuyo `penaltyYards` es nulo, es decir, sin castigo que anule o altere el resultado.
- **Tabla_Maestra**: Tabla con una fila por Jugada que une las variables de `Features_Module` y `Tracking_Module`.
- **is_success**: Variable objetivo binaria: 1 si `prePenaltyPlayResult` ≥ 40% de `yardsToGo` en 1er down, ≥ 60% en 2do down, ≥ 100% en 3er y 4to down; 0 en otro caso.
- **n_rushers**: Conteo de jugadores con `pff_role` igual a `Pass Rush` en una Jugada.
- **n_blockers**: Conteo de jugadores con `pff_role` igual a `Pass Block` en una Jugada.
- **protection_advantage**: `n_blockers` menos `n_rushers`.
- **is_blitz**: Bandera igual a 1 cuando `n_rushers` ≥ 5.
- **any_pressure**: Bandera igual a 1 cuando algún jugador con `pff_role` `Pass Rush` tiene `pff_hit`, `pff_hurry` o `pff_sack` igual a 1.
- **any_beaten**: Bandera igual a 1 cuando algún jugador con `pff_role` `Pass Block` tiene `pff_beatenByDefender` igual a 1.
- **Frame_Snap**: Primer frame de la Jugada con `event` igual a `ball_snap` o `autoevent_ballsnap`.
- **Frame_Resolucion**: Primer frame de la Jugada, posterior o igual al Frame_Snap, con `event` igual a `pass_forward`, `autoevent_passforward`, `qb_sack` o `qb_strip_sack`.
- **x_norm / y_norm**: Coordenadas normalizadas para que la ofensiva ataque hacia +X.
- **time_to_throw**: Segundos entre Frame_Snap y Frame_Resolucion, calculados como la diferencia de `frameId` dividida entre 10 (los frames avanzan a 10 Hz, 0.1 s por frame). No se usa `time`, que viene truncado al segundo.
- **frame_dt_ok**: Bandera igual a 1 cuando una Jugada tiene al menos 2 frames, sus `frameId` consecutivos avanzan siempre de 1 en 1 (sin saltos) y `time` es monótono no decreciente al ordenar por `frameId`, y 0 en otro caso.
- **Pasador**: Jugador que lanza el balón en una Jugada. Su fuente principal es el jugador con `pff_role` igual a `Pass` en `pffScoutingData.csv`; como respaldo, cuando la Jugada no tiene ningún registro con ese rol, es el jugador con `officialPosition` igual a `QB` en `players.csv` cuyo `nflId` está presente en el tracking o en los registros PFF de la Jugada.
- **Defensivo_Jugada**: Jugador de tracking con `team` distinto de `football` y perteneciente al equipo igual al `defensiveTeam` de `plays.csv` para la Jugada.
- **Linebacker**: Defensivo_Jugada cuya `officialPosition` en `players.csv` (obtenida cruzando `nflId`) está en {ILB, MLB, OLB, LB}.
- **min_rusher_dist_at_throw**: Distancia euclidiana mínima, en yardas, en el Frame_Resolucion entre el Pasador y cualquier jugador con `pff_role` `Pass Rush`.
- **lb_bite_yards**: Promedio, sobre los Linebackers de la Jugada, de `x_norm` en el Frame_Snap menos `x_norm` en el frame 10 posterior al Frame_Snap (1.0 s después). Como `x_norm` hace que la ofensiva ataque hacia +X, la defensa está en mayor X y un linebacker que avanza hacia la línea de golpeo se mueve hacia -X; un valor positivo indica avance hacia la línea de golpeo (mordió el engaño) y un valor negativo indica retroceso a cobertura.
- **Celda**: Subgrupo de Jugadas definido por una combinación de variables de segmentación en el reporte.
- **Celda_Pequena**: Celda con n menor que 30.
- **Reporte**: Archivo `outputs/COACH_INSIGHTS.md`.
- **Bloque A**: Sección del Reporte que compara Jugadas con play action contra Jugadas sin play action.
- **Bloque B**: Sección del Reporte que mide el efecto del blitz y de la ventaja de protección.
- **Reporte_Ejecucion**: Registro de ejecución del Pipeline que contiene conteos y avisos de la corrida, incluido el número de jugadas excluidas.
- **Log**: Salida de registro del Pipeline durante su ejecución.
- **IC95**: Intervalo de confianza al 95%.

## Requirements

### Requirement 1: Carga y filtrado de tablas base

**User Story:** Como analista del perfil Coach, quiero cargar y filtrar las tablas base, para que el análisis use solo jugadas válidas y con mérito táctico medible.

#### Acceptance Criteria

1. WHEN el Features_Module se ejecuta, THE Features_Module SHALL cargar `plays.csv`, `games.csv`, `players.csv` y `pffScoutingData.csv` desde `data/nfl-big-data-bowl-regional-event-data/data/` usando rutas relativas a la raíz del proyecto, independientemente del directorio de trabajo desde el que se invoque.
2. WHEN las tablas base se han cargado, THE Features_Module SHALL conservar únicamente las Jugadas_Validas (`down` en {1, 2, 3, 4}) y excluir toda Jugada cuyo `down` sea nulo, 0 o un valor fuera de {1, 2, 3, 4}.
3. WHEN el filtrado de Jugadas_Validas ha concluido, THE Features_Module SHALL agregar a cada Jugada conservada una columna booleana `no_penalty` con valor verdadero para las Jugadas_Sin_Castigo y valor falso para el resto, sin valores nulos.
4. WHEN el Features_Module genera la salida, THE Features_Module SHALL conservar en cada fila de la salida las columnas `prePenaltyPlayResult` y `playResult` con los mismos valores que tienen en `plays.csv`.
5. THE Features_Module SHALL dejar sin modificación el contenido, el tamaño y la fecha de modificación de todos los archivos bajo `data/`, abriéndolos únicamente en modo de lectura.
6. IF un archivo base no existe en la ruta esperada, THEN THE Features_Module SHALL terminar con un mensaje de error que indique la ruta faltante, finalizar con código de salida distinto de cero y no generar archivos de salida parciales.
7. IF un archivo base existe pero no puede leerse o carece de una columna requerida (`down`, `prePenaltyPlayResult` o `playResult` en `plays.csv`), THEN THE Features_Module SHALL terminar con un mensaje de error que indique el archivo y, cuando aplique, la columna faltante, finalizar con código de salida distinto de cero y no generar archivos de salida parciales.

### Requirement 2: Variable objetivo is_success

**User Story:** Como analista, quiero una variable objetivo de éxito por down y distancia, para medir la eficiencia sin disponer de EPA.

#### Acceptance Criteria

1. WHEN `down` es 1, THE Features_Module SHALL asignar `is_success` igual a 1 si `prePenaltyPlayResult` ≥ 0.4 × `yardsToGo` (comparación numérica en yardas, con igualdad incluida), y 0 en otro caso.
2. WHEN `down` es 2, THE Features_Module SHALL asignar `is_success` igual a 1 si `prePenaltyPlayResult` ≥ 0.6 × `yardsToGo` (comparación numérica en yardas, con igualdad incluida), y 0 en otro caso.
3. WHEN `down` es 3 o 4, THE Features_Module SHALL asignar `is_success` igual a 1 si `prePenaltyPlayResult` ≥ `yardsToGo` (comparación numérica en yardas, con igualdad incluida), y 0 en otro caso.
4. THE Features_Module SHALL producir `is_success` con valores exclusivamente en {0, 1} y sin nulos para toda Jugada_Valida.
5. IF `down` no es un entero en {1, 2, 3, 4}, o `prePenaltyPlayResult` o `yardsToGo` es nulo o no numérico, THEN THE Features_Module SHALL excluir la jugada del cálculo de `is_success`, dejar el resto de los datos de entrada sin modificar, y registrar el número de jugadas excluidas por esta causa en el Reporte_Ejecucion.
6. WHEN `yardsToGo` es 0 y `down` está en {1, 2, 3, 4}, THE Features_Module SHALL asignar `is_success` igual a 1 si `prePenaltyPlayResult` ≥ 0, y 0 en otro caso.

### Requirement 3: Métricas PFF de protección y presión

**User Story:** Como coach, quiero métricas de protección y presión por jugada, para analizar el efecto del blitz y del bolsillo.

#### Acceptance Criteria

1. WHEN el Features_Module procesa `pffScoutingData.csv`, THE Features_Module SHALL agrupar los registros por (`gameId`, `playId`) y calcular para cada Jugada `n_rushers` como el número de registros con `pff_role` igual a `Pass Rush`, `n_blockers` como el número de registros con `pff_role` igual a `Pass Block`, y `protection_advantage` como `n_blockers` menos `n_rushers`.
2. THE Features_Module SHALL comparar `pff_role` con los valores exactos `Pass Block`, `Pass Rush`, `Coverage`, `Pass Route` y `Pass`, respetando mayúsculas y minúsculas, y SHALL excluir de `n_rushers` y `n_blockers` los registros cuyo `pff_role` no coincida exactamente con `Pass Rush` o `Pass Block`, respectivamente.
3. THE Features_Module SHALL asignar `is_blitz` igual a 1 cuando `n_rushers` ≥ 5, y 0 cuando `n_rushers` sea menor que 5.
4. THE Features_Module SHALL asignar `any_pressure` igual a 1 cuando al menos un registro de la Jugada con `pff_role` igual a `Pass Rush` tiene `pff_hit`, `pff_hurry` o `pff_sack` igual a 1, y 0 en otro caso, tratando los valores nulos de esas tres columnas como 0.
5. THE Features_Module SHALL asignar `any_beaten` igual a 1 cuando al menos un registro de la Jugada con `pff_role` igual a `Pass Block` tiene `pff_beatenByDefender` igual a 1, y 0 en otro caso, tratando los valores nulos como 0.
6. WHEN una Jugada_Valida no tiene registros en `pffScoutingData.csv`, THE Features_Module SHALL conservar la Jugada en la tabla de salida con `n_rushers`, `n_blockers`, `protection_advantage`, `is_blitz`, `any_pressure` y `any_beaten` en nulo.
7. THE Features_Module SHALL producir exactamente una fila por combinación única de (`gameId`, `playId`) en su tabla de salida, sin filas duplicadas.
8. THE Features_Module SHALL incorporar a la tabla de salida, mediante unión por `gameId` con `games.csv` y por `nflId` con `players.csv`, las columnas de `games.csv` necesarias para el análisis, sin modificar el número de filas de la tabla de salida; la posición oficial (`officialPosition`) de `players.csv` se utiliza en el Tracking_Module, cruzando por `nflId`, para identificar al Pasador de respaldo y a los Linebackers.
9. IF `pffScoutingData.csv` no existe o carece de alguna de las columnas `gameId`, `playId`, `pff_role`, `pff_hit`, `pff_hurry`, `pff_sack` o `pff_beatenByDefender`, THEN THE Features_Module SHALL abortar el procesamiento, emitir un error que indique el archivo o las columnas faltantes, y no escribir la tabla de salida.

### Requirement 4: Procesamiento de tracking por archivo

**User Story:** Como analista, quiero procesar el tracking archivo por archivo, para no saturar la memoria RAM.

#### Acceptance Criteria

1. WHEN el Tracking_Module se ejecuta, THE Tracking_Module SHALL procesar de forma secuencial los archivos `data/nfl-big-data-bowl-regional-event-data/data/tracking/tracking_[gameId].csv`, uno a la vez, de modo que en ningún momento haya más de un archivo de tracking cargado en memoria.
2. THE Tracking_Module SHALL leer únicamente las columnas `gameId`, `playId`, `nflId`, `frameId`, `time`, `team`, `playDirection`, `x`, `y`, `s`, `a` y `event`, y SHALL NOT cargar ninguna otra columna del archivo.
3. WHEN el Tracking_Module termina de procesar un archivo, THE Tracking_Module SHALL conservar solo las métricas agregadas por Jugada (una fila por combinación de `gameId` y `playId`) y SHALL liberar los datos de frames de ese archivo antes de leer el siguiente.
4. WHEN `playDirection` es `left`, THE Tracking_Module SHALL calcular `x_norm` igual a 120 − `x` y `y_norm` igual a 53.3 − `y`.
5. WHEN `playDirection` es `right`, THE Tracking_Module SHALL asignar `x_norm` igual a `x` y `y_norm` igual a `y`.
6. WHEN el Tracking_Module calcula velocidades o posiciones de jugadores, THE Tracking_Module SHALL excluir las filas con `team` igual a `football`.
7. WHEN el Tracking_Module calcula velocidades de jugadores, THE Tracking_Module SHALL descartar los valores de `s` mayores a 15 yd/s, sin descartar los valores de `s` iguales o menores a 15 yd/s, y SHALL excluir los valores descartados del cálculo de las métricas agregadas.
8. IF un archivo de tracking no existe, no puede leerse o tiene un formato que impide obtener las columnas requeridas, THEN THE Tracking_Module SHALL registrar el `gameId` afectado, omitir ese archivo sin conservar métricas parciales de él y continuar con el siguiente archivo.
9. WHEN el Tracking_Module termina, THE Tracking_Module SHALL informar el número de archivos procesados correctamente y el número de archivos con error, de modo que la suma de ambos sea igual al número de archivos de tracking que se intentó procesar.
10. IF `playDirection` tiene un valor distinto de `left` y `right`, THEN THE Tracking_Module SHALL excluir esas filas del cálculo de `x_norm` y `y_norm`, y SHALL registrar el `gameId` y el `playId` afectados.

### Requirement 5: Snap, resolución y tiempo al lanzamiento

**User Story:** Como coach, quiero identificar el snap y la resolución de cada jugada, para medir el tiempo al lanzamiento.

#### Acceptance Criteria

1. WHEN el Tracking_Module procesa una Jugada que contiene al menos un evento `ball_snap` o `autoevent_ballsnap`, THE Tracking_Module SHALL asignar como Frame_Snap el frame con el menor `time` entre los frames que contienen alguno de esos eventos.
2. WHEN el Tracking_Module procesa una Jugada que contiene al menos un evento `pass_forward`, `autoevent_passforward`, `qb_sack` o `qb_strip_sack`, THE Tracking_Module SHALL asignar como Frame_Resolucion el frame con el menor `time` entre los frames que contienen alguno de esos eventos.
3. WHEN una Jugada tiene Frame_Snap y Frame_Resolucion, THE Tracking_Module SHALL calcular `time_to_throw` como el `frameId` del Frame_Resolucion menos el `frameId` del Frame_Snap, dividido entre 10 (0.1 s por frame), en segundos, con una precisión de 0.01 s.
4. WHEN el Tracking_Module calcula `time_to_throw` para una Jugada, THE Tracking_Module SHALL registrar `frame_dt_ok` igual a 1 si los `frameId` consecutivos de esa Jugada avanzan siempre de 1 en 1 y `time` es monótono no decreciente al ordenar por `frameId`, o igual a 0 en caso contrario, y SHALL registrar además `mean_dt_time`, el promedio de la diferencia de `time` entre frames consecutivos en segundos, solo como diagnóstico.
5. IF una Jugada carece de Frame_Snap o de Frame_Resolucion, THEN THE Tracking_Module SHALL asignar `time_to_throw` nulo para esa Jugada, conservar el resto de los datos de la Jugada y continuar procesando las demás Jugadas.
6. IF `time_to_throw` resulta menor que 0 s, THEN THE Tracking_Module SHALL asignar `time_to_throw` nulo para esa Jugada, conservar el resto de los datos de la Jugada y continuar procesando las demás Jugadas.
7. IF una Jugada tiene menos de 2 frames, THEN THE Tracking_Module SHALL registrar `frame_dt_ok` igual a 0 para esa Jugada.

### Requirement 6: Distancia del rusher y mordida de linebackers

**User Story:** Como coach, quiero medir la cercanía del rusher al QB y el avance de los linebackers, para cuantificar presión y mordida al play action.

#### Acceptance Criteria

1. WHEN una Jugada tiene Frame_Resolucion y Pasador, THE Tracking_Module SHALL calcular `min_rusher_dist_at_throw` como la distancia euclidiana mínima, en yardas, entre el Pasador y cualquier jugador con `pff_role` `Pass Rush`, usando `x_norm` y `y_norm` del Frame_Resolucion, redondeada a 2 decimales.
2. THE Tracking_Module SHALL identificar al Pasador usando como fuente principal al jugador con `pff_role` igual a `Pass` en `pffScoutingData.csv`, y, solo cuando la Jugada no tiene ningún registro con ese rol, usando como respaldo al jugador con `officialPosition` igual a `QB` en `players.csv` cuyo `nflId` está presente en el tracking o en los registros PFF de la Jugada, y SHALL obtener el rol `Pass Rush` de `pffScoutingData.csv`.
3. IF la Jugada tiene más de un jugador con rol `Pass`, o no tiene ninguno y tiene más de un QB de respaldo, THEN THE Tracking_Module SHALL seleccionar como Pasador al jugador con rol `Pass` (y, en caso de empate entre candidatos de la misma fuente, al de menor `nflId`) y SHALL registrar la ambigüedad con el `gameId` y el `playId` afectados en el Log.
4. IF una Jugada no tiene Pasador por ninguna de las dos vías, no tiene jugador con rol `Pass Rush`, o el Pasador o algún jugador `Pass Rush` carece de valor `x_norm` o `y_norm` en el Frame_Resolucion, THEN THE Tracking_Module SHALL asignar `min_rusher_dist_at_throw` nulo para esa Jugada, sin descartar la fila y sin interrumpir el procesamiento de las demás Jugadas.
5. WHEN una Jugada tiene Frame_Snap, THE Tracking_Module SHALL calcular `lb_bite_yards` como el promedio, sobre los Linebackers de la Jugada (cruzando `nflId` del tracking con `officialPosition` de `players.csv`, sin usar `pff_positionLinedUp`, con `team` distinto de `football` y equipo igual al `defensiveTeam` de `plays.csv`), de `x_norm` en el Frame_Snap menos `x_norm` en el frame 10 posterior al Frame_Snap (frame_snap + 10, 1.0 s después), expresado en yardas y redondeado a 2 decimales, donde un valor positivo indica avance hacia la línea de golpeo ofensiva y un valor negativo indica retroceso a cobertura.
6. IF una Jugada tiene menos de 10 frames posteriores al Frame_Snap, no tiene Linebackers, o ningún Linebacker tiene `x_norm` en ambos frames (Frame_Snap y frame_snap + 10), THEN THE Tracking_Module SHALL asignar `lb_bite_yards` nulo para esa Jugada, sin descartar la fila.
7. WHEN algunos Linebackers carecen de `x_norm` en alguno de los dos frames, THE Tracking_Module SHALL calcular el promedio de `lb_bite_yards` solo con los Linebackers que tienen ambos valores.
8. THE Tracking_Module SHALL producir exactamente una fila por (`gameId`, `playId`) en su tabla de salida, incluyendo las Jugadas con `min_rusher_dist_at_throw` o `lb_bite_yards` nulos.

### Requirement 7: Tabla maestra persistida

**User Story:** Como analista, quiero una tabla maestra persistida, para reutilizar los resultados sin reprocesar el tracking.

#### Acceptance Criteria

1. WHEN el Pipeline termina el procesamiento, THE Pipeline SHALL unir por (`gameId`, `playId`) las salidas de `Features_Module` y `Tracking_Module` en la Tabla_Maestra, conservando el 100% de las Jugadas_Validas, con exactamente una fila por cada par (`gameId`, `playId`) y sin filas duplicadas.
2. IF una Jugada_Valida no tiene registro en la salida de `Features_Module` o de `Tracking_Module`, THEN THE Pipeline SHALL conservar la fila en la Tabla_Maestra con valores nulos en las columnas del módulo ausente y registrar en el Log el número de jugadas afectadas.
3. WHERE el paquete `pyarrow` está instalado en `.venv`, THE Pipeline SHALL guardar la Tabla_Maestra en `outputs/plays_enriched.parquet`.
4. WHERE el paquete `pyarrow` no está instalado en `.venv`, THE Pipeline SHALL guardar la Tabla_Maestra en `outputs/plays_enriched.csv`.
5. IF el directorio `outputs/` no existe, THEN THE Pipeline SHALL crear el directorio `outputs/` antes de guardar la Tabla_Maestra.
6. IF la escritura de la Tabla_Maestra falla (por ejemplo, por falta de permisos o de espacio en disco), THEN THE Pipeline SHALL terminar con código de salida distinto de 0, mostrar un mensaje de error que indique la ruta de destino y la causa, y no dejar un archivo parcial en `outputs/`.
7. WHEN la Tabla_Maestra ha sido guardada, THE Pipeline SHALL leer el archivo y verificar que coincide con la tabla original en el mismo número de filas, los mismos nombres de columnas en el mismo orden, y los mismos valores de `is_success` en cada fila (propiedad de ida y vuelta).
8. THE Pipeline SHALL escribir en el Log, antes de terminar, una entrada que indique el formato de archivo elegido (`parquet` o `csv`) y el motivo (presencia o ausencia de `pyarrow` en `.venv`).

### Requirement 8: Reporte con intervalos de confianza

**User Story:** Como coach, quiero un reporte con estadísticas e intervalos de confianza, para saber qué conclusiones son estables.

#### Acceptance Criteria

1. WHEN el Analysis_Module se ejecuta, THE Analysis_Module SHALL ejecutar el Pipeline y guardar el Reporte en `outputs/COACH_INSIGHTS.md`, sobrescribiendo cualquier versión previa del archivo.
2. IF el Pipeline falla o `outputs/COACH_INSIGHTS.md` no se puede escribir, THEN THE Analysis_Module SHALL terminar con un indicador de error que identifique la causa, y SHALL conservar sin modificar la versión previa del Reporte si existe.
3. THE Analysis_Module SHALL reportar para cada Celda el tamaño n (entero ≥ 0), la media de la métrica de interés, la tasa de éxito (media de `is_success`, en el rango 0 a 1) y el IC95 de la media y de la tasa de éxito, con los valores decimales redondeados a 3 decimales.
4. THE Analysis_Module SHALL calcular el IC95 de la tasa de éxito con el método de Wilson usando z = 1.96.
5. THE Analysis_Module SHALL calcular el IC95 de una media continua como media ± 1.96 × (desviación estándar muestral con n−1 / √n).
6. WHEN una Celda tiene n < 30, THE Analysis_Module SHALL marcar esa Celda en el Reporte con la etiqueta "no concluyente".
7. IF una Celda tiene n igual a 0 o 1, THEN THE Analysis_Module SHALL reportar el IC95 de la media y de la tasa de éxito como "no disponible", y SHALL marcar la Celda como no concluyente.
8. THE Analysis_Module SHALL declarar en el Reporte las siguientes limitaciones de los datos: solo jugadas de pase, 8 semanas de la temporada 2021, ausencia de EPA y uso de `prePenaltyPlayResult` para el mérito táctico.
9. THE Analysis_Module SHALL incluir en el Reporte el número de Jugadas_Validas y el número de Jugadas con valor no nulo en `time_to_throw`, en `min_rusher_dist_at_throw` y en `lb_bite_yards`, cada uno como entero ≥ 0.

### Requirement 9: Bloque A: Play Action

**User Story:** Como coordinador ofensivo, quiero el Bloque A de play action, para decidir cuándo llamarlo según cobertura y caja.

#### Acceptance Criteria

1. THE Analysis_Module SHALL incluir en el Reporte un Bloque A que compare las Jugadas con `pff_playAction` igual a 1 contra las Jugadas con `pff_playAction` igual a 0, excluyendo del Bloque A las Jugadas con `pff_playAction` nulo y declarando en el Reporte el número de Jugadas excluidas por este motivo.
2. THE Analysis_Module SHALL reportar en el Bloque A, para cada comparación, la diferencia de medias de `prePenaltyPlayResult` (grupo 1 menos grupo 0), la diferencia de medias de `playResult` (grupo 1 menos grupo 0) y la diferencia de tasa de éxito en puntos porcentuales (grupo 1 menos grupo 0), cada una con su IC95 expresado como límite inferior y límite superior, y el tamaño de muestra n de cada grupo.
3. THE Analysis_Module SHALL desglosar el Bloque A por `pff_passCoverageType`, con una Celda para el valor Man y una Celda para el valor Zone.
4. THE Analysis_Module SHALL desglosar el Bloque A por cada valor distinto de `pff_passCoverage` presente en los datos, con una Celda por valor.
5. THE Analysis_Module SHALL desglosar el Bloque A por cada valor entero distinto de `defendersInBox` presente en los datos, con una Celda por valor.
6. THE Analysis_Module SHALL desglosar el Bloque A por rangos de `lb_bite_yards`, con los límites de cada rango y su unidad (yardas) declarados en el Reporte, y con cada Jugada asignada a un solo rango.
7. WHEN se calcula una Celda del Bloque A, THE Analysis_Module SHALL excluir de esa Celda las Jugadas con valor nulo en la variable de desglose correspondiente y declarar en el Reporte, por cada desglose, el número de Jugadas excluidas.
8. IF una Celda del Bloque A tiene cero Jugadas en alguno de los dos grupos de `pff_playAction`, THEN THE Analysis_Module SHALL marcar en el Reporte como "no disponible" la diferencia de yardas, la diferencia de tasa de éxito y sus IC95 de esa Celda, y conservar el n de cada grupo.
9. IF una Celda del Bloque A tiene al menos una Jugada en cada grupo de `pff_playAction` pero menos de 2 Jugadas en alguno de ellos, THEN THE Analysis_Module SHALL marcar en el Reporte como "no disponible" el IC95 de esa Celda, y conservar la diferencia puntual y el n de cada grupo.

### Requirement 10: Bloque B: Blitz y bolsillo

**User Story:** Como coordinador defensivo y ofensivo, quiero el Bloque B de blitz y bolsillo, para entender el efecto de los rushers y la protección.

#### Acceptance Criteria

1. WHEN se genera el Reporte, THE Analysis_Module SHALL incluir un Bloque B que, para cada una de las métricas `any_pressure`, `min_rusher_dist_at_throw`, `time_to_throw` e `is_success`, reporte la media o proporción de las Jugadas con `is_blitz` verdadero, la de las Jugadas con `is_blitz` falso y su diferencia con IC95.
2. WHEN se genera el Reporte, THE Analysis_Module SHALL medir en el Bloque B, para cada categoría de `protection_advantage` declarada según el criterio 5, la media o proporción de `any_pressure`, `min_rusher_dist_at_throw`, `time_to_throw` e `is_success`, con IC95 por categoría.
3. WHEN se genera el Bloque B, THE Analysis_Module SHALL segmentar las mediciones de los criterios 1 y 2 por cada valor de `pff_passCoverage` y por cada valor de `offenseFormation`, de forma independiente (una segmentación por variable, no el cruce de ambas).
4. WHEN se genera el Bloque B, THE Analysis_Module SHALL reportar en cada Celda el n de Jugadas, la media (métricas continuas) o proporción (métricas binarias) de cada métrica y el IC95 al 95% de confianza, con la media o proporción y los límites del IC95 redondeados a 3 decimales.
5. WHEN se genera el Bloque B, THE Analysis_Module SHALL agrupar los valores de `protection_advantage` en un máximo de 5 categorías, declarar en el Reporte los límites de cada categoría antes de la segmentación, y asegurar que cada categoría tenga n ≥ 30 Jugadas en el conjunto total.
6. IF una categoría de `protection_advantage` tiene n < 30 en el conjunto total, THEN THE Analysis_Module SHALL fusionarla con la categoría adyacente hasta que todas cumplan n ≥ 30, y declarar la fusión en el Reporte.
7. IF una Celda del Bloque B tiene n < 30 Jugadas o una métrica no puede calcularse por valores nulos o varianza cero, THEN THE Analysis_Module SHALL marcar la Celda como "n insuficiente" o "no calculable", reportar su n, omitir el IC95 y conservar las demás Celdas del Bloque B.
8. THE Analysis_Module SHALL calcular las métricas del Bloque B a nivel Jugada, contando cada Jugada una sola vez, de modo que la suma de n de las Celdas de una segmentación no exceda el número total de Jugadas del conjunto analizado.
9. IF una Jugada tiene valor nulo en una métrica, THEN THE Analysis_Module SHALL excluirla únicamente del cálculo de esa métrica y reportar en el Reporte el número de Jugadas excluidas por métrica.

### Requirement 11: Restricciones del proyecto

**User Story:** Como miembro del equipo, quiero que el pipeline respete las restricciones del proyecto, para que se ejecute en el entorno oficial.

#### Acceptance Criteria

1. THE Pipeline SHALL importar únicamente los paquetes pandas 2.2.3 y numpy 2.1.3 y los módulos de la biblioteca estándar de Python 3.12, ejecutándose en el entorno virtual `.venv`.
2. THE Pipeline SHALL resolver todas las rutas de archivos de entrada y salida de forma relativa a la raíz del proyecto, de modo que el resultado sea idéntico al ejecutarlo desde cualquier directorio de trabajo.
3. THE Pipeline SHALL escribir sus salidas exclusivamente dentro del directorio `outputs/` y no modificar ningún archivo fuera de ese directorio.
4. WHERE el entorno de ejecución es el servidor de la aplicación, THE Pipeline SHALL permitir que el backend lea la Tabla_Maestra o la recalcule en memoria, y la solicitud SHALL completarse correctamente cuando `outputs/` no contiene ningún archivo previo.
5. WHEN el Pipeline procesa cada archivo de tracking, THE Pipeline SHALL mantener en memoria los datos de un solo archivo de tracking a la vez y liberar los datos del archivo anterior antes de cargar el siguiente.
6. THE Pipeline SHALL exponer cada módulo como funciones importables sin ejecución de código al importar, de modo que `Analysis_Module` invoque a `Features_Module` y a `Tracking_Module` sin duplicar lógica.
