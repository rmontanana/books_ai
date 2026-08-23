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

15 ficheros PDF, ~3,36 M palabras y 7.612 páginas, repartidas en dos Universos que no
comparten absolutamente nada. Martin representa cerca del 73% del texto.

Los 17 ficheros originales incluían dos que quedan **excluidos**, anotados como tales en
el manifiesto y no borrados del disco:

| Obra | Motivo |
| --- | --- |
| *Dominio de dragones* | Folleto promocional cuyo texto está íntegramente dentro de *Danza de dragones*. Verificado. Indexarlo produce resultados duplicados y sobre-representa esas páginas al entrenar. |
| *El Dragón de Hielo* | Cuento independiente que no transcurre en ninguno de los dos Universos. Con el filtro obligatorio por Universo no tiene casilla donde caer. |

Cada Obra restante lleva registrado su **Tipo de Obra**, porque no todas merecen la misma
autoridad. *Fuego y Sangre* y *El Mundo de Hielo y Fuego* son crónicas escritas desde
dentro del Universo por narradores explícitamente parciales, con versiones contradictorias
del mismo suceso; los *Apéndices* de Tolkien son material de referencia. El Modo Consulta
refleja esa diferencia en la respuesta en lugar de presentarlo todo como hecho.

Un detalle que condiciona la extracción: *El Señor de los Anillos* es **una Obra repartida
en cuatro ficheros**. Hay 15 ficheros, no 15 Obras.

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
  afirmación. La **Cita** lo acompaña con Obra y página, anclada a donde empieza el Pasaje
  y no a donde empieza el Fragmento — que casi siempre cruza un salto de página.
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
- **Primera vuelta** con un Modelo Base de clase 8B. El objetivo de la primera vuelta no
  es un buen asistente, es cerrar el circuito completo y ver números. Un modelo pequeño lo
  dice en una tarde; uno grande tardaría tres días en no decir nada más.

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

## Pendiente de decidir

Los tres son baratos de cambiar y se deciden mejor con el pipeline delante:

- El Modelo Base concreto — está elegida la clase (8B), no el nombre
- El modelo grande que generará los pares sintéticos
- El número exacto de preguntas del Conjunto de Evaluación, dentro del rango 50–100
- **Si los *Apéndices* siguen en el Corpus**: el 81% de sus páginas muestreadas tienen su
  texto literal dentro de *El retorno del rey*, que ya los incluye. Es el mismo caso que
  *Dominio de dragones* y está sin resolver.

El planteamiento original del proyecto, previo a este diseño, se conserva en
[`docs/app-planteamiento-inicial.md`](./docs/app-planteamiento-inicial.md).
