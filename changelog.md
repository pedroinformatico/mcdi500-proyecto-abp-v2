# Registro de cambios

Cambios del proyecto por fase, del más reciente al más antiguo. Cada entrada indica el commit donde se puede verificar y el motivo. Los identificadores son los de la rama `main`; `git show <commit>` muestra el detalle.

La primera sección reúne las observaciones recibidas en las evaluaciones anteriores y lo que se hizo con cada una.

## Observaciones recibidas y mejoras

| Observación | Origen | Acción | Commit | Impacto |
|---|---|---|---|---|
| `data/raw/` contenía RUT y nombres de proveedores que son personas naturales | Sumativa 1 | Se reemplazaron por un código estable (`PN-0001`…) y se reescribió el historial para que tampoco los conserve | `5e1db32`, `03e5399`, `d0a4091` | **Modularidad:** la anonimización quedó en un módulo propio (`anonimizacion.py`) con 18 pruebas. **Documentación:** se corrigió el registro que decía «sin datos personales». El resultado del análisis no cambió |
| Faltó analizar los montos extremos | Sumativa 1 | Límite sobre el logaritmo del monto, variable `monto_extremo` y octava regla de validación | `65f8334`, `b9415f4`, `27c49b0` | **Resultados:** los indicadores se informan con y sin las 84 órdenes extremas; el aumento de la concentración entre años desaparece al excluirlas. **Modularidad:** el límite se aprende en una clase (`OutlierFlagger`) |
| El historial se concentró en el último día | Sumativa 1 | Trabajo repartido en ramas por integrante y por componente, con *pull request* y *merge commit* | `e1063e2`, `9d85d28`, `688a3bf` | **Documentación:** cada componente de la Fase 3 tiene su rama, su autor y su fecha en el historial |
| Un commit sin descripción y hecho desde la web | Sumativa 1 | Convención `tipo(alcance): descripción` en todos los commits siguientes e identidades unificadas | `4b8b53d` | **Documentación:** `git shortlog -sn` muestra una línea por integrante |
| El mapa conceptual no incluía la anonimización ni los montos extremos | Sumativa 1 | Página nueva en el mapa conceptual | `f50cca4` | **Documentación:** el mapa coincide con el pipeline actual |
| `seaborn` declarado y sin usar | Sumativa 1 | Se quitó de `requirements.txt` y se regeneró el registro del entorno | `8758f22` | **Reproducibilidad:** el entorno declara solo lo que se importa |
| El registro de ejecución no correspondía a la versión entregada | Sumativa 1 | Registro regenerado después de cada integración | `c94ecb8`, `82e1e5c`, `5f9fd79` | **Documentación:** cada entrega tiene su evidencia de ejecución completa |
| El índice del informe no tenía números de página | Sumativa 1 | Índice con páginas desde el informe de la Sumativa 2 | Informe | **Documentación:** no cambia el repositorio |

## [F4] 2026-11-25 · Comunicación y cierre de la Sumativa 3

### Agregado
- Módulo `src/pipeline/comunicacion.py` con sus pruebas, notebook `F4/F4_Comunicacion.ipynb` y las tres figuras de `F4/figuras/` (commits `f0f57cb` y `1221a37`).
- Tabla única de hallazgos `docs/hallazgos_f4.csv` y composición de las órdenes de monto extremo por modalidad, rubro y unidad (commit `5161ad3`).
- Dos decisiones de la Fase 4 en `docs/decisiones.md`: datos ausentes y copia interpretable sin normalizar ni escalar (commit `ce84c79`). Responde a la retroalimentación de la Sumativa 2.
- Medición de eficiencia sobre tamaños crecientes: `escalamiento.py`, `scripts/measure_efficiency.py` y `F3/F3_escalamiento.ipynb` (commit `6871e69`). Responde a la retroalimentación de la Sumativa 2.

### Cambiado
- El notebook de F1 ya no menciona el conjunto de licitaciones, que el proyecto no procesa; alcance, restricciones y supuestos quedan en tres listas (commit `2f1ce21`). Responde a la retroalimentación de la Sumativa 1.
- `Transformer` se declara como clase abstracta con `abc`: no se puede instanciar y cada paso debe implementar `_learn` y `_apply`.
- `F3_eficiencia.ipynb` y `F3_Nucleo.ipynb`: se retiran las afirmaciones sin medición que las respalde y se corrige el número de comparaciones (tres). Responde a la retroalimentación de la Sumativa 2.
- `F4/README.md` con el contenido de la fase.

## [F3] 2026-11-18 · Cierre de la Sumativa 2

### Agregado
- `.mailmap` con las identidades de cada integrante (commit `4b8b53d`). La guía pide que el historial muestre tantos autores como integrantes.
- Registro de la ejecución completa con la Fase 3 integrada: 10 de 10 pasos y 121 pruebas (commit `5f9fd79`).

### Cambiado
- Las pruebas de las clases usan la interfaz `fit` y `transform` y la regla de montos extremos (commit `47c35cb`). Se escribieron antes de que existieran las clases, con otros nombres: 14 se omitían y una fallaba.
- README con el notebook de eficiencia y las contribuciones de la Fase 3 (commit `3705cdd`).

## [F3] 2026-11-17 · Medición de eficiencia

### Agregado
- Módulo `medicion.py` con el medidor y tres pares de implementaciones (commits `4835619`, `d321e49`). El notebook y las pruebas comparten el mismo código.
- Notebook `F3/F3_eficiencia.ipynb` con datos reales, gráficos e interpretación (commits `f9337f9`, `11c675c`, `c3413f6`).
- Pruebas de equivalencia y de costo de cada par (commits `96f4fb0`, `bdea74f`).

### Cambiado
- La interpretación de la conversión de montos: la versión vectorizada no es más rápida que `apply`, y se informa así (commits `d321e49`, `11c675c`). La medición contradijo lo que se esperaba.

## [F3] 2026-11-15 · Pruebas y datos sintéticos

### Agregado
- Pruebas de las clases y de regresión contra la Fase 2 (commit `50d1fa3`). Comprueban que reorganizar el código no cambió el resultado.
- Generador de órdenes sintéticas con semilla (commits `dca97ff`, `b4da70b`, `0b70a2c`). Permite probar y medir sin tocar `data/raw/`.

## [F3] 2026-11-13 · Clases y pipeline

### Agregado
- Clase base `Transformer` con el contrato `fit` y `transform` (commit `d4ed913`).
- `OutlierFlagger`, `TopSupplierMarker` y `SupplierAnonymizer`, que aprenden de los datos (commits `4c520d9`, `0573626`, `44abf01`).
- `FunctionStep`, que adapta una función de la Fase 2 al contrato (commit `2568e63`). Evita reescribir como clases las funciones que no guardan estado.
- `OrdersPipeline`, que encadena los pasos y lleva una bitácora (commit `7c49c82`).
- Notebook `F3/F3_Nucleo.ipynb` con la equivalencia contra la Fase 2 (commit `da99d3d`).

## [F2] 2026-11-13 · Correcciones de la Sumativa 1

### Agregado
- Anonimización de proveedores que son personas naturales (commit `5e1db32`) y prueba que impide que vuelvan a entrar datos personales (commit `03e5399`).
- Límite y marca de montos extremos, con su regla de validación (commit `65f8334`) y su análisis en los notebooks (commit `b9415f4`).

### Cambiado
- `data/processed/ordenes.csv` pasa de 13 a 14 variables y la validación, de siete a ocho reglas (commit `65f8334`).
- Se quitó `seaborn` de las dependencias (commit `8758f22`).

## [F2] 2026-11-11 · Pipeline de datos

### Agregado
- Obtención reproducible desde ChileCompra, con filtro por sector y región y copia congelada con SHA-256 (commits `2e7ee2d`, `b8e081e`).
- Funciones de limpieza, tipos, modalidad y agregación por orden, con sus pruebas (commit `86cfed9`).
- Cinco notebooks, de la obtención a la validación (commits `eab3916`, `2e4c3e5`, `ce757d6`, `f80d675`, `bf56bda`).

## [F1] 2026-11-11 · Definición

### Agregado
- Contexto, problemática, preguntas y referencias (commits `5f5b841`, `bfed848`, `55fb1bd`, `c55be76`).
- Objetivos, alcance y supuestos (commit `5c61448`).
- Mapa conceptual técnico (commit `b9f9e6d`).

## [F1] 2026-11-02 · Estructura y entorno

### Agregado
- Estructura por fases y paquete `src/pipeline/` (commit `363cafa`).
- Entorno con versiones fijadas y verificación (commit `1dcccf8`), ejecución completa con registro (commit `bbde351`) e integración continua (commit `0b8b434`).
