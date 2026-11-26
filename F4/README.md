# Fase 4 · Presentación y comunicación

Entrega: Sumativa 3 (30 %), proyecto final integrador, miércoles 25-nov-2026, 23:59.

La Fase 4 no vuelve a procesar los datos: parte del conjunto que deja el pipeline (`data/processed/ordenes.csv`) y lo comunica con tres figuras y una tabla única de hallazgos.

| Archivo | Contenido |
|---|---|
| `F4_Comunicacion.ipynb` | Notebook de la fase: modalidades, montos extremos, concentración con y sin órdenes extremas, dependencia entre unidad y proveedor, y tabla de hallazgos |
| `figuras/01_modalidades.png` | Figura 1: órdenes y monto según modalidad de compra, por período |
| `figuras/02_extremos.png` | Figura 2: distribución del monto por orden y límite de monto extremo |
| `figuras/03_concentracion.png` | Figura 3: participación acumulada de los diez mayores proveedores |

## Cómo ejecutarlo

```bash
python scripts/run_all.py                 # entorno, pruebas y notebooks de F1 a F4, en orden
jupyter lab F4/F4_Comunicacion.ipynb      # de forma interactiva
```

El notebook lee `data/processed/ordenes.csv`, que genera `F2/04_transformacion.ipynb`; `run_all.py` respeta ese orden.

## Dónde está el código y qué deja

| Elemento | Contenido |
|---|---|
| `src/pipeline/comunicacion.py` | Validación de la entrada, tablas de indicadores y funciones de cada figura |
| `tests/test_comunicacion.py` | Pruebas de las tablas y de la validación de la entrada |
| `docs/hallazgos_f4.csv` | Tabla única de hallazgos: el informe y el video usan estas cifras |
| `docs/extremas_oe5_*.csv` | Composición de las órdenes de monto extremo por modalidad, rubro y unidad |

## Límites del análisis

Dos meses de una región; montos nominales, sin ajuste por inflación; los cambios entre períodos coinciden con la Ley N.º 21.634, pero no miden su efecto.
