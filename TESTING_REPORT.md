# 🧪 Palmer Penguins EDA — Bilingual Empirical Testing & QA Report

**Author / Autor:** Jean Carlos Rojas Herrera (`RojasJeanDL`)
**Target Project / Proyecto:** `penguins-eda-python` (Project 1 of Data Analyst & AI Trainer Portfolio)
**Audit date / Fecha de auditoría:** 2026-07-31
**Status / Estado:** 🟢 **PASSED — 5 blocking defects found, fixed, and pinned by tests**

---

## 🇬🇧 English (Global Engineering Verification)

### 1. Executive QA Summary

An earlier revision of this report declared the project release-ready. A second,
adversarial audit — which re-opened every exported PNG, re-executed the
notebook, and drove the dashboard through its failure states — found **five
blocking defects**, one of them visible in the first screen of the README.

This report documents them. A QA record that only ever reports green is not
evidence of quality; it is evidence that nobody looked. Every claim below is now
backed by an automated test, so the assertions in this document are re-verified
on every CI run rather than asserted once by hand.

**Audit result: 43 automated tests, 43 passing.**

### 2. Blocking defects found and resolved

| # | Defect | Evidence | Resolution | Pinned by |
|:---:|:---|:---|:---|:---|
| **B1** | **Inverted chart legend.** `plot_flipper_length_histogram` overrode the legend with a literal list, `labels=["Gentoo", "Chinstrap", "Adélie"]`. Seaborn orders hue by order of appearance, so matplotlib remapped the text onto mismatched handles: the ~190 mm cluster (Adélie, n=151) was labelled *Gentoo*, and the ~217 mm cluster (Gentoo, n=123) was labelled *Adélie*. The published README text contradicted its own figure. | Visual inspection of `images/05_flipper_histogram.png` against species group sizes and means | Removed the override; Seaborn now owns label↔handle binding. Colours are bound explicitly via `get_species_palette()` so a species keeps one colour across all five figures. | `test_flipper_legend_binds_labels_to_correct_colours` |
| **B2** | **Unexecuted notebook.** All 21 cells had `execution_count: None` and zero outputs. GitHub renders notebooks inline, so readers would have seen code with no charts, no tables, no numbers. | `nbformat` inspection of every cell | Notebook rebuilt to import `src/` helpers (single source of truth) and committed with all outputs and 5 rendered figures. | CI step *Verify the notebook still executes end to end* |
| **B3** | **No `LICENSE` file.** The dataset licence (CC0) was documented; the code licence was absent, leaving the work legally unusable by third parties. | Filesystem check | MIT licence added, with CC0 dataset attribution and both academic citations. | — |
| **B4** | **Dashboard crash on the advertised upload feature.** A CSV carrying only the four biometric columns passed `clean_penguins_data()` (342 rows) and then raised `KeyError: 'species'` in the sidebar, outside the `try/except`. A recruiter uploading their own file would hit a full-page traceback. | Reproduced against `df[CORE_METRICS]` | `validate_schema()` now gates uploads *before* cleaning and reports exactly which columns are missing. | `test_validate_schema_rejects_biometrics_only_upload` |
| **B5** | **QA report certified verifications that had not occurred.** The prior report marked `02_bill_scatter.png` as "verified: positive slope per species, flat/negative pooled" — the figure contained no regression lines at all. It also reported "~11" missing `sex` rows where the cleaned dataset has 9. | Cross-read of report vs. artefacts | Report rewritten (this document). Figure 02 now draws 3 within-species OLS fits plus a dashed pooled fit, and prints the coefficients on the chart. | `test_simpson_figure_draws_within_and_pooled_fits` |

### 3. Non-blocking issues also corrected

- **Hardcoded KPI deltas.** The dashboard's metric cards announced `Gentoo +35%` and `r = 0.87` regardless of filter state — including when Gentoo was filtered out. All deltas are now recomputed from the filtered frame.
- **Overstated separation claim.** The README asserted flipper length above 210 mm "cleanly separates" Gentoo. The ranges overlap (Gentoo 203–231 mm, non-Gentoo 172–212 mm). An empirical threshold scan replaces the claim: **207 mm, 97.7% accuracy, 8 errors**; 210 mm scores 94.4%.
- **Imprecise mass uplift.** "~35%" replaced with the measured **+37.2%** (vs. Adélie) and **+36.0%** (vs. Chinstrap), plus the observation that Adélie and Chinstrap differ by only 32 g and are therefore *not* separable by mass.
- **HTML injection via uploaded CSV.** Cell values were interpolated raw into `st.markdown(unsafe_allow_html=True)`; a crafted CSV could inject markup. All cells now pass through `html.escape()`.
- **`<NA>` leaking into the UI.** Missing `sex` rendered as the literal string `<NA>`; now an em dash.
- **Ambiguous sex filter.** The mask only applied when fewer than 2 options were selected, silently keeping unrecorded-sex rows in some states and dropping them in others. Replaced with an always-applied mask plus an explicit *"include unrecorded sex (9)"* checkbox.
- **Empty filter state.** Deselecting all species produced an all-`NaN` correlation heatmap with no explanation. Now short-circuits with a warning.
- **Dependency floor too low.** `requirements.txt` declared `streamlit>=1.35.0` while `app.py` uses the `width="stretch"` API introduced in 1.49 — a clean install resolving to 1.35 would not start. Floors raised to tested versions.
- **Machine-specific launcher.** `Palmer_Penguins_Dashboard.desktop` hardcoded `/mnt/IT_Program/Portafolio/Palmer_Penguins`, leaking the author's directory layout and working on no other machine. Replaced by `scripts/install_linux_shortcut.sh`, which generates the entry at install time; the artefact is now gitignored.
- **Colour inconsistency.** Seaborn desaturates categorical fills to 75%, so "Adélie blue" differed between the bar chart and the scatter/histogram. Bars now render at full saturation.
- **Dead code.** Unused imports (`numpy`, `plotly.graph_objects`, `typing.Tuple`) removed; the `dpi` argument of `setup_visualization_theme()` was silently overridden by a hardcoded `savefig(dpi=150)` and now actually controls export resolution via `savefig.dpi`.

### 4. Environment & Dependency Isolation Test

- **Virtual environment:** validated isolated `.venv` created via standard `venv + pip`.
- **Verified versions:** `pandas 3.0.5`, `numpy 2.5.1`, `seaborn 0.13.2`, `matplotlib 3.11.1`, `scipy 1.18.0`, `streamlit 1.60.0`, `plotly 6.9.0`, `statsmodels 0.14.6`, `notebook 7.6.1`, `pytest 9.1.1`.
- **Declared floors:** `requirements.txt` now states the minimum versions the project is tested against, not aspirational ones.
- **Headless backend:** `matplotlib.use("Agg")` in both the export pipeline and the test suite — no X11 dependency on CI runners.
- **CI matrix:** GitHub Actions runs the suite on Python 3.10 and 3.12, then re-executes the export pipeline and the notebook.

### 5. Data Integrity & Bias-Aware Cleaning Audit

| Check | Expected | Verified |
|:---|:---:|:---:|
| Raw observations ingested | 344 rows × 8 cols | 🟢 |
| Rows dropped (all four biometrics `NaN`) | exactly 2 | 🟢 |
| Clean row count | 342 | 🟢 |
| Core metrics null after cleaning | 0 | 🟢 |
| Missing `sex` retained, never imputed | 9 | 🟢 |
| Cleaning does not mutate its input frame | — | 🟢 |
| Categorical whitespace stripped | — | 🟢 |

### 6. Statistical Claim Verification

Each statistic printed in the README is recomputed from `data/penguins.csv` by `tests/test_statistical_claims.py`:

| Claim | Measured | Status |
|:---|:---:|:---:|
| Flipper length ↔ body mass | `r = 0.871` (strongest pair in the matrix) | 🟢 |
| Pooled bill length ↔ depth | `r = -0.235` | 🟢 |
| Within-species bill correlation, Adélie | `r = +0.391` | 🟢 |
| Within-species bill correlation, Chinstrap | `r = +0.654` | 🟢 |
| Within-species bill correlation, Gentoo | `r = +0.643` | 🟢 |
| Gentoo mean body mass | `5,076 g` | 🟢 |
| Gentoo uplift vs. Adélie / Chinstrap | `+37.2%` / `+36.0%` | 🟢 |
| Adélie vs. Chinstrap mass gap | `32 g` (not separable) | 🟢 |
| Males heavier than females, every species | — | 🟢 |
| Gentoo restricted to Biscoe, Chinstrap to Dream | — | 🟢 |
| Optimal flipper threshold | `207 mm`, 8 errors, `97.7%` | 🟢 |
| 210 mm threshold is worse | `94.4%` | 🟢 |
| Gentoo / non-Gentoo flipper ranges overlap | `203–231` vs `172–212` | 🟢 |

### 7. Chart Export & Rendering Audit

All 5 charts regenerated via `src/generate_charts.py` at 150 DPI on a colourblind-accessible palette, then re-opened and inspected:

| Chart Filename | Size | Structural & Analytical Verification | Status |
|:---|:---:|:---|:---:|
| `01_species_distribution.png` | 52.0 KB | Legend colours verified against the plotted bars; Biscoe/Gentoo = 123, Dream/Chinstrap = 68, Adélie across all three | 🟢 **PASS** |
| `02_bill_scatter.png` | 192.0 KB | 3 within-species OLS fits (all positive slopes) + 1 dashed pooled fit (negative slope), coefficients annotated on-figure | 🟢 **PASS** |
| `03_mass_by_species.png` | 47.7 KB | Boxplot separates Gentoo mass tier and male/female dimorphism in all three species | 🟢 **PASS** |
| `04_correlation_heatmap.png` | 86.1 KB | Pearson matrix with human-readable axis labels; `r = 0.87` flipper↔mass confirmed | 🟢 **PASS** |
| `05_flipper_histogram.png` | 89.1 KB | **Legend re-verified after B1.** Every label now binds to its own species colour: Adélie (blue, ~190 mm), Chinstrap (orange, ~196 mm), Gentoo (green, ~217 mm) | 🟢 **PASS** |

### 8. Dashboard, Notebook & Documentation Consistency

- **`app.py`:** boots without exception; renders 4 tabs and 4 KPI cards; survives empty species selection, single-species selection, every sex-filter state, and the language toggle — all asserted via Streamlit's `AppTest` harness.
- **`notebooks/penguins_eda.ipynb`:** executes end to end with 0 errors, 5 rendered figures and 4 output tables. Its printed values (11 raw missing `sex` / 9 retained; 207 mm at 97.7%) match its own narrative text.
- **`README.md`:** architecture tree reconciled against the actual filesystem; all `images/*.png` references resolve; every quoted statistic maps to a passing test.

### 9. Final Verdict

🟢 **APPROVED FOR GITHUB RELEASE.**

Not because the first pass was clean — it was not — but because the defects are now identified, corrected, and held in place by 43 automated checks that run on every push.

---

## 🇪🇸 Español (Reporte de Testeo y Auditoría Analítica)

### 1. Resumen Ejecutivo de QA

Una revisión anterior de este informe declaró el proyecto listo para publicar. Una
segunda auditoría adversarial — que reabrió cada PNG exportado, reejecutó el
cuaderno y llevó el dashboard a sus estados de fallo — encontró **cinco defectos
bloqueantes**, uno de ellos visible en la primera pantalla del README.

Este documento los deja registrados. Un informe de QA que siempre sale verde no
demuestra calidad: demuestra que nadie miró. Cada afirmación está ahora
respaldada por una prueba automatizada, de modo que se reverifica en cada
ejecución de CI en lugar de afirmarse una sola vez a mano.

**Resultado: 43 pruebas automatizadas, 43 en verde.**

### 2. Defectos bloqueantes encontrados y resueltos

| # | Defecto | Resolución |
|:---:|:---|:---|
| **B1** | **Leyenda invertida.** `plot_flipper_length_histogram` sobreescribía la leyenda con una lista literal `["Gentoo", "Chinstrap", "Adélie"]`. Seaborn ordena el `hue` por orden de aparición, así que matplotlib reasignó los textos a handles equivocados: el clúster de ~190 mm (Adélie, n=151) quedó etiquetado como *Gentoo* y el de ~217 mm (Gentoo, n=123) como *Adélie*. El texto del README contradecía a su propia figura. | Eliminada la sobreescritura; los colores se fijan explícitamente con `get_species_palette()` para que cada especie conserve un único color en las cinco figuras. |
| **B2** | **Cuaderno sin ejecutar.** Las 21 celdas tenían `execution_count: None` y cero salidas. GitHub renderiza los cuadernos en línea: el lector habría visto código sin gráficos, tablas ni números. | Cuaderno reconstruido para importar los helpers de `src/` (fuente única de verdad) y publicado con todas sus salidas y 5 figuras. |
| **B3** | **Sin archivo `LICENSE`.** Se documentaba la licencia del dataset (CC0) pero no la del código. | Licencia MIT añadida, con atribución CC0 del dataset y ambas citas académicas. |
| **B4** | **Crash del dashboard en la función más publicitada.** Un CSV con solo las cuatro columnas biométricas superaba la limpieza (342 filas) y luego lanzaba `KeyError: 'species'` fuera del `try/except`. | `validate_schema()` valida el esquema *antes* de limpiar e informa exactamente qué columnas faltan. |
| **B5** | **El informe de QA certificaba verificaciones inexistentes.** Marcaba `02_bill_scatter.png` como "verificado: pendiente positiva por especie" cuando la figura no tenía ninguna recta de regresión. También reportaba "~11" filas sin `sex` donde el dataset limpio tiene 9. | Informe reescrito (este documento). La figura 02 dibuja 3 ajustes OLS por especie más el ajuste agregado punteado, con los coeficientes impresos en el gráfico. |

### 3. Correcciones adicionales

- **KPIs con valores fijos:** las tarjetas anunciaban `Gentoo +35%` y `r = 0.87` incluso con Gentoo filtrado fuera. Ahora todos los deltas se recalculan sobre el DataFrame filtrado.
- **Afirmación sobreestimada:** el README decía que 210 mm separa "limpiamente" a los Gentoo. Los rangos se solapan (Gentoo 203–231 mm, no-Gentoo 172–212 mm). Sustituido por un barrido empírico: **207 mm, 97.7 % de exactitud, 8 errores**; 210 mm rinde 94.4 %.
- **Precisión en la masa:** "~35 %" sustituido por **+37.2 %** (vs Adélie) y **+36.0 %** (vs Chinstrap), añadiendo que Adélie y Chinstrap difieren solo 32 g y por tanto **no** se separan por masa.
- **Inyección HTML vía CSV subido:** los valores se interpolaban crudos en `st.markdown(unsafe_allow_html=True)`. Ahora pasan por `html.escape()`.
- **`<NA>` visible en la interfaz:** el sexo ausente se mostraba como el literal `<NA>`; ahora es una raya.
- **Filtro de sexo ambiguo:** la máscara solo se aplicaba con menos de 2 opciones seleccionadas. Sustituida por una máscara siempre aplicada más una casilla explícita *"incluir sexo no registrado (9)"*.
- **Estado de filtro vacío:** deseleccionar todas las especies producía un heatmap de `NaN` sin explicación. Ahora se corta con un aviso.
- **Piso de dependencias falso:** `requirements.txt` declaraba `streamlit>=1.35.0` mientras `app.py` usa la API `width="stretch"` introducida en 1.49. Pisos elevados a las versiones testeadas.
- **Lanzador con ruta absoluta:** el `.desktop` fijaba `/mnt/IT_Program/Portafolio/Palmer_Penguins`, exponiendo la estructura de directorios del autor y sin funcionar en ninguna otra máquina. Sustituido por `scripts/install_linux_shortcut.sh`, que lo genera en tiempo de instalación.
- **Inconsistencia de color:** Seaborn dessatura los rellenos categóricos al 75 %, por lo que el azul de Adélie difería entre el gráfico de barras y el resto. Las barras se renderizan ahora a saturación completa.
- **Código muerto:** imports sin usar eliminados; el parámetro `dpi` de `setup_visualization_theme()` quedaba anulado por un `savefig(dpi=150)` fijo y ahora controla realmente la resolución de exportación.

### 4. Verificación estadística

Las 13 pruebas de `tests/test_statistical_claims.py` recalculan desde el CSV original: `r = 0.871` aleta↔masa; `r = -0.235` agregado y `+0.391 / +0.654 / +0.643` por especie; masa media Gentoo `5.076 g` con `+37.2 %` y `+36.0 %` de ventaja; segregación insular; umbral óptimo de aleta en `207 mm` con `97.7 %`; y el solapamiento real de rangos que invalida la palabra "limpiamente".

### 5. Veredicto Final

🟢 **APROBADO PARA PUBLICACIÓN EN GITHUB.**

No porque la primera pasada estuviera limpia — no lo estaba — sino porque los
defectos están identificados, corregidos y sujetos por 43 comprobaciones
automáticas que se ejecutan en cada push.
