# El índice vive en SQLite, no en un servidor de vectores

La recuperación es híbrida (densa + léxica), lo que normalmente empuja hacia un almacén
de vectores dedicado. Elegimos `sqlite-vec` + FTS5: un único fichero que se copia,
versiona, borra y regenera, y que no obliga a levantar ningún proceso para arrancar la
aplicación. Es la forma que mejor encaja con un pipeline por etapas donde cada etapa deja
un artefacto.

El precio es concreto y conocido: BGE-M3 produce pesos léxicos aprendidos y FTS5 no sabe
consumirlos, así que la mitad léxica del híbrido es BM25 clásico. Sobre un corpus lleno de
onomástica inventada — Invernalia, Bombadil, Meñique — BM25 captura casi todo lo que esos
pesos aportarían.

## Cuándo reconsiderarlo

Si el Conjunto de Evaluación muestra consultas que se pierden por la vía léxica, o si el
Corpus crece hasta donde SQLite deje de rendir, el destino previsto es **Milvus** u otro
servidor con soporte de vectores dispersos, que sí aprovecharía los tres modos de BGE-M3.
Cambiar de almacén es reescribir una etapa del pipeline y regenerar el índice, no
rediseñar la aplicación — y para entonces el Conjunto de Evaluación permitirá demostrar
que el cambio mejora algo.
