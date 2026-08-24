# 01 — Esqueleto de etapas y entorno reproducible

**What to build:** Un proyecto en el que se puede lanzar una etapa del pipeline, verla
producir su artefacto, volver a lanzarla y comprobar que reusa la caché en vez de rehacer
el trabajo. Y un servicio de embeddings que devuelve un vector real para una frase en
castellano. A partir de aquí, cualquier etapa posterior sólo tiene que declarar qué
consume y qué produce.

**Blocked by:** None — can start immediately.

**Status:** done

- [x] El entorno corre sobre Python 3.12 gestionado con `uv`; el 3.14 del sistema no se usa
- [x] Una etapa declara sus artefactos de entrada y salida, y se relanza por separado
- [x] Relanzar una etapa sin cambios en su entrada no rehace el trabajo
- [x] Invalidar la entrada de una etapa fuerza su recálculo y el de las que dependen de ella
- [x] `llama-server` sirve un Modelo de Embeddings y devuelve un vector para una frase en castellano
- [x] **Queda confirmado si BGE-M3 en GGUF carga en la build actual**; si no, se elige aquí el Modelo de Embeddings alternativo y se anota el motivo
- [x] El Modo Consulta no depende de PyTorch en ningún punto

## Comments

### Cerrado — 2026-08-24

Las siete casillas quedan comprobadas sobre la máquina, no sólo sobre el papel.

**El entorno.** `uv` con `.python-version` fijado a `3.12`; el intérprete que resuelve es
`cpython-3.12.12`, no el 3.14 del sistema. `requires-python = ">=3.12,<3.13"` impide que
un `uv sync` se vaya al 3.13 por su cuenta.

**Las etapas.** `books_ai.pipeline` es el esqueleto: una etapa declara `consumes` y
`produces` sobre artefactos con nombre, y el `Runner` decide si tiene que correr. El
criterio es un **recibo** por etapa —`.cache/receipts/<etapa>.json`— con la huella sha256
de cada entrada, la de cada salida y la versión de la etapa. Como la huella de un
artefacto intermedio es a la vez salida de una etapa y entrada de la siguiente, un cambio
en el origen se propaga solo hasta donde llega, sin que nadie tenga que declarar la
cascada. Las huellas se memorizan contra `(tamaño, mtime)`, que es lo que evita releer los
91 MB del Corpus en cada arranque: la segunda pasada tarda 0,13 s frente a 0,73 s.

Hay además una salida explícita para lo que el contenido no delata: subir la `version` de
una etapa invalida su recibo aunque su entrada sea idéntica. Es la vía para un cambio de
lógica —otro troceado, otra limpieza— que los datos no distinguen.

`pipeline invalidate <etapa>` tira el recibo de la etapa **y el de todas sus
dependientes**, que es la casilla de la invalidación en cascada. Sobre el pipeline real:
`invalidadas: inventario, resumen-corpus`.

**Las dos primeras etapas** son deliberadamente pequeñas: `inventario` (los PDF del Corpus
con su cuenta de páginas) y `resumen-corpus` (ese inventario en markdown). Existen para
que el esqueleto tenga algo real que masticar sin adelantar decisiones que son del ticket
03: aquí no hay Obras, ni Universos, ni Tipos de Obra, sólo ficheros y páginas.

Un subproducto útil: el inventario da **7.712 páginas en 17 ficheros**, y descontando los
dos excluidos (50 + 50) salen exactamente las **7.612** que dice `app.md`. La cifra del
diseño queda verificada contra el disco.

**BGE-M3 carga.** Es la incógnita que abría el ticket y se cierra en positivo:
`gpustack/bge-m3-GGUF`, fichero `bge-m3-FP16.gguf` (1,16 GB), en la build `b10590` de
`llama.cpp` del toolbox `llama-vulkan-radv`. Devuelve **1.024 dimensiones**, contexto de
8.192, vectores ya normalizados a norma 1. No hace falta modelo alternativo.

Se sirve en **FP16 y no cuantizado** a propósito: cuantizar un modelo de embeddings se
paga en calidad de recuperación, y a 1,16 GB no hay nada que ganar apretándolo.

Dos detalles del arranque que no son opcionales, y por eso viven en
`scripts/embeddings-server.sh` con su motivo escrito al lado:

- `--pooling cls` — BGE-M3 agrupa por el token CLS. Con `--pooling none`, `llama-server`
  devuelve un vector **por token** en vez de uno por texto; el cliente lo detecta y lo
  dice, en vez de aplastarlo en silencio.
- `--ubatch-size 8192` — igual al contexto. Si el ubatch se queda corto, el servidor
  trocea la secuencia y la agrupación deja de ser la del CLS.

**El vector significa algo**, que es más de lo que pedía la casilla. Con acentos y
onomástica inventada, «¿Cuántos enanos acompañan a Bilbo en su viaje?» da coseno **0,7163**
contra «Trece enanos partieron con Bilbo Bolsón desde Bolsón Cerrado», mientras que contra
frases de Martin se queda en 0,28–0,29. Queda como prueba viva en
`tests/test_embeddings_live.py`, que se salta sola si no hay servicio levantado.

**Sin PyTorch.** Las dependencias del Modo Consulta son `click`, `httpx` y `pypdf`. El
Modelo de Embeddings se habla por HTTP y no se carga nunca en proceso, que es lo que
sostiene el ADR-0003. `tests/test_sin_pytorch.py` lo vigila por dos vías: que no haya
`torch`/`transformers`/`accelerate` importables en el entorno, y que ninguno esté
declarado en `pyproject.toml`.

**Lo que queda para quien coja el 02.** El esqueleto está listo para que una etapa nueva
sólo tenga que declarar qué consume y qué produce; `books_ai/corpus.py` sirve de ejemplo
de las dos formas de etapa (leer del disco, transformar un artefacto).

### Una discrepancia detectada, sin resolver aquí

El ticket **03** dice «las **15 Obras** del Corpus quedan indexadas», pero `app.md` dice
«Hay **15 ficheros, no 15 Obras**» y que *El Señor de los Anillos* es una Obra repartida en
cuatro. Con esa regla salen **12 Obras** en 15 ficheros, no 15. No se toca aquí porque la
cuenta depende de si los *Apéndices* siguen en el Corpus, que es la decisión que `app.md`
deja explícitamente pendiente. Quien coja el 03 se lo encuentra de frente.

### Ronda de revisión

Una pasada de `/code-review` sacó siete defectos, todos corregidos con su prueba de
regresión antes de cerrar:

- `status()` reventaba en vez de informar cuando faltaba un artefacto intermedio — justo lo
  que `pipeline list` existe para contar. Ahora un hueco es un motivo («falta la entrada
  'inventario'»), no una excepción; levantar el error sigue siendo cosa de `_execute`.
- Un fallo dentro del cuerpo de una etapa salía como traza de Python. Ahora sale nombrando
  la etapa que lo produjo.
- Una entrada mal formada en la caché de huellas tumbaba cualquier comando con un
  `IndexError`. La caché es una optimización: si está mal, se descarta y se recalcula.
- Las huellas se memorizan contra `(tamaño, mtime)`, y un artefacto recién reescrito no
  puede juzgarse con lo que se recordaba de antes: en sistemas de ficheros con mtime de
  resolución gruesa, una reescritura del mismo tamaño habría colado la huella anterior en
  el recibo, y con ella una etapa siguiente «al día» contra contenido que nunca vio. Se
  olvida la huella de cada salida antes de volver a medirla.
- El script del servicio escuchaba en `0.0.0.0`: un `llama-server` sin autenticación
  abierto a toda la red. Escucha en loopback; el que es público en la LAN es el backend del
  ticket 07.
- Faltaba `encoding="utf-8"` en todas las lecturas y escrituras, que con un locale heredado
  mataba la etapa de resumen en el guion largo.
- El guardia del ADR-0003 sólo reconocía `==` y `>=`: una dependencia declarada como
  `torch<3` o `torch~=2` se le habría colado.

Y una que salió tirando del hilo de la anterior, más de fondo: con un locale no UTF-8,
Python decodifica mal los **nombres de fichero**, y «El Señor de los Anillos» se convierte
en «El SeÃ±or...». No es cosmético: de ese nombre saldrá el nombre de la Obra en cada Cita,
y la corrupción entra además en la huella del artefacto, así que el pipeline produciría
resultados distintos según el shell desde el que se lance. Un entorno reproducible no puede
depender de eso, de modo que el CLI ahora se niega a arrancar y explica la salida
(`PYTHONUTF8=1` o un locale UTF-8) en vez de fabricar Citas mojibake.
