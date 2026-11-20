# Implementation Plan: coach-metrics-pipeline

## Overview

Plan de implementación en Python 3.12 (`.venv`, solo pandas 2.2.3, numpy 2.1.3 y biblioteca estándar). Se construyen en orden `src/features.py`, `src/tracking_metrics.py` y `src/analyze.py` (estadística, Bloque A, Bloque B, reporte y persistencia). Después se verifica el pipeline con los datos reales. Ninguna tarea agrega dependencias. Las pruebas usan pytest y propiedades con `numpy.random.default_rng(seed)` (100 iteraciones o más, sin `hypothesis`). Cada prueba de propiedad lleva el comentario `# Feature: coach-metrics-pipeline, Property N: <título>`.

## Tasks

- [x] 1. Estructura base, rutas y utilidades comunes
  - Crear `src/__init__.py` vacío.
  - Crear `src/features.py` con las constantes `PROJECT_ROOT`, `DATA_DIR`, `TRACKING_DIR`, `OUTPUT_DIR` (rutas relativas a la raíz del proyecto vía `Path(__file__)`), `ROLE_PASS_RUSH`, `ROLE_PASS_BLOCK`, `ROLE_PASS`, `VALID_DOWNS`, `SUCCESS_THRESHOLD`.
  - Definir `PipelineError` y el dataclass `RunReport` (`counts`, `warnings`, `add`, `warn` con `logging`), sin código ejecutable al importar y sin configurar handlers.
  - Crear `tests/helpers.py` con una utilidad `run_property(seed, n_iter, fn)` que ejecuta ≥ 100 iteraciones con `numpy.random.default_rng` e imprime semilla e iteración al fallar. No agregar dependencias.
  - _Requirements: 1.1, 11.1, 11.2, 11.6_

- [x] 2. Módulo `src/features.py`
  - [x] 2.1 Implementar `load_base_tables`
    - Cargar `plays`, `games`, `players` y `pff` con `read_csv` (solo lectura) desde `DATA_DIR`.
    - Lanzar `PipelineError` con la ruta si falta un archivo, y con archivo y columna si falta `down`, `prePenaltyPlayResult` o `playResult` en `plays`, o alguna columna requerida de PFF (`gameId`, `playId`, `pff_role`, `pff_hit`, `pff_hurry`, `pff_sack`, `pff_beatenByDefender`).
    - No escribir ninguna salida antes de validar.
    - _Requirements: 1.1, 1.5, 1.6, 1.7, 3.9_

  - [x] 2.2 Implementar `filter_valid_plays` y `compute_is_success`
    - Conservar `down` en {1,2,3,4}; agregar `no_penalty` booleana sin nulos (`penaltyYards.isna()`); conservar `prePenaltyPlayResult` y `playResult` sin cambios.
    - Calcular `is_success` (int8) con umbrales 0.4, 0.6, 1.0, 1.0 sobre `yardsToGo` e igualdad incluida; `yardsToGo = 0` cuenta como éxito si `prePenaltyPlayResult ≥ 0`.
    - Excluir y contar en `RunReport` las jugadas con `yardsToGo` o `prePenaltyPlayResult` nulos o no numéricos.
    - _Requirements: 1.2, 1.3, 1.4, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6_

  - [x] 2.3 Implementar `compute_pff_features`, `attach_positions` y `build_features`
    - Calcular por jugada `n_rushers`, `n_blockers`, `protection_advantage`, `is_blitz` (≥ 5), `any_pressure`, `any_beaten` con comparación exacta de `pff_role` y nulos como 0 en los flags.
    - `attach_positions` hace left join por `nflId` sin cambiar el número de filas.
    - `build_features` une plays válidas, `games` y PFF por left join, con una fila por (`gameId`, `playId`); las jugadas sin PFF quedan con nulos en las columnas PFF.
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8_

  - [ ]* 2.4 Escribir prueba de propiedad para el filtro de jugadas
    - Archivo `tests/test_prop_filter_plays.py`.
    - **Property 1: El filtro de jugadas conserva exactamente las jugadas válidas**
    - **Validates: Requirements 1.2, 1.3, 1.4**

  - [ ]* 2.5 Escribir prueba de propiedad para `is_success`
    - Archivo `tests/test_prop_is_success.py`. Incluir `yardsToGo = 0`.
    - **Property 2: `is_success` sigue el umbral por down**
    - **Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.6**

  - [ ]* 2.6 Escribir prueba de propiedad para exclusiones por datos no calculables
    - Archivo `tests/test_prop_exclusions.py`.
    - **Property 3: Las jugadas con datos no calculables se excluyen y se cuentan**
    - **Validates: Requirements 2.5**

  - [ ]* 2.7 Escribir prueba de propiedad para las métricas PFF
    - Archivo `tests/test_prop_pff.py`, con modelo de referencia en bucles simples y roles con variantes de mayúsculas.
    - **Property 4: Las métricas PFF coinciden con un modelo de referencia**
    - **Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5**

  - [ ]* 2.8 Escribir pruebas unitarias de carga de tablas
    - Archivo `tests/test_features_loading.py`: carga con `cwd` distinto, archivo o columna faltante (mensaje con ruta, sin salidas), `data/` sin cambios de hash y `mtime`.
    - _Requirements: 1.1, 1.5, 1.6, 1.7, 3.9, 11.2_

- [x] 3. Módulo `src/tracking_metrics.py`
  - [x] 3.1 Constantes, contexto y funciones base
    - Definir `TRACKING_COLUMNS`, `TRACKING_DTYPES`, `SNAP_EVENTS`, `RESOLUTION_EVENTS`, `LB_POSITIONS`, `SPEED_MAX`, `BITE_OFFSET_FRAMES`.
    - Implementar `TrackingContext` y `build_context` (`pff_roles`, `plays_def`, `positions`, `team_map` por `gameId`).
    - Implementar `normalize_xy` (devuelve también las llaves con `playDirection` inválido y las registra), `filter_speed` (pone NaN a `s > 15`, no altera posición) y `add_time_seconds` (factoriza `time` y parsea solo únicos).
    - _Requirements: 4.2, 4.4, 4.5, 4.6, 4.7, 4.10_

  - [x] 3.2 Implementar `find_event_frames` y `frame_dt_flags`
    - Deduplicar por frame; Frame_Snap = menor `time` entre eventos de snap; Frame_Resolucion = menor `time` entre eventos de resolución con `time ≥` snap; `time_to_throw = (res_frameId − snap_frameId)/10` redondeado a 0.01, nulo si falta snap o resolución o si es negativo (D12: `time` viene truncado al segundo).
    - `frame_dt_ok` = 1 si hay ≥ 2 frames, `frameId` avanza de 1 en 1 y `time` es no decreciente; 0 en otro caso. Columna diagnóstica `mean_dt_time`.
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7_

  - [x] 3.3 Implementar `select_passer` y `rusher_distance`
    - Pasador: mínimo `nflId` entre `Pass` de PFF; respaldo QB por `officialPosition` solo si no hay ningún `Pass`; `passer_source`, `passer_ambiguous` y aviso en el Log con `gameId` y `playId`.
    - `min_rusher_dist_at_throw`: distancia euclidiana mínima en el Frame_Resolucion entre el Pasador y los `Pass Rush` con coordenadas, redondeada a 2 decimales; nulo si no hay Pasador, rusher o coordenadas.
    - _Requirements: 6.1, 6.2, 6.3, 6.4_

  - [x] 3.4 Implementar `lb_bite` y normalización de `team`
    - Normalizar `team` a abreviatura (si es `home`/`away`, mapear con `games`; si ya es abreviatura, usar tal cual).
    - Linebackers de la defensa (`ILB`, `MLB`, `OLB`, `LB` vía `officialPosition`): promedio de `x_norm(snap) − x_norm(snap+10)` solo con los que tienen ambos valores, redondeado a 2 decimales; nulo si no existe el frame `snap_frameId + 10` o no hay valores.
    - _Requirements: 6.5, 6.6, 6.7_

  - [x] 3.5 Implementar `process_tracking_frame`, `process_tracking_file` y `compute_tracking_metrics`
    - `process_tracking_frame` (sin I/O) devuelve una fila por jugada con todas las columnas del agregado, incluidas `n_speed_outliers` y `max_speed_player`, excluyendo el balón.
    - `process_tracking_file` lee con `usecols=TRACKING_COLUMNS` y `dtype=TRACKING_DTYPES`.
    - `compute_tracking_metrics` itera archivos ordenados, captura `OSError`, `ValueError`, `KeyError` y `pd.errors.ParserError` por archivo, conserva solo el agregado, ejecuta `del` y `gc.collect()` por archivo, y devuelve `{"ok", "error", "attempted"}` con `ok + error == attempted`; admite `game_ids` para subconjuntos.
    - _Requirements: 4.1, 4.2, 4.3, 4.6, 4.7, 4.8, 4.9, 6.8, 11.5_

  - [ ]* 3.6 Escribir prueba de propiedad para la normalización de coordenadas
    - Archivo `tests/test_prop_normalize_xy.py`.
    - **Property 6: La normalización de coordenadas es correcta e involutiva**
    - **Validates: Requirements 4.4, 4.5, 4.10**

  - [ ]* 3.7 Escribir prueba de propiedad para el filtro de velocidad
    - Archivo `tests/test_prop_speed_filter.py`.
    - **Property 8: El filtro de velocidad respeta el umbral**
    - **Validates: Requirements 4.7**

  - [ ]* 3.8 Escribir prueba de propiedad para snap, resolución y `time_to_throw`
    - Archivo `tests/test_prop_event_frames.py`, con eventos repetidos en todas las filas del frame.
    - **Property 10: Snap, resolución y `time_to_throw` coinciden con un modelo de referencia**
    - **Validates: Requirements 5.1, 5.2, 5.3, 5.5, 5.6**

  - [ ]* 3.9 Escribir prueba de propiedad para `frame_dt_ok`
    - Archivo `tests/test_prop_frame_dt.py`.
    - **Property 11: `frame_dt_ok` refleja el promedio de dt**
    - **Validates: Requirements 5.4, 5.7**

  - [ ]* 3.10 Escribir prueba de propiedad para la selección del Pasador
    - Archivo `tests/test_prop_passer.py`.
    - **Property 12: La selección del Pasador respeta la prioridad y el desempate**
    - **Validates: Requirements 6.2, 6.3**

  - [ ]* 3.11 Escribir prueba de propiedad para `min_rusher_dist_at_throw`
    - Archivo `tests/test_prop_rusher_dist.py`.
    - **Property 13: `min_rusher_dist_at_throw` coincide con la distancia mínima de referencia**
    - **Validates: Requirements 6.1, 6.4**

  - [ ]* 3.12 Escribir prueba de propiedad para `lb_bite_yards`
    - Archivo `tests/test_prop_lb_bite.py`.
    - **Property 14: `lb_bite_yards` coincide con el promedio de referencia y tiene el signo correcto**
    - **Validates: Requirements 6.5, 6.6, 6.7**

  - [ ]* 3.13 Escribir prueba de propiedad para una fila por jugada
    - Archivo `tests/test_prop_one_row_per_play.py`.
    - **Property 15: El agregado de tracking tiene una fila por jugada**
    - **Validates: Requirements 4.3, 6.8**

  - [ ]* 3.14 Escribir prueba de propiedad para el balón
    - Archivo `tests/test_prop_football.py`.
    - **Property 7: El balón no afecta las métricas de jugadores**
    - **Validates: Requirements 4.6**

  - [ ]* 3.15 Escribir prueba de propiedad para el conteo de archivos
    - Archivo `tests/test_prop_file_counts.py`, con archivos válidos, ausentes y corruptos en un directorio temporal.
    - **Property 9: Los archivos ok más con error suman los intentados**
    - **Validates: Requirements 4.8, 4.9**

  - [ ]* 3.16 Escribir pruebas unitarias de procesamiento de tracking
    - Archivo `tests/test_tracking_examples.py`: `read_csv` con `usecols=TRACKING_COLUMNS`, nunca dos DataFrames de tracking vivos (espía sobre `read_csv`), archivo corrupto omitido y registrado.
    - _Requirements: 4.1, 4.2, 4.8, 11.5_

- [x] 4. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 5. Módulo `src/analyze.py`: estadística, bloques y reporte
  - [x] 5.1 Implementar estadística base
    - Crear `src/analyze.py` sin código ejecutable al importar. Definir `CellStats` y `DiffStats`.
    - Implementar `wilson_ci`, `mean_ci`, `summarize_cell`, `diff_means_ci` (Welch, z = 1.96) y `diff_props_ci` (Newcombe con Wilson).
    - Aplicar las etiquetas: "no concluyente" y "n insuficiente" con n < 30, "no disponible" con n ≤ 1, "no calculable" con varianza cero en métricas continuas del Bloque B.
    - _Requirements: 8.3, 8.4, 8.5, 8.6, 8.7, 9.8, 9.9, 10.7_

  - [x] 5.2 Implementar rangos y fusión de categorías
    - `quartile_edges` (cuartiles redondeados a 2 decimales y deduplicados), `assign_bins` (`np.searchsorted(..., side="right")`) y `merge_small_bins` (n ≥ 30, máximo 5 categorías, determinista, una sola categoría si el total es < 30).
    - _Requirements: 9.6, 10.5, 10.6_

  - [x] 5.3 Implementar `build_block_a`
    - Comparar `pff_playAction` 1 contra 0 (diferencia de `prePenaltyPlayResult`, de `playResult` y de tasa de éxito en puntos porcentuales, con IC95 y n de cada grupo).
    - Desgloses: total, `pff_passCoverageType` (Man y Zone), `pff_passCoverage`, `defendersInBox` y rangos de `lb_bite_yards` con bordes declarados.
    - Declarar las jugadas excluidas por nulo (en `pff_playAction` y por desglose). Agregar `to_dict()` con tipos nativos de Python.
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7, 9.8, 9.9_

  - [x] 5.4 Implementar `build_block_b`
    - Métricas `any_pressure`, `min_rusher_dist_at_throw`, `time_to_throw`, `is_success`: blitz contra no blitz con diferencia e IC95; por categoría fusionada de `protection_advantage` (límites calculados una vez sobre el total); segmentación independiente por `pff_passCoverage` y por `offenseFormation`.
    - Excluir por métrica las jugadas con nulo y declararlas; cada jugada cuenta una vez. Agregar `to_dict()`.
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7, 10.8, 10.9_

  - [x] 5.5 Implementar `render_report` y `write_report_atomic`
    - Generar todo el texto en memoria con: resumen de cobertura (jugadas válidas y no nulos de `time_to_throw`, `min_rusher_dist_at_throw`, `lb_bite_yards`, `frame_dt_ok`, archivos ok y con error), limitaciones (solo pases, 8 semanas de 2021, sin EPA, `prePenaltyPlayResult`), Bloque A, Bloque B y anexo de ejecución. Valores a 3 decimales.
    - Escribir a un temporal en `outputs/` y `os.replace`; ante fallo conservar el reporte previo.
    - _Requirements: 8.1, 8.2, 8.3, 8.8, 8.9_

  - [ ]* 5.6 Escribir prueba de propiedad para el intervalo de Wilson
    - Archivo `tests/test_prop_wilson.py`.
    - **Property 17: El intervalo de Wilson es válido y coincide con la fórmula**
    - **Validates: Requirements 8.4**

  - [ ]* 5.7 Escribir prueba de propiedad para el intervalo de la media
    - Archivo `tests/test_prop_mean_ci.py`.
    - **Property 18: El intervalo de la media es simétrico y coincide con la fórmula**
    - **Validates: Requirements 8.5, 8.7**

  - [ ]* 5.8 Escribir prueba de propiedad para las celdas
    - Archivo `tests/test_prop_cells.py`.
    - **Property 19: Las celdas informan n, métricas, redondeo y etiquetas coherentes**
    - **Validates: Requirements 8.3, 8.6, 10.4, 10.7**

  - [ ]* 5.9 Escribir prueba de propiedad para las diferencias con IC95
    - Archivo `tests/test_prop_diffs.py`.
    - **Property 20: Las diferencias con IC95 son coherentes**
    - **Validates: Requirements 9.2, 9.8, 9.9, 10.1**

  - [ ]* 5.10 Escribir prueba de propiedad para la partición de desgloses
    - Archivo `tests/test_prop_breakdowns.py`.
    - **Property 21: Los desgloses particionan las jugadas sin duplicar**
    - **Validates: Requirements 9.1, 9.4, 9.5, 9.7, 10.8, 10.9**

  - [ ]* 5.11 Escribir prueba de propiedad para los rangos de `lb_bite_yards`
    - Archivo `tests/test_prop_bins.py`.
    - **Property 22: Los rangos de `lb_bite_yards` son disjuntos y cubren todos los valores**
    - **Validates: Requirements 9.6**

  - [ ]* 5.12 Escribir prueba de propiedad para la fusión de categorías
    - Archivo `tests/test_prop_merge_bins.py`.
    - **Property 23: La fusión de categorías de `protection_advantage` cumple n ≥ 30 y máximo 5**
    - **Validates: Requirements 10.5, 10.6**

  - [ ]* 5.13 Escribir pruebas unitarias del reporte
    - Archivo `tests/test_report_examples.py`: con una tabla pequeña conocida, el reporte contiene limitaciones, conteos de cobertura, celdas Man, Zone, cobertura, caja y rangos con bordes declarados, y segmentaciones sin cruce; el reporte previo se conserva si falla la escritura.
    - _Requirements: 8.1, 8.2, 8.8, 8.9, 9.3, 9.6, 10.3_

- [x] 6. Persistencia y orquestación del pipeline
  - [x] 6.1 Implementar `build_master` y persistencia
    - `build_master`: left join de features con tracking por (`gameId`, `playId`), columna `has_tracking`, orden de columnas definido en el diseño, conteo de jugadas con nulos por módulo ausente en el Log.
    - `detect_format` con `importlib.util.find_spec("pyarrow")` sin importarlo; `save_master` crea `outputs/` si falta, escribe a temporal y `os.replace`, limpia el temporal y lanza `PipelineError` con ruta y causa si falla; `load_master`; `verify_roundtrip` (filas, columnas en orden, `is_success`). Registrar formato y motivo en el Log.
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8, 11.3_

  - [x] 6.2 Implementar `run_pipeline`, `load_or_build_master` y `main`
    - `run_pipeline` encadena `build_features`, `build_context`, `compute_tracking_metrics`, `build_master`, `save_master` y `verify_roundtrip`.
    - `load_or_build_master` lee `outputs/plays_enriched.*` o calcula en memoria (`write=False`) y continúa en memoria si la escritura falla.
    - `main` genera el reporte con `write_report_atomic`, captura `PipelineError` y excepciones inesperadas, imprime en `stderr` y devuelve 0 o 1; bajo `if __name__ == "__main__"`, invocable con `.venv/bin/python -m src.analyze`.
    - _Requirements: 7.1, 7.2, 8.1, 8.2, 11.2, 11.3, 11.4, 11.6_

  - [ ]* 6.3 Escribir prueba de propiedad para tablas de features y maestra
    - Archivo `tests/test_prop_master.py`.
    - **Property 5: La tabla de features y la maestra conservan una fila por jugada válida**
    - **Validates: Requirements 3.6, 3.7, 3.8, 7.1, 7.2**

  - [ ]* 6.4 Escribir prueba de propiedad para ida y vuelta de la tabla maestra
    - Archivo `tests/test_prop_roundtrip.py`, con directorio temporal.
    - **Property 16: La tabla maestra sobrevive a guardar y leer**
    - **Validates: Requirements 7.7**

  - [ ]* 6.5 Escribir pruebas unitarias de persistencia
    - Archivo `tests/test_persistence_examples.py`: `detect_format` con `find_spec` simulado en ambos sentidos, creación de `outputs/`, fallo de escritura sin archivo parcial y con `PipelineError` con ruta, formato y motivo en el Log (`caplog`).
    - _Requirements: 7.3, 7.4, 7.5, 7.6, 7.8_

  - [ ]* 6.6 Escribir pruebas de humo de restricciones
    - Archivo `tests/test_smoke_constraints.py`: escaneo AST de imports de `src/*.py` (solo pandas, numpy y biblioteca estándar) e importación de cada módulo en un subproceso sin crear archivos ni imprimir.
    - _Requirements: 11.1, 11.6_

- [x] 7. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 8. Verificación con datos reales
  - [x] 8.1 Crear `src/verify_data.py` con las verificaciones de supuestos
    - Función `main()` (sin efectos al importar, solo pandas, numpy y biblioteca estándar) que inspecciona una muestra de archivos de tracking y escribe `outputs/VERIFICATION_RUN.md` con:
      - valores distintos de `team` del tracking (¿`home`/`away` o abreviaturas?) para confirmar la normalización D8;
      - si el jugador con `pff_role == "Pass"` tiene `officialPosition == "QB"` (proporción de coincidencia);
      - proporción de jugadas con `frame_dt_ok == 1` y distribución del dt promedio;
      - tiempo por archivo y pico de memoria (`tracemalloc` o `resource`) al procesar los archivos de la muestra.
    - _Requirements: 4.1, 5.4, 6.2, 11.5_

  - [x] 8.2 Ejecutar el pipeline completo y corregir hallazgos
    - Ejecutar `.venv/bin/python -m src.verify_data` y `.venv/bin/python -m src.analyze` (corrida de 1 a 2 minutos) y revisar `outputs/plays_enriched.*` y `outputs/COACH_INSIGHTS.md`.
    - Si la verificación contradice un supuesto del diseño (valores de `team`, rol `Pass` frente a QB, `frame_dt_ok`, memoria), corregir el código correspondiente y volver a ejecutar. Registrar el tiempo total y el pico de RAM en `outputs/VERIFICATION_RUN.md`.
    - _Requirements: 4.1, 4.9, 5.4, 6.2, 7.7, 8.1, 8.9, 11.5_

  - [ ]* 8.3 Escribir prueba de integración sobre datos reales
    - Archivo `tests/test_integration_real.py`, con `pytest.mark.skipif` si no existe `data/`: corrida sobre 2 o 3 archivos de tracking vía `game_ids`, comprobar una fila por jugada, que `data/` no cambia y que solo se escribe dentro de `outputs/`; `load_or_build_master` con `outputs/` vacío calcula en memoria.
    - _Requirements: 1.5, 4.9, 6.8, 7.1, 11.3, 11.4_

- [x] 9. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Las tareas marcadas con `*` son opcionales y pueden omitirse para un MVP más rápido.
- Cada tarea referencia requisitos específicos para trazabilidad.
- Los checkpoints validan el avance de forma incremental.
- Las pruebas de propiedades validan propiedades universales de corrección con `numpy.random.default_rng(seed)` y sin `hypothesis`; las pruebas unitarias validan ejemplos y casos límite.
- Ninguna tarea agrega dependencias nuevas; `data/` es de solo lectura y las escrituras ocurren solo en `outputs/`.

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1"] },
    { "id": 1, "tasks": ["2.1"] },
    { "id": 2, "tasks": ["2.2"] },
    { "id": 3, "tasks": ["2.3"] },
    { "id": 4, "tasks": ["2.4", "2.5", "2.6", "2.7", "2.8", "3.1"] },
    { "id": 5, "tasks": ["3.2"] },
    { "id": 6, "tasks": ["3.3"] },
    { "id": 7, "tasks": ["3.4"] },
    { "id": 8, "tasks": ["3.5"] },
    { "id": 9, "tasks": ["3.6", "3.7", "3.8", "3.9", "3.10", "3.11", "3.12", "3.13", "3.14", "3.15", "3.16"] },
    { "id": 10, "tasks": ["4"] },
    { "id": 11, "tasks": ["5.1"] },
    { "id": 12, "tasks": ["5.2"] },
    { "id": 13, "tasks": ["5.3"] },
    { "id": 14, "tasks": ["5.4"] },
    { "id": 15, "tasks": ["5.5"] },
    { "id": 16, "tasks": ["5.6", "5.7", "5.8", "5.9", "5.10", "5.11", "5.12", "5.13"] },
    { "id": 17, "tasks": ["6.1"] },
    { "id": 18, "tasks": ["6.2"] },
    { "id": 19, "tasks": ["6.3", "6.4", "6.5", "6.6"] },
    { "id": 20, "tasks": ["7"] },
    { "id": 21, "tasks": ["8.1"] },
    { "id": 22, "tasks": ["8.2"] },
    { "id": 23, "tasks": ["8.3"] },
    { "id": 24, "tasks": ["9"] }
  ]
}
```
