# Los hechos salen de recuperación; el fine tuning sólo aporta voz

El planteamiento inicial del proyecto era afinar un modelo con los libros para poder
consultarlos. El fine tuning sobre ~5M tokens de narrativa memoriza de forma irregular,
no distingue lo aprendido de lo alucinado y no puede indicar de dónde salió una
afirmación, así que no sirve para responder hechos de forma verificable.

Decidimos que el **Modo Consulta** responda por recuperación sobre el Corpus, con Pasaje
y Cita, y que el entrenamiento propio se reserve al **Modo Personaje**, donde lo que se
busca es voz y registro y no hay nada que verificar. Las dos técnicas dejan de competir:
cada una cubre el modo para el que es buena.

## Consecuencias

- La calidad del Modo Consulta depende del troceado y del Modelo de Embeddings, no del
  Modelo Base elegido.
- El proyecto conserva el fine tuning como objetivo de aprendizaje sin que de él dependa
  que la aplicación funcione.
