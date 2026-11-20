# DATA_CONTEXT: NFL Big Data Bowl (regional), UNAM

Generado con `src/explore.py` (salida cruda en `src/explore_output.json`). El script no carga ningún CSV completo: lee encabezados, tamaños, conteo aproximado de filas (bytes totales / bytes por fila de la muestra) y las primeras 10,000 filas de cada tabla. Para tracking toma las primeras 10,000 filas de cada uno de los 122 archivos, solo con las columnas necesarias. El vocabulario completo de `event` se verificó leyendo únicamente esa columna en chunks de 200k filas.

Ruta de datos: `data/nfl-big-data-bowl-regional-event-data/data/`

## 1. Diccionario técnico de tablas

| Tabla | Archivo | MB | Filas (aprox.) | Muestra leída | Llave |
|---|---|---|---|---|---|
| games | `games.csv` | 0.006 | 122 | completa | `gameId` |
| plays | `plays.csv` | 2.24 | 8,557 | completa (< 10k) | `gameId`+`playId` |
| players | `players.csv` | 0.10 | 1,679 | completa | `nflId` |
| pffScoutingData | `pffScoutingData.csv` | 12.41 | 188,250 | 10,000 | `gameId`+`playId`+`nflId` |
| tracking | `tracking/tracking_[gameId].csv` (122 archivos) | 810.47 | 8,360,171 | 10,000 por archivo | `gameId`+`playId`+`nflId`+`frameId` |

Los 122 archivos de tracking tienen encabezado idéntico y sus `gameId` coinciden exactamente con `games.csv`. El balón es la fila con `nflId` nulo y `team == "football"`.

### games (7 columnas)
`gameId` int64, `season` int64, `week` int64, `gameDate` object (mm/dd/yyyy), `gameTimeEastern` object, `homeTeamAbbr` object, `visitorTeamAbbr` object.

### plays (32 columnas, % nulos)
- Identificación: `gameId` int64, `playId` int64, `playDescription` object.
- Situación: `quarter` int64, `down` int64, `yardsToGo` int64, `possessionTeam` object, `defensiveTeam` object, `yardlineSide` object (1.5% nulo), `yardlineNumber` int64, `absoluteYardlineNumber` float64, `gameClock` object, `preSnapHomeScore` int64, `preSnapVisitorScore` int64.
- Resultado: `passResult` object (0% nulo), `prePenaltyPlayResult` int64, `playResult` int64, `penaltyYards` float64 (91% nulo), `foulName1..3` object y `foulNFLId1..3` float64 (91% a 100% nulo).
- Esquema: `offenseFormation` object, `personnelO` object, `personnelD` object, `defendersInBox` float64, `dropBackType` object (6.2% nulo), `pff_playAction` int64, `pff_passCoverage` object, `pff_passCoverageType` object.

### players (7 columnas)
`nflId` int64, `height` object (formato `"6-4"`), `weight` int64 (158 a 380 lb, media 246), `birthDate` object (13.8% nulo), `collegeName` object (13.3% nulo, 236 universidades), `officialPosition` object, `displayName` object.

### pffScoutingData (15 columnas)
`gameId`, `playId`, `nflId` (int64); `pff_role` object; `pff_positionLinedUp` object; `pff_hit`, `pff_hurry`, `pff_sack` float64 (solo defensa, ~50% nulo); `pff_beatenByDefender`, `pff_hitAllowed`, `pff_hurryAllowed`, `pff_sackAllowed`, `pff_nflIdBlockedPlayer`, `pff_blockType` object, `pff_backFieldBlock` (solo bloqueadores, ~75% nulo).

### tracking (16 columnas, % nulos en la muestra)
`gameId` int64, `playId` int64, `nflId` float64 (4.3% nulo = balón), `frameId` int64, `time` object, `jerseyNumber` float64, `team` object, `playDirection` object (`left`/`right`), `x`, `y`, `s` (yd/s), `a` (yd/s²), `dis` (yd), `o` (grados), `dir` (grados) float64, `event` object (91.9% nulo).

### Llaves de unión (verificadas en la muestra)
```
games.gameId ──< plays(gameId, playId) ──< pffScoutingData(gameId, playId, nflId) >── players.nflId
                       └──< tracking_[gameId](gameId, playId, nflId, frameId)   (tracking.nflId >── players.nflId)
```
- `plays.gameId` está en `games`: 100%.
- `pffScoutingData.nflId` está en `players`: 100% (muestra).
- `pffScoutingData(gameId, playId)` está en `plays`: 100% (muestra).
- `plays(gameId, playId)` sin duplicados.
- No verifiqué la unión tracking↔plays jugada por jugada (habría que leer los 810 MB). Verifiqué solo que los `gameId` de tracking coinciden con `games`.

### Horizonte temporal
Una sola temporada (2021), semanas 1 a 8, 122 juegos, del 09/09/2021 al 01/11/2021, 32 equipos. El README de los datos indica que el tracking cubre las mismas 122 juegos.

## 2. Valores únicos de columnas clave

**`tracking.event`** (escaneo completo por chunks; cuenta filas, y cada evento se repite en ~23 filas por frame, una por jugador y balón):
`ball_snap` 196,236 · `pass_forward` 173,604 · `autoevent_ballsnap` 86,641 · `autoevent_passforward` 85,882 · `play_action` 45,471 · `run` 10,902 · `qb_sack` 10,373 · `pass_arrived` 8,441 · `autoevent_passinterrupted` 4,623 · `man_in_motion` 4,071 · `line_set` 3,220 · `shift` 3,059 · `pass_tipped` 2,553 · `first_contact` 1,840 · `qb_strip_sack` 1,334 · `pass_outcome_incomplete` 920 · `pass_outcome_caught` 529 · `fumble` 391 · `fumble_offense_recovered` 253 · `handoff` 230 · `huddle_break_offense` 69 · `tackle` 69 · `penalty_flag` 46 · `lateral` 23 · `dropped_pass` 23 · `out_of_bounds` 23.

**plays** (completo):
- `down`: 1 (3,071), 2 (2,826), 3 (2,394), 4 (231), 0 (35, valor atípico a revisar).
- `quarter`: 1 a 4, más 5 (98, tiempo extra).
- `passResult`: C 4,620 · I 2,755 · S 543 · R 449 · IN 190. Ninguna jugada tiene `passResult` nulo.
- `offenseFormation`: SHOTGUN 5,481 · EMPTY 1,396 · SINGLEBACK 1,189 · I_FORM 298 · PISTOL 154 · JUMBO 30 · WILDCAT 2.
- `personnelO`: 30 valores (el más común, `1 RB, 1 TE, 3 WR`: 5,750). `personnelD`: 29 valores (el más común, `4 DL, 2 LB, 5 DB`: 2,420).
- `defendersInBox`: 1 a 11 (moda 6: 4,003).
- `dropBackType`: TRADITIONAL, SCRAMBLE, DESIGNED_ROLLOUT_RIGHT/LEFT, SCRAMBLE_ROLLOUT_RIGHT/LEFT, DESIGNED_RUN, UNKNOWN.
- `pff_playAction`: 0 (6,519), 1 (2,038).
- `pff_passCoverage`: Cover-3 2,665 · Cover-1 2,011 · Cover-2 1,085 · Quarters 1,033 · Cover-6 805 · Red Zone 376 · Cover-0 270 · 2-Man 200 · Bracket 47 · Prevent 32 · Goal Line 25 · Miscellaneous 8.
- `pff_passCoverageType`: Zone 5,588 · Man 2,481 · Other 488.
- `playResult`: media 6.56, mediana 5, mínimo -34, máximo 91.

**pffScoutingData** (solo las primeras 10,000 filas, ≈455 jugadas, no representativo de todo el archivo):
- `pff_role`: Coverage, Pass Block, Pass Route, Pass Rush, Pass. La documentación escribe `Pass block` y `Pass rush`, pero el archivo usa mayúscula inicial en cada palabra (`Pass Block`, `Pass Rush`). Hay que filtrar con los valores reales.
- `pff_positionLinedUp`: 56 valores (QB, C, RG, LT, RCB, FS, LEO, SCBR, HB-R, ...).
- `pff_blockType`: PP, PT, PA, SW, CL, CH, NB, PU, BH, SR, UP, PR.
- Eventos de presión en la muestra: hit 54, hurry 155, sack 30 (de ~5,000 filas defensivas).

**players**: 19 `officialPosition` (WR, CB, DE, OLB, RB, T, TE, DT, G, ILB, FS, SS, QB, C, NT, MLB, FB, LB, DB), 236 universidades.

**Valores físicos del tracking en la muestra**: `s` máxima 27.77 yd/s y `a` máxima 30.03 yd/s². Una velocidad de 27.77 yd/s no es humana. Es probable que corresponda al balón o a un error de medición, pero no lo verifiqué. Hay que filtrar por `team != "football"` y revisar atípicos antes de calcular velocidades máximas.

## 3. Lo que NO existe en el workspace

- No hay EPA, WPA, ni probabilidad de victoria. Solo `playResult` (yardas) y el marcador previo a la jugada.
- No hay datos de Combine (40 yardas, salto, press de banca), ni de Draft (ronda, pick), ni ninguna tabla de temporadas anteriores.
- `plays.csv` solo contiene jugadas de pase o dropback (`passResult` siempre presente). No hay jugadas terrestres puras.
- El tracking termina cerca del resultado del pase: solo hay 69 eventos `tackle` y 23 `out_of_bounds`. Las yardas después de la recepción no se pueden medir en tracking.
- Los eventos pre-snap `line_set` (~140 jugadas), `shift` (~133) y `man_in_motion` (~177) son escasos. Estas cifras son una estimación mía: filas del evento divididas entre ~23 filas por frame. Para movimiento pre-snap conviene comparar el primer frame de la jugada contra `ball_snap` en lugar de depender de esos eventos.

## 4. Evaluación de perfiles (1 = no explotable, 5 = muy explotable)

| Perfil | Nota | Por qué |
|---|---|---|
| **Coach** | **4** | Tiene down, distancia, cuarto, reloj, marcador, yarda, formación ofensiva, personal ofensivo y defensivo, defensores en la caja, tipo de dropback, play action y cobertura PFF (12 clases, y Man/Zone). Cruzado con el tracking en el snap permite medir alineación y movimiento. PFF agrega roles y bloqueos para analizar matchups de pass rush contra protección. Señales iniciales ya visibles: play action rinde 7.83 yd frente a 6.17 sin él; Cover-0 concede 5.04 yd y Goal Line/Red Zone 0.64 y 2.30. Limitaciones: sin EPA (se debe usar éxito por down y distancia o yardas), solo pases, solo 8 semanas de una temporada, y muestras pequeñas en celdas raras (Goal Line 25, Misc. 8). |
| **Comentarista** | **3** | El tracking frame por frame (frecuencia de 10 Hz según la convención de NGS, no verificada en las marcas `time`) de ~8.4M filas con `x`, `y`, `s`, `a`, `dis`, `o`, `dir` y eventos claros (`ball_snap`, `pass_forward`, `pass_arrived`, `qb_sack`) permite visuales tipo Next Gen Stats: velocidad del rusher, tiempo de lanzamiento, separación al llegar el pase. Pero faltan eventos de final de jugada (solo 69 `tackle`), así que no hay yardas después de la recepción ni jugadas espectaculares de carrera. Una "probabilidad de éxito" necesita un modelo propio sin EPA. Requiere además más trabajo de ingeniería (normalizar dirección, filtrar atípicos, animar frames). |
| **Scout** | **2** | `players.csv` solo tiene altura, peso, fecha de nacimiento (13.8% nula), universidad (13.3% nula) y posición. No hay Combine ni Draft, así que no se puede contrastar atletismo medido contra impacto. Lo más cercano es derivar velocidad y aceleración desde tracking y contrastarla con métricas PFF (hurry, sack, beaten), pero eso mide rendimiento y no talento de proyección, y 8 semanas son una muestra corta por jugador. |

**Ganador: Coach.** Es el único perfil en el que todas las variables necesarias existen en el workspace, con 8,557 jugadas etiquetadas con cobertura y esquema, y el tracking como capa de verificación. Los otros dos dependen de datos ausentes (Combine, final de jugada, EPA).

## 5. Dos ideas de métrica e hipótesis para el perfil Coach

### Idea 1: Eficiencia del play action condicionada a cobertura y caja
- **Métrica:** `Δ éxito PA` = tasa de éxito (o yardas por dropback) con `pff_playAction = 1` menos sin él, por celda de `pff_passCoverage`/`pff_passCoverageType` × `defendersInBox` × grupo de down y distancia. Éxito por down y distancia: 40% de yardas necesarias en 1ª, 60% en 2ª, 100% en 3ª y 4ª.
- **Hipótesis:** el aumento observado de 1.66 yd (7.83 vs 6.17) no es uniforme: es mayor contra coberturas Man y con cajas de 7 o más defensores, y se reduce o desaparece en Cover-2 y Quarters, donde los safeties no muerden. Es verificable con `plays.csv` completo (8,557 filas) y se puede refinar con tracking midiendo cuánto avanzan los linebackers entre el snap y `pass_forward`.
- **Entregable para el coach:** matriz "cuándo llamar play action" con intervalos de confianza, y marcado de celdas con n < 30 como no concluyentes.

### Idea 2: Ventaja numérica de pass rush y presión permitida
- **Métrica:** `Ventaja de protección` = (número de `Pass Block` − número de `Pass Rush`) por jugada desde `pffScoutingData`, combinada con `pff_beatenByDefender`, `pff_hurryAllowed`/`pff_sackAllowed` y la cobertura (`pff_passCoverageType`). Complemento con tracking: tiempo entre `ball_snap` y `pass_forward` (en frames; asumiendo 10 por segundo, a confirmar con `time`) como "tiempo al lanzamiento".
- **Hipótesis:** las jugadas con rusher extra (blitz) contra coberturas Man (Cover-0 y Cover-1) elevan la probabilidad de presión pero también las yardas concedidas cuando la protección gana, y el tiempo al lanzamiento más corto mitiga el efecto. Para el coach ofensivo: identificar qué formaciones y personal (`personnelO`) producen menos presión permitida; para el coordinador defensivo: qué combinación de personal defensivo y cobertura maximiza presión sin conceder yardas largas.
- **Rigor:** agrupar por jugada (`gameId`, `playId`), no por fila de jugador; usar `Pass Block`/`Pass Rush` con la mayúscula real del archivo; reportar tamaños de muestra por celda.

## 6. Notas de rigor para el siguiente paso
- Procesar el tracking por juego (un archivo a la vez, solo columnas necesarias) y agregar a nivel jugada antes de guardar. Unir a `plays` y `pffScoutingData` solo con las jugadas ya agregadas.
- Normalizar coordenadas con `playDirection` antes de comparar posiciones (equivale a invertir `x` y `y` cuando `playDirection == "left"`).
- Solo hay 8 semanas de una temporada: evitar afirmar tendencias por equipo; mostrar incertidumbre.
- El backend es de solo lectura sobre `data/`, y calcula en el arranque o por petición (el servidor es efímero), según las reglas del proyecto.
