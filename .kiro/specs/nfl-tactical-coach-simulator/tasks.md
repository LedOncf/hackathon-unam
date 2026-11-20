# Implementation Plan: NFL Tactical Coach Simulator

## Overview

El plan sigue el orden del diseño: backend (carga de datos, estadística, filtros, recomendación, jugada real con tracking), servicio estático y proxy de Vite, dashboard React, escenarios, reproducción cuadro por cuadro, `src/plots.py`, `README.md` y verificación final. Lenguajes: Python (FastAPI, pandas, numpy) y TypeScript (React, Recharts, Tailwind), según el diseño. Las pruebas de propiedades usan `run_property` de `tests/helpers.py` (sin hypothesis) y, para TypeScript, `node --test`. No se añade ninguna dependencia fuera del stack fijo. En particular, ninguna tarea instala matplotlib: el supuesto A1 deja esa decisión al equipo, y `src/plots.py` lo importa de forma perezosa y falla con código 2 si no está.

## Tasks

- [x] 1. Fundamentos del backend: configuración, almacén de datos, estadística y validación de filtros
  - [x] 1.1 Crear `backend/config.py` y `backend/store.py`
    - Rutas absolutas desde `Path(__file__).resolve().parent.parent`, constantes `MIN_N` y `Z95`
    - `PlaysStore`: carga única del CSV, validación de columnas requeridas, columnas derivadas (`ytg_bucket`, `box_int`, `bite_bin`, `prot_cat`, `play_id`), exclusión de `down` fuera de 1 a 4 y de nulos obligatorios, `filter_values` precalculados, `store.error` y dependencia `require_store()` que lanza 503 en español
    - _Requirements: 1.1, 1.2, 1.4, 1.5, 3.10_

  - [x] 1.2 Crear `backend/stats.py`
    - `wilson_pct`, `newcombe_diff_pp` (envuelven `src.analyze.wilson_ci` y `diff_props_ci`), `mean_or_none`, `r1`/`r2`/`r3` que normalizan `-0.0`
    - Redondear una sola vez al devolver
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.7, 4.10, 16.14_

  - [x] 1.3 Crear `backend/situation.py`
    - `SituationFilter`, `parse_situation` (valida todos los parámetros y nombra todos los inválidos en un 422 con `{"detail", "invalid"}`) y `subset_mask`
    - Cadena vacía omite el criterio; `down` acepta `1,2,3,4,3-4`; `defenders_in_box` acepta `"7"` y `"7.0"`
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.10_

  - [ ]* 1.4 Escribir pruebas de propiedades de `situation.py` en `tests/test_situation.py`
    - **Property 2: El Subset es exactamente el conjunto de jugadas que cumplen todos los criterios**
    - **Property 3: Los filtros inválidos se rechazan con 422 y se nombran todos**
    - Añadir una prueba de ejemplo por cada rama de 422
    - **Validates: Requirements 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.10, 15.5**

  - [ ]* 1.5 Escribir prueba de propiedad de Wilson en `tests/test_recommend_props.py`
    - Crear `make_plays_df(rng)` y los generadores de filtros válidos e inválidos en `tests/helpers.py` o en un módulo de generadores de `tests/`
    - **Property 5: El intervalo de Wilson coincide con la fórmula y es coherente**
    - **Validates: Requirements 4.1, 4.2, 4.10**

- [x] 2. Aplicación FastAPI, endpoint de filtros y servicio estático
  - [x] 2.1 Implementar `backend/filters_service.py` y reemplazar `backend/main.py`
    - `GET /api/filters` con listas ordenadas, sin nulos, enteros sin `.0` y categorías de Yards_To_Go_Bucket
    - `main.py`: conservar `app` y `GET /health` (200 aunque falle la carga), `lifespan` que carga el store y registra errores en stderr sin terminar, router `/api`, manejador global 500 en español, CORS solo con `APP_ENV=dev` y origen `http://localhost:5173`, montaje de `StaticFiles(dashboard/dist, html=True)` en `/` al final y solo si el directorio existe
    - Endpoints como `def` (no `async`)
    - _Requirements: 1.1, 1.3, 1.5, 1.6, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 10.1, 10.2, 10.3, 10.7, 10.8, 10.9, 10.10_

  - [ ]* 2.2 Escribir prueba de propiedad de filtros en `tests/test_filters.py`
    - **Property 1: Los valores de filtros están bien formados y existen en los datos**
    - **Validates: Requirements 2.1, 2.2, 2.3, 2.7**

  - [ ]* 2.3 Escribir pruebas de ejemplo del contrato de la aplicación en `tests/test_app_contract.py`
    - Con `TestClient`: `/health` 200 con CSV ausente; 503 en `/api/*` para CSV ausente, ilegible o con columnas faltantes
    - Ninguna ruta de negocio fuera de `/api` salvo `/health`; sin CORS sin `APP_ENV=dev`; con él solo `http://localhost:5173`; arranque sin `dashboard/dist`
    - Espía de `open` y `pandas.read_csv` durante `/api/filters` y `/api/recommend` (0 lecturas); revisión del código de `backend/` sin dependencias extra ni escrituras a disco
    - _Requirements: 1.3, 1.5, 1.6, 10.1, 10.3, 10.7, 10.8, 10.9, 10.10, 15.6_

- [x] 3. Checkpoint - Backend base
  - Ensure all tests pass, ask the user if questions arise.

- [x] 4. Servicio de recomendación y Verdict
  - [x] 4.1 Crear `backend/schemas.py` y `backend/recommend_service.py`
    - Modelos Pydantic de `/api/recommend` (intervalos como listas `[lo, hi]`)
    - Grupos Play Action y Tradicional, Blitz y Estándar, medias con conteo `n_used`, etiqueta "Muestra insuficiente (n < 30)", diferencias nulas si falta un grupo, `play_action.effect_yards`, `blitz.effect_pp_ci`, `pressure_pp`, diferencias de `time_to_throw` y `min_rusher_dist_at_throw`
    - Tablas `lb_bite_table` (4 filas, bordes 0.10, 0.69, 1.16, con `n_pa` y `n_trad`) y `protection_table` (5 filas, A7)
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9, 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 16.13, 16.14_

  - [x] 4.2 Crear `backend/verdict.py`
    - Lógica de decisión con los cuatro códigos, texto de máximo 280 caracteres, caso `Red Zone`, nota de blitz solo con ambos n ≥ 30, aclaración "Éxito por down y distancia; sin EPA.", Subset vacío (A8) y efecto nulo si algún n es 0
    - Evitar los verbos "gana", "pierde", "supera" y "mejora"
    - _Requirements: 3.9, 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8, 7.9_

  - [x] 4.3 Registrar `GET /api/recommend` en `backend/main.py`
    - Conectar `parse_situation`, `recommend_service` y `verdict`; 422 con detalle en español; 200 con `subset_n = 0` para Subset vacío
    - _Requirements: 3.5, 3.6, 3.7, 3.8, 3.9, 7.1, 1.7_

  - [ ]* 4.4 Escribir pruebas de propiedades de estadística de grupos en `tests/test_recommend_props.py`
    - **Property 4: Los grupos particionan el Subset**
    - **Property 6: Las diferencias coinciden con el cálculo directo y son nulas si falta un grupo**
    - **Property 7: Las medias excluyen solo los nulos de su métrica**
    - **Property 8: La etiqueta de muestra insuficiente depende solo de n**
    - **Validates: Requirements 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9, 5.2, 5.3, 5.4, 5.5, 5.6, 6.4, 16.13, 16.14**

  - [ ]* 4.5 Escribir pruebas de propiedades de tablas en `tests/test_recommend_tables.py`
    - **Property 9: La tabla de `lb_bite_yards` asigna cada valor a un único rango**
    - **Property 10: La tabla de `protection_advantage` siempre tiene cinco filas completas**
    - **Validates: Requirements 6.1, 6.2, 6.3, 6.5, 6.6**

  - [ ]* 4.6 Escribir pruebas de propiedades del Verdict en `tests/test_verdict.py`
    - **Property 11: El código del Verdict se decide solo por n y el intervalo**
    - **Property 12: El texto del Verdict tiene el formato y el límite exigidos**
    - **Property 13: El signo del Effect_pp del Verdict coincide con la diferencia de Success_Rate**
    - **Validates: Requirements 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8, 7.9**

  - [ ]* 4.7 Escribir pruebas con datos reales en `tests/test_real_data.py`
    - Omitir con `pytest.skip` si falta `outputs/plays_enriched.csv`
    - Filtro vacío: n = 2,024 y 6,498, diferencia 6.809 ± 0.01 pp; `any_pressure` 47.3% y 33.8% ± 0.1
    - Tres escenarios con las tolerancias de 16.22 (94 y 105, +24.3 ± 0.1; 80 y 278, -1.79 ± 0.01, -0.8 ± 0.1, `SIN_VENTAJA_CLARA`; n = 265, 50.9 ± 0.1, 2.60 ± 0.01)
    - Medir el percentil 95 de 100 peticiones secuenciales (informativo)
    - _Requirements: 1.7, 4.11, 5.7, 16.22_

- [x] 5. Checkpoint - Recomendación
  - Ensure all tests pass, ask the user if questions arise.

- [x] 6. Jugada real con tracking
  - [x] 6.1 Crear `backend/tracking.py`
    - `read_play_tracking` por bloques de 100,000 filas con `usecols` y filtro por `playId`, un solo archivo por petición
    - `normalize_xy` (idéntico a `src.tracking_metrics`), `find_range` con respaldo a `snap_frameId`/`res_frameId` y aviso, descarte con `SinRango`
    - `assign_roles` con carga perezosa y `threading.Lock` de `pffScoutingData.csv` y `players.csv`, tabla de roles, `is_lb` (A4) y `make_label`; exclusión del balón de `players`
    - `LB_POSITIONS` igual al de `src.tracking_metrics`
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7, 9.9, 9.10, 9.11, 9.12, 9.13, 17.12, 17.13, 17.14, 17.15, 17.16, 17.17_

  - [x] 6.2 Crear `backend/sample_play_service.py` y registrar `GET /api/sample-play`
    - Parámetros de situación más `focus` (`bite`, `pa_fallida`, `blitz_exitoso`; otro valor da 422 que nombra `focus`) y `exclude` (máximo 100)
    - Orden de candidatas `pref \ exclude`, `resto \ exclude`, `pref`, `resto` (A6); hasta 20 aperturas y 5 descartes por rango; 404 sin candidatas; 503 con la ruta esperada si no hay tracking; `random.Random` inyectable
    - Respuesta con `preferred`, `play` (campos no disponibles como `null`), `snap_frame`, `pass_forward_frame`, `frames`, `players` (con `position`, `label`, `side`, `is_lb`) y `ball`
    - Mantener `/api/filters` y `/api/recommend` operativos sin tracking
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8, 8.9, 9.8, 9.13, 9.14, 15.6, 16.15, 16.16, 16.17, 16.18, 16.19, 17.12_

  - [ ]* 6.3 Escribir prueba de propiedad de selección en `tests/test_sample_play_select.py`
    - **Property 14: La selección de jugada respeta tracking, preferencia, `focus` y `exclude`**
    - **Validates: Requirements 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 16.15, 16.16, 16.17, 16.18**

  - [ ]* 6.4 Escribir pruebas de propiedades de tracking en `tests/test_tracking.py`
    - Usar tracking sintético en `tmp_path`
    - **Property 15: El recorte de tracking devuelve solo la jugada y el rango pedidos**
    - **Property 16: La normalización de coordenadas es una ida y vuelta**
    - **Property 17: Cada jugador tiene un solo rol y la etiqueta sigue la tabla**
    - **Validates: Requirements 9.1, 9.3, 9.5, 9.6, 9.7, 9.9, 9.10, 9.11, 9.12, 9.13, 17.12, 17.13, 17.14, 17.15, 17.16, 17.17**

  - [ ]* 6.5 Escribir pruebas de integración de tracking en `tests/test_sample_play_io.py`
    - Directorio sin archivos: 503 con la ruta; solo el archivo de la tercera candidata: éxito tras 2 fallos; archivo sintético de más de 100,000 filas leído por bloques
    - Con tracking real (omitir si falta): consistencia de "Avance de LB" en `snap + 10` con `lb_bite_yards` y de la distancia QB–Rush con `min_rusher_dist_at_throw` (≤ 0.1), solo en jugadas con resolución `pass_forward` (A5); con `TRACKING_DIR` inexistente, `/api/filters` y `/api/recommend` responden 200
    - _Requirements: 8.8, 8.9, 9.2, 9.14, 15.6, 17.25, 17.26_

- [x] 7. Checkpoint - Backend completo
  - Ensure all tests pass, ask the user if questions arise.

- [x] 8. Dashboard React
  - [x] 8.1 Configurar proxy y base del cliente en `dashboard/`
    - `vite.config.ts`: conservar `base: './'` y añadir `server.proxy` de `/api` hacia `http://localhost:8000`
    - `api/types.ts`, `api/client.ts` (`fetch('api/...')` sin diagonal inicial, tiempo de espera de 10 s, `ApiError`, mensajes en español), `hooks/useRequest.ts` (contador de solicitud, `AbortController`, conserva el último `data`, `retry` con la URL vigente), `lib/format.ts`, `state/situation.ts` (`toQuery` con `URLSearchParams`), `state/scenarios.ts` (tres presets sin cifras de resultados)
    - _Requirements: 10.4, 10.5, 10.6, 11.7, 11.8, 11.9, 11.10, 11.11, 16.7_

  - [x] 8.2 Crear `dashboard/src/lib/board.ts`
    - Funciones puras: `viewWindow` (margen de 3 yardas, proporción 1:1), `liveLbAdvance`, `liveQbRushDist` (nulas si falta QB, LB o Pass Rush), `fieldYardNumber`
    - Sin dependencias para poder probarlo con `node --test`
    - _Requirements: 13.6, 17.19, 17.20, 17.23_

  - [ ]* 8.3 Escribir pruebas de propiedades de TypeScript
    - `dashboard/tests/board.test.ts` con PRNG sembrado, excluido de `tsconfig`; `tests/test_board_ts.py` lo ejecuta con `subprocess` y se omite si no hay `node`
    - **Property 18: Las métricas en vivo siguen su definición**
    - **Property 19: La ventana visible contiene todas las posiciones con margen**
    - **Validates: Requirements 13.6, 17.19, 17.20, 17.23**

  - [x] 8.4 Crear `FilterPanel.tsx` y `ScenarioBar.tsx`
    - Selectores Down (Todos, 1, 2, 3-4), Yardas por Recorrer (Todos, corta, media, larga), Cobertura, Formación y Defensores en la Caja (con 5, 6, 7 y 8 siempre presentes, sin duplicados), "Restablecer", valor inicial "Todos"
    - Scenario_Bar con los tres botones y `aria-pressed`
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.6, 16.1, 16.5_

  - [x] 8.5 Crear panel central: `PanelState.tsx`, `VerdictCard.tsx`, `ComparisonCharts.tsx`, `PhysicsChart.tsx`, `ScopeFooter.tsx`
    - Tarjeta con color por código, gráficas Recharts con `ErrorBar` del Wilson_CI, `n=` junto a cada barra, opacidad entre 0.3 y 0.5 y aviso para n < 30, nulos como "–", mensaje y ocultación si `subset_n = 0`
    - Tema oscuro con contraste ≥ 4.5:1, sin `slate-500` ni más oscuro sobre fondo oscuro; pie con el alcance de los datos
    - _Requirements: 11.7, 11.8, 12.1, 12.2, 12.3, 12.4, 12.5, 12.6, 12.7, 12.8, 12.9, 12.10, 12.11_

  - [x] 8.6 Crear `ScenarioCard.tsx`
    - Cifras solo desde la respuesta de `/api/recommend` según el escenario activo; etiqueta "no concluyente" si el IC contiene 0; etiqueta de muestra insuficiente por grupo; texto "Jugada de ejemplo sin el patrón destacado" si `preferred = false`; pie fijo "Éxito medido por down y distancia; sin EPA. Una sola jugada ilustra, no prueba."
    - Texto de "Caja de 7" (A3); sin los verbos prohibidos
    - _Requirements: 16.7, 16.8, 16.9, 16.10, 16.11, 16.12, 16.17, 16.21_

  - [x] 8.7 Crear componentes de la pizarra
    - `FieldSvg.tsx`, `PlayerMarker.tsx` (forma y color únicos por rol), `Legend.tsx`, `PlayMeta.tsx` ("No disponible" para ausentes), `CoachBoard.tsx`
    - Trayectorias, flechas de LB con `lb_bite_yards`, línea QB–Pass Rush con `min_rusher_dist_at_throw`, `Player_Label` (texto de 1.6 yardas para QB, LB y Rush; 1.1 para el resto), texto "Jugada real de ejemplo: ilustra, no prueba, la tendencia", mensaje de error conservando la última jugada
    - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5, 13.6, 13.7, 13.10, 13.12, 17.11, 17.18_

  - [x] 8.8 Crear `hooks/usePlayback.ts`, `PlaybackController.tsx` y `LiveMetrics.tsx`
    - `setInterval` de 100 ms con limpieza al desmontar y al cambiar de jugada, reinicio en `snap` al llegar al final, botón Reproducir/Pausa, deslizador con "Tiempo desde el snap: X.X s", "Ir a pass_forward", deshabilitado con un solo frame
    - Métricas "Avance de LB" y "Distancia QB–Rush más cercano" con referencias en `snap + 10` y en `pass_forward`; "–" si faltan elementos
    - _Requirements: 13.11, 17.1, 17.2, 17.3, 17.4, 17.5, 17.6, 17.7, 17.8, 17.9, 17.10, 17.19, 17.20, 17.21, 17.22, 17.23, 17.24, 17.27_

  - [x] 8.9 Integrar todo en `dashboard/src/App.tsx`
    - Estado `situation`, `activeScenario`, `exclude` (últimos 100), `focus`; canales independientes `filters`, `recommend` y `samplePlay`
    - Cambio de selector y "Restablecer" cierran la Scenario_Card y vacían `exclude`; presets aplican filtro y `focus`; "Cargar otra jugada real" deshabilitado durante la carga; errores solo en el panel afectado con "Reintentar"
    - Diseño de tres paneles (izquierdo, central, derecho)
    - _Requirements: 11.5, 11.6, 11.7, 11.8, 11.9, 11.10, 13.8, 13.9, 13.10, 16.2, 16.3, 16.4, 16.5, 16.6, 16.20, 17.27_

  - [ ]* 8.10 Escribir verificación estática del dashboard en `tests/test_dashboard_source.py`
    - Sin `fetch` con ruta que empiece con `/`; sin `localhost`, `127.0.0.1`, `http://` ni `https://` en `dashboard/src` y `dashboard/dist` (si existe), salvo la configuración de `vite.config.ts`
    - `vite.config.ts` conserva `base: './'` y el proxy; las cifras "12.3", "24.3", "1.8", "50.9" y "2.60" ausentes como constantes de resultado; verbos prohibidos ausentes en la Scenario_Card
    - _Requirements: 10.4, 10.5, 10.6, 16.7, 16.11_

- [x] 9. Checkpoint - Dashboard
  - Ensure all tests pass, ask the user if questions arise.

- [x] 10. Figuras estáticas
  - [x] 10.1 Crear `src/plots.py` con las funciones de cálculo
    - Docstring que declara que matplotlib no pertenece al stack fijo y que su uso está pendiente de decisión del equipo (A1)
    - `load_plays` valida archivo y columnas (salida 1 con mensaje en español); `cells_fig1`, `cells_fig2`, `cells_fig3` sin matplotlib, con `wilson_ci` y `diff_props_ci` de `src.analyze` y marca "no concluyente" con n < 30
    - No abrir tracking; no añadir matplotlib a `requirements.txt` ni importarlo desde `backend/`
    - _Requirements: 14.3, 14.4, 14.5, 14.6, 14.9, 14.11, 14.12, 14.13_

  - [ ]* 10.2 Escribir prueba de propiedad de celdas en `tests/test_plots_cells.py`
    - **Property 20: Las celdas de las figuras suman al total y marcan las muestras pequeñas**
    - Comparar celdas conocidas de `COACH_INSIGHTS.md` (omitir si falta el CSV)
    - **Validates: Requirements 14.4, 14.5, 14.6, 14.12**

  - [x] 10.3 Añadir el dibujo y `main` a `src/plots.py`
    - Importar matplotlib de forma perezosa con backend `Agg`; si falta, mensaje en español que lo nombra y salida 2 antes de escribir cualquier PNG
    - Renderizar las tres figuras en memoria y luego guardar a 300 DPI en `outputs/fig1_play_action_coverage.png`, `fig2_lb_bite_box.png` y `fig3_blitz_protection.png`; textos en español; imprimir rutas y salida 0
    - Pruebas de ejemplo (CSV ausente, columna faltante, matplotlib ausente simulado, sin PNG creados); la ejecución completa solo si matplotlib ya está instalado
    - _Requirements: 14.1, 14.2, 14.7, 14.8, 14.9, 14.10, 14.13_

- [x] 11. Reporte ejecutivo
  - [x] 11.1 Redactar `README.md` en la raíz
    - Secciones en orden: "Resumen del problema" (≤ 150 palabras), "Metodología", "Hallazgos principales" (tres, con cifra, IC y n, tomados de `outputs/COACH_INSIGHTS.md`), "Limitaciones", "Cómo correr la app"
    - Imágenes con rutas relativas sin `/` inicial y texto alternativo en español; si los PNG no existen, nota visible con `python src/plots.py` (A1)
    - Bloques copiables de `.venv`, instalación, Uvicorn, `npm run dev`, `npm run build` y `plots.py`; rutas de la API; una frase sobre escenarios y otra sobre la reproducción
    - Verbos de asociación, sin "causa" ni "garantiza", sin credenciales, `localhost` solo en bloques de código, máximo 1,200 palabras sin código ni tablas
    - _Requirements: 15.4, 18.1, 18.2, 18.3, 18.4, 18.5, 18.6, 18.7, 18.8, 18.9, 18.10, 18.11, 18.12, 18.13, 18.14_

  - [ ]* 11.2 Escribir `tests/test_readme.py`
    - Cinco secciones y su orden; rutas de imagen existentes o nota de 18.13; ausencia de palabras y cadenas prohibidas; límite de palabras; cifras de hallazgos contra `COACH_INSIGHTS.md`
    - _Requirements: 18.5, 18.7, 18.8, 18.12, 18.13, 18.14, 18.15_

- [x] 12. Verificación de compilación y operación
  - [x] 12.1 Ejecutar y corregir las verificaciones de build e importación
    - `npm run build` en `dashboard/` sin errores de TypeScript ni Vite y con `dist/index.html`
    - `python -c "import backend.main"` con `.venv` sin excepciones
    - Prueba de humo con `TestClient` y `dashboard/dist`: `/` devuelve `index.html`, `/health`, `/api/filters` y `/api/recommend` responden 200 en menos de 5 s
    - _Requirements: 10.2, 15.1, 15.2, 15.3, 15.5_

- [x] 13. Checkpoint final - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Las tareas con `*` son opcionales (pruebas) y se pueden omitir para un MVP más rápido.
- Cada tarea cita criterios concretos de `requirements.md` y las propiedades numeradas de `design.md`.
- Las pruebas de propiedades usan `run_property` de `tests/helpers.py` con mínimo 100 iteraciones y el comentario `# Feature: nfl-tactical-coach-simulator, Property N: ...`.
- Las pruebas que dependen de `outputs/plays_enriched.csv`, del tracking real (A2) o de matplotlib (A1) se omiten si el recurso no existe.
- Ninguna tarea instala matplotlib; instalarlo queda como decisión del equipo (A1).

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1"] },
    { "id": 1, "tasks": ["1.2", "1.3"] },
    { "id": 2, "tasks": ["1.4", "1.5", "2.1"] },
    { "id": 3, "tasks": ["2.2", "2.3"] },
    { "id": 4, "tasks": ["3"] },
    { "id": 5, "tasks": ["4.1", "4.2"] },
    { "id": 6, "tasks": ["4.3"] },
    { "id": 7, "tasks": ["4.4", "4.5", "4.6", "4.7"] },
    { "id": 8, "tasks": ["5"] },
    { "id": 9, "tasks": ["6.1"] },
    { "id": 10, "tasks": ["6.2"] },
    { "id": 11, "tasks": ["6.3", "6.4", "6.5"] },
    { "id": 12, "tasks": ["7"] },
    { "id": 13, "tasks": ["8.1", "8.2"] },
    { "id": 14, "tasks": ["8.3", "8.4", "8.5", "8.6", "8.7", "8.8"] },
    { "id": 15, "tasks": ["8.9"] },
    { "id": 16, "tasks": ["8.10"] },
    { "id": 17, "tasks": ["9"] },
    { "id": 18, "tasks": ["10.1"] },
    { "id": 19, "tasks": ["10.2", "10.3"] },
    { "id": 20, "tasks": ["11.1"] },
    { "id": 21, "tasks": ["11.2"] },
    { "id": 22, "tasks": ["12.1"] },
    { "id": 23, "tasks": ["13"] }
  ]
}
```
