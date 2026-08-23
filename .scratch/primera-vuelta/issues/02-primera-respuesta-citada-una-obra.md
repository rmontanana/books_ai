# 02 — Primera respuesta citada sobre una sola Obra

**What to build:** Preguntar por línea de comandos algo sobre *El Hobbit* y recibir una
respuesta con su Pasaje literal, la Obra y la página. Es la bala trazadora: recorre
extracción, troceado, indexado, recuperación y generación, pero sobre una sola Obra
pequeña y limpia para que el circuito completo quepa de una vez.

**Blocked by:** 01.

**Status:** ready-for-agent

- [ ] *El Hobbit* queda extraído con su mapa de páginas y troceado en Fragmentos de ~450 palabras con ~15% de solape
- [ ] Cada Fragmento lleva antepuesta su cabecera de Obra y Universo antes de vectorizarse
- [ ] El índice es un único fichero SQLite, sin ningún proceso que levantar para consultarlo
- [ ] La recuperación es híbrida: vector denso más BM25 léxico
- [ ] La respuesta incluye Pasaje literal, Obra y página, con la página anclada al comienzo del Pasaje y no a la del Fragmento
- [ ] **T03** («¿Cuántos enanos acompañan a Bilbo?») se responde «Trece» citando *El Hobbit*, p. 8
- [ ] **T04** (Smaug) se responde citando *El Hobbit*, p. 15
- [ ] Se comprueba a mano que la página citada contiene de verdad el Pasaje en el PDF original
