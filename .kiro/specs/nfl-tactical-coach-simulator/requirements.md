# Requirements Document

## Introduction

NFL Tactical Coach Simulator es una aplicación web de solo lectura para el perfil Coach del hackathon NFL Big Data Bowl (UNAM). Permite filtrar situaciones de juego (down, distancia, cobertura, formación, defensores en la caja) y obtiene, a partir de `outputs/plays_enriched.csv` (8,522 jugadas de pase, temporada 2021, semanas 1 a 8), la comparación entre Play Action y dropback tradicional, la comparación entre Blitz y cobertura estándar, y una recomendación táctica en español. Una pizarra SVG reproduce una jugada real con datos de tracking.

Estado actual del proyecto, verificado al redactar:
- `backend/main.py` contiene solo `GET /health`. No existe `.venv/` ni el directorio `data/` en el workspace.
- `dashboard/` tiene React 18.3.1, Vite, Tailwind 3 y Recharts 3.10.1, con `src/App.tsx`, `src/main.tsx` y `src/index.css`.
- `outputs/plays_enriched.csv` ya contiene `is_success`, `prePenaltyPlayResult`, `pff_playAction`, `pff_passCoverage`, `pff_passCoverageType`, `offenseFormation`, `defendersInBox`, `is_blitz`, `any_pressure`, `protection_advantage`, `time_to_throw`, `min_rusher_dist_at_throw`, `lb_bite_yards`, `snap_frameId`, `res_frameId`, `down`, `yardsToGo`.
- `.hackathon/rules.md` fija el stack (sin matplotlib), exige rutas `fetch('api/...')` sin diagonal inicial, API bajo `/api`, `GET /health`, y que el servidor sirva `dashboard/dist` en la misma URL y puerto.
- Existe la especificación `coach-metrics-pipeline`, que produjo `plays_enriched.csv` y `COACH_INSIGHTS.md`.

Mejoras para la presentación (requisitos 16 a 18): barra de Escenarios Tácticos Rápidos, animación cuadro por cuadro en la pizarra y README ejecutivo. Son aditivas: no cambian el contrato de `/api/filters`, `/api/recommend` ni `/api/sample-play` para quien no envíe los nuevos parámetros, y solo añaden campos a las respuestas. Las cifras citadas para los escenarios se verificaron contra `outputs/plays_enriched.csv` (8,522 jugadas en 122 partidos, confirmado):
- Play Action contra Cover-2 con 7 en la caja: la diferencia de éxito es +24.3 pp (94 Play Action, 105 tradicionales), no +12.3 pp. El valor +12.3 pp corresponde a Cover-2 con cualquier número de defensores en la caja (261 y 824 jugadas).
- Play Action en `Red Zone` (cobertura): la diferencia de `prePenaltyPlayResult` es -1.79 yardas (confirmado, redondea a -1.8), pero la diferencia de éxito es -0.8 pp con intervalo [-12.3, 11.5] pp, no concluyente. El Verdict de esa situación es `SIN_VENTAJA_CLARA`.
- Blitz con formación `EMPTY`: éxito ofensivo 50.9% (n = 265) y `time_to_throw` medio 2.60 s (n = 254), confirmados. La referencia sin blitz da 46.6% y 2.89 s. La diferencia de éxito es +4.3 pp con intervalo [-2.3, 11.0] pp, no concluyente.
- Por eso los requisitos 16 y 17 obligan a mostrar el valor calculado por la API y prohíben escribir esas cifras en el código del Dashboard.

Restricciones y puntos abiertos:
- El tracking (`data/nfl-big-data-bowl-regional-event-data/data/tracking/tracking_[gameId].csv`) no está en el workspace actual. Los requisitos de `/api/sample-play` dependen de que exista en la máquina de ejecución.
- `src/plots.py` pide PNG a 300 DPI, lo que normalmente requiere matplotlib. Matplotlib no está en el stack fijo. Este documento exige cumplir el requisito con las dependencias permitidas o declarar la desviación al equipo antes de añadir la dependencia (decisión pendiente del equipo).
- `COACH_INSIGHTS.md` no tiene un formato de máquina estable. La API calcula sus cifras desde el CSV y usa `COACH_INSIGHTS.md` solo como referencia de validación.

## Glossary

- **Backend**: Aplicación FastAPI en `backend/main.py` que expone la API bajo `/api`.
- **Dashboard**: Aplicación React + TypeScript + Tailwind + Recharts en `dashboard/`.
- **Plays_Store**: Estructura en memoria del Backend con el contenido de `outputs/plays_enriched.csv`.
- **Filter_Service**: Componente del Backend que calcula los valores únicos de filtros (`GET /api/filters`).
- **Recommend_Service**: Componente del Backend que calcula comparativas y recomendación (`GET /api/recommend`).
- **Sample_Play_Service**: Componente del Backend que devuelve una jugada real con tracking (`GET /api/sample-play`).
- **Plots_Script**: Script `src/plots.py` que genera las figuras estáticas.
- **Situation_Filter**: Conjunto de criterios opcionales: `down`, `yards_to_go_bucket`, `coverage`, `formation`, `defenders_in_box`.
- **Subset**: Jugadas de Plays_Store que cumplen el Situation_Filter.
- **Yards_To_Go_Bucket**: Categoría de `yardsToGo`: `corta` (1 a 3), `media` (4 a 7), `larga` (8 o más).
- **Play_Action_Group**: Jugadas del Subset con `pff_playAction = 1`.
- **Traditional_Group**: Jugadas del Subset con `pff_playAction = 0`.
- **Blitz_Group**: Jugadas del Subset con `is_blitz = 1` (5 o más rushers).
- **Standard_Group**: Jugadas del Subset con `is_blitz = 0`.
- **Success_Rate**: Media de `is_success` de un grupo, expresada en porcentaje.
- **Wilson_CI**: Intervalo de confianza del 95% de Wilson para una proporción.
- **Insufficient_Sample**: Condición de un grupo con n menor que 30. Se etiqueta "Muestra insuficiente (n < 30)".
- **Effect_pp**: Diferencia de Success_Rate entre dos grupos, en puntos porcentuales (pp), calculada como grupo de tratamiento menos grupo de referencia.
- **Verdict**: Texto de recomendación táctica en español devuelto por Recommend_Service.
- **Sample_Play**: Jugada real elegida por Sample_Play_Service con sus frames de tracking.
- **Tracking_File**: Archivo `tracking_[gameId].csv` del directorio de datos de tracking.
- **Normalized_Coordinates**: `x_norm` y `y_norm`, con el ataque siempre hacia `x` creciente (se invierte `x` y `y` cuando `playDirection` es `left`).
- **Coach_Board**: Panel derecho del Dashboard con el SVG de cancha.
- **Scenario_Preset**: Botón de acceso directo del Dashboard que fija un Situation_Filter predefinido y carga una jugada real representativa. Hay tres: `play_action_cover2_caja7`, `trampa_red_zone` y `blitz_empty`.
- **Scenario_Card**: Tarjeta del Dashboard que muestra las cifras del escenario activo, calculadas por la API.
- **Scenario_Bar**: Barra con los tres Scenario_Preset, en la parte superior del Panel Izquierdo.
- **Focus**: Parámetro opcional `focus` de `/api/sample-play` con valores `bite`, `pa_fallida` o `blitz_exitoso`, que fija el criterio de jugada representativa.
- **Playback_Controller**: Control del Coach_Board formado por el botón Reproducir/Pausa, el deslizador de tiempo y el botón "Ir a pass_forward".
- **Playback_Frame**: Frame de tracking mostrado en la pizarra, entre el `ball_snap` y el `pass_forward`, ambos inclusive.
- **Player_Label**: Etiqueta de texto de un jugador en la pizarra, calculada por Sample_Play_Service en el campo `label`.
- **Executive_README**: El archivo `README.md` en la raíz del proyecto, con el reporte ejecutivo y las instrucciones de ejecución.
- **Static_Figures**: Los PNG `fig1_play_action_coverage.png`, `fig2_lb_bite_box.png` y `fig3_blitz_protection.png` en `outputs/`.

## Requirements

### Requirement 1: Carga de datos en memoria

**User Story:** Como coach, quiero respuestas instantáneas, para explorar situaciones sin esperas.

#### Acceptance Criteria

1. WHEN el Backend inicia, THE Backend SHALL cargar todas las filas de `outputs/plays_enriched.csv` en Plays_Store exactamente una vez y completar la carga antes de aceptar la primera petición HTTP.
2. THE Backend SHALL resolver la ruta de `outputs/plays_enriched.csv` relativa a la raíz del proyecto, con independencia del directorio de trabajo desde el que se inicie el proceso.
3. WHILE el Backend atiende peticiones a `/api/filters` o `/api/recommend`, THE Backend SHALL responder sin abrir ningún archivo de tracking y sin volver a leer `outputs/plays_enriched.csv` (0 lecturas de archivo por petición).
4. THE Backend SHALL abrir `outputs/plays_enriched.csv` y los demás archivos de datos solo en modo lectura, sin crear, modificar ni eliminar ningún archivo de datos.
5. IF `outputs/plays_enriched.csv` no existe, no se puede leer o no contiene alguna columna requerida, THEN THE Backend SHALL iniciar el proceso sin terminar, registrar un mensaje que nombre el archivo o las columnas faltantes, y responder HTTP 503 con un mensaje en español que indique que los datos no están disponibles, en las rutas `/api/filters`, `/api/recommend` y `/api/sample-play`.
6. WHEN el Backend recibe `GET /health`, THE Backend SHALL responder HTTP 200 con el cuerpo `{"status": "ok"}`, incluso si Plays_Store no pudo cargarse.
7. WHEN el Backend recibe una petición `/api/recommend` o `/api/filters` con Plays_Store cargado, THE Backend SHALL responder en un máximo de 500 ms, medido como percentil 95 sobre 100 peticiones secuenciales en el equipo de desarrollo.

### Requirement 2: Endpoint de filtros

**User Story:** Como coach, quiero conocer los valores disponibles de cada filtro, para elegir solo situaciones que existen en los datos.

#### Acceptance Criteria

1. WHEN se recibe `GET /api/filters`, THE Filter_Service SHALL devolver, para cada uno de los campos `down`, `pff_passCoverage`, `pff_passCoverageType`, `offenseFormation` y `defendersInBox`, una lista de valores únicos en orden ascendente (numérico para `down` y `defendersInBox`, alfabético sin distinguir mayúsculas para los demás campos).
2. THE Filter_Service SHALL excluir de cada lista los valores nulos y las cadenas vacías.
3. THE Filter_Service SHALL devolver los valores de `defendersInBox` como enteros sin parte decimal.
4. WHEN se recibe `GET /api/filters`, THE Filter_Service SHALL incluir la lista de categorías de Yards_To_Go_Bucket, donde cada categoría contiene su nombre, su límite inferior en yardas y su límite superior en yardas (o sin límite superior para la última categoría).
5. IF el Plays_Store está vacío o no está cargado cuando se recibe `GET /api/filters`, THEN THE Filter_Service SHALL devolver una respuesta de error que indique que los datos no están disponibles, sin devolver listas parciales.
6. IF un campo no tiene ningún valor no nulo en Plays_Store, THEN THE Filter_Service SHALL devolver una lista vacía para ese campo y mantener las listas de los demás campos.
7. FOR ALL valores `v` devueltos por `/api/filters` en cada campo `f`, existe al menos una jugada en Plays_Store con `f = v` (propiedad de invariante).

### Requirement 3: Validación del Situation_Filter

**User Story:** Como coach, quiero que los filtros inválidos se rechacen con un mensaje claro, para corregir mi selección.

#### Acceptance Criteria

1. THE Recommend_Service SHALL aceptar los parámetros de consulta `down`, `yards_to_go_bucket`, `coverage`, `formation` y `defenders_in_box`, todos opcionales, y cada uno con un único valor por solicitud.
2. WHEN un parámetro no se envía o se envía con cadena vacía, THE Recommend_Service SHALL omitir ese criterio del Subset.
3. WHEN `down` es `3-4`, THE Recommend_Service SHALL incluir en el Subset las jugadas con `down` igual a 3 o igual a 4.
4. WHEN `down` es 1, 2, 3 o 4, THE Recommend_Service SHALL incluir en el Subset únicamente las jugadas cuyo `down` sea igual a ese valor.
5. IF `down` no es 1, 2, 3, 4 ni `3-4` (incluidos 0, valores negativos, valores mayores que 4 y texto no numérico), THEN THE Recommend_Service SHALL responder HTTP 422 con un mensaje en español que nombre el parámetro `down` y SHALL NOT calcular ni devolver recomendaciones.
6. IF `yards_to_go_bucket` no es exactamente `corta`, `media` ni `larga` (sensible a mayúsculas), THEN THE Recommend_Service SHALL responder HTTP 422 con un mensaje en español que nombre el parámetro `yards_to_go_bucket` y SHALL NOT calcular ni devolver recomendaciones.
7. IF `coverage`, `formation` o `defenders_in_box` tienen un valor que no aparece en la columna correspondiente de Plays_Store, THEN THE Recommend_Service SHALL responder HTTP 422 con un mensaje en español que nombre el parámetro y el valor recibido, y SHALL NOT calcular ni devolver recomendaciones.
8. IF más de un parámetro es inválido en la misma solicitud, THEN THE Recommend_Service SHALL responder HTTP 422 con un mensaje en español que nombre todos los parámetros inválidos.
9. WHEN todos los parámetros enviados son válidos y el Subset tiene 0 jugadas, THE Recommend_Service SHALL responder HTTP 200 con n igual a 0 en todos los grupos y un Verdict que indique que no hay jugadas para la situación elegida.
10. THE Recommend_Service SHALL excluir del Subset toda jugada con `down` igual a 0, por ser atípica, aun cuando no se envíe el parámetro `down`.

### Requirement 4: Comparativa Play Action contra dropback tradicional

**User Story:** Como coach ofensivo, quiero comparar Play Action con dropback tradicional en mi situación, para decidir la llamada.

#### Acceptance Criteria

1. WHEN se recibe `GET /api/recommend` con un Situation_Filter válido, THE Recommend_Service SHALL devolver para Play_Action_Group y Traditional_Group: n (entero ≥ 0), Success_Rate (porcentaje de 0 a 100 con 1 decimal), Wilson_CI, media de `prePenaltyPlayResult` (yardas, con 2 decimales) y promedio de `lb_bite_yards` (yardas, con 2 decimales).
2. THE Recommend_Service SHALL calcular el Wilson_CI con z igual a 1.96 y devolver los límites inferior y superior en porcentaje, entre 0 y 100, con 1 decimal.
3. THE Recommend_Service SHALL calcular el promedio de `lb_bite_yards` solo con valores no nulos y devolver el conteo de valores usados (entero entre 0 y n del grupo).
4. IF el promedio de `lb_bite_yards` de un grupo no tiene valores no nulos, THEN THE Recommend_Service SHALL devolver el promedio como nulo y el conteo de valores usados igual a 0.
5. IF el n de un grupo es mayor que 0 y menor que 30, THEN THE Recommend_Service SHALL marcar ese grupo con la etiqueta "Muestra insuficiente (n < 30)" y seguir devolviendo sus métricas calculadas.
6. IF el n de un grupo es 0, THEN THE Recommend_Service SHALL devolver valores nulos para Success_Rate, Wilson_CI, media de `prePenaltyPlayResult` y promedio de `lb_bite_yards`, y la etiqueta de Insufficient_Sample.
7. WHEN ambos grupos tienen n mayor que 0, THE Recommend_Service SHALL devolver el Effect_pp de Play_Action_Group menos Traditional_Group, en puntos porcentuales con 1 decimal, y un intervalo de confianza del 95% de esa diferencia con límites inferior y superior en puntos porcentuales.
8. IF algún grupo tiene n igual a 0, THEN THE Recommend_Service SHALL devolver el Effect_pp y su intervalo de confianza como nulos.
9. FOR ALL Subsets, n de Play_Action_Group más n de Traditional_Group SHALL ser igual al tamaño del Subset (propiedad de invariante).
10. FOR ALL grupos con n mayor que 0, el límite inferior del Wilson_CI SHALL ser menor o igual que Success_Rate y este menor o igual que el límite superior, con ambos límites entre 0 y 100 (propiedad de invariante).
11. WHEN el Situation_Filter está vacío, THE Recommend_Service SHALL devolver valores que coinciden con la sección "Total" del Bloque A de `COACH_INSIGHTS.md` para n (2,024 y 6,498) y diferencia de Success_Rate (6.809 pp, con tolerancia de 0.01 pp).

### Requirement 5: Comparativa Blitz contra cobertura estándar

**User Story:** Como coordinador defensivo y coach ofensivo, quiero comparar el blitz con la cobertura estándar, para entender presión y riesgo.

#### Acceptance Criteria

1. WHEN se recibe `GET /api/recommend`, THE Recommend_Service SHALL devolver para Blitz_Group y Standard_Group: n (entero ≥ 0), Success_Rate ofensiva con Wilson_CI (95%, valores en porcentaje con 1 decimal, límites entre 0.0 y 100.0), proporción de `any_pressure` (porcentaje con 1 decimal), media de `time_to_throw` (segundos, 2 decimales) y media de `min_rusher_dist_at_throw` (yardas, 2 decimales).
2. THE Recommend_Service SHALL calcular cada media excluyendo solo los valores nulos de esa métrica y devolver el conteo de valores no nulos usado por cada métrica.
3. WHEN el n de un grupo es menor que 30, THE Recommend_Service SHALL marcar ese grupo con la etiqueta "Muestra insuficiente (n < 30)" y SHALL seguir devolviendo sus métricas calculadas.
4. IF el n de un grupo es 0 o una métrica no tiene valores no nulos, THEN THE Recommend_Service SHALL devolver valor nulo para esa métrica (sin error de ejecución), conteo 0 para esa métrica, y SHALL devolver como nula la diferencia correspondiente del criterio 5.
5. THE Recommend_Service SHALL devolver la diferencia Blitz_Group menos Standard_Group para Success_Rate (en pp, 1 decimal), `any_pressure` (en pp, 1 decimal), `time_to_throw` (en segundos, 2 decimales) y `min_rusher_dist_at_throw` (en yardas, 2 decimales).
6. FOR ALL Subsets, n de Blitz_Group más n de Standard_Group SHALL ser igual al tamaño del Subset (propiedad de invariante).
7. WHEN el Situation_Filter está vacío, THE Recommend_Service SHALL devolver `any_pressure` de 47.3% para Blitz_Group y 33.8% para Standard_Group, con tolerancia de 0.1 pp, según `COACH_INSIGHTS.md`.

### Requirement 6: Física del tracking agregada

**User Story:** Como coach, quiero ver cómo `lb_bite_yards` y `protection_advantage` se relacionan con la presión y el éxito, para entender el mecanismo detrás de la recomendación.

#### Acceptance Criteria

1. WHEN se recibe `GET /api/recommend` con un Subset válido, THE Recommend_Service SHALL devolver, para el Subset, una tabla por rangos de `lb_bite_yards` en la que cada fila contenga el rango, n (entero ≥ 0), Success_Rate de Play_Action_Group y Success_Rate de Traditional_Group, y la proporción de `any_pressure` de cada grupo (`pa_pressure_rate`, `trad_pressure_rate`, nula si el grupo está vacío), expresadas como proporción entre 0.000 y 1.000 con 3 decimales.
2. THE Recommend_Service SHALL agrupar `lb_bite_yards` en los rangos [mínimo, 0.10), [0.10, 0.69), [0.69, 1.16) y [1.16, máximo], con intervalos cerrados a la izquierda y con los bordes 0.10, 0.69 y 1.16 yardas, como en `COACH_INSIGHTS.md`.
3. WHEN se recibe `GET /api/recommend` con un Subset válido, THE Recommend_Service SHALL devolver una tabla con una fila por cada categoría de `protection_advantage` (`-2 a -1`, `0`, `1`, `2`, `3 a 6`), en la que cada fila contenga n (entero ≥ 0), la proporción de `any_pressure` y el Success_Rate, expresadas como proporción entre 0.000 y 1.000 con 3 decimales.
4. IF una fila de cualquiera de las tablas tiene n menor que 30, THEN THE Recommend_Service SHALL marcar esa fila con la etiqueta "Muestra insuficiente (n < 30)" y conservar en la fila los valores calculados.
5. IF una fila tiene n igual a 0 o un grupo (Play_Action_Group o Traditional_Group) sin jugadas, THEN THE Recommend_Service SHALL devolver la fila con n igual a 0 y las tasas correspondientes como nulas, sin omitir la fila ni devolver un error.
6. THE Recommend_Service SHALL excluir de cada tabla solo las jugadas con valor nulo en la columna usada para agrupar, e incluir en el cálculo de n y de las tasas todas las demás jugadas del Subset.

### Requirement 7: Recomendación táctica automática

**User Story:** Como coach, quiero una recomendación clara en español, para tomar una decisión sin interpretar tablas.

#### Acceptance Criteria

1. WHEN se recibe `GET /api/recommend` con un Situation_Filter válido, THE Recommend_Service SHALL devolver un Verdict con un código de acción (`LLAMAR_PLAY_ACTION`, `EVITAR_PLAY_ACTION`, `SIN_VENTAJA_CLARA` o `MUESTRA_INSUFICIENTE`), un texto en español de máximo 280 caracteres, el Effect_pp en puntos porcentuales con un decimal y su intervalo de confianza del 95% con límite inferior y superior en puntos porcentuales con un decimal.
2. WHEN ambos grupos tienen n de 30 o más y el límite inferior del intervalo de Effect_pp es mayor que 0, THE Recommend_Service SHALL devolver `LLAMAR_PLAY_ACTION` con texto "LLAMAR PLAY ACTION (+X.X pp de éxito esperado)", donde X.X es el Effect_pp con un decimal.
3. WHEN ambos grupos tienen n de 30 o más y el límite superior del intervalo de Effect_pp es menor que 0, THE Recommend_Service SHALL devolver `EVITAR_PLAY_ACTION` con texto que incluya el valor absoluto del Effect_pp con un decimal seguido de "pp".
4. WHEN el Situation_Filter selecciona la cobertura `Red Zone` y se cumple la condición de `EVITAR_PLAY_ACTION`, THE Recommend_Service SHALL devolver el texto "EVITAR PLAY ACTION EN RED ZONE" seguido del valor absoluto del Effect_pp con un decimal y "pp".
5. WHEN ambos grupos tienen n de 30 o más y el límite inferior del intervalo de Effect_pp es menor o igual que 0 y el límite superior es mayor o igual que 0, THE Recommend_Service SHALL devolver `SIN_VENTAJA_CLARA` con un texto que indique que la diferencia no es concluyente.
6. IF algún grupo de la comparación Play Action tiene n menor que 30, THEN THE Recommend_Service SHALL devolver `MUESTRA_INSUFICIENTE` con un texto que indique el n de cada grupo, y SHALL devolver Effect_pp e intervalo de confianza como nulos cuando alguno de los grupos tenga n igual a 0.
7. WHEN ambos grupos de blitz tienen n de 30 o más, THE Recommend_Service SHALL incluir en el Verdict una nota sobre blitz que cite la diferencia de `any_pressure` en pp con un decimal.
8. THE Recommend_Service SHALL calcular el Verdict solo con `is_success` y no con `prePenaltyPlayResult`, y SHALL incluir en el texto una aclaración de que el éxito se mide por down y distancia y de que no hay EPA.
9. FOR ALL Subsets, el signo de Effect_pp en el Verdict SHALL coincidir con el signo de la diferencia de Success_Rate devuelta en el criterio 4.7 (propiedad de invariante), considerando el signo igual cuando ambos valores son 0.0 tras redondear a un decimal.

### Requirement 8: Selección de jugada real

**User Story:** Como coach, quiero ver una jugada real que ilustre la situación elegida, para validar visualmente los números.

#### Acceptance Criteria

1. WHEN se recibe `GET /api/sample-play` con un Situation_Filter, THE Sample_Play_Service SHALL seleccionar una jugada del Subset cuyo `has_tracking` sea verdadero y cuyos `snap_frameId` y `res_frameId` sean no nulos.
2. WHERE el Subset contiene jugadas de Play_Action_Group con `is_success = 1` y `lb_bite_yards` mayor o igual que 1.16, THE Sample_Play_Service SHALL seleccionar la jugada únicamente entre esas jugadas preferentes y SHALL responder con `preferred = true`.
3. WHERE el Subset contiene jugadas de Blitz_Group con `any_pressure = 1`, THE Sample_Play_Service SHALL incluir esas jugadas en el conjunto de candidatas preferentes junto con las del criterio 2 y SHALL responder con `preferred = true` si elige una de ellas.
4. IF el Subset contiene jugadas con tracking pero ninguna cumple los criterios preferentes de los criterios 2 y 3, THEN THE Sample_Play_Service SHALL seleccionar cualquier jugada del Subset que cumpla el criterio 1 y SHALL responder con `preferred = false`.
5. WHEN el parámetro opcional `exclude` contiene una lista de identificadores de jugadas (máximo 100, separados por coma), THE Sample_Play_Service SHALL seleccionar una jugada cuyo identificador no esté en la lista, siempre que exista alguna candidata que cumpla el criterio 1 fuera de ella.
6. IF todas las candidatas que cumplen el criterio 1 están en `exclude`, THEN THE Sample_Play_Service SHALL seleccionar una de ellas ignorando `exclude`.
7. IF el Subset no contiene jugadas que cumplan el criterio 1, THEN THE Sample_Play_Service SHALL responder HTTP 404 con un mensaje en español que indique que no hay jugadas con tracking para la situación elegida, sin devolver datos de jugada.
8. IF el Tracking_File de la jugada elegida no existe, THEN THE Sample_Play_Service SHALL probar las demás candidatas, primero las preferentes y después las no preferentes, hasta un máximo de 20 intentos, y SHALL responder con la primera cuyo Tracking_File exista.
9. IF no existe el Tracking_File de ninguna candidata probada, THEN THE Sample_Play_Service SHALL responder HTTP 503 con un mensaje en español que indique la ruta esperada del directorio de tracking, sin devolver datos de jugada.

### Requirement 9: Lectura de tracking y normalización

**User Story:** Como coach, quiero ver las trayectorias de los jugadores de la jugada elegida, para entender el movimiento de linebackers y rushers.

#### Acceptance Criteria

1. WHEN Sample_Play_Service lee tracking para la jugada elegida, THE Sample_Play_Service SHALL leer solo el Tracking_File correspondiente al `gameId` de la jugada y devolver solo las filas con ese `playId`.
2. THE Sample_Play_Service SHALL leer el Tracking_File en bloques de como máximo 100,000 filas, cargando solo las columnas necesarias para los campos devueltos, y SHALL abrir exactamente 1 de los 122 Tracking_File por petición.
3. WHEN Sample_Play_Service devuelve los frames de la jugada, THE Sample_Play_Service SHALL incluir únicamente los frames con `frameId` entre el `frameId` del evento `ball_snap` y el `frameId` del evento `pass_forward`, ambos inclusive, ordenados por `frameId` ascendente.
4. WHEN Sample_Play_Service devuelve datos de un jugador, THE Sample_Play_Service SHALL incluir por cada jugador y frame los campos `nflId`, `frameId`, `x_norm`, `y_norm`, `s` y `a`, además de la posición del balón (`x_norm`, `y_norm`) por frame.
5. WHEN `playDirection` es `left`, THE Sample_Play_Service SHALL calcular `x_norm` como 120 menos `x` y `y_norm` como 53.3 menos `y`.
6. WHEN `playDirection` es `right`, THE Sample_Play_Service SHALL devolver `x_norm` igual a `x` y `y_norm` igual a `y`.
7. WHEN Sample_Play_Service devuelve un jugador, THE Sample_Play_Service SHALL asignarle exactamente un rol entre `QB`, `Pass Route`, `Pass Block`, `Pass Rush`, `Coverage` y `LB`, usando `pff_role` y `pff_positionLinedUp` de `pffScoutingData.csv` para esa jugada, y SHALL asignar el rol `Football` al balón.
8. WHEN Sample_Play_Service devuelve la jugada elegida, THE Sample_Play_Service SHALL incluir en la misma respuesta que las coordenadas los valores de `lb_bite_yards`, `min_rusher_dist_at_throw`, `time_to_throw`, `pff_playAction`, `is_blitz`, `any_pressure` e `is_success`, y SHALL devolver `null` en cada campo cuyo valor no esté disponible.
9. THE Sample_Play_Service SHALL excluir las filas con `team` igual a `football` de la lista de jugadores y de las métricas de velocidad por jugador, y SHALL devolver la posición del balón en un campo aparte de la lista de jugadores.
10. FOR ALL jugadores y frames devueltos, THE Sample_Play_Service SHALL devolver `x_norm` y `y_norm` tales que aplicar la normalización inversa según `playDirection` produzca `x` y `y` originales con una diferencia absoluta menor o igual a 0.01 yardas (propiedad de ida y vuelta).
11. THE Sample_Play_Service SHALL devolver `x_norm` creciente hacia la zona de anotación ofensiva en todas las jugadas, de modo que el ataque apunte siempre a la derecha del Coach_Board.
12. IF la jugada elegida no tiene evento `ball_snap` o `pass_forward` en su tracking, THEN THE Sample_Play_Service SHALL usar `snap_frameId` y `res_frameId` de Plays_Store como límites del rango de frames y SHALL registrar 1 aviso que indique qué evento faltó.
13. IF la jugada elegida no tiene evento `ball_snap` o `pass_forward` en su tracking y Plays_Store no tiene `snap_frameId` o `res_frameId`, THEN THE Sample_Play_Service SHALL descartar esa jugada, probar otra jugada candidata hasta un máximo de 5 intentos y, si ninguno tiene rango válido, SHALL devolver un error que indique que no hay jugada con tracking utilizable.
14. WHILE el Backend atiende `/api/sample-play`, THE Backend SHALL completar la lectura de tracking de cada petición en menos de 2 segundos medidos en el equipo de desarrollo.

### Requirement 10: Servicio de la aplicación y contrato de despliegue

**User Story:** Como organizador del hackathon, quiero que la app cumpla el contrato de hospedaje, para que AWS la despliegue sin cambios.

#### Acceptance Criteria

1. THE Backend SHALL exponer todos los endpoints de negocio bajo el prefijo de ruta `/api/` y ningún endpoint de negocio fuera de ese prefijo.
2. WHERE existe el directorio `dashboard/dist` al iniciar el Backend, THE Backend SHALL servir el contenido de `dashboard/dist` en el mismo host y puerto que la API, y SHALL responder con el archivo `index.html` a las peticiones GET a la ruta raíz `/`.
3. IF el directorio `dashboard/dist` no existe al iniciar el Backend, THEN THE Backend SHALL iniciar sin error, SHALL seguir respondiendo las rutas bajo `/api/` y SHALL no servir contenido estático.
4. WHEN el Dashboard realiza una llamada a la API, THE Dashboard SHALL usar una ruta relativa sin diagonal inicial (por ejemplo `fetch('api/recommend')`), y el código fuente del Dashboard SHALL contener 0 llamadas a la API con rutas que comiencen con `/`.
5. THE Dashboard SHALL referenciar imágenes, estilos, scripts y enlaces con rutas relativas, y el código fuente y el contenido de `dashboard/dist` SHALL contener 0 apariciones de `localhost`, `127.0.0.1` o URLs que comiencen con `http://` o `https://` en esas referencias.
6. THE Dashboard SHALL conservar en `vite.config.ts` la opción `base: './'` y un proxy de `/api` hacia `http://localhost:8000`.
7. THE Backend SHALL usar como dependencias de terceros únicamente FastAPI, Uvicorn, Pydantic, pandas y numpy, según el stack fijo de `.hackathon/rules.md`.
8. WHILE el Backend está en ejecución, THE Backend SHALL no crear, modificar ni eliminar archivos en disco, incluidos archivos temporales, cachés y registros en archivo.
9. WHERE el Backend se ejecuta en modo desarrollo, THE Backend SHALL incluir la cabecera de permiso CORS solo para el origen `http://localhost:5173` en las respuestas a peticiones con ese origen.
10. WHERE el Backend se ejecuta en modo producción, THE Backend SHALL no incluir cabeceras de permiso CORS en sus respuestas.

### Requirement 11: Panel de control situacional

**User Story:** Como coach, quiero seleccionar la situación de juego en un panel, para ver el análisis de esa situación.

#### Acceptance Criteria

1. WHEN el coach abre el Dashboard, THE Dashboard SHALL mostrar el Panel Izquierdo con cuatro selectores de un solo valor: Down (opciones: Todos, 1, 2, 3-4), Cobertura, Formación y Defensores en la Caja, además del selector de Yardas por Recorrer, y cada selector SHALL tener "Todos" como valor inicial.
2. WHEN el Dashboard recibe una respuesta exitosa de `/api/filters`, THE Dashboard SHALL poblar los selectores de Cobertura, Formación y Defensores en la Caja con los valores devueltos, ordenados alfabéticamente (numéricamente ascendente para Defensores en la Caja), y cada selector SHALL incluir la opción "Todos" como primera opción.
3. THE Dashboard SHALL ofrecer en el selector de Defensores en la Caja las opciones 5, 6, 7 y 8 aunque la API no las devuelva, junto con todas las demás opciones devueltas por la API, sin valores duplicados.
4. THE Dashboard SHALL ofrecer en el selector de Yardas por Recorrer exactamente las opciones "Todos", `corta`, `media` y `larga`.
5. WHEN el coach cambia el valor de un selector, THE Dashboard SHALL solicitar `/api/recommend` con el Situation_Filter que contiene los valores actuales de todos los selectores, y SHALL actualizar los paneles central y derecho en un máximo de 1 s tras recibir la respuesta.
6. WHEN el coach pulsa "Restablecer", THE Dashboard SHALL poner los cinco selectores en "Todos" y solicitar `/api/recommend` una sola vez con el Situation_Filter sin restricciones.
7. WHILE una solicitud a la API está en curso, THE Dashboard SHALL mostrar un indicador de carga en cada panel afectado por esa solicitud y SHALL ocultarlo cuando la solicitud termine con éxito o con error.
8. IF una solicitud a la API falla por error de red, tiempo de espera de 10 s agotado o respuesta con error, THEN THE Dashboard SHALL mostrar en el panel afectado un mensaje de error en español y un botón "Reintentar", y SHALL conservar sin cambios los datos y los valores de los selectores mostrados antes del fallo.
9. WHEN el coach pulsa "Reintentar", THE Dashboard SHALL repetir la solicitud fallida con el Situation_Filter vigente en ese momento y SHALL ocultar el mensaje de error al iniciar la solicitud.
10. WHEN el coach cambia un selector mientras hay una solicitud a `/api/recommend` pendiente, THE Dashboard SHALL descartar la respuesta de la solicitud anterior, sea exitosa o con error, y SHALL mostrar únicamente el resultado de la solicitud más reciente.
11. THE Dashboard SHALL mostrar en español todo el texto de interfaz generado por el Dashboard, incluidos etiquetas, botones, indicadores de carga y mensajes de error.

### Requirement 12: Panel central de decisión y gráficas

**User Story:** Como coach, quiero ver el veredicto y las gráficas comparativas, para justificar la llamada con evidencia.

#### Acceptance Criteria

1. WHEN el backend devuelve un resultado para la situación elegida, THE Dashboard SHALL mostrar en el Panel Central una tarjeta destacada con el texto del Verdict y el Effect_pp en puntos porcentuales con un decimal, junto con los límites inferior y superior de su intervalo de confianza.
2. WHEN el Dashboard muestra la tarjeta del Verdict, THE Dashboard SHALL colorear la tarjeta según el código de acción: verde para `LLAMAR_PLAY_ACTION`, rojo para `EVITAR_PLAY_ACTION`, ámbar para `SIN_VENTAJA_CLARA` y gris para `MUESTRA_INSUFICIENTE`.
3. WHEN el Subset no está vacío, THE Dashboard SHALL mostrar con Recharts una gráfica comparativa de Success_Rate (en porcentaje) y de media de `prePenaltyPlayResult` (en yardas) para Play Action contra Tradicional, con el Wilson_CI como barras de error en Success_Rate.
4. WHEN el Subset no está vacío, THE Dashboard SHALL mostrar con Recharts una gráfica comparativa de Success_Rate (en porcentaje) y de `any_pressure` (en porcentaje de jugadas) para Blitz contra No Blitz.
5. WHEN el Dashboard muestra una barra de grupo, THE Dashboard SHALL mostrar el n de ese grupo como entero junto a la barra.
6. IF un grupo tiene n menor que 30, THEN THE Dashboard SHALL mostrar en ese grupo la advertencia visual con el texto "Muestra insuficiente (n < 30)" y reducir la opacidad de su barra a un valor entre 0.3 y 0.5.
7. WHEN el Subset no está vacío, THE Dashboard SHALL mostrar con Recharts una gráfica de Física del Tracking con el Success_Rate y la presión por cada rango de `lb_bite_yards` y por cada categoría de `protection_advantage`.
8. IF un valor a graficar es nulo, THEN THE Dashboard SHALL mostrar un guion "–" en lugar de un número y omitir la barra correspondiente sin afectar las demás barras.
9. IF el Subset está vacío, THEN THE Dashboard SHALL mostrar un mensaje en español que indique que no hay jugadas para la situación elegida y ocultar la tarjeta del Verdict y todas las gráficas.
10. THE Dashboard SHALL mostrar un pie de nota con el texto del alcance de los datos: solo jugadas de pase, 8 semanas de la temporada 2021, sin EPA.
11. THE Dashboard SHALL usar un tema oscuro de alto contraste, con una relación de contraste de al menos 4.5:1 entre el color del texto y el color de fondo en todos los textos del Panel Central.

### Requirement 13: Pizarra de tracking

**User Story:** Como coach, quiero ver una jugada real sobre una cancha, para entender el desplazamiento de linebackers y la presión.

#### Acceptance Criteria

1. THE Dashboard SHALL mostrar en el Panel Derecho un SVG de una sección de cancha NFL con líneas de yarda cada 5 yardas y números de yarda cada 10 yardas.
2. WHEN el Dashboard recibe una respuesta exitosa de `/api/sample-play`, THE Dashboard SHALL dibujar un marcador por cada jugador devuelto en su posición del Playback_Frame seleccionado (inicialmente `ball_snap`) y una trayectoria por jugador que una sus posiciones desde `ball_snap` hasta `pass_forward` (el requisito 17 define el avance del Playback_Frame).
3. THE Dashboard SHALL distinguir cada uno de los roles QB, Pass Route, Pass Block, Pass Rush, Coverage y LB con una combinación única de color y forma, y SHALL mostrar una leyenda con los 6 roles junto a la pizarra.
4. WHEN el Dashboard dibuja una jugada, THE Dashboard SHALL dibujar para cada LB una flecha desde su posición en `ball_snap` hasta su posición en `pass_forward`, y SHALL mostrar el valor de `lb_bite_yards` de la jugada en yardas con 1 decimal.
5. WHEN el Dashboard dibuja una jugada con al menos un jugador con rol Pass Rush, THE Dashboard SHALL dibujar una línea entre el QB y el jugador Pass Rush más cercano al QB en `pass_forward`, con la etiqueta de `min_rusher_dist_at_throw` en yardas con 1 decimal.
6. WHEN el Dashboard dibuja una jugada, THE Dashboard SHALL ajustar la ventana visible de la cancha de modo que las posiciones de todos los jugadores devueltos en todos los frames de `ball_snap` a `pass_forward` queden dentro de ella con un margen de 3 yardas en cada borde.
7. WHEN el Dashboard dibuja una jugada, THE Dashboard SHALL mostrar los metadatos: equipo ofensivo, equipo defensivo, semana, down, yardas por recorrer, cobertura, formación, Play Action (Sí/No), Blitz (Sí/No) y jugada exitosa (Sí/No), y SHALL mostrar "No disponible" para cualquier metadato ausente en la respuesta.
8. WHEN el coach pulsa "Cargar otra jugada real", THE Dashboard SHALL solicitar `/api/sample-play` con el Situation_Filter vigente y la lista `exclude` con los identificadores de todas las jugadas ya mostradas desde el último reinicio de `exclude`, y SHALL deshabilitar el botón hasta recibir la respuesta.
9. WHEN el coach cambia el Situation_Filter, THE Dashboard SHALL vaciar la lista `exclude` y solicitar `/api/sample-play` con el nuevo filtro.
10. IF `/api/sample-play` responde 404 o 503, THEN THE Dashboard SHALL mostrar en el Coach_Board el mensaje de la API en español, conservar visible la última jugada dibujada sin cambios, y mantener los paneles izquierdo y central sin cambios y operativos.
11. THE Dashboard SHALL ofrecer el Playback_Controller definido en el requisito 17, que anima los frames de `ball_snap` a `pass_forward` a 10 frames por segundo y conserva el control "Ir a pass_forward" que muestra de inmediato el frame de `pass_forward`.
12. THE Dashboard SHALL mostrar en la pizarra el texto exacto "Jugada real de ejemplo: ilustra, no prueba, la tendencia".

### Requirement 14: Figuras estáticas de respaldo

**User Story:** Como miembro del equipo, quiero figuras estáticas con los hallazgos, para presentar aunque la aplicación no esté disponible.

#### Acceptance Criteria

1. WHEN se ejecuta `src/plots.py` con `outputs/plays_enriched.csv` disponible, THE Plots_Script SHALL generar los archivos `outputs/fig1_play_action_coverage.png`, `outputs/fig2_lb_bite_box.png` y `outputs/fig3_blitz_protection.png`, sobrescribiendo cualquier versión previa.
2. THE Plots_Script SHALL guardar cada PNG con una resolución de 300 DPI.
3. THE Plots_Script SHALL calcular las cifras de las figuras únicamente a partir de `outputs/plays_enriched.csv` y no abrir ningún archivo de tracking.
4. THE Plots_Script SHALL mostrar en `fig1_play_action_coverage.png` la diferencia de Success_Rate (Play Action menos Tradicional, en pp) por cada valor de `pff_passCoverage`, con su intervalo de confianza del 95 %, y marcar con una etiqueta "no concluyente" las celdas con n menor que 30 en cualquiera de los dos grupos comparados.
5. THE Plots_Script SHALL mostrar en `fig2_lb_bite_box.png` la diferencia de Success_Rate de Play Action (en pp) por cada rango de `lb_bite_yards` y por cada valor de `defendersInBox`, con el n de cada celda visible en la figura.
6. THE Plots_Script SHALL mostrar en `fig3_blitz_protection.png`, por cada categoría de `protection_advantage` y por separado para Blitz y No Blitz, la proporción de `any_pressure` (0 a 100 %) y el Success_Rate (0 a 100 %).
7. THE Plots_Script SHALL escribir en español todos los títulos, etiquetas de ejes, leyendas y marcas de texto de las tres figuras.
8. WHEN la ejecución termina sin errores, THE Plots_Script SHALL imprimir en la salida estándar la ruta de cada uno de los tres archivos generados y terminar con código de salida 0.
9. IF `outputs/plays_enriched.csv` no existe, THEN THE Plots_Script SHALL no generar ni modificar ningún PNG, terminar con código de salida distinto de 0 y mostrar un mensaje en español que nombre `outputs/plays_enriched.csv`.
10. IF la biblioteca de gráficos no está disponible en el entorno, THEN THE Plots_Script SHALL no generar ni modificar ningún PNG, terminar con código de salida distinto de 0 y mostrar un mensaje en español que nombre la dependencia faltante.
11. THE Plots_Script SHALL declarar en su docstring de módulo que matplotlib no pertenece al stack fijo y que su uso está pendiente de la decisión del equipo.
12. FOR ALL celdas mostradas en las figuras que también aparecen en `outputs/COACH_INSIGHTS.md`, THE Plots_Script SHALL producir valores de n idénticos y diferencias de Success_Rate que difieran en 0.01 pp o menos de los de ese documento (propiedad de consistencia).
13. IF una columna requerida (`pff_passCoverage`, `lb_bite_yards`, `defendersInBox`, `protection_advantage`, `any_pressure` o `is_success`) no existe en `outputs/plays_enriched.csv`, THEN THE Plots_Script SHALL no generar ni modificar ningún PNG, terminar con código de salida distinto de 0 y mostrar un mensaje en español que nombre la columna faltante.

### Requirement 15: Verificación y operación

**User Story:** Como miembro del equipo, quiero comandos claros y verificaciones de compilación, para levantar la app sin errores.

#### Acceptance Criteria

1. WHEN se ejecuta `npm run build` en `dashboard/`, THE Dashboard SHALL terminar con código de salida 0, reportar 0 errores de TypeScript y 0 errores de Vite, y generar el directorio `dashboard/dist` que contiene un `index.html`.
2. WHEN se ejecuta `python -c "import backend.main"` desde la raíz del proyecto con `.venv` activado, THE Backend SHALL terminar con código de salida 0 sin escribir ninguna excepción en stderr.
3. WHEN el Backend se ejecuta con Uvicorn y recibe una solicitud GET a `/health`, a `/api/filters` o a `/api/recommend` (esta última con un Situation_Filter vacío), THE Backend SHALL responder HTTP 200 en un máximo de 5 segundos con un cuerpo JSON válido.
4. THE proyecto SHALL documentar en la sección "Cómo correr la app" del Executive_README (requisito 18), como bloques de código copiables, los comandos exactos para crear `.venv`, instalar dependencias del Backend, levantar el Backend con Uvicorn, levantar el Dashboard en desarrollo, construir el Dashboard y ejecutar `src/plots.py`.
5. WHERE existen pruebas en `tests/`, THE proyecto SHALL incluir al menos una prueba automatizada del Recommend_Service por cada invariante de los criterios 4.9, 4.10, 5.6 y 9.10, y al menos una prueba por cada caso de error del requisito 3, y todas SHALL pasar al ejecutarse con `pytest`.
6. IF el directorio de tracking no existe, THEN THE Backend SHALL responder HTTP 200 en `/api/filters` y `/api/recommend` (con un Situation_Filter vacío) en un máximo de 5 segundos, sin finalizar el proceso ni escribir excepciones no controladas en stderr.

### Requirement 16: Escenarios Tácticos Rápidos

**User Story:** Como coach en una presentación, quiero tres botones que configuren la situación y carguen una jugada real representativa con un clic, para mostrar los hallazgos principales sin manipular los filtros a mano.

#### Acceptance Criteria

1. THE Dashboard SHALL mostrar la Scenario_Bar en la parte superior del Panel Izquierdo, encima de los selectores, con exactamente tres botones con los textos "Play Action vs Cover-2 (Caja de 7)", "La Trampa de Red Zone" y "Blitz vs Formación Empty".
2. WHEN el coach pulsa el botón "Play Action vs Cover-2 (Caja de 7)", THE Dashboard SHALL fijar Cobertura en `Cover-2` y Defensores en la Caja en 7, fijar Down, Yardas por Recorrer y Formación en "Todos", y solicitar `/api/recommend` y `/api/sample-play` con `focus=bite`.
3. WHEN el coach pulsa el botón "La Trampa de Red Zone", THE Dashboard SHALL fijar Cobertura en `Red Zone`, fijar Down, Yardas por Recorrer, Formación y Defensores en la Caja en "Todos", y solicitar `/api/recommend` y `/api/sample-play` con `focus=pa_fallida`.
4. WHEN el coach pulsa el botón "Blitz vs Formación Empty", THE Dashboard SHALL fijar Formación en `EMPTY`, fijar Down, Yardas por Recorrer, Cobertura y Defensores en la Caja en "Todos", y solicitar `/api/recommend` y `/api/sample-play` con `focus=blitz_exitoso`.
5. WHEN el coach pulsa un Scenario_Preset, THE Dashboard SHALL vaciar la lista `exclude` del requisito 13.9, marcar visualmente el botón activo con el atributo `aria-pressed="true"` y actualizar los cinco selectores para que reflejen el filtro del escenario.
6. WHEN el coach cambia manualmente un selector o pulsa "Restablecer" con un Scenario_Preset activo, THE Dashboard SHALL quitar la marca de botón activo y cerrar la Scenario_Card.
7. WHEN el Dashboard recibe la respuesta de `/api/recommend` de un Scenario_Preset, THE Dashboard SHALL mostrar una Scenario_Card con cifras tomadas únicamente de esa respuesta, y SHALL no contener en el código fuente ninguna de las cifras "12.3", "24.3", "1.8", "50.9" ni "2.60" como texto o constante de resultado.
8. WHILE el Scenario_Preset `play_action_cover2_caja7` está activo, THE Scenario_Card SHALL mostrar el Effect_pp con su intervalo de confianza del 95%, el n de Play_Action_Group y de Traditional_Group, y el promedio de `lb_bite_yards` de ambos grupos con 2 decimales.
9. WHILE el Scenario_Preset `trampa_red_zone` está activo, THE Scenario_Card SHALL mostrar la diferencia de media de `prePenaltyPlayResult` (Play Action menos Tradicional, en yardas con 2 decimales), el Effect_pp de éxito con su intervalo de confianza del 95% y el código del Verdict.
10. WHILE el Scenario_Preset `blitz_empty` está activo, THE Scenario_Card SHALL mostrar el Success_Rate de Blitz_Group con su Wilson_CI, la media de `time_to_throw` de Blitz_Group en segundos con 2 decimales y su n de valores no nulos, la diferencia de Success_Rate (Blitz menos Standard) con su intervalo de confianza del 95% y el n de ambos grupos.
11. IF el intervalo de confianza del 95% de una diferencia de Success_Rate mostrada en la Scenario_Card contiene el 0, THEN THE Scenario_Card SHALL mostrar junto a esa diferencia la etiqueta "no concluyente" y SHALL no usar los verbos "gana", "pierde", "supera" ni "mejora" en el texto del escenario para describir esa diferencia.
12. IF algún grupo mostrado en la Scenario_Card tiene n menor que 30, THEN THE Scenario_Card SHALL mostrar la etiqueta "Muestra insuficiente (n < 30)" junto a ese grupo.
13. THE Recommend_Service SHALL incluir en la respuesta de `/api/recommend`, además de los campos existentes, el campo `play_action.effect_yards` (media de `prePenaltyPlayResult` de Play_Action_Group menos la de Traditional_Group, en yardas con 2 decimales, nulo si algún grupo tiene n igual a 0) y el campo `blitz.effect_pp_ci` (intervalo de confianza del 95% de la diferencia de Success_Rate Blitz menos Standard, límites inferior y superior en pp con 1 decimal, nulo si algún grupo tiene n igual a 0).
14. THE Recommend_Service SHALL calcular `blitz.effect_pp_ci` con el mismo método de diferencia de proporciones que `play_action` usa para el intervalo del Effect_pp (criterio 4.7).
15. WHEN `/api/sample-play` recibe el parámetro opcional `focus`, THE Sample_Play_Service SHALL restringir el conjunto de candidatas preferentes según el valor: `bite` a jugadas de Play_Action_Group con `is_success = 1` y `lb_bite_yards` mayor o igual que 1.16; `pa_fallida` a jugadas de Play_Action_Group con `is_success = 0`; `blitz_exitoso` a jugadas de Blitz_Group con `is_success = 1`.
16. WHEN `/api/sample-play` recibe `focus`, THE Sample_Play_Service SHALL aplicar el criterio 1 del requisito 8 (tracking disponible) y el parámetro `exclude` del requisito 8 sobre las candidatas preferentes, y SHALL ignorar las preferencias de los criterios 8.2 y 8.3.
17. IF `/api/sample-play` recibe `focus` y ninguna candidata del Subset cumple la preferencia, THEN THE Sample_Play_Service SHALL seleccionar según el criterio 8.4 y responder con `preferred = false`, y THE Scenario_Card SHALL mostrar el texto "Jugada de ejemplo sin el patrón destacado".
18. IF `focus` no es `bite`, `pa_fallida` ni `blitz_exitoso`, THEN THE Sample_Play_Service SHALL responder HTTP 422 con un mensaje en español que nombre el parámetro `focus`.
19. WHEN `/api/sample-play` no recibe `focus`, THE Sample_Play_Service SHALL comportarse según los criterios del requisito 8 sin cambios.
20. WHEN el coach pulsa un Scenario_Preset y la solicitud a `/api/recommend` o `/api/sample-play` falla, THE Dashboard SHALL mostrar el mensaje de error y el botón "Reintentar" del requisito 11.8 solo en el panel afectado, y SHALL conservar la parte de la pantalla cuya solicitud tuvo éxito.
21. THE Dashboard SHALL mostrar en la Scenario_Card el texto "Éxito medido por down y distancia; sin EPA. Una sola jugada ilustra, no prueba." en español.
22. FOR ALL ejecuciones con `outputs/plays_enriched.csv` de 8,522 jugadas, WHEN se solicita `/api/recommend` con cada filtro de Scenario_Preset, THE Recommend_Service SHALL devolver valores dentro de las siguientes tolerancias: para `play_action_cover2_caja7` n de Play_Action_Group igual a 94, n de Traditional_Group igual a 105 y Effect_pp de 24.3 pp ± 0.1; para `trampa_red_zone` n de 80 y 278, `play_action.effect_yards` de -1.79 ± 0.01 y Effect_pp de -0.8 pp ± 0.1 con código `SIN_VENTAJA_CLARA`; para `blitz_empty` n de Blitz_Group igual a 265, Success_Rate de 50.9% ± 0.1 y media de `time_to_throw` de 2.60 s ± 0.01.

### Requirement 17: Animación cuadro por cuadro en la pizarra

**User Story:** Como coach, quiero reproducir la jugada cuadro por cuadro y arrastrar una línea de tiempo, para ver cómo los linebackers avanzan hacia la línea y cómo se cierra el bolsillo.

#### Acceptance Criteria

1. THE Dashboard SHALL mostrar el Playback_Controller debajo de la pizarra con un botón alternable con los textos "Reproducir" y "Pausa", un deslizador de tiempo y el botón "Ir a pass_forward".
2. THE Dashboard SHALL configurar el deslizador con mínimo en el frame de `ball_snap`, máximo en el frame de `pass_forward`, paso de 1 frame y la etiqueta "Tiempo desde el snap: X.X s", donde X.X es (frame actual menos frame de `ball_snap`) dividido entre 10, con 1 decimal.
3. WHEN el Dashboard carga una jugada, THE Dashboard SHALL poner el Playback_Frame en `ball_snap`, dejar la animación en pausa y mostrar el botón con el texto "Reproducir".
4. WHEN el coach pulsa "Reproducir", THE Dashboard SHALL avanzar el Playback_Frame 1 frame cada 100 ms (10 frames por segundo) hasta `pass_forward`, actualizando marcadores, etiquetas, deslizador y métricas en vivo en cada paso.
5. WHEN el Playback_Frame llega a `pass_forward` durante la reproducción, THE Dashboard SHALL detener la animación y mostrar el botón con el texto "Reproducir".
6. WHEN el coach pulsa "Reproducir" con el Playback_Frame en `pass_forward`, THE Dashboard SHALL reiniciar el Playback_Frame en `ball_snap` y comenzar la reproducción.
7. WHEN el coach pulsa "Pausa", THE Dashboard SHALL detener el avance y conservar el Playback_Frame actual.
8. WHEN el coach mueve el deslizador, THE Dashboard SHALL pausar la animación, mostrar el frame seleccionado y mantener el valor del deslizador sincronizado con el Playback_Frame.
9. WHEN el coach pulsa "Ir a pass_forward", THE Dashboard SHALL pausar la animación y mostrar el frame de `pass_forward`.
10. WHEN el coach carga otra jugada o cambia el Situation_Filter, THE Dashboard SHALL detener cualquier animación en curso antes de dibujar la nueva jugada.
11. THE Dashboard SHALL mostrar encima de cada marcador de jugador su Player_Label, y SHALL mostrar solo un Player_Label por jugador.
12. THE Sample_Play_Service SHALL incluir en cada jugador de la respuesta de `/api/sample-play`, además de los campos del criterio 9.4, el campo `position` con el valor de `pff_positionLinedUp` (nulo si no está disponible) y el campo `label` con el Player_Label calculado según los criterios 13 a 17.
13. WHEN el rol de un jugador es `QB`, THE Sample_Play_Service SHALL asignar `label` igual a "QB".
14. WHEN el rol de un jugador es `LB`, THE Sample_Play_Service SHALL asignar `label` igual a "LB".
15. WHEN el rol de un jugador es `Pass Route`, THE Sample_Play_Service SHALL asignar `label` igual a `position` si `position` no es nulo, y "WR" en caso contrario.
16. WHEN el rol de un jugador es `Pass Rush`, THE Sample_Play_Service SHALL asignar `label` igual a "Rush", incluso si `position` indica un linebacker o un liniero defensivo.
17. WHEN el rol de un jugador es `Pass Block` o `Coverage`, THE Sample_Play_Service SHALL asignar `label` igual a `position` si `position` no es nulo, y "OL" (Pass Block) o "DB" (Coverage) en caso contrario, de modo que los bloqueadores muestren posiciones como LT, LG, C, RG, RT, TE o HB y la cobertura muestre posiciones como CB, FS o SS.
18. THE Dashboard SHALL mostrar el Player_Label de los jugadores con rol `Pass Route`, `Pass Block` y `Coverage` con tamaño de texto menor que el de QB, LB y Rush, para que las etiquetas de QB, LB y Rush resulten legibles en la pizarra.
19. WHILE el Playback_Frame cambia, THE Dashboard SHALL mostrar la métrica en vivo "Avance de LB": promedio, sobre los jugadores con rol `LB` del equipo defensivo, de la `x_norm` en `ball_snap` menos la `x_norm` en el Playback_Frame, en yardas con 1 decimal.
20. WHILE el Playback_Frame cambia, THE Dashboard SHALL mostrar la métrica en vivo "Distancia QB–Rush más cercano": distancia euclidiana, en yardas con 1 decimal, entre el QB y el jugador con rol `Pass Rush` más cercano en el Playback_Frame.
21. WHEN el Playback_Frame es el frame `ball_snap` más 10, THE Dashboard SHALL mostrar junto al "Avance de LB" el valor de `lb_bite_yards` devuelto por la API como referencia, con el texto "Referencia lb_bite_yards (1 s tras el snap)".
22. WHEN el Playback_Frame es `pass_forward`, THE Dashboard SHALL mostrar junto a la "Distancia QB–Rush más cercano" el valor de `min_rusher_dist_at_throw` devuelto por la API como referencia.
23. IF la jugada no tiene jugadores con rol `LB`, rol `Pass Rush` o QB, THEN THE Dashboard SHALL mostrar "–" en la métrica en vivo correspondiente y SHALL seguir animando los demás elementos.
24. IF la jugada tiene un solo frame entre `ball_snap` y `pass_forward`, THEN THE Dashboard SHALL deshabilitar el botón "Reproducir" y el deslizador y mostrar ese frame.
25. FOR ALL jugadas con `lb_bite_yards` no nulo y con el frame `ball_snap` más 10 dentro del rango devuelto, el "Avance de LB" en ese frame SHALL diferir de `lb_bite_yards` en 0.1 yardas o menos (propiedad de consistencia con el pipeline).
26. FOR ALL jugadas con `min_rusher_dist_at_throw` no nulo, la "Distancia QB–Rush más cercano" en `pass_forward` SHALL diferir de `min_rusher_dist_at_throw` en 0.1 yardas o menos (propiedad de consistencia con el pipeline).
27. WHILE la animación está en curso, THE Dashboard SHALL mantener operativos los selectores, el Panel Central y los botones "Cargar otra jugada real" y "Restablecer".

### Requirement 18: Reporte ejecutivo en README.md

**User Story:** Como organizador o jurado, quiero un documento ejecutivo en la raíz del proyecto, para entender el problema, el método, los hallazgos y cómo ejecutar la app sin leer el código.

#### Acceptance Criteria

1. THE Executive_README SHALL estar en `README.md` en la raíz del proyecto, escrito en español, y SHALL contener, en este orden, las secciones "Resumen del problema", "Metodología", "Hallazgos principales", "Limitaciones" y "Cómo correr la app".
2. THE Executive_README SHALL describir en "Resumen del problema" la pregunta táctica de Play Action contra dropback tradicional y de blitz contra cobertura estándar para el perfil Coach, en un máximo de 150 palabras.
3. THE Executive_README SHALL declarar en "Metodología" que el análisis usa 8,522 jugadas de pase válidas de 122 partidos de las semanas 1 a 8 de la temporada 2021, y que la tasa de éxito (`is_success`) se mide por down y distancia a partir de `prePenaltyPlayResult`.
4. THE Executive_README SHALL declarar en "Metodología" que las proporciones llevan intervalos de confianza de Wilson al 95%, que las diferencias entre grupos llevan intervalos de confianza del 95% del método usado en `outputs/COACH_INSIGHTS.md`, y que se marcan como "no concluyente" las celdas con n menor que 30 o con intervalo que contiene el 0.
5. THE Executive_README SHALL presentar en "Hallazgos principales" exactamente tres hallazgos tomados de `outputs/COACH_INSIGHTS.md`, cada uno con título, cifra con su intervalo de confianza y n de cada grupo, y el hallazgo SHALL coincidir en su cifra con `outputs/COACH_INSIGHTS.md` dentro de 0.1 pp o 0.01 yardas.
6. THE Executive_README SHALL incrustar en "Hallazgos principales" las tres imágenes `outputs/fig1_play_action_coverage.png`, `outputs/fig2_lb_bite_box.png` y `outputs/fig3_blitz_protection.png` con la sintaxis de imagen Markdown, rutas relativas sin diagonal inicial y texto alternativo en español, una imagen por hallazgo.
7. THE Executive_README SHALL citar solo hallazgos cuyo intervalo de confianza del 95% excluya el 0 y cuyo n sea de 30 o más en ambos grupos, o SHALL etiquetarlos explícitamente como "no concluyente".
8. THE Executive_README SHALL describir los hallazgos con verbos de asociación (por ejemplo "se asocia con") y SHALL no usar los verbos "causa" ni "garantiza" para ningún resultado.
9. THE Executive_README SHALL declarar en "Limitaciones" que los datos solo incluyen jugadas de pase, que cubren 8 semanas de la temporada 2021, que no hay EPA y que `prePenaltyPlayResult` ignora el efecto de castigos.
10. THE Executive_README SHALL incluir en "Cómo correr la app" los bloques de código copiables del criterio 15.4 y la nota de que `dashboard/dist` se genera con `npm run build` y se sirve desde el mismo puerto que la API.
11. THE Executive_README SHALL listar en "Cómo correr la app" las rutas de la API (`/health`, `/api/filters`, `/api/recommend`, `/api/sample-play`) y mencionar los Scenario_Preset y el Playback_Controller con una frase cada uno.
12. THE Executive_README SHALL no contener llaves, credenciales, contenido de `.env`, ni las cadenas `localhost`, `127.0.0.1` fuera de los bloques de código de ejecución local.
13. IF alguno de los tres archivos de imagen de `outputs/` no existe al redactar o actualizar el Executive_README, THEN THE proyecto SHALL generar primero esos archivos con `src/plots.py` (requisito 14) o SHALL dejar en el README una nota visible que indique el comando para generarlos, y SHALL no dejar enlaces rotos sin esa nota.
14. THE Executive_README SHALL tener una longitud máxima de 1,200 palabras sin contar los bloques de código ni las tablas.
15. THE proyecto SHALL verificar el Executive_README con una revisión que confirme que cada ruta de imagen apunta a un archivo existente, que existen las cinco secciones del criterio 1 y que las cifras del criterio 5 coinciden con `outputs/COACH_INSIGHTS.md`.
