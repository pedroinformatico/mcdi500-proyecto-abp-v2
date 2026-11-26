# Declaración de uso de IA generativa

Conforme a los Lineamientos de la Universidad Andrés Bello para el uso de IA generativa, el equipo declara que utilizó herramientas de inteligencia artificial como apoyo auxiliar, y no como autora ni como fuente bibliográfica.

El equipo revisó y validó todo el contenido y las referencias, y asume la responsabilidad por el trabajo entregado. Las decisiones de análisis, la interpretación y la redacción son del equipo.

## Formato

Cada integrante escribe su propia declaración, en su propia rama, con este formato:

```markdown
### Nombre Apellido

- **Para qué la usé:** tareas concretas, una por línea.
- **Qué hice yo:** qué escribí, decidí o verifiqué por mi cuenta.
- **Cómo lo validé:** cómo comprobé que el resultado era correcto.
```

Reglas:

- Se declara el **uso**, no la marca: se escribe «un asistente de IA generativa», sin nombres de herramientas ni de modelos.
- Se declara todo uso en productos evaluados: informe, notebooks, código, mapa conceptual y referencias.
- La declaración debe ser verdadera y específica. «La usé como apoyo» no basta.
- Esta declaración cubre el repositorio; el informe incluye un resumen de ella.

## Declaraciones

### Cristián Cordero

- **Para qué la usé:**
  - Aprender el flujo de trabajo con Git y GitHub (ramas, commits y pull requests).
  - Entender los requisitos de la guía y la rúbrica de las sumativas 1 a 3.
  - Recibir sugerencias de claridad y formato sobre borradores que redacté yo.
  - Explorar las columnas de los datos de ChileCompra para evaluar qué preguntas se podían responder.
  - Buscar referencias y revisar su formato APA.
  - Sumativa 3: proponer la redacción del notebook de F1 sin el conjunto de licitaciones, con alcance, restricciones y supuestos en tres listas.
  - Sumativa 3: contar los datos ausentes de la fuente y del dataset procesado, y redactar las dos decisiones de la Fase 4 en `docs/decisiones.md`.
  - Sumativa 3: preparar un primer borrador del informe y del guion del video a partir de la tabla de hallazgos.
- **Qué hice yo:** propuse la línea de análisis (concentración del gasto en pocos proveedores); redacté con mis palabras el contexto, la problemática y las preguntas del análisis; armé la lista de referencias; en la Sumativa 3 revisé y ajusté cada cambio del notebook de F1, del registro de decisiones, del informe y del guion; y subí mis cambios en ramas y pull requests propios.
- **Cómo lo validé:** abrí las fuentes originales para comprobar las referencias (OCDE, Ley 21.634 y ChileCompra), contrasté las cifras del contexto con la documentación de los datos, ejecuté el notebook de F1 completo, comparé cada cifra del informe y del guion con `docs/hallazgos_f4.csv` y revisé cada cambio en el diff antes de hacer el commit.

### Pedro Hernández

- **Para qué la usé:**
  - Armar la estructura del repositorio, el entorno reproducible y la ejecución automática.
  - Escribir y depurar el código de obtención, limpieza, transformación y validación de los datos, junto con sus pruebas.
  - Redactar y ordenar los notebooks de la Fase 2 y la documentación técnica (README y registro de decisiones).
  - Revisar los aportes del equipo y los requisitos de la rúbrica.
- **Qué hice yo:** elegí el conjunto de datos, el período y el enfoque del análisis; definí la estructura del proyecto y el flujo de trabajo en ramas; y decidí qué se aceptaba en cada cambio.
- **Cómo lo validé:** ejecuté el proyecto completo (pruebas y notebooks) en mi equipo, revisé los resultados contra los datos originales y revisé cada cambio antes de subirlo.

### Felipe Contreras

>### Felipe Contreras

- **Para qué la usé:**
  - Utilicé un asistente de IA generativa para contrastar mis tareas con la guía de la Sumativa 3 y la retroalimentación del profesor, delimitando el trabajo a visualizaciones y resultados de F4 y a la corrección de afirmaciones de eficiencia de F3.
  - Generar el módulo `src/pipeline/comunicacion.py` y el notebook `F4/F4_Comunicacion.ipynb`: tablas y figuras de modalidades de compra, montos extremos y concentración de proveedores con y sin órdenes extremas, a partir de datos ya procesados y sin repetir la limpieza.
  - Elaborar la tabla de dependencia entre unidad y proveedor y `docs/hallazgos_f4.csv`, y redactar las interpretaciones de las figuras con sus alcances y limitaciones. El apoyo incluyó la generación de código y texto, no solo sugerencias de formato.
  - Escribir y ejecutar las pruebas de `tests/test_comunicacion.py`, ejecutar los notebooks y contrastar cifras con los datos procesados.
  - Corregir `F3/F3_eficiencia.ipynb` y la documentación de `src/pipeline/medicion.py`: retirar la comparación no medida con `itertuples`, limitar las conclusiones al volumen evaluado y remitir al notebook de escalamiento para los tamaños crecientes. No desarrollé mediante este apoyo el núcleo orientado a objetos asignado a otro integrante.
  - Preparar una minuta para mi segmento del video sobre las tres figuras y empaquetar los archivos de mi aporte para trasladarlos a otro repositorio.
  - Incorporar, a solicitud de Cristián para el OE5 del informe, tres tablas de órdenes extremas por modalidad, rubro y unidad. El apoyo incluyó vincular el detalle de productos con las órdenes ya procesadas, documentar el prorrateo estimado del monto por rubro y probar que no se duplica el monto de las órdenes multirrubro.
- **Qué hice yo:** proporcioné la guía, los comentarios del profesor y el reparto de tareas; delimité el alcance a mi responsabilidad como Felipe; solicité las correcciones de las afirmaciones sin medición y las revisiones de cumplimiento; y pedí una minuta centrada en los resultados para preparar mi exposición. No presento el código ni los textos generados con este apoyo como escritos íntegramente por mí.
- **Cómo lo validé:** solicité al asistente comprobaciones ejecutables en el entorno local. El asistente ejecutó las 139 pruebas del proyecto antes de las últimas correcciones de texto y, después de ellas, 29 pruebas enfocadas en eficiencia, escalamiento y comunicación, todas satisfactorias. También ejecutó los notebooks de eficiencia, escalamiento y comunicación; verificó la equivalencia de las implementaciones antes de medir tiempo y memoria; y contrastó las cifras de extremos y concentración con el CSV procesado. Estas comprobaciones fueron ejecutadas por el asistente, no constituyen una revisión humana independiente ni certifican por sí solas el cumplimiento completo de la rúbrica. Al registrar esta declaración, quedan pendientes la revisión final del equipo, la integración mediante un pull request revisado y la grabación del video; si cambia la salida del pipeline, deben actualizarse y verificarse las figuras, los hallazgos y la minuta antes de entregar.
 Pendiente: completar con el formato.
