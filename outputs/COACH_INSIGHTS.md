# Coach Insights

## Resumen de cobertura

| Concepto | Valor |
|---|---|
| Jugadas válidas | 8522 |
| `time_to_throw` no nulo | 8036 |
| `min_rusher_dist_at_throw` no nulo | 8057 |
| `lb_bite_yards` no nulo | 8498 |
| `frame_dt_ok` = 1 | 8522 |
| Archivos de tracking procesados (ok) | 122 |
| Archivos de tracking con error | 0 |

## Limitaciones

- Solo hay jugadas de pase (dropbacks); no se describen jugadas de carrera.
- Los datos cubren 8 semanas de la temporada 2021.
- No hay EPA; el éxito se mide con `is_success` a partir de down y distancia.
- El mérito táctico usa `prePenaltyPlayResult`, que ignora el efecto de castigos.

## Bloque A: play action

Diferencia = play action (1) menos sin play action (0). La tasa de éxito va en puntos porcentuales; las otras diferencias, en yardas.

- Jugadas totales: 8522
- Jugadas con `pff_playAction` válido: 8522
- Excluidas por `pff_playAction` nulo: 0

### Total

| Celda | n play action | n sin play action | Diferencia | IC95 | Unidad | Etiquetas |
|---|---|---|---|---|---|---|
| Total: prePenaltyPlayResult | 2024 | 6498 | 1.645 | [1.089, 2.200] | yardas | — |
| Total: playResult | 2024 | 6498 | 1.694 | [1.117, 2.271] | yardas | — |
| Total: tasa de éxito | 2024 | 6498 | 6.809 | [4.316, 9.293] | pp | — |

### Desglose por `pff_passCoverageType` (coverage_type)

Jugadas excluidas por valor nulo en `pff_passCoverageType`: 0

| Celda | n play action | n sin play action | Diferencia | IC95 | Unidad | Etiquetas |
|---|---|---|---|---|---|---|
| Man: prePenaltyPlayResult | 433 | 2032 | 0.853 | [-0.351, 2.056] | yardas | — |
| Man: playResult | 433 | 2032 | 1.399 | [0.145, 2.654] | yardas | — |
| Man: tasa de éxito | 433 | 2032 | 3.492 | [-1.636, 8.663] | pp | — |
| Zone: prePenaltyPlayResult | 1491 | 4096 | 2.161 | [1.506, 2.817] | yardas | — |
| Zone: playResult | 1491 | 4096 | 2.080 | [1.399, 2.762] | yardas | — |
| Zone: tasa de éxito | 1491 | 4096 | 7.530 | [4.568, 10.469] | pp | — |

### Desglose por `pff_passCoverage` (coverage)

Jugadas excluidas por valor nulo en `pff_passCoverage`: 0

| Celda | n play action | n sin play action | Diferencia | IC95 | Unidad | Etiquetas |
|---|---|---|---|---|---|---|
| 2-Man: prePenaltyPlayResult | 7 | 193 | 0.641 | [-8.046, 9.328] | yardas | no concluyente |
| 2-Man: playResult | 7 | 193 | 0.665 | [-7.945, 9.275] | yardas | no concluyente |
| 2-Man: tasa de éxito | 7 | 193 | 25.833 | [-10.394, 47.312] | pp | no concluyente |
| Bracket: prePenaltyPlayResult | 0 | 47 | — | — | yardas | no concluyente, no disponible |
| Bracket: playResult | 0 | 47 | — | — | yardas | no concluyente, no disponible |
| Bracket: tasa de éxito | 0 | 47 | — | — | pp | no concluyente, no disponible |
| Cover-0: prePenaltyPlayResult | 50 | 210 | 2.908 | [-0.691, 6.506] | yardas | — |
| Cover-0: playResult | 50 | 210 | 3.156 | [-0.442, 6.754] | yardas | — |
| Cover-0: tasa de éxito | 50 | 210 | 22.952 | [7.550, 36.648] | pp | — |
| Cover-1: prePenaltyPlayResult | 376 | 1629 | 0.738 | [-0.558, 2.035] | yardas | — |
| Cover-1: playResult | 376 | 1629 | 1.339 | [-0.021, 2.699] | yardas | — |
| Cover-1: tasa de éxito | 376 | 1629 | 0.748 | [-4.748, 6.337] | pp | — |
| Cover-2: prePenaltyPlayResult | 261 | 824 | 3.145 | [1.652, 4.637] | yardas | — |
| Cover-2: playResult | 261 | 824 | 3.240 | [1.648, 4.832] | yardas | — |
| Cover-2: tasa de éxito | 261 | 824 | 12.345 | [5.388, 19.083] | pp | — |
| Cover-3: prePenaltyPlayResult | 832 | 1832 | 2.145 | [1.265, 3.024] | yardas | — |
| Cover-3: playResult | 832 | 1832 | 2.008 | [1.101, 2.915] | yardas | — |
| Cover-3: tasa de éxito | 832 | 1832 | 7.876 | [3.782, 11.923] | pp | — |
| Cover-6: prePenaltyPlayResult | 167 | 638 | 0.708 | [-1.155, 2.571] | yardas | — |
| Cover-6: playResult | 167 | 638 | 1.125 | [-0.812, 3.063] | yardas | — |
| Cover-6: tasa de éxito | 167 | 638 | 5.331 | [-3.162, 13.681] | pp | — |
| Goal Line: prePenaltyPlayResult | 20 | 5 | -0.150 | [-0.958, 0.658] | yardas | no concluyente |
| Goal Line: playResult | 20 | 5 | -0.450 | [-1.440, 0.540] | yardas | no concluyente |
| Goal Line: tasa de éxito | 20 | 5 | -25.000 | [-51.467, 21.580] | pp | no concluyente |
| Miscellaneous: prePenaltyPlayResult | 0 | 8 | — | — | yardas | no concluyente, no disponible |
| Miscellaneous: playResult | 0 | 8 | — | — | yardas | no concluyente, no disponible |
| Miscellaneous: tasa de éxito | 0 | 8 | — | — | pp | no concluyente, no disponible |
| Prevent: prePenaltyPlayResult | 0 | 32 | — | — | yardas | no concluyente, no disponible |
| Prevent: playResult | 0 | 32 | — | — | yardas | no concluyente, no disponible |
| Prevent: tasa de éxito | 0 | 32 | — | — | pp | no concluyente, no disponible |
| Quarters: prePenaltyPlayResult | 231 | 802 | 2.230 | [0.393, 4.066] | yardas | — |
| Quarters: playResult | 231 | 802 | 1.821 | [-0.086, 3.728] | yardas | — |
| Quarters: tasa de éxito | 231 | 802 | 1.793 | [-5.446, 9.071] | pp | — |
| Red Zone: prePenaltyPlayResult | 80 | 278 | -1.795 | [-2.908, -0.682] | yardas | — |
| Red Zone: playResult | 80 | 278 | -1.677 | [-2.908, -0.446] | yardas | — |
| Red Zone: tasa de éxito | 80 | 278 | -0.818 | [-12.341, 11.472] | pp | — |

### Desglose por `defendersInBox` (defenders_in_box)

Jugadas excluidas por valor nulo en `defendersInBox`: 7

| Celda | n play action | n sin play action | Diferencia | IC95 | Unidad | Etiquetas |
|---|---|---|---|---|---|---|
| 1: prePenaltyPlayResult | 0 | 1 | — | — | yardas | no concluyente, no disponible |
| 1: playResult | 0 | 1 | — | — | yardas | no concluyente, no disponible |
| 1: tasa de éxito | 0 | 1 | — | — | pp | no concluyente, no disponible |
| 2: prePenaltyPlayResult | 0 | 5 | — | — | yardas | no concluyente, no disponible |
| 2: playResult | 0 | 5 | — | — | yardas | no concluyente, no disponible |
| 2: tasa de éxito | 0 | 5 | — | — | pp | no concluyente, no disponible |
| 3: prePenaltyPlayResult | 1 | 49 | -5.490 | — | yardas | no concluyente, no disponible |
| 3: playResult | 1 | 49 | -5.531 | — | yardas | no concluyente, no disponible |
| 3: tasa de éxito | 1 | 49 | -42.857 | — | pp | no concluyente, no disponible |
| 4: prePenaltyPlayResult | 5 | 480 | -2.071 | [-6.347, 2.205] | yardas | no concluyente |
| 4: playResult | 5 | 480 | -5.302 | [-12.259, 1.655] | yardas | no concluyente |
| 4: tasa de éxito | 5 | 480 | 0.208 | [-28.377, 37.384] | pp | no concluyente |
| 5: prePenaltyPlayResult | 58 | 1584 | 2.373 | [-0.563, 5.310] | yardas | — |
| 5: playResult | 58 | 1584 | 2.785 | [-0.139, 5.710] | yardas | — |
| 5: tasa de éxito | 58 | 1584 | 4.987 | [-7.715, 17.685] | pp | — |
| 6: prePenaltyPlayResult | 795 | 3199 | 1.629 | [0.764, 2.493] | yardas | — |
| 6: playResult | 795 | 3199 | 1.798 | [0.888, 2.707] | yardas | — |
| 6: tasa de éxito | 795 | 3199 | 5.216 | [1.334, 9.078] | pp | — |
| 7: prePenaltyPlayResult | 793 | 1024 | 2.354 | [1.348, 3.359] | yardas | — |
| 7: playResult | 793 | 1024 | 2.164 | [1.124, 3.204] | yardas | — |
| 7: tasa de éxito | 793 | 1024 | 9.103 | [4.471, 13.684] | pp | — |
| 8: prePenaltyPlayResult | 326 | 142 | 1.522 | [-0.451, 3.495] | yardas | — |
| 8: playResult | 326 | 142 | 1.799 | [-0.209, 3.808] | yardas | — |
| 8: tasa de éxito | 326 | 142 | -2.113 | [-11.806, 7.673] | pp | — |
| 9: prePenaltyPlayResult | 24 | 7 | 0.256 | [-8.051, 8.563] | yardas | no concluyente |
| 9: playResult | 24 | 7 | 1.810 | [-7.483, 11.102] | yardas | no concluyente |
| 9: tasa de éxito | 24 | 7 | 11.310 | [-26.037, 43.757] | pp | no concluyente |
| 10: prePenaltyPlayResult | 10 | 0 | — | — | yardas | no concluyente, no disponible |
| 10: playResult | 10 | 0 | — | — | yardas | no concluyente, no disponible |
| 10: tasa de éxito | 10 | 0 | — | — | pp | no concluyente, no disponible |
| 11: prePenaltyPlayResult | 9 | 3 | 0.111 | [-0.739, 0.962] | yardas | no concluyente |
| 11: playResult | 9 | 3 | 0.111 | [-0.739, 0.962] | yardas | no concluyente |
| 11: tasa de éxito | 9 | 3 | -11.111 | [-50.781, 41.430] | pp | no concluyente |

### Desglose por `lb_bite_yards` (lb_bite_range)

Jugadas excluidas por valor nulo en `lb_bite_yards`: 24
Bordes de rango (yardas): 0.10, 0.69, 1.16. Intervalos cerrados a la izquierda, [inferior, superior). Valores altos indican que los linebackers avanzaron hacia la línea de golpeo (mordieron).

| Celda | n play action | n sin play action | Diferencia | IC95 | Unidad | Etiquetas |
|---|---|---|---|---|---|---|
| < 0.10: prePenaltyPlayResult | 174 | 1935 | 3.355 | [1.558, 5.153] | yardas | — |
| < 0.10: playResult | 174 | 1935 | 2.726 | [0.853, 4.599] | yardas | — |
| < 0.10: tasa de éxito | 174 | 1935 | 13.788 | [6.049, 21.072] | pp | — |
| [0.10, 0.69): prePenaltyPlayResult | 842 | 1282 | 0.951 | [0.044, 1.857] | yardas | — |
| [0.10, 0.69): playResult | 842 | 1282 | 1.131 | [0.188, 2.074] | yardas | — |
| [0.10, 0.69): tasa de éxito | 842 | 1282 | 2.982 | [-1.363, 7.311] | pp | — |
| [0.69, 1.16): prePenaltyPlayResult | 732 | 1400 | 1.179 | [0.185, 2.173] | yardas | — |
| [0.69, 1.16): playResult | 732 | 1400 | 0.880 | [-0.150, 1.909] | yardas | — |
| [0.69, 1.16): tasa de éxito | 732 | 1400 | 5.919 | [1.452, 10.358] | pp | — |
| >= 1.16: prePenaltyPlayResult | 273 | 1860 | 2.599 | [1.024, 4.174] | yardas | — |
| >= 1.16: playResult | 273 | 1860 | 3.210 | [1.552, 4.868] | yardas | — |
| >= 1.16: tasa de éxito | 273 | 1860 | 10.412 | [4.087, 16.681] | pp | — |

## Bloque B: blitz y bolsillo

Blitz = 5 o más rushers. Cada métrica excluye solo sus propios nulos.

- Jugadas totales: 8522
- Jugadas con `is_blitz` válido: 8522
- Excluidas por `is_blitz` nulo: 0

Jugadas excluidas por nulo en cada métrica (conjunto total):

| Métrica | Excluidas |
|---|---|
| any_pressure | 0 |
| min_rusher_dist_at_throw | 465 |
| time_to_throw | 486 |
| is_success | 0 |

### Categorías de `protection_advantage`

Límites calculados una vez sobre el total y aplicados a toda segmentación.

| Categoría | Mínimo | Máximo | n | Etiquetas |
|---|---|---|---|---|
| -2 a -1 | -2 | -1 | 122 | — |
| 0 | 0 | 0 | 1094 | — |
| 1 | 1 | 1 | 5368 | — |
| 2 | 2 | 2 | 1441 | — |
| 3 a 6 | 3 | 6 | 497 | — |

Fusiones:

- Valores -2 a -1 fusionados en una categoría (n = 122).
- Valores 3 a 6 fusionados en una categoría (n = 497).

### Total (n = 8522)

Blitz contra no blitz (diferencia = blitz menos no blitz):

| Métrica | Excluidas por nulo | n blitz | Media blitz | IC95 blitz | n no blitz | Media no blitz | IC95 no blitz | Diferencia | IC95 diferencia | Etiquetas |
|---|---|---|---|---|---|---|---|---|---|---|
| any_pressure (binary) | 0 | 2095 | 0.473 | [0.451, 0.494] | 6427 | 0.338 | [0.326, 0.350] | 0.135 | [0.110, 0.159] | — |
| min_rusher_dist_at_throw (continuous) | 465 | 2019 | 2.670 | [2.612, 2.727] | 6038 | 2.959 | [2.923, 2.995] | -0.290 | [-0.358, -0.222] | — |
| time_to_throw (continuous) | 486 | 2016 | 2.902 | [2.847, 2.958] | 6020 | 3.107 | [3.077, 3.137] | -0.205 | [-0.268, -0.142] | — |
| is_success (binary) | 0 | 2095 | 0.457 | [0.436, 0.478] | 6427 | 0.475 | [0.463, 0.487] | -0.018 | [-0.042, 0.007] | — |

Por categoría de `protection_advantage`:

| Categoría | n total | Métrica | n | Media o proporción | IC95 | Etiquetas |
|---|---|---|---|---|---|---|
| -2 a -1 | 122 | any_pressure | 122 | 0.615 | [0.526, 0.696] | — |
| -2 a -1 | 122 | min_rusher_dist_at_throw | 118 | 2.705 | [2.474, 2.936] | — |
| -2 a -1 | 122 | time_to_throw | 118 | 2.542 | [2.322, 2.761] | — |
| -2 a -1 | 122 | is_success | 122 | 0.393 | [0.311, 0.482] | — |
| 0 | 1094 | any_pressure | 1094 | 0.459 | [0.430, 0.488] | — |
| 0 | 1094 | min_rusher_dist_at_throw | 1052 | 2.661 | [2.586, 2.736] | — |
| 0 | 1094 | time_to_throw | 1050 | 2.777 | [2.696, 2.858] | — |
| 0 | 1094 | is_success | 1094 | 0.470 | [0.440, 0.499] | — |
| 1 | 5368 | any_pressure | 5368 | 0.362 | [0.350, 0.375] | — |
| 1 | 5368 | min_rusher_dist_at_throw | 5078 | 2.799 | [2.763, 2.835] | — |
| 1 | 5368 | time_to_throw | 5062 | 3.019 | [2.987, 3.050] | — |
| 1 | 5368 | is_success | 5368 | 0.470 | [0.457, 0.483] | — |
| 2 | 1441 | any_pressure | 1441 | 0.347 | [0.323, 0.372] | — |
| 2 | 1441 | min_rusher_dist_at_throw | 1342 | 3.193 | [3.105, 3.280] | — |
| 2 | 1441 | time_to_throw | 1338 | 3.348 | [3.283, 3.414] | — |
| 2 | 1441 | is_success | 1441 | 0.473 | [0.448, 0.499] | — |
| 3 a 6 | 497 | any_pressure | 497 | 0.282 | [0.244, 0.323] | — |
| 3 a 6 | 497 | min_rusher_dist_at_throw | 467 | 3.514 | [3.350, 3.677] | — |
| 3 a 6 | 497 | time_to_throw | 468 | 3.375 | [3.276, 3.474] | — |
| 3 a 6 | 497 | is_success | 497 | 0.485 | [0.441, 0.529] | — |

### Segmentación por `pff_passCoverage` (coverage)

Jugadas excluidas por valor nulo en `pff_passCoverage`: 0

#### 2-Man (n = 200)

Blitz contra no blitz (diferencia = blitz menos no blitz):

| Métrica | Excluidas por nulo | n blitz | Media blitz | IC95 blitz | n no blitz | Media no blitz | IC95 no blitz | Diferencia | IC95 diferencia | Etiquetas |
|---|---|---|---|---|---|---|---|---|---|---|
| any_pressure (binary) | 0 | 22 | 0.500 | — | 178 | 0.376 | [0.309, 0.449] | 0.124 | — | n insuficiente |
| min_rusher_dist_at_throw (continuous) | 21 | 20 | 2.203 | — | 159 | 2.718 | [2.540, 2.896] | -0.515 | — | n insuficiente |
| time_to_throw (continuous) | 21 | 20 | 3.290 | — | 159 | 3.302 | [3.105, 3.499] | -0.012 | — | n insuficiente |
| is_success (binary) | 0 | 22 | 0.364 | — | 178 | 0.478 | [0.405, 0.551] | -0.114 | — | n insuficiente |

Por categoría de `protection_advantage`:

| Categoría | n total | Métrica | n | Media o proporción | IC95 | Etiquetas |
|---|---|---|---|---|---|---|
| -2 a -1 | 0 | any_pressure | 0 | — | — | n insuficiente |
| -2 a -1 | 0 | min_rusher_dist_at_throw | 0 | — | — | n insuficiente |
| -2 a -1 | 0 | time_to_throw | 0 | — | — | n insuficiente |
| -2 a -1 | 0 | is_success | 0 | — | — | n insuficiente |
| 0 | 4 | any_pressure | 4 | 0.500 | — | n insuficiente |
| 0 | 4 | min_rusher_dist_at_throw | 4 | 2.495 | — | n insuficiente |
| 0 | 4 | time_to_throw | 4 | 2.500 | — | n insuficiente |
| 0 | 4 | is_success | 4 | 0.250 | — | n insuficiente |
| 1 | 154 | any_pressure | 154 | 0.377 | [0.304, 0.455] | — |
| 1 | 154 | min_rusher_dist_at_throw | 141 | 2.591 | [2.412, 2.769] | — |
| 1 | 154 | time_to_throw | 141 | 3.274 | [3.062, 3.487] | — |
| 1 | 154 | is_success | 154 | 0.468 | [0.390, 0.546] | — |
| 2 | 34 | any_pressure | 34 | 0.412 | [0.264, 0.578] | — |
| 2 | 34 | min_rusher_dist_at_throw | 27 | 2.933 | — | n insuficiente |
| 2 | 34 | time_to_throw | 27 | 3.463 | — | n insuficiente |
| 2 | 34 | is_success | 34 | 0.441 | [0.289, 0.605] | — |
| 3 a 6 | 8 | any_pressure | 8 | 0.500 | — | n insuficiente |
| 3 a 6 | 8 | min_rusher_dist_at_throw | 7 | 3.104 | — | n insuficiente |
| 3 a 6 | 8 | time_to_throw | 7 | 3.657 | — | n insuficiente |
| 3 a 6 | 8 | is_success | 8 | 0.625 | — | n insuficiente |

#### Bracket (n = 47)

Blitz contra no blitz (diferencia = blitz menos no blitz):

| Métrica | Excluidas por nulo | n blitz | Media blitz | IC95 blitz | n no blitz | Media no blitz | IC95 no blitz | Diferencia | IC95 diferencia | Etiquetas |
|---|---|---|---|---|---|---|---|---|---|---|
| any_pressure (binary) | 0 | 6 | 0.000 | — | 41 | 0.439 | [0.299, 0.590] | -0.439 | — | n insuficiente |
| min_rusher_dist_at_throw (continuous) | 2 | 6 | 2.735 | — | 39 | 2.796 | [2.345, 3.248] | -0.061 | — | n insuficiente |
| time_to_throw (continuous) | 2 | 6 | 2.667 | — | 39 | 3.451 | [3.074, 3.829] | -0.785 | — | n insuficiente |
| is_success (binary) | 0 | 6 | 0.500 | — | 41 | 0.439 | [0.299, 0.590] | 0.061 | — | n insuficiente |

Por categoría de `protection_advantage`:

| Categoría | n total | Métrica | n | Media o proporción | IC95 | Etiquetas |
|---|---|---|---|---|---|---|
| -2 a -1 | 0 | any_pressure | 0 | — | — | n insuficiente |
| -2 a -1 | 0 | min_rusher_dist_at_throw | 0 | — | — | n insuficiente |
| -2 a -1 | 0 | time_to_throw | 0 | — | — | n insuficiente |
| -2 a -1 | 0 | is_success | 0 | — | — | n insuficiente |
| 0 | 2 | any_pressure | 2 | 0.000 | — | n insuficiente |
| 0 | 2 | min_rusher_dist_at_throw | 2 | 2.475 | — | n insuficiente |
| 0 | 2 | time_to_throw | 2 | 2.500 | — | n insuficiente |
| 0 | 2 | is_success | 2 | 0.500 | — | n insuficiente |
| 1 | 40 | any_pressure | 40 | 0.350 | [0.221, 0.505] | — |
| 1 | 40 | min_rusher_dist_at_throw | 38 | 2.906 | [2.480, 3.332] | — |
| 1 | 40 | time_to_throw | 38 | 3.221 | [2.886, 3.556] | — |
| 1 | 40 | is_success | 40 | 0.500 | [0.352, 0.648] | — |
| 2 | 5 | any_pressure | 5 | 0.800 | — | n insuficiente |
| 2 | 5 | min_rusher_dist_at_throw | 5 | 2.016 | — | n insuficiente |
| 2 | 5 | time_to_throw | 5 | 4.640 | — | n insuficiente |
| 2 | 5 | is_success | 5 | 0.000 | — | n insuficiente |
| 3 a 6 | 0 | any_pressure | 0 | — | — | n insuficiente |
| 3 a 6 | 0 | min_rusher_dist_at_throw | 0 | — | — | n insuficiente |
| 3 a 6 | 0 | time_to_throw | 0 | — | — | n insuficiente |
| 3 a 6 | 0 | is_success | 0 | — | — | n insuficiente |

#### Cover-0 (n = 260)

Blitz contra no blitz (diferencia = blitz menos no blitz):

| Métrica | Excluidas por nulo | n blitz | Media blitz | IC95 blitz | n no blitz | Media no blitz | IC95 no blitz | Diferencia | IC95 diferencia | Etiquetas |
|---|---|---|---|---|---|---|---|---|---|---|
| any_pressure (binary) | 0 | 222 | 0.550 | [0.484, 0.614] | 38 | 0.289 | [0.170, 0.448] | 0.260 | [0.089, 0.396] | — |
| min_rusher_dist_at_throw (continuous) | 7 | 215 | 2.781 | [2.617, 2.945] | 38 | 3.177 | [2.865, 3.490] | -0.396 | [-0.749, -0.043] | — |
| time_to_throw (continuous) | 7 | 215 | 2.580 | [2.434, 2.725] | 38 | 2.708 | [2.409, 3.007] | -0.128 | [-0.461, 0.204] | — |
| is_success (binary) | 0 | 222 | 0.419 | [0.356, 0.485] | 38 | 0.526 | [0.373, 0.675] | -0.107 | [-0.269, 0.060] | — |

Por categoría de `protection_advantage`:

| Categoría | n total | Métrica | n | Media o proporción | IC95 | Etiquetas |
|---|---|---|---|---|---|---|
| -2 a -1 | 91 | any_pressure | 91 | 0.670 | [0.569, 0.758] | — |
| -2 a -1 | 91 | min_rusher_dist_at_throw | 89 | 2.630 | [2.376, 2.884] | — |
| -2 a -1 | 91 | time_to_throw | 89 | 2.583 | [2.309, 2.858] | — |
| -2 a -1 | 91 | is_success | 91 | 0.352 | [0.261, 0.454] | — |
| 0 | 87 | any_pressure | 87 | 0.460 | [0.359, 0.564] | — |
| 0 | 87 | min_rusher_dist_at_throw | 82 | 2.885 | [2.641, 3.129] | — |
| 0 | 87 | time_to_throw | 82 | 2.552 | [2.348, 2.757] | — |
| 0 | 87 | is_success | 87 | 0.402 | [0.306, 0.507] | — |
| 1 | 52 | any_pressure | 52 | 0.462 | [0.333, 0.595] | — |
| 1 | 52 | min_rusher_dist_at_throw | 52 | 2.881 | [2.530, 3.233] | — |
| 1 | 52 | time_to_throw | 52 | 2.713 | [2.469, 2.958] | — |
| 1 | 52 | is_success | 52 | 0.519 | [0.387, 0.649] | — |
| 2 | 23 | any_pressure | 23 | 0.304 | — | n insuficiente |
| 2 | 23 | min_rusher_dist_at_throw | 23 | 3.190 | — | n insuficiente |
| 2 | 23 | time_to_throw | 23 | 2.587 | — | n insuficiente |
| 2 | 23 | is_success | 23 | 0.609 | — | n insuficiente |
| 3 a 6 | 7 | any_pressure | 7 | 0.143 | — | n insuficiente |
| 3 a 6 | 7 | min_rusher_dist_at_throw | 7 | 3.547 | — | n insuficiente |
| 3 a 6 | 7 | time_to_throw | 7 | 2.529 | — | n insuficiente |
| 3 a 6 | 7 | is_success | 7 | 0.714 | — | n insuficiente |

#### Cover-1 (n = 2005)

Blitz contra no blitz (diferencia = blitz menos no blitz):

| Métrica | Excluidas por nulo | n blitz | Media blitz | IC95 blitz | n no blitz | Media no blitz | IC95 no blitz | Diferencia | IC95 diferencia | Etiquetas |
|---|---|---|---|---|---|---|---|---|---|---|
| any_pressure (binary) | 0 | 819 | 0.466 | [0.432, 0.501] | 1186 | 0.347 | [0.321, 0.375] | 0.119 | [0.075, 0.162] | — |
| min_rusher_dist_at_throw (continuous) | 99 | 799 | 2.556 | [2.472, 2.641] | 1107 | 2.946 | [2.862, 3.030] | -0.389 | [-0.508, -0.270] | — |
| time_to_throw (continuous) | 104 | 797 | 2.930 | [2.844, 3.017] | 1104 | 3.034 | [2.965, 3.102] | -0.103 | [-0.213, 0.007] | — |
| is_success (binary) | 0 | 819 | 0.431 | [0.397, 0.465] | 1186 | 0.438 | [0.410, 0.467] | -0.007 | [-0.051, 0.037] | — |

Por categoría de `protection_advantage`:

| Categoría | n total | Métrica | n | Media o proporción | IC95 | Etiquetas |
|---|---|---|---|---|---|---|
| -2 a -1 | 13 | any_pressure | 13 | 0.538 | — | n insuficiente |
| -2 a -1 | 13 | min_rusher_dist_at_throw | 13 | 2.036 | — | n insuficiente |
| -2 a -1 | 13 | time_to_throw | 13 | 2.731 | — | n insuficiente |
| -2 a -1 | 13 | is_success | 13 | 0.385 | — | n insuficiente |
| 0 | 520 | any_pressure | 520 | 0.471 | [0.429, 0.514] | — |
| 0 | 520 | min_rusher_dist_at_throw | 503 | 2.505 | [2.404, 2.605] | — |
| 0 | 520 | time_to_throw | 502 | 2.824 | [2.723, 2.926] | — |
| 0 | 520 | is_success | 520 | 0.440 | [0.398, 0.483] | — |
| 1 | 1112 | any_pressure | 1112 | 0.377 | [0.349, 0.406] | — |
| 1 | 1112 | min_rusher_dist_at_throw | 1042 | 2.771 | [2.694, 2.848] | — |
| 1 | 1112 | time_to_throw | 1040 | 2.982 | [2.908, 3.055] | — |
| 1 | 1112 | is_success | 1112 | 0.437 | [0.408, 0.466] | — |
| 2 | 275 | any_pressure | 275 | 0.349 | [0.295, 0.407] | — |
| 2 | 275 | min_rusher_dist_at_throw | 266 | 3.183 | [2.974, 3.392] | — |
| 2 | 275 | time_to_throw | 264 | 3.293 | [3.142, 3.444] | — |
| 2 | 275 | is_success | 275 | 0.411 | [0.354, 0.470] | — |
| 3 a 6 | 85 | any_pressure | 85 | 0.318 | [0.228, 0.423] | — |
| 3 a 6 | 85 | min_rusher_dist_at_throw | 82 | 3.450 | [3.086, 3.813] | — |
| 3 a 6 | 85 | time_to_throw | 82 | 3.187 | [2.987, 3.387] | — |
| 3 a 6 | 85 | is_success | 85 | 0.471 | [0.368, 0.576] | — |

#### Cover-2 (n = 1085)

Blitz contra no blitz (diferencia = blitz menos no blitz):

| Métrica | Excluidas por nulo | n blitz | Media blitz | IC95 blitz | n no blitz | Media no blitz | IC95 no blitz | Diferencia | IC95 diferencia | Etiquetas |
|---|---|---|---|---|---|---|---|---|---|---|
| any_pressure (binary) | 0 | 93 | 0.495 | [0.395, 0.594] | 992 | 0.326 | [0.297, 0.355] | 0.169 | [0.065, 0.273] | — |
| min_rusher_dist_at_throw (continuous) | 48 | 91 | 2.886 | [2.520, 3.253] | 946 | 2.942 | [2.853, 3.031] | -0.056 | [-0.433, 0.321] | — |
| time_to_throw (continuous) | 51 | 91 | 2.980 | [2.782, 3.178] | 943 | 3.133 | [3.057, 3.209] | -0.153 | [-0.365, 0.059] | — |
| is_success (binary) | 0 | 93 | 0.441 | [0.344, 0.542] | 992 | 0.489 | [0.458, 0.520] | -0.048 | [-0.150, 0.058] | — |

Por categoría de `protection_advantage`:

| Categoría | n total | Métrica | n | Media o proporción | IC95 | Etiquetas |
|---|---|---|---|---|---|---|
| -2 a -1 | 0 | any_pressure | 0 | — | — | n insuficiente |
| -2 a -1 | 0 | min_rusher_dist_at_throw | 0 | — | — | n insuficiente |
| -2 a -1 | 0 | time_to_throw | 0 | — | — | n insuficiente |
| -2 a -1 | 0 | is_success | 0 | — | — | n insuficiente |
| 0 | 41 | any_pressure | 41 | 0.415 | [0.278, 0.566] | — |
| 0 | 41 | min_rusher_dist_at_throw | 41 | 3.041 | [2.483, 3.598] | — |
| 0 | 41 | time_to_throw | 41 | 2.712 | [2.439, 2.986] | — |
| 0 | 41 | is_success | 41 | 0.512 | [0.365, 0.657] | — |
| 1 | 720 | any_pressure | 720 | 0.349 | [0.315, 0.384] | — |
| 1 | 720 | min_rusher_dist_at_throw | 689 | 2.820 | [2.724, 2.916] | — |
| 1 | 720 | time_to_throw | 685 | 3.032 | [2.942, 3.122] | — |
| 1 | 720 | is_success | 720 | 0.482 | [0.446, 0.518] | — |
| 2 | 250 | any_pressure | 250 | 0.332 | [0.277, 0.393] | — |
| 2 | 250 | min_rusher_dist_at_throw | 239 | 3.147 | [2.941, 3.354] | — |
| 2 | 250 | time_to_throw | 239 | 3.312 | [3.169, 3.454] | — |
| 2 | 250 | is_success | 250 | 0.496 | [0.435, 0.558] | — |
| 3 a 6 | 74 | any_pressure | 74 | 0.243 | [0.160, 0.352] | — |
| 3 a 6 | 74 | min_rusher_dist_at_throw | 68 | 3.324 | [2.911, 3.738] | — |
| 3 a 6 | 74 | time_to_throw | 69 | 3.567 | [3.342, 3.791] | — |
| 3 a 6 | 74 | is_success | 74 | 0.459 | [0.351, 0.572] | — |

#### Cover-3 (n = 2664)

Blitz contra no blitz (diferencia = blitz menos no blitz):

| Métrica | Excluidas por nulo | n blitz | Media blitz | IC95 blitz | n no blitz | Media no blitz | IC95 no blitz | Diferencia | IC95 diferencia | Etiquetas |
|---|---|---|---|---|---|---|---|---|---|---|
| any_pressure (binary) | 0 | 708 | 0.458 | [0.421, 0.494] | 1956 | 0.326 | [0.305, 0.347] | 0.132 | [0.090, 0.174] | — |
| min_rusher_dist_at_throw (continuous) | 137 | 672 | 2.726 | [2.626, 2.826] | 1855 | 3.051 | [2.985, 3.117] | -0.325 | [-0.445, -0.205] | — |
| time_to_throw (continuous) | 143 | 671 | 2.920 | [2.818, 3.022] | 1850 | 3.116 | [3.062, 3.171] | -0.197 | [-0.312, -0.081] | — |
| is_success (binary) | 0 | 708 | 0.508 | [0.472, 0.545] | 1956 | 0.498 | [0.476, 0.521] | 0.010 | [-0.033, 0.053] | — |

Por categoría de `protection_advantage`:

| Categoría | n total | Métrica | n | Media o proporción | IC95 | Etiquetas |
|---|---|---|---|---|---|---|
| -2 a -1 | 9 | any_pressure | 9 | 0.333 | — | n insuficiente |
| -2 a -1 | 9 | min_rusher_dist_at_throw | 9 | 3.183 | — | n insuficiente |
| -2 a -1 | 9 | time_to_throw | 9 | 2.178 | — | n insuficiente |
| -2 a -1 | 9 | is_success | 9 | 0.778 | — | n insuficiente |
| 0 | 348 | any_pressure | 348 | 0.445 | [0.394, 0.498] | — |
| 0 | 348 | min_rusher_dist_at_throw | 332 | 2.768 | [2.637, 2.899] | — |
| 0 | 348 | time_to_throw | 331 | 2.745 | [2.578, 2.912] | — |
| 0 | 348 | is_success | 348 | 0.520 | [0.468, 0.572] | — |
| 1 | 1613 | any_pressure | 1613 | 0.356 | [0.333, 0.380] | — |
| 1 | 1613 | min_rusher_dist_at_throw | 1542 | 2.891 | [2.822, 2.960] | — |
| 1 | 1613 | time_to_throw | 1539 | 3.020 | [2.961, 3.078] | — |
| 1 | 1613 | is_success | 1613 | 0.497 | [0.472, 0.521] | — |
| 2 | 503 | any_pressure | 503 | 0.358 | [0.317, 0.401] | — |
| 2 | 503 | min_rusher_dist_at_throw | 462 | 3.143 | [2.999, 3.287] | — |
| 2 | 503 | time_to_throw | 460 | 3.382 | [3.268, 3.496] | — |
| 2 | 503 | is_success | 503 | 0.503 | [0.459, 0.546] | — |
| 3 a 6 | 191 | any_pressure | 191 | 0.251 | [0.195, 0.317] | — |
| 3 a 6 | 191 | min_rusher_dist_at_throw | 182 | 3.478 | [3.247, 3.709] | — |
| 3 a 6 | 191 | time_to_throw | 182 | 3.263 | [3.123, 3.403] | — |
| 3 a 6 | 191 | is_success | 191 | 0.487 | [0.417, 0.557] | — |

#### Cover-6 (n = 805)

Blitz contra no blitz (diferencia = blitz menos no blitz):

| Métrica | Excluidas por nulo | n blitz | Media blitz | IC95 blitz | n no blitz | Media no blitz | IC95 no blitz | Diferencia | IC95 diferencia | Etiquetas |
|---|---|---|---|---|---|---|---|---|---|---|
| any_pressure (binary) | 0 | 39 | 0.487 | [0.339, 0.638] | 766 | 0.332 | [0.299, 0.366] | 0.156 | [0.003, 0.310] | — |
| min_rusher_dist_at_throw (continuous) | 42 | 39 | 2.655 | [2.237, 3.074] | 724 | 2.852 | [2.750, 2.954] | -0.197 | [-0.627, 0.234] | — |
| time_to_throw (continuous) | 42 | 39 | 2.890 | [2.544, 3.236] | 724 | 3.062 | [2.987, 3.137] | -0.173 | [-0.527, 0.181] | — |
| is_success (binary) | 0 | 39 | 0.410 | [0.271, 0.566] | 766 | 0.495 | [0.459, 0.530] | -0.085 | [-0.228, 0.075] | — |

Por categoría de `protection_advantage`:

| Categoría | n total | Métrica | n | Media o proporción | IC95 | Etiquetas |
|---|---|---|---|---|---|---|
| -2 a -1 | 0 | any_pressure | 0 | — | — | n insuficiente |
| -2 a -1 | 0 | min_rusher_dist_at_throw | 0 | — | — | n insuficiente |
| -2 a -1 | 0 | time_to_throw | 0 | — | — | n insuficiente |
| -2 a -1 | 0 | is_success | 0 | — | — | n insuficiente |
| 0 | 14 | any_pressure | 14 | 0.429 | — | n insuficiente |
| 0 | 14 | min_rusher_dist_at_throw | 14 | 3.067 | — | n insuficiente |
| 0 | 14 | time_to_throw | 14 | 2.071 | — | n insuficiente |
| 0 | 14 | is_success | 14 | 0.500 | — | n insuficiente |
| 1 | 654 | any_pressure | 654 | 0.344 | [0.309, 0.381] | — |
| 1 | 654 | min_rusher_dist_at_throw | 620 | 2.733 | [2.634, 2.833] | — |
| 1 | 654 | time_to_throw | 620 | 3.014 | [2.934, 3.093] | — |
| 1 | 654 | is_success | 654 | 0.489 | [0.451, 0.528] | — |
| 2 | 105 | any_pressure | 105 | 0.314 | [0.233, 0.408] | — |
| 2 | 105 | min_rusher_dist_at_throw | 99 | 3.208 | [2.857, 3.559] | — |
| 2 | 105 | time_to_throw | 99 | 3.309 | [3.090, 3.528] | — |
| 2 | 105 | is_success | 105 | 0.476 | [0.383, 0.571] | — |
| 3 a 6 | 32 | any_pressure | 32 | 0.281 | [0.156, 0.454] | — |
| 3 a 6 | 32 | min_rusher_dist_at_throw | 30 | 3.774 | [3.067, 4.481] | — |
| 3 a 6 | 32 | time_to_throw | 30 | 3.493 | [3.106, 3.880] | — |
| 3 a 6 | 32 | is_success | 32 | 0.562 | [0.393, 0.718] | — |

#### Goal Line (n = 25)

Blitz contra no blitz (diferencia = blitz menos no blitz):

| Métrica | Excluidas por nulo | n blitz | Media blitz | IC95 blitz | n no blitz | Media no blitz | IC95 no blitz | Diferencia | IC95 diferencia | Etiquetas |
|---|---|---|---|---|---|---|---|---|---|---|
| any_pressure (binary) | 0 | 25 | 0.400 | — | 0 | — | — | — | — | n insuficiente, no disponible |
| min_rusher_dist_at_throw (continuous) | 3 | 22 | 3.741 | — | 0 | — | — | — | — | n insuficiente, no disponible |
| time_to_throw (continuous) | 3 | 22 | 2.727 | — | 0 | — | — | — | — | n insuficiente, no disponible |
| is_success (binary) | 0 | 25 | 0.600 | — | 0 | — | — | — | — | n insuficiente, no disponible |

Por categoría de `protection_advantage`:

| Categoría | n total | Métrica | n | Media o proporción | IC95 | Etiquetas |
|---|---|---|---|---|---|---|
| -2 a -1 | 6 | any_pressure | 6 | 0.667 | — | n insuficiente |
| -2 a -1 | 6 | min_rusher_dist_at_throw | 4 | 4.307 | — | n insuficiente |
| -2 a -1 | 6 | time_to_throw | 4 | 2.575 | — | n insuficiente |
| -2 a -1 | 6 | is_success | 6 | 0.500 | — | n insuficiente |
| 0 | 3 | any_pressure | 3 | 0.000 | — | n insuficiente |
| 0 | 3 | min_rusher_dist_at_throw | 3 | 3.163 | — | n insuficiente |
| 0 | 3 | time_to_throw | 3 | 2.167 | — | n insuficiente |
| 0 | 3 | is_success | 3 | 1.000 | — | n insuficiente |
| 1 | 8 | any_pressure | 8 | 0.625 | — | n insuficiente |
| 1 | 8 | min_rusher_dist_at_throw | 8 | 2.446 | — | n insuficiente |
| 1 | 8 | time_to_throw | 8 | 2.913 | — | n insuficiente |
| 1 | 8 | is_success | 8 | 0.625 | — | n insuficiente |
| 2 | 6 | any_pressure | 6 | 0.000 | — | n insuficiente |
| 2 | 6 | min_rusher_dist_at_throw | 6 | 4.307 | — | n insuficiente |
| 2 | 6 | time_to_throw | 6 | 2.450 | — | n insuficiente |
| 2 | 6 | is_success | 6 | 0.500 | — | n insuficiente |
| 3 a 6 | 2 | any_pressure | 2 | 0.500 | — | n insuficiente |
| 3 a 6 | 2 | min_rusher_dist_at_throw | 1 | 10.170 | — | n insuficiente |
| 3 a 6 | 2 | time_to_throw | 1 | 5.200 | — | n insuficiente |
| 3 a 6 | 2 | is_success | 2 | 0.500 | — | n insuficiente |

#### Miscellaneous (n = 8)

Blitz contra no blitz (diferencia = blitz menos no blitz):

| Métrica | Excluidas por nulo | n blitz | Media blitz | IC95 blitz | n no blitz | Media no blitz | IC95 no blitz | Diferencia | IC95 diferencia | Etiquetas |
|---|---|---|---|---|---|---|---|---|---|---|
| any_pressure (binary) | 0 | 0 | — | — | 8 | 0.375 | — | — | — | n insuficiente, no disponible |
| min_rusher_dist_at_throw (continuous) | 2 | 0 | — | — | 6 | 2.632 | — | — | — | n insuficiente, no disponible |
| time_to_throw (continuous) | 2 | 0 | — | — | 6 | 2.850 | — | — | — | n insuficiente, no disponible |
| is_success (binary) | 0 | 0 | — | — | 8 | 0.250 | — | — | — | n insuficiente, no disponible |

Por categoría de `protection_advantage`:

| Categoría | n total | Métrica | n | Media o proporción | IC95 | Etiquetas |
|---|---|---|---|---|---|---|
| -2 a -1 | 0 | any_pressure | 0 | — | — | n insuficiente |
| -2 a -1 | 0 | min_rusher_dist_at_throw | 0 | — | — | n insuficiente |
| -2 a -1 | 0 | time_to_throw | 0 | — | — | n insuficiente |
| -2 a -1 | 0 | is_success | 0 | — | — | n insuficiente |
| 0 | 0 | any_pressure | 0 | — | — | n insuficiente |
| 0 | 0 | min_rusher_dist_at_throw | 0 | — | — | n insuficiente |
| 0 | 0 | time_to_throw | 0 | — | — | n insuficiente |
| 0 | 0 | is_success | 0 | — | — | n insuficiente |
| 1 | 6 | any_pressure | 6 | 0.333 | — | n insuficiente |
| 1 | 6 | min_rusher_dist_at_throw | 4 | 3.072 | — | n insuficiente |
| 1 | 6 | time_to_throw | 4 | 2.650 | — | n insuficiente |
| 1 | 6 | is_success | 6 | 0.167 | — | n insuficiente |
| 2 | 2 | any_pressure | 2 | 0.500 | — | n insuficiente |
| 2 | 2 | min_rusher_dist_at_throw | 2 | 1.750 | — | n insuficiente |
| 2 | 2 | time_to_throw | 2 | 3.250 | — | n insuficiente |
| 2 | 2 | is_success | 2 | 0.500 | — | n insuficiente |
| 3 a 6 | 0 | any_pressure | 0 | — | — | n insuficiente |
| 3 a 6 | 0 | min_rusher_dist_at_throw | 0 | — | — | n insuficiente |
| 3 a 6 | 0 | time_to_throw | 0 | — | — | n insuficiente |
| 3 a 6 | 0 | is_success | 0 | — | — | n insuficiente |

#### Prevent (n = 32)

Blitz contra no blitz (diferencia = blitz menos no blitz):

| Métrica | Excluidas por nulo | n blitz | Media blitz | IC95 blitz | n no blitz | Media no blitz | IC95 no blitz | Diferencia | IC95 diferencia | Etiquetas |
|---|---|---|---|---|---|---|---|---|---|---|
| any_pressure (binary) | 0 | 4 | 0.250 | — | 28 | 0.357 | — | -0.107 | — | n insuficiente |
| min_rusher_dist_at_throw (continuous) | 2 | 4 | 2.532 | — | 26 | 3.594 | — | -1.062 | — | n insuficiente |
| time_to_throw (continuous) | 2 | 4 | 5.125 | — | 26 | 4.454 | — | 0.671 | — | n insuficiente |
| is_success (binary) | 0 | 4 | 0.250 | — | 28 | 0.393 | — | -0.143 | — | n insuficiente |

Por categoría de `protection_advantage`:

| Categoría | n total | Métrica | n | Media o proporción | IC95 | Etiquetas |
|---|---|---|---|---|---|---|
| -2 a -1 | 0 | any_pressure | 0 | — | — | n insuficiente |
| -2 a -1 | 0 | min_rusher_dist_at_throw | 0 | — | — | n insuficiente |
| -2 a -1 | 0 | time_to_throw | 0 | — | — | n insuficiente |
| -2 a -1 | 0 | is_success | 0 | — | — | n insuficiente |
| 0 | 3 | any_pressure | 3 | 0.333 | — | n insuficiente |
| 0 | 3 | min_rusher_dist_at_throw | 3 | 2.480 | — | n insuficiente |
| 0 | 3 | time_to_throw | 3 | 5.833 | — | n insuficiente |
| 0 | 3 | is_success | 3 | 0.333 | — | n insuficiente |
| 1 | 8 | any_pressure | 8 | 0.500 | — | n insuficiente |
| 1 | 8 | min_rusher_dist_at_throw | 8 | 3.126 | — | n insuficiente |
| 1 | 8 | time_to_throw | 8 | 4.537 | — | n insuficiente |
| 1 | 8 | is_success | 8 | 0.250 | — | n insuficiente |
| 2 | 10 | any_pressure | 10 | 0.400 | — | n insuficiente |
| 2 | 10 | min_rusher_dist_at_throw | 9 | 2.834 | — | n insuficiente |
| 2 | 10 | time_to_throw | 9 | 4.078 | — | n insuficiente |
| 2 | 10 | is_success | 10 | 0.600 | — | n insuficiente |
| 3 a 6 | 11 | any_pressure | 11 | 0.182 | — | n insuficiente |
| 3 a 6 | 11 | min_rusher_dist_at_throw | 10 | 4.562 | — | n insuficiente |
| 3 a 6 | 11 | time_to_throw | 10 | 4.580 | — | n insuficiente |
| 3 a 6 | 11 | is_success | 11 | 0.273 | — | n insuficiente |

#### Quarters (n = 1033)

Blitz contra no blitz (diferencia = blitz menos no blitz):

| Métrica | Excluidas por nulo | n blitz | Media blitz | IC95 blitz | n no blitz | Media no blitz | IC95 no blitz | Diferencia | IC95 diferencia | Etiquetas |
|---|---|---|---|---|---|---|---|---|---|---|
| any_pressure (binary) | 0 | 114 | 0.474 | [0.384, 0.565] | 919 | 0.338 | [0.309, 0.370] | 0.135 | [0.041, 0.231] | — |
| min_rusher_dist_at_throw (continuous) | 71 | 109 | 2.566 | [2.340, 2.792] | 853 | 2.872 | [2.785, 2.960] | -0.306 | [-0.549, -0.064] | — |
| time_to_throw (continuous) | 78 | 109 | 2.962 | [2.663, 3.262] | 846 | 3.075 | [2.997, 3.153] | -0.112 | [-0.422, 0.197] | — |
| is_success (binary) | 0 | 114 | 0.430 | [0.343, 0.522] | 919 | 0.471 | [0.439, 0.503] | -0.041 | [-0.134, 0.056] | — |

Por categoría de `protection_advantage`:

| Categoría | n total | Métrica | n | Media o proporción | IC95 | Etiquetas |
|---|---|---|---|---|---|---|
| -2 a -1 | 3 | any_pressure | 3 | 0.000 | — | n insuficiente |
| -2 a -1 | 3 | min_rusher_dist_at_throw | 3 | 4.253 | — | n insuficiente |
| -2 a -1 | 3 | time_to_throw | 3 | 1.533 | — | n insuficiente |
| -2 a -1 | 3 | is_success | 3 | 0.333 | — | n insuficiente |
| 0 | 44 | any_pressure | 44 | 0.500 | [0.358, 0.642] | — |
| 0 | 44 | min_rusher_dist_at_throw | 41 | 2.593 | [2.270, 2.916] | — |
| 0 | 44 | time_to_throw | 41 | 2.905 | [2.213, 3.596] | — |
| 0 | 44 | is_success | 44 | 0.500 | [0.358, 0.642] | — |
| 1 | 757 | any_pressure | 757 | 0.354 | [0.321, 0.389] | — |
| 1 | 757 | min_rusher_dist_at_throw | 707 | 2.685 | [2.601, 2.769] | — |
| 1 | 757 | time_to_throw | 700 | 2.948 | [2.869, 3.027] | — |
| 1 | 757 | is_success | 757 | 0.457 | [0.422, 0.493] | — |
| 2 | 163 | any_pressure | 163 | 0.337 | [0.269, 0.413] | — |
| 2 | 163 | min_rusher_dist_at_throw | 150 | 3.285 | [3.065, 3.506] | — |
| 2 | 163 | time_to_throw | 150 | 3.442 | [3.245, 3.639] | — |
| 2 | 163 | is_success | 163 | 0.509 | [0.433, 0.585] | — |
| 3 a 6 | 66 | any_pressure | 66 | 0.303 | [0.206, 0.422] | — |
| 3 a 6 | 66 | min_rusher_dist_at_throw | 61 | 3.600 | [3.052, 4.147] | — |
| 3 a 6 | 66 | time_to_throw | 61 | 3.616 | [3.259, 3.974] | — |
| 3 a 6 | 66 | is_success | 66 | 0.455 | [0.340, 0.574] | — |

#### Red Zone (n = 358)

Blitz contra no blitz (diferencia = blitz menos no blitz):

| Métrica | Excluidas por nulo | n blitz | Media blitz | IC95 blitz | n no blitz | Media no blitz | IC95 no blitz | Diferencia | IC95 diferencia | Etiquetas |
|---|---|---|---|---|---|---|---|---|---|---|
| any_pressure (binary) | 0 | 43 | 0.488 | [0.346, 0.632] | 315 | 0.400 | [0.347, 0.455] | 0.088 | [-0.064, 0.242] | — |
| min_rusher_dist_at_throw (continuous) | 31 | 42 | 2.824 | [2.208, 3.440] | 285 | 3.085 | [2.874, 3.297] | -0.261 | [-0.913, 0.390] | — |
| time_to_throw (continuous) | 31 | 42 | 3.145 | [2.780, 3.510] | 285 | 3.235 | [3.085, 3.385] | -0.089 | [-0.484, 0.305] | — |
| is_success (binary) | 0 | 43 | 0.419 | [0.284, 0.567] | 315 | 0.390 | [0.338, 0.445] | 0.028 | [-0.117, 0.185] | — |

Por categoría de `protection_advantage`:

| Categoría | n total | Métrica | n | Media o proporción | IC95 | Etiquetas |
|---|---|---|---|---|---|---|
| -2 a -1 | 0 | any_pressure | 0 | — | — | n insuficiente |
| -2 a -1 | 0 | min_rusher_dist_at_throw | 0 | — | — | n insuficiente |
| -2 a -1 | 0 | time_to_throw | 0 | — | — | n insuficiente |
| -2 a -1 | 0 | is_success | 0 | — | — | n insuficiente |
| 0 | 28 | any_pressure | 28 | 0.500 | — | n insuficiente |
| 0 | 28 | min_rusher_dist_at_throw | 27 | 2.902 | — | n insuficiente |
| 0 | 28 | time_to_throw | 27 | 3.048 | — | n insuficiente |
| 0 | 28 | is_success | 28 | 0.464 | — | n insuficiente |
| 1 | 244 | any_pressure | 244 | 0.410 | [0.350, 0.472] | — |
| 1 | 244 | min_rusher_dist_at_throw | 227 | 2.863 | [2.651, 3.074] | — |
| 1 | 244 | time_to_throw | 227 | 3.205 | [3.039, 3.372] | — |
| 1 | 244 | is_success | 244 | 0.393 | [0.334, 0.456] | — |
| 2 | 65 | any_pressure | 65 | 0.354 | [0.249, 0.475] | — |
| 2 | 65 | min_rusher_dist_at_throw | 54 | 3.812 | [3.225, 4.400] | — |
| 2 | 65 | time_to_throw | 54 | 3.435 | [3.049, 3.822] | — |
| 2 | 65 | is_success | 65 | 0.308 | [0.209, 0.428] | — |
| 3 a 6 | 21 | any_pressure | 21 | 0.476 | — | n insuficiente |
| 3 a 6 | 21 | min_rusher_dist_at_throw | 19 | 3.359 | — | n insuficiente |
| 3 a 6 | 21 | time_to_throw | 19 | 3.084 | — | n insuficiente |
| 3 a 6 | 21 | is_success | 21 | 0.571 | — | n insuficiente |

### Segmentación por `offenseFormation` (formation)

Jugadas excluidas por valor nulo en `offenseFormation`: 7

#### EMPTY (n = 1387)

Blitz contra no blitz (diferencia = blitz menos no blitz):

| Métrica | Excluidas por nulo | n blitz | Media blitz | IC95 blitz | n no blitz | Media no blitz | IC95 no blitz | Diferencia | IC95 diferencia | Etiquetas |
|---|---|---|---|---|---|---|---|---|---|---|
| any_pressure (binary) | 0 | 265 | 0.445 | [0.387, 0.505] | 1122 | 0.335 | [0.308, 0.363] | 0.110 | [0.045, 0.176] | — |
| min_rusher_dist_at_throw (continuous) | 76 | 254 | 2.776 | [2.640, 2.911] | 1057 | 2.854 | [2.786, 2.922] | -0.078 | [-0.230, 0.074] | — |
| time_to_throw (continuous) | 77 | 254 | 2.598 | [2.434, 2.761] | 1056 | 2.891 | [2.821, 2.961] | -0.293 | [-0.471, -0.116] | — |
| is_success (binary) | 0 | 265 | 0.509 | [0.450, 0.569] | 1122 | 0.466 | [0.437, 0.495] | 0.043 | [-0.023, 0.110] | — |

Por categoría de `protection_advantage`:

| Categoría | n total | Métrica | n | Media o proporción | IC95 | Etiquetas |
|---|---|---|---|---|---|---|
| -2 a -1 | 25 | any_pressure | 25 | 0.560 | — | n insuficiente |
| -2 a -1 | 25 | min_rusher_dist_at_throw | 25 | 2.984 | — | n insuficiente |
| -2 a -1 | 25 | time_to_throw | 25 | 2.264 | — | n insuficiente |
| -2 a -1 | 25 | is_success | 25 | 0.400 | — | n insuficiente |
| 0 | 225 | any_pressure | 225 | 0.431 | [0.368, 0.496] | — |
| 0 | 225 | min_rusher_dist_at_throw | 214 | 2.745 | [2.601, 2.889] | — |
| 0 | 225 | time_to_throw | 214 | 2.614 | [2.427, 2.801] | — |
| 0 | 225 | is_success | 225 | 0.529 | [0.464, 0.593] | — |
| 1 | 955 | any_pressure | 955 | 0.352 | [0.322, 0.383] | — |
| 1 | 955 | min_rusher_dist_at_throw | 903 | 2.791 | [2.717, 2.864] | — |
| 1 | 955 | time_to_throw | 902 | 2.875 | [2.799, 2.950] | — |
| 1 | 955 | is_success | 955 | 0.461 | [0.429, 0.492] | — |
| 2 | 170 | any_pressure | 170 | 0.265 | [0.204, 0.336] | — |
| 2 | 170 | min_rusher_dist_at_throw | 157 | 3.181 | [3.008, 3.355] | — |
| 2 | 170 | time_to_throw | 157 | 3.000 | [2.820, 3.180] | — |
| 2 | 170 | is_success | 170 | 0.482 | [0.408, 0.557] | — |
| 3 a 6 | 12 | any_pressure | 12 | 0.167 | — | n insuficiente |
| 3 a 6 | 12 | min_rusher_dist_at_throw | 12 | 3.347 | — | n insuficiente |
| 3 a 6 | 12 | time_to_throw | 12 | 2.717 | — | n insuficiente |
| 3 a 6 | 12 | is_success | 12 | 0.583 | — | n insuficiente |

#### I_FORM (n = 297)

Blitz contra no blitz (diferencia = blitz menos no blitz):

| Métrica | Excluidas por nulo | n blitz | Media blitz | IC95 blitz | n no blitz | Media no blitz | IC95 no blitz | Diferencia | IC95 diferencia | Etiquetas |
|---|---|---|---|---|---|---|---|---|---|---|
| any_pressure (binary) | 0 | 112 | 0.393 | [0.307, 0.485] | 185 | 0.292 | [0.231, 0.361] | 0.101 | [-0.009, 0.212] | — |
| min_rusher_dist_at_throw (continuous) | 18 | 107 | 2.879 | [2.612, 3.146] | 172 | 3.388 | [3.136, 3.641] | -0.509 | [-0.877, -0.142] | — |
| time_to_throw (continuous) | 18 | 107 | 3.056 | [2.892, 3.220] | 172 | 3.352 | [3.210, 3.494] | -0.296 | [-0.512, -0.079] | — |
| is_success (binary) | 0 | 112 | 0.509 | [0.418, 0.600] | 185 | 0.535 | [0.463, 0.606] | -0.026 | [-0.142, 0.090] | — |

Por categoría de `protection_advantage`:

| Categoría | n total | Métrica | n | Media o proporción | IC95 | Etiquetas |
|---|---|---|---|---|---|---|
| -2 a -1 | 6 | any_pressure | 6 | 0.667 | — | n insuficiente |
| -2 a -1 | 6 | min_rusher_dist_at_throw | 5 | 2.580 | — | n insuficiente |
| -2 a -1 | 6 | time_to_throw | 5 | 3.700 | — | n insuficiente |
| -2 a -1 | 6 | is_success | 6 | 0.500 | — | n insuficiente |
| 0 | 29 | any_pressure | 29 | 0.517 | — | n insuficiente |
| 0 | 29 | min_rusher_dist_at_throw | 27 | 2.601 | — | n insuficiente |
| 0 | 29 | time_to_throw | 27 | 2.867 | — | n insuficiente |
| 0 | 29 | is_success | 29 | 0.483 | — | n insuficiente |
| 1 | 113 | any_pressure | 113 | 0.327 | [0.248, 0.418] | — |
| 1 | 113 | min_rusher_dist_at_throw | 108 | 3.031 | [2.703, 3.358] | — |
| 1 | 113 | time_to_throw | 108 | 3.193 | [3.017, 3.368] | — |
| 1 | 113 | is_success | 113 | 0.566 | [0.474, 0.654] | — |
| 2 | 83 | any_pressure | 83 | 0.253 | [0.172, 0.356] | — |
| 2 | 83 | min_rusher_dist_at_throw | 78 | 3.480 | [3.126, 3.833] | — |
| 2 | 83 | time_to_throw | 78 | 3.385 | [3.162, 3.607] | — |
| 2 | 83 | is_success | 83 | 0.482 | [0.378, 0.588] | — |
| 3 a 6 | 66 | any_pressure | 66 | 0.318 | [0.218, 0.438] | — |
| 3 a 6 | 66 | min_rusher_dist_at_throw | 61 | 3.427 | [3.058, 3.795] | — |
| 3 a 6 | 66 | time_to_throw | 61 | 3.259 | [3.064, 3.454] | — |
| 3 a 6 | 66 | is_success | 66 | 0.530 | [0.412, 0.646] | — |

#### JUMBO (n = 30)

Blitz contra no blitz (diferencia = blitz menos no blitz):

| Métrica | Excluidas por nulo | n blitz | Media blitz | IC95 blitz | n no blitz | Media no blitz | IC95 no blitz | Diferencia | IC95 diferencia | Etiquetas |
|---|---|---|---|---|---|---|---|---|---|---|
| any_pressure (binary) | 0 | 24 | 0.375 | — | 6 | 0.333 | — | 0.042 | — | n insuficiente |
| min_rusher_dist_at_throw (continuous) | 0 | 24 | 3.662 | — | 6 | 4.227 | — | -0.565 | — | n insuficiente |
| time_to_throw (continuous) | 1 | 24 | 3.038 | — | 5 | 3.840 | — | -0.803 | — | n insuficiente |
| is_success (binary) | 0 | 24 | 0.583 | — | 6 | 0.333 | — | 0.250 | — | n insuficiente |

Por categoría de `protection_advantage`:

| Categoría | n total | Métrica | n | Media o proporción | IC95 | Etiquetas |
|---|---|---|---|---|---|---|
| -2 a -1 | 2 | any_pressure | 2 | 0.500 | — | n insuficiente |
| -2 a -1 | 2 | min_rusher_dist_at_throw | 2 | 4.450 | — | n insuficiente |
| -2 a -1 | 2 | time_to_throw | 2 | 2.500 | — | n insuficiente |
| -2 a -1 | 2 | is_success | 2 | 0.500 | — | n insuficiente |
| 0 | 6 | any_pressure | 6 | 0.333 | — | n insuficiente |
| 0 | 6 | min_rusher_dist_at_throw | 6 | 2.743 | — | n insuficiente |
| 0 | 6 | time_to_throw | 6 | 2.883 | — | n insuficiente |
| 0 | 6 | is_success | 6 | 0.667 | — | n insuficiente |
| 1 | 11 | any_pressure | 11 | 0.455 | — | n insuficiente |
| 1 | 11 | min_rusher_dist_at_throw | 11 | 3.816 | — | n insuficiente |
| 1 | 11 | time_to_throw | 11 | 3.218 | — | n insuficiente |
| 1 | 11 | is_success | 11 | 0.727 | — | n insuficiente |
| 2 | 9 | any_pressure | 9 | 0.222 | — | n insuficiente |
| 2 | 9 | min_rusher_dist_at_throw | 9 | 3.769 | — | n insuficiente |
| 2 | 9 | time_to_throw | 8 | 3.062 | — | n insuficiente |
| 2 | 9 | is_success | 9 | 0.333 | — | n insuficiente |
| 3 a 6 | 2 | any_pressure | 2 | 0.500 | — | n insuficiente |
| 3 a 6 | 2 | min_rusher_dist_at_throw | 2 | 5.995 | — | n insuficiente |
| 3 a 6 | 2 | time_to_throw | 2 | 4.950 | — | n insuficiente |
| 3 a 6 | 2 | is_success | 2 | 0.000 | — | n insuficiente |

#### PISTOL (n = 154)

Blitz contra no blitz (diferencia = blitz menos no blitz):

| Métrica | Excluidas por nulo | n blitz | Media blitz | IC95 blitz | n no blitz | Media no blitz | IC95 no blitz | Diferencia | IC95 diferencia | Etiquetas |
|---|---|---|---|---|---|---|---|---|---|---|
| any_pressure (binary) | 0 | 36 | 0.250 | [0.138, 0.411] | 118 | 0.322 | [0.244, 0.411] | -0.072 | [-0.215, 0.106] | — |
| min_rusher_dist_at_throw (continuous) | 14 | 32 | 3.143 | [2.761, 3.524] | 108 | 3.367 | [3.028, 3.707] | -0.225 | [-0.735, 0.286] | — |
| time_to_throw (continuous) | 14 | 32 | 2.884 | [2.575, 3.194] | 108 | 3.243 | [3.005, 3.480] | -0.358 | [-0.748, 0.032] | — |
| is_success (binary) | 0 | 36 | 0.444 | [0.295, 0.604] | 118 | 0.517 | [0.428, 0.605] | -0.073 | [-0.246, 0.110] | — |

Por categoría de `protection_advantage`:

| Categoría | n total | Métrica | n | Media o proporción | IC95 | Etiquetas |
|---|---|---|---|---|---|---|
| -2 a -1 | 0 | any_pressure | 0 | — | — | n insuficiente |
| -2 a -1 | 0 | min_rusher_dist_at_throw | 0 | — | — | n insuficiente |
| -2 a -1 | 0 | time_to_throw | 0 | — | — | n insuficiente |
| -2 a -1 | 0 | is_success | 0 | — | — | n insuficiente |
| 0 | 15 | any_pressure | 15 | 0.133 | — | n insuficiente |
| 0 | 15 | min_rusher_dist_at_throw | 15 | 3.520 | — | n insuficiente |
| 0 | 15 | time_to_throw | 15 | 2.373 | — | n insuficiente |
| 0 | 15 | is_success | 15 | 0.333 | — | n insuficiente |
| 1 | 73 | any_pressure | 73 | 0.370 | [0.268, 0.485] | — |
| 1 | 73 | min_rusher_dist_at_throw | 68 | 3.085 | [2.761, 3.409] | — |
| 1 | 73 | time_to_throw | 68 | 3.046 | [2.770, 3.321] | — |
| 1 | 73 | is_success | 73 | 0.452 | [0.343, 0.566] | — |
| 2 | 45 | any_pressure | 45 | 0.267 | [0.160, 0.410] | — |
| 2 | 45 | min_rusher_dist_at_throw | 38 | 3.337 | [2.962, 3.712] | — |
| 2 | 45 | time_to_throw | 38 | 3.303 | [3.040, 3.565] | — |
| 2 | 45 | is_success | 45 | 0.622 | [0.476, 0.749] | — |
| 3 a 6 | 21 | any_pressure | 21 | 0.286 | — | n insuficiente |
| 3 a 6 | 21 | min_rusher_dist_at_throw | 19 | 3.940 | — | n insuficiente |
| 3 a 6 | 21 | time_to_throw | 19 | 3.911 | — | n insuficiente |
| 3 a 6 | 21 | is_success | 21 | 0.524 | — | n insuficiente |

#### SHOTGUN (n = 5461)

Blitz contra no blitz (diferencia = blitz menos no blitz):

| Métrica | Excluidas por nulo | n blitz | Media blitz | IC95 blitz | n no blitz | Media no blitz | IC95 no blitz | Diferencia | IC95 diferencia | Etiquetas |
|---|---|---|---|---|---|---|---|---|---|---|
| any_pressure (binary) | 0 | 1292 | 0.493 | [0.466, 0.520] | 4169 | 0.348 | [0.334, 0.363] | 0.145 | [0.114, 0.176] | — |
| min_rusher_dist_at_throw (continuous) | 282 | 1250 | 2.513 | [2.448, 2.578] | 3929 | 2.825 | [2.785, 2.865] | -0.312 | [-0.388, -0.236] | — |
| time_to_throw (continuous) | 299 | 1247 | 2.872 | [2.797, 2.948] | 3915 | 3.090 | [3.053, 3.128] | -0.218 | [-0.302, -0.134] | — |
| is_success (binary) | 0 | 1292 | 0.440 | [0.414, 0.468] | 4169 | 0.459 | [0.444, 0.474] | -0.018 | [-0.049, 0.013] | — |

Por categoría de `protection_advantage`:

| Categoría | n total | Métrica | n | Media o proporción | IC95 | Etiquetas |
|---|---|---|---|---|---|---|
| -2 a -1 | 79 | any_pressure | 79 | 0.646 | [0.536, 0.742] | — |
| -2 a -1 | 79 | min_rusher_dist_at_throw | 77 | 2.521 | [2.286, 2.756] | — |
| -2 a -1 | 79 | time_to_throw | 77 | 2.504 | [2.202, 2.806] | — |
| -2 a -1 | 79 | is_success | 79 | 0.354 | [0.258, 0.464] | — |
| 0 | 703 | any_pressure | 703 | 0.474 | [0.437, 0.511] | — |
| 0 | 703 | min_rusher_dist_at_throw | 681 | 2.525 | [2.444, 2.605] | — |
| 0 | 703 | time_to_throw | 679 | 2.801 | [2.697, 2.906] | — |
| 0 | 703 | is_success | 703 | 0.455 | [0.419, 0.492] | — |
| 1 | 3771 | any_pressure | 3771 | 0.373 | [0.357, 0.388] | — |
| 1 | 3771 | min_rusher_dist_at_throw | 3573 | 2.703 | [2.664, 2.743] | — |
| 1 | 3771 | time_to_throw | 3558 | 3.032 | [2.993, 3.071] | — |
| 1 | 3771 | is_success | 3771 | 0.461 | [0.446, 0.477] | — |
| 2 | 740 | any_pressure | 740 | 0.354 | [0.320, 0.389] | — |
| 2 | 740 | min_rusher_dist_at_throw | 690 | 3.048 | [2.940, 3.156] | — |
| 2 | 740 | time_to_throw | 689 | 3.297 | [3.198, 3.396] | — |
| 2 | 740 | is_success | 740 | 0.435 | [0.400, 0.471] | — |
| 3 a 6 | 168 | any_pressure | 168 | 0.226 | [0.169, 0.295] | — |
| 3 a 6 | 168 | min_rusher_dist_at_throw | 158 | 3.578 | [3.313, 3.843] | — |
| 3 a 6 | 168 | time_to_throw | 159 | 3.312 | [3.101, 3.523] | — |
| 3 a 6 | 168 | is_success | 168 | 0.423 | [0.350, 0.498] | — |

#### SINGLEBACK (n = 1184)

Blitz contra no blitz (diferencia = blitz menos no blitz):

| Métrica | Excluidas por nulo | n blitz | Media blitz | IC95 blitz | n no blitz | Media no blitz | IC95 no blitz | Diferencia | IC95 diferencia | Etiquetas |
|---|---|---|---|---|---|---|---|---|---|---|
| any_pressure (binary) | 0 | 362 | 0.472 | [0.422, 0.524] | 822 | 0.302 | [0.271, 0.334] | 0.171 | [0.110, 0.230] | — |
| min_rusher_dist_at_throw (continuous) | 74 | 348 | 2.974 | [2.791, 3.156] | 762 | 3.634 | [3.487, 3.782] | -0.660 | [-0.895, -0.426] | — |
| time_to_throw (continuous) | 76 | 348 | 3.177 | [3.073, 3.281] | 760 | 3.417 | [3.344, 3.489] | -0.240 | [-0.366, -0.113] | — |
| is_success (binary) | 0 | 362 | 0.456 | [0.405, 0.507] | 822 | 0.550 | [0.516, 0.584] | -0.094 | [-0.155, -0.032] | — |

Por categoría de `protection_advantage`:

| Categoría | n total | Métrica | n | Media o proporción | IC95 | Etiquetas |
|---|---|---|---|---|---|---|
| -2 a -1 | 10 | any_pressure | 10 | 0.500 | — | n insuficiente |
| -2 a -1 | 10 | min_rusher_dist_at_throw | 9 | 3.188 | — | n insuficiente |
| -2 a -1 | 10 | time_to_throw | 9 | 3.000 | — | n insuficiente |
| -2 a -1 | 10 | is_success | 10 | 0.600 | — | n insuficiente |
| 0 | 115 | any_pressure | 115 | 0.461 | [0.373, 0.552] | — |
| 0 | 115 | min_rusher_dist_at_throw | 108 | 3.219 | [2.824, 3.613] | — |
| 0 | 115 | time_to_throw | 108 | 2.980 | [2.800, 3.159] | — |
| 0 | 115 | is_success | 115 | 0.443 | [0.356, 0.535] | — |
| 1 | 439 | any_pressure | 439 | 0.301 | [0.260, 0.345] | — |
| 1 | 439 | min_rusher_dist_at_throw | 410 | 3.519 | [3.328, 3.710] | — |
| 1 | 439 | time_to_throw | 410 | 3.169 | [3.073, 3.264] | — |
| 1 | 439 | is_success | 439 | 0.540 | [0.493, 0.586] | — |
| 2 | 392 | any_pressure | 392 | 0.401 | [0.353, 0.450] | — |
| 2 | 392 | min_rusher_dist_at_throw | 368 | 3.385 | [3.169, 3.602] | — |
| 2 | 392 | time_to_throw | 366 | 3.598 | [3.486, 3.710] | — |
| 2 | 392 | is_success | 392 | 0.526 | [0.476, 0.574] | — |
| 3 a 6 | 228 | any_pressure | 228 | 0.316 | [0.259, 0.379] | — |
| 3 a 6 | 228 | min_rusher_dist_at_throw | 215 | 3.440 | [3.202, 3.677] | — |
| 3 a 6 | 228 | time_to_throw | 215 | 3.429 | [3.317, 3.541] | — |
| 3 a 6 | 228 | is_success | 228 | 0.513 | [0.449, 0.577] | — |

#### WILDCAT (n = 2)

Blitz contra no blitz (diferencia = blitz menos no blitz):

| Métrica | Excluidas por nulo | n blitz | Media blitz | IC95 blitz | n no blitz | Media no blitz | IC95 no blitz | Diferencia | IC95 diferencia | Etiquetas |
|---|---|---|---|---|---|---|---|---|---|---|
| any_pressure (binary) | 0 | 0 | — | — | 2 | 0.500 | — | — | — | n insuficiente, no disponible |
| min_rusher_dist_at_throw (continuous) | 0 | 0 | — | — | 2 | 2.935 | — | — | — | n insuficiente, no disponible |
| time_to_throw (continuous) | 0 | 0 | — | — | 2 | 2.300 | — | — | — | n insuficiente, no disponible |
| is_success (binary) | 0 | 0 | — | — | 2 | 0.500 | — | — | — | n insuficiente, no disponible |

Por categoría de `protection_advantage`:

| Categoría | n total | Métrica | n | Media o proporción | IC95 | Etiquetas |
|---|---|---|---|---|---|---|
| -2 a -1 | 0 | any_pressure | 0 | — | — | n insuficiente |
| -2 a -1 | 0 | min_rusher_dist_at_throw | 0 | — | — | n insuficiente |
| -2 a -1 | 0 | time_to_throw | 0 | — | — | n insuficiente |
| -2 a -1 | 0 | is_success | 0 | — | — | n insuficiente |
| 0 | 0 | any_pressure | 0 | — | — | n insuficiente |
| 0 | 0 | min_rusher_dist_at_throw | 0 | — | — | n insuficiente |
| 0 | 0 | time_to_throw | 0 | — | — | n insuficiente |
| 0 | 0 | is_success | 0 | — | — | n insuficiente |
| 1 | 2 | any_pressure | 2 | 0.500 | — | n insuficiente |
| 1 | 2 | min_rusher_dist_at_throw | 2 | 2.935 | — | n insuficiente |
| 1 | 2 | time_to_throw | 2 | 2.300 | — | n insuficiente |
| 1 | 2 | is_success | 2 | 0.500 | — | n insuficiente |
| 2 | 0 | any_pressure | 0 | — | — | n insuficiente |
| 2 | 0 | min_rusher_dist_at_throw | 0 | — | — | n insuficiente |
| 2 | 0 | time_to_throw | 0 | — | — | n insuficiente |
| 2 | 0 | is_success | 0 | — | — | n insuficiente |
| 3 a 6 | 0 | any_pressure | 0 | — | — | n insuficiente |
| 3 a 6 | 0 | min_rusher_dist_at_throw | 0 | — | — | n insuficiente |
| 3 a 6 | 0 | time_to_throw | 0 | — | — | n insuficiente |
| 3 a 6 | 0 | is_success | 0 | — | — | n insuficiente |

## Anexo de ejecución

### Conteos

| Concepto | Valor |
|---|---|
| block_a_excluded_null_coverage | 0 |
| block_a_excluded_null_coverage_type | 0 |
| block_a_excluded_null_defenders_in_box | 7 |
| block_a_excluded_null_lb_bite | 24 |
| block_a_excluded_play_action | 0 |
| block_b_excluded_null_any_pressure | 0 |
| block_b_excluded_null_blitz | 0 |
| block_b_excluded_null_coverage | 0 |
| block_b_excluded_null_formation | 7 |
| block_b_excluded_null_is_success | 0 |
| block_b_excluded_null_min_rusher_dist_at_throw | 465 |
| block_b_excluded_null_time_to_throw | 486 |
| master_format_csv | 1 |
| master_plays_without_pff | 0 |
| master_plays_without_tracking | 0 |
| tracking_files_attempted | 122 |
| tracking_files_error | 0 |
| tracking_files_ok | 122 |
| tracking_ok | 122 |

### Avisos

Sin avisos.
