# books_ai

Aplicación local para consultar, mediante un LLM ejecutado en la propia máquina,
la información contenida en un corpus de libros de dos universos de ficción.

## Language

### Corpus

**Universo**:
Cada uno de los dos cuerpos de ficción independientes que cubre la aplicación: el
de Tolkien y el de Martin. No comparten personajes, lugares ni cronología, y toda
consulta pertenece obligatoriamente a uno solo.
_Avoid_: saga, mundo, colección, dominio

**Corpus**:
El conjunto de textos que la aplicación considera canónicos. Es la única fuente de
verdad: lo que no está en el Corpus, la aplicación no lo sabe.
_Avoid_: biblioteca, base de conocimiento, dataset

**Obra**:
La unidad canónica del Corpus: un texto publicado, con independencia de en cuántos
ficheros PDF llegue. *El Señor de los Anillos* es una Obra repartida en cuatro
Volúmenes; no son cuatro Obras. El Corpus tiene 12 Obras. No es lo que la Cita
nombra: eso es el Volumen.
_Avoid_: libro, título, fichero, documento

**Volumen**:
La parte de una Obra que llega en un fichero propio y numera sus páginas desde 1. Es
lo que nombra la Cita y lo que lleva el Tipo de Texto. El Corpus tiene 15 Volúmenes:
once Obras de un solo Volumen y *El Señor de los Anillos*, que tiene cuatro. Sin él,
«*El Señor de los Anillos*, p. 263» señalaría a tres sitios a la vez.
_Avoid_: tomo, parte, entrega, fichero

**Tipo de Texto**:
La clase de texto que es un Volumen y, con ella, la autoridad que la aplicación le
concede: narrativa canónica, crónica interna escrita por un narrador del propio
Universo y por tanto parcial, o material de referencia. Cuelga del Volumen y no de la
Obra, que es lo que permite que los tres tomos de *El Señor de los Anillos* sean
narrativa canónica y sus *Apéndices* material de referencia sin dejar de ser la misma
Obra. Se llamó «Tipo de Obra» hasta el ADR-0006, y ese nombre apuntaba al dueño
equivocado.
_Avoid_: tipo de obra, categoría, género, fuente

### Modos

**Modo Consulta**:
Modo en el que la aplicación responde con hechos extraídos del Corpus y acompañados
de su procedencia, y declara no saber cuando el Corpus no lo cubre.
_Avoid_: modo factual, modo RAG, modo búsqueda

**Modo Personaje**:
Modo en el que la aplicación responde con la voz y el registro del Universo, sin
procedencia y sin obligación de limitarse a lo literalmente escrito.
_Avoid_: modo in-universe, modo rol, modo narrativo

### Respuesta

**Pasaje**:
El fragmento literal del Corpus que sostiene una afirmación concreta del Modo
Consulta. Se reproduce textualmente; es lo que permite verificar la respuesta sin
abrir el PDF.
_Avoid_: extracto, cita, snippet, contexto

**Fragmento**:
La unidad en que se trocea el Corpus para poder recuperarlo. Puede cruzar saltos de
página, pero nunca el límite de un Volumen —si lo cruzara, su Cita no podría nombrar
una sola página—, y no coincide con el Pasaje: el Fragmento es lo que se busca, el
Pasaje es lo que se cita.
_Avoid_: chunk, trozo, bloque, segmento

**Cita**:
La procedencia de un Pasaje: el Volumen y la página en las que aparece. Acompaña
siempre al Pasaje, nunca lo sustituye. Nombra el Volumen y no la Obra porque cada
Volumen numera sus páginas desde 1, y una Cita que apunta a tres sitios no verifica
nada.
_Avoid_: referencia, fuente, atribución

### Modelos

**Modelo Base**:
El modelo generativo preentrenado del que parte un experimento, antes de cualquier
modificación propia. Es un parámetro elegible, nunca una constante del proyecto.
_Avoid_: el modelo, modelo de partida, checkpoint

**Modelo Afinado**:
El resultado de aplicar el proceso de entrenamiento propio sobre un Modelo Base con
el Corpus.
_Avoid_: el modelo, modelo entrenado, modelo final

**Modelo de Embeddings**:
El modelo que convierte texto en vectores para poder recuperar pasajes del Corpus.
Es independiente del Modelo Base y se elige por separado.
_Avoid_: el modelo, encoder, vectorizador

**Adaptador**:
El conjunto de pesos añadidos que resulta del entrenamiento propio y que se activa
sobre un Modelo Base sin modificarlo. Es lo que da al Modo Personaje su voz, y sólo
interviene en ese modo.
_Avoid_: LoRA, delta, fine tune, parche

### Evaluación

**Conjunto de Evaluación**:
Las preguntas sobre el Corpus con respuesta y Cita conocidas de antemano, contra las
que se mide cualquier cambio. Se escribe antes de elegir Modelo Base y no cambia entre
experimentos: si cambia, deja de servir para comparar.
_Avoid_: benchmark, tests, batería, golden set

**Pregunta Negativa**:
Pregunta del Conjunto de Evaluación cuya respuesta correcta es que el Corpus no lo
cubre. Es la única familia que detecta alucinación.
_Avoid_: pregunta trampa, control, caso límite

**Pregunta Cruzada**:
Pregunta sobre un Universo formulada con el filtro puesto en el otro. La respuesta
correcta es no contestar; comprueba que la separación entre Universos se sostiene.
_Avoid_: contaminación, fuga, cross-check
