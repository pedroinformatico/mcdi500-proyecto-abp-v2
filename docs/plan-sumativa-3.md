# Sumativa 3 · Plan y reparto de tareas (Grupo 5)

_Escrito el viernes 2026-11-20 y actualizado el lunes 2026-11-23 con el nuevo plazo y la retroalimentación de la Sumativa 2. Es una propuesta: los nombres y las horas los confirma el grupo._

## Actualización del lunes 23-nov

Lo que sigue reemplaza al calendario y ajusta el reparto de más abajo.

### Qué cambió

- **Nuevo plazo: miércoles 25-nov, 23:59** (anuncio del docente del 20-nov).
- **Llegó la retroalimentación de la Sumativa 2.** Los descuentos fueron en preprocesamiento, eficiencia y notebook; el detalle está en la tabla de pendientes.
- **`main` no tiene todavía nada de la Fase 4:** el último commit de Felipe y de Cristián es del 17-nov.
- **Ramas y *pull request* siempre.** El docente observó que los cambios del 20-nov se subieron directo a `main`. En la Fase 4 cada integrante trabaja en su rama y la integra con un *pull request* que revisa otro.

### Pendientes de la Fase 3 que la rúbrica de la Fase 4 vuelve a evaluar

| Pendiente | Dónde | Estado | Quién |
|---|---|---|---|
| Medir sobre tamaños crecientes | `escalamiento.py`, `F3/F3_escalamiento.ipynb` | Hecho el 20-nov | Pedro |
| Retirar las afirmaciones sin medición: «en todos los tamaños medidos» y la comparación con `itertuples` | `F3/F3_eficiencia.ipynb` | Pendiente | Felipe |
| La sección 7 dice «dos pares» y hay tres comparaciones | `F3/F3_Nucleo.ipynb` | Pendiente | Pedro |
| Documentar qué se hace con los ausentes y cuántos quedan, y la decisión de no normalizar ni escalar | Tabla de transformaciones del informe y `docs/decisiones.md` | Pendiente | Cristián |
| Declarar `Transformer` como clase abstracta con `abc` | `src/pipeline/transformers.py` | Pendiente | Pedro |
| Referencia de `tracemalloc` en la bibliografía | Informe (ya está en `docs/arquitectura.md`) | Pendiente | Cristián |

### Sugerencias del docente para el análisis, frente a las tres figuras propuestas

| Sugerencia | ¿Está en el plan? | Qué hacer |
|---|---|---|
| Partir del pipeline ajustado con 2024 y aplicado a 2025, sin volver a procesar | Sí | Decirlo en la metodología |
| Modalidad en 2024 y 2025 con barras al 100 %, en número de órdenes y en monto | Solo en monto | Figura 1 con dos paneles |
| Más de un indicador de concentración: HHI y curva de Lorenz, con intervalos por *bootstrap* | No | La figura 3 pasa a ser la curva de Lorenz; HHI e intervalos en la tabla de hallazgos |
| Rotación de proveedores: los diez mayores de 2024 concentran solo el 7,2 % en 2025 | No | Agregarlo como hallazgo, con una figura o una cifra |
| Indicadores con y sin órdenes extremas | Sí | Se mantiene |
| Montos comparables: UF o IPC, con la fuente del índice | No | Convertir antes de comparar montos entre años, o declararlo como límite si no alcanza |
| «Coincide con» o «se asocia con», nunca «efecto de la ley» | Sí | Revisar el informe y el guion |
| Proveedores personas naturales solo con su código en las figuras | Sí | Revisar las etiquetas |
| Una tabla de hallazgos generada desde el notebook; informe y guion se escriben desde ella | Sí | `docs/hallazgos_f4.csv` |
| Video en tres actos; cada integrante presenta lo que desarrolló; más figuras que código | Sí | Ajustar el guion a los tres actos |

Lo mínimo que no puede faltar: las tres figuras, la tabla de hallazgos y el HHI. La curva de Lorenz, el *bootstrap* y la conversión a UF se hacen si el lunes en la noche las figuras base ya están.

### Calendario nuevo

| Cuándo | Qué | Quién |
|---|---|---|
| **Lun 23** | Ramas creadas y primer commit de cada uno. Figura 1 y tabla de hallazgos. F1 sin licitaciones | Los tres |
| **Mar 24, mediodía** | Las tres figuras y los indicadores unidos a `main` por *pull request*. Pendientes de la Fase 3 cerrados | Felipe; Pedro |
| **Mar 24, tarde** | Informe completo en borrador. Guion y láminas | Cristián; Pedro |
| **Mar 24, noche** | Ensayo con cronómetro y grabación del video | Los tres |
| **Mié 25, mañana** | Clon limpio y ejecución completa. Cada cifra del informe contra el notebook. Video subido a Canvas Studio | Pedro; los tres |
| **Mié 25, 18:00** | PDF final. Etiqueta `entrega-s3`. Entrega antes de las 20:00 | Pedro |

## En corto

- **Entrega:** miércoles 25-nov, 23:59 (al escribir el plan era el domingo 22). Pondera 30 % (150 puntos, 26 criterios). Un solo intento; la sube Pedro.
- **Cuatro productos que deben decir lo mismo:** informe PDF de hasta 10 páginas, notebooks que corran completos, repositorio con F1 a F4 y video de 5 a 8 minutos en Canvas Studio.
- El código de las fases 1 a 3 está en `main` y pasa (133 pruebas, 11 de 11 pasos). Lo que falta es casi todo comunicación: figuras, informe y video.
- **El historial es el riesgo que más se repite:** sin contar las uniones, `main` tiene 63 commits de Pedro, 11 de Felipe y 9 de Cristián. La Fase 4 la escriben Felipe y Cristián en sus ramas; Pedro integra y revisa.
- **Antes de crear una rama:** `git checkout main` y `git pull`. `main` cambió el viernes 20.

## Dónde estamos frente a la rúbrica

| Ámbito (puntos) | Estado | Qué falta |
|---|---|---|
| Código y notebooks (54) | Hecho en su mayor parte | Notebook de F4, notebook de F1 sin licitaciones |
| Informe: contenido analítico (39) | Sin empezar | Tres figuras, copia interpretable, metodología, resultados, discusión, conclusiones |
| Informe: forma y contexto (27) | Reutilizable de la S1 y la S2 | Alcance, restricciones y supuestos como tres listas separadas; relevancia; bibliografía |
| Repositorio y trazabilidad (18) | Hecho en su mayor parte | Contenido de `F4/`, sección de la Fase 4 en `changelog.md`, commits de los tres |
| Video (12) | Sin empezar | Guion, láminas, grabación y subida a Canvas Studio |

El detalle criterio por criterio está en [`trazabilidad.md`](trazabilidad.md).

## Observaciones recibidas (alimentan el apartado 27)

La tabla con la acción, el commit y el impacto de cada una está en [`../changelog.md`](../changelog.md). Quedan dos abiertas:

| Observación | Origen | Estado |
|---|---|---|
| El notebook de F1 menciona las licitaciones | Sumativa 1 | **Pendiente** (10 menciones). Lo toma Cristián |
| Retroalimentación de la Fase 3 | Sumativa 2 | **Sin recibir.** Se revisa el sábado; si no llega, se declara en el informe |

Además, el historial concentrado en el último día quedó corregido solo en parte: la Fase 4 debe repartirse entre viernes, sábado y domingo.

## Las tres figuras propuestas

Tres tipos distintos, en el orden contexto, contraste y resolución. Cada título dice el hallazgo. Las cifras son las de `data/processed/ordenes.csv`.

| # | Movimiento | Tipo | Qué muestra | Pregunta que responde |
|---|---|---|---|---|
| 1 | Contexto | Barras apiladas al 100 % | Composición del monto por modalidad en 2024 y 2025. La compra ágil pasa de 6,1 % a 11,8 % del monto, la licitación baja de 59,5 % a 43,3 % y «Otra» sube de 2,8 % a 16,2 % | Pregunta 4, objetivo 4 |
| 2 | Contraste | Histograma del monto por orden, en escala logarítmica, con el límite de $74,0 millones | 84 órdenes (0,8 %) reúnen el 33,5 % del monto | Pregunta 5 |
| 3 | Resolución | Líneas: participación acumulada de los proveedores ordenados por monto, con y sin órdenes extremas, por año | Los diez mayores pasan de 22,2 % a 26,0 %; sin las extremas, de 16,1 % a 15,4 %: el aumento desaparece | Preguntas 1 y central, objetivo 2 |

- **Copia interpretable:** `ordenes.csv` ya conserva categorías y pesos. La Fase 4 parte de ahí y agrega solo columnas para graficar (monto en millones, etiqueta del año); no se codifica ni se escala. Eso se escribe tal cual en el apartado 20.
- **Vacío a decidir:** las preguntas 2 y 3 (unidades que dependen de uno o dos proveedores) no tienen resultado todavía. Propuesta: una tabla breve en el notebook de F4 y una frase en resultados. Si no alcanza, se declara como límite en la discusión.
- **Límite que va junto a cada cifra:** dos meses no permiten atribuir el cambio a la ley.

## Presentación para el video

- **Formato:** láminas en HTML generadas con la plantilla que Pedro usa en el magíster. El deck lo genera Pedro, con el guion de Cristián y las figuras de Felipe.
- **Contenido, una lámina por idea y entre 8 y 10 en total:** portada con equipo y repositorio; problema y relevancia; datos y alcance; pipeline y clases; reproducibilidad y pruebas; las tres figuras, una por lámina, con el hallazgo como título; límites; conclusiones y mejoras.
- **Figuras:** las mismas imágenes de `F4/figuras/`, sin rehacerlas, para que informe, notebook y video muestren lo mismo.
- **Tiempos del guion:** apertura 0:45, contexto 1:15, metodología 2:00, resultados 2:30, conclusiones 1:30. Total 8:00 como tope; ensayar para quedar cerca de 7:00.
- **Entrega del deck:** el HTML y una copia en PDF quedan en `F4/presentacion/`.

## Reparto por persona

### Felipe · Visualizaciones y resultados
- **Rama:** `feature/f4-visualizaciones`
- **Archivos:** `src/pipeline/comunicacion.py`, `F4/F4_Comunicacion.ipynb`, `F4/figuras/`, `tests/test_comunicacion.py`
- **Tareas:**
  - Funciones que preparan la tabla de cada figura y funciones que la dibujan, con título, ejes, leyenda y fuente.
  - Notebook de F4: lee `data/processed/ordenes.csv`, no vuelve a limpiar; bajo cada figura, qué muestra, qué se infiere y qué límite tiene.
  - Tabla de hallazgos (`docs/hallazgos_f4.csv`) con las cifras que cita el informe.
  - Tabla breve de dependencia entre unidad y proveedor.
- **En el video:** resultados (las tres figuras).

### Cristián · Informe y narrativa
- **Rama:** `docs/f1-alcance`; el informe se trabaja fuera del repositorio
- **Archivos:** `F1/F1_Definición.ipynb`, informe, guion del video
- **Tareas:**
  - Notebook de F1 sin licitaciones, con alcance, restricciones y supuestos en tres listas.
  - Informe con los 29 apartados en el orden del entregable. Máximo 10 páginas: los apartados 2 a 18 salen resumidos de los informes de la S1 y la S2; el espacio va a los apartados 20 a 27.
  - Tabla de fases previas (qué había, qué hay, por qué cambió) para el apartado 23. Punto de partida: la sección «Evolución» de [`arquitectura.md`](arquitectura.md).
  - Bibliografía: cinco fuentes en APA 7, todas citadas.
  - Guion del video por tramos.
- **En el video:** contexto, problema y conclusiones.

### Pedro · Integración, trazabilidad y entrega
- **Ramas:** `feature/f4-eficiencia-tamanos` y `docs/f4-trazabilidad`, ya unidas a `main`

| Tarea | Estado |
|---|---|
| Medición sobre tamaños crecientes: `escalamiento.py`, `scripts/measure_efficiency.py`, `F3/F3_escalamiento.ipynb` y sus pruebas. Reutiliza `medicion.py` de Felipe | Hecho (`0a6b678`) |
| `changelog.md` con la tabla de observaciones, acción, commit e impacto | Hecho; falta la sección de la Fase 4 |
| `docs/arquitectura.md` y `docs/trazabilidad.md` con los 26 criterios | Hecho (`78f1c99`) |
| `run_all.py` e integración continua con los notebooks de F3 y F4 | Hecho |
| Revisar y unir los *pull requests* de la Fase 4 | Pendiente |
| Láminas del video | Pendiente: dependen de las figuras y del guion |
| Clon limpio, PDF final, etiqueta `entrega-s3` y entrega | Domingo |

- **En el video:** metodología y reproducibilidad.

## Calendario original (reemplazado por el de la actualización)

| Cuándo | Qué | Quién |
|---|---|---|
| **Vie 20** | Ramas creadas y primer commit de cada uno. Figura 1 y copia interpretable. F1 sin licitaciones | Felipe; Cristián |
| **Sáb 21, mediodía** | Las tres figuras y la tabla de hallazgos unidas a `main`. Revisar si llegó la retroalimentación de la Fase 3 | Felipe; Pedro |
| **Sáb 21, tarde** | Informe completo en borrador. Guion y láminas | Cristián; Pedro |
| **Sáb 21, noche** | Ensayo con cronómetro y grabación del video | Los tres |
| **Dom 22, mañana** | Clon limpio y ejecución completa. Cada cifra del informe contra el notebook. Video subido a Canvas Studio | Pedro; los tres |
| **Dom 22, 18:00** | PDF final. Etiqueta `entrega-s3`. Entrega antes de las 20:00 | Pedro |

## Riesgos

- **Diez páginas para 29 apartados.** El informe de la S2 ocupó 13 páginas con 11 apartados. Tablas en lugar de párrafos y el detalle en el repositorio.
- **El video depende de las figuras.** Si las figuras no están el sábado a mediodía, no hay margen para grabar.
- **Coherencia.** Una cifra que cambie en el notebook debe cambiar en el informe, el README y las láminas.
- **Nombre del archivo del informe:** tomarlo de la plantilla institucional de la Sumativa 3.
