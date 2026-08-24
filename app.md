# Aplicación de consulta local sobre un corpus de libros

Aplicación que corre íntegramente en local y permite interrogar, mediante un LLM, la
información contenida en los libros de dos universos de ficción: el de Tolkien y el de
Martin.

El vocabulario que usa este documento está definido en [`CONTEXT.md`](./CONTEXT.md). Las
decisiones que costaría revertir están registradas en [`docs/adr/`](./docs/adr/).

## Objetivo

El proyecto persigue dos cosas a la vez, y una manda sobre la otra:

1. **Una herramienta que funcione** — poder preguntar por el contenido de los libros y
   recibir respuestas verificables.
2. **Aprender el proceso de fine tuning** sobre la máquina disponible, de forma repetible
   con cualquier Modelo Base.

Cuando ambas entren en conflicto, gana la primera. Esa prioridad no es una declaración de
intenciones: está construida dentro de la arquitectura, y el ADR-0002 explica cómo.

## No objetivos

- No es un servicio público ni multiusuario. Uso personal, en la red local del autor.
- No responde sobre nada que no esté en el Corpus.
- No hay control de spoilers. La estructura de datos no lo impide, pero no se construye.

## El Corpus

15 ficheros PDF que son **15 Volúmenes** de **12 Obras** —8 de Martin y 4 de Tolkien—,
con 7.612 páginas repartidas en dos Universos que no comparten absolutamente nada. Martin es el **74,8%** de
las páginas: 5.695 frente a 1.917.

Ficheros, Obras y páginas están contados contra el disco por la etapa `inventario` del
ticket 01. El recuento de palabras —~3,36 M— y el reparto por texto —cerca del 73% de
Martin— vienen del planteamiento inicial y **no se han vuelto a medir**; la extracción del
ticket 02 los dará exactos, y es de esperar que se muevan poco.

Los 17 ficheros originales incluían dos que quedan **excluidos**, anotados como tales en
el manifiesto y no borrados del disco:

| Obra | Motivo |
| --- | --- |
| *Dominio de dragones* | Folleto promocional cuyo texto está íntegramente dentro de *Danza de dragones*. Verificado. Indexarlo produce resultados duplicados y sobre-representa esas páginas al entrenar. |
| *El Dragón de Hielo* | Cuento independiente que no transcurre en ninguno de los dos Universos. Con el filtro obligatorio por Universo no tiene casilla donde caer. |

Cada Volumen lleva registrado su **Tipo de Obra**, porque no todos merecen la misma
autoridad. *Fuego y Sangre* y *El Mundo de Hielo y Fuego* son crónicas escritas desde
dentro del Universo por narradores explícitamente parciales, con versiones contradictorias
del mismo suceso; los *Apéndices* de Tolkien son material de referencia. El Modo Consulta
refleja esa diferencia en la respuesta en lugar de presentarlo todo como hecho.

Un detalle que condiciona la extracción: *El Señor de los Anillos* es **una Obra repartida
en cuatro Volúmenes** —los tres tomos y los *Apéndices*—. De ahí que haya 15 Volúmenes y 12
Obras.

Y un aviso para quien escriba el manifiesto: el cuarto fichero se llama «El señor de los
anillos 4 - Apendices», en minúsculas y sin tilde, mientras que los otros tres empiezan por
«El Señor de los Anillos - 0N». Agruparlos por prefijo deja los *Apéndices* fuera sin decir
nada. La correspondencia entre fichero y Obra se declara a mano; no se adivina del nombre.

## Arquitectura

La aplicación tiene dos modos, y cada uno usa la técnica en la que es bueno.

### Modo Consulta

Responde hechos, con procedencia, y admite no saber.

- El **Universo es un parámetro obligatorio y explícito** de cada consulta, elegido en la
  interfaz. No se infiere: ante una pregunta ambigua —«¿quién es el rey?»— la inferencia
  falla en silencio y cita el corpus equivocado con total aplomo.
- Recuperación **híbrida**: vector denso de BGE-M3 más BM25 léxico. El corpus está lleno
  de onomástica inventada (Invernalia, Meñique, Bombadil) y ahí la búsqueda léxica gana
  donde los embeddings flaquean.
- El **Fragmento** es la unidad de recuperación: ~450 palabras, 15% de solape, precedido
  al vectorizar por una cabecera con su Obra y su Universo, de modo que la procedencia
  viaje dentro del propio embedding.
- El **Pasaje** es la unidad de cita, y es cosa distinta: el texto literal que sostiene la
  afirmación. La **Cita** lo acompaña con **Volumen** y página, anclada a donde empieza el
  Pasaje y no a donde empieza el Fragmento — que casi siempre cruza un salto de página,
  aunque nunca el límite de un Volumen. Nombra el Volumen y no la Obra por el motivo que
  recoge el [ADR-0006](./docs/adr/0006-la-cita-nombra-un-volumen-no-una-obra.md): cada
  Volumen numera sus páginas desde 1.
- Corre **siempre sobre el Modelo Base sin modificar**.

### Modo Personaje

Responde con la voz y el registro del Universo. Sin Citas, sin obligación de ceñirse a lo
literalmente escrito.

- Lo sirve un **Adaptador** conmutado en caliente sobre el mismo Modelo Base.
- Se entrena con **pares sintéticos de diálogo en formato de chat**, no con prosa cruda:
  el Adaptador se sirve por plantilla de chat, y entrenar sobre prosa pelea contra ese
  formato y produce un modelo que completa párrafos en lugar de conversar. Como los hechos
  ya no son su trabajo, la prosa cruda no compensa ese daño.
- Los pares los genera, en un **lote único offline**, el modelo más grande que quepa en la
  memoria disponible — no el modelo pequeño que se va a afinar. Un modelo generando su
  propio material de entrenamiento se enseña sus propios tics.

## Pipeline

Por etapas, con caché. Cada etapa consume el artefacto de la anterior y produce el suyo,
así que se relanzan por separado y cambiar de Modelo Base no obliga a rehacerlo todo.

| # | Etapa | Produce |
| --- | --- | --- |
| 1 | Extracción | Texto por Obra con su mapa de páginas |
| 2 | Limpieza | Texto sin paratexto editorial, **con el mapa de páginas intacto** |
| 3 | Troceado | Fragmentos con cabecera de Obra y Universo |
| 4 | Indexado | Índice SQLite (`sqlite-vec` + FTS5) |
| 5 | Generación | Pares sintéticos de diálogo en personaje |
| 6 | Entrenamiento | Adaptador |
| 7 | Conversión | Adaptador y modelo en GGUF |
| 8 | Servicio | Backend en marcha |
| 9 | Evaluación | Resultados contra el Conjunto de Evaluación |

La limpieza (etapa 2) tiene una restricción fácil de romper sin notarlo: **no puede
alterar el mapa de páginas**. Como la Cita es Obra + página, si los saltos se recolocan
todas las citas apuntarán ligeramente mal y no se detectará hasta verificar una a mano.
Se limpia dentro de cada página, nunca entre páginas.

El pie editorial afecta a **los dos Universos**, no sólo a Martin: `www.lectulandia.com`
en los cinco tomos de Canción de hielo y fuego y en *El Mundo de Hielo y Fuego*, y
`www.ArchivoTolkien.org` en *Las dos torres* (337 líneas), *El retorno del rey* (411) y
los *Apéndices* (188). *El Hobbit*, *El Silmarillion*, *Beren y Lúthien*, *La comunidad
del anillo* y *Fuego y Sangre* están limpios.

Hay además **paratexto que no debe citarse nunca**: la presentación del editor al frente
de *Juego de tronos* y el epílogo del autor al final de *Danza de dragones* hablan de los
libros desde fuera de la ficción, y una Cita que apunte ahí es una Cita falsa.

## Infraestructura

Dos stacks separados, por el motivo que recoge el ADR-0003.

- **Servicio**: `llama.cpp` + GGUF sobre los toolboxes de ROCm ya instalados en la
  máquina. Funciona hoy, sin trabajo previo.
- **Entrenamiento**: contenedor nuevo, Python 3.12 y PyTorch de las nightlies ROCm de
  TheRock para `gfx1151`. No se reutiliza un toolbox existente: bajarle el Python 3.14
  rompería la razón por la que ese toolbox funciona.
- **Frontend**: web servida por el backend, accesible desde otros dispositivos de la red
  local, sin autenticación. Universo y Modo son dos selectores explícitos.
- **Primera vuelta** con `Qwen/Qwen3-8B` como Modelo Base. El objetivo de la primera
  vuelta no es un buen asistente, es cerrar el circuito completo y ver números. Un modelo
  pequeño lo dice en una tarde; uno grande tardaría tres días en no decir nada más.

### Modelos elegidos

| Rol | Modelo | Por qué |
| --- | --- | --- |
| Modelo Base, primera vuelta | `Qwen/Qwen3-8B` | Apache-2.0, GGUF publicado por los propios Qwen, 4,8% de alucinación en el leaderboard de Vectara, y el ecosistema de LoRA mejor rodado en su talla. Es el camino con menos incógnitas para cerrar el circuito. |
| Modelo Base, segunda vuelta | `google/gemma-4-31B-it` | Apache-2.0, 140+ idiomas con el español de primera, 256K de contexto. Aquí sí se busca calidad, y es donde debe notarse en el marcador. |
| Modelo generador (ticket 10) | `google/gemma-4-31B-it` | Denso, mejor español que la base, y **de otra familia** que el modelo a afinar, que es lo que evita la auto-imitación. |
| Modelo de Embeddings | BGE-M3 — `gpustack/bge-m3-GGUF`, FP16 | Multilingüe y servible por `llama-server`. **Confirmado en el ticket 01**: carga en la build actual (`b10590`), 1024 dimensiones, contexto de 8192, agrupación por CLS. Se sirve en FP16 (1,16 GB) porque cuantizar un modelo de embeddings se paga en calidad de recuperación y a este tamaño no compensa. |

Ninguna de estas elecciones es cara de revertir: para eso están el pipeline repetible y el
Conjunto de Evaluación. Lo que sí es una restricción con la que hay que contar está en el
[ADR-0005](./docs/adr/0005-solo-modelos-de-licencia-permisiva-y-sin-restriccion-de-acceso.md).

**Ojo con la segunda vuelta:** si pasa a usar `gemma-4-31B-it` como Modelo Base y los pares
sintéticos los generó ese mismo modelo, la auto-imitación vuelve por la puerta de atrás.
Habría que regenerar el lote con otra familia, o aceptarlo a sabiendas.

## Evaluación

Sin vara de medir, «he probado con otro Modelo Base» es una impresión, no un dato — y es
donde muere este tipo de proyecto. El **Conjunto de Evaluación** se escribe *antes* de
elegir modelo y no cambia entre experimentos.

Entre 50 y 100 preguntas con respuesta y Cita conocidas, repartidas **50-50 entre los dos
Universos** pese a que Martin sea tres cuartas partes del Corpus — si no, Tolkien queda
infra-evaluado sin que nadie se entere:

- **50% factuales directas**
- **20% de varios saltos** — relaciones entre dos elementos
- **20% Preguntas Negativas** — no están en el Corpus, la respuesta correcta es no saberlo
- **10% Preguntas Cruzadas** — sobre un Universo con el filtro puesto en el otro

Las dos últimas familias son las que valen: las Negativas son lo único que detecta
alucinación, que es el único fallo que importa en Modo Consulta; las Cruzadas son lo único
que demuestra que la separación entre Universos se sostiene. Un examen sin ellas sólo sabe
premiar.

El Modo Personaje no se mide igual: se juzga a ojo sobre un puñado de prompts fijos que se
releen en cada experimento.

## Orden de trabajo

En serie. El Modo Consulta primero, completo y evaluado; después la pista de fine tuning.
El motivo no es la infraestructura —ROCm ya está resuelto en la máquina— sino que el
Conjunto de Evaluación es un subproducto del trabajo del Modo Consulta: arrancar el
entrenamiento antes es entrenar a ciegas, sin nada contra lo que comparar.

Construir el contenedor de entrenamiento no depende de nada y puede hacerse en cualquier
momento.

## Decisiones registradas

- [ADR-0001](./docs/adr/0001-recuperacion-para-hechos-fine-tuning-para-voz.md) — Los hechos salen de recuperación; el fine tuning sólo aporta voz
- [ADR-0002](./docs/adr/0002-adaptador-conmutable-sobre-modelo-base-intacto.md) — El Adaptador se conmuta sobre un Modelo Base intacto
- [ADR-0003](./docs/adr/0003-entrenamiento-y-servicio-en-stacks-separados.md) — Entrenamiento y servicio viven en stacks separados
- [ADR-0004](./docs/adr/0004-indice-en-sqlite-y-no-en-un-servidor-de-vectores.md) — El índice vive en SQLite, no en un servidor de vectores
- [ADR-0005](./docs/adr/0005-solo-modelos-de-licencia-permisiva-y-sin-restriccion-de-acceso.md) — Sólo modelos de licencia permisiva y sin restricción de acceso
- [ADR-0006](./docs/adr/0006-la-cita-nombra-un-volumen-no-una-obra.md) — La Cita nombra un Volumen, no una Obra

## Pendiente de decidir

- **Si los *Apéndices* siguen en el Corpus**. Tira una fuerza en cada sentido y no se puede
  desempatar todavía. A favor de conservarlos: el Conjunto de Evaluación los cita en **X02**
  («Apéndices, p. 61») y está congelado, así que excluirlos deja esa pregunta sin la Cita
  que espera. En contra: el 81% de sus páginas muestreadas tienen su texto literal dentro de
  *El retorno del rey*, que ya los incluye, y meter los dos en el índice es el duplicado por
  el que se excluyó *Dominio de dragones*. Lo que falta para decidir es saber en qué página
  de *El retorno del rey* cae el pasaje de X02, y eso lo dará la extracción del ticket 02.
  Si acaban fuera, el Corpus baja a 14 Volúmenes y 7.423 páginas, pero **sigue teniendo 12
  Obras**: los *Apéndices* no son una Obra, son un Volumen de *El Señor de los Anillos*.

El planteamiento original del proyecto, previo a este diseño, se conserva en
[`docs/app-planteamiento-inicial.md`](./docs/app-planteamiento-inicial.md).
