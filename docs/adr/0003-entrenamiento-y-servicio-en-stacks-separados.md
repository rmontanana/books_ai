# Entrenamiento y servicio viven en stacks separados

La máquina ya tiene 16 toolboxes de `kyuz0/amd-strix-halo-toolboxes` con ROCm y
`llama.cpp` compilado para `gfx1151`, funcionando. Ninguno de ellos, sin embargo, lleva
PyTorch, PEFT, transformers ni TRL, y todos corren Python 3.14, que no tiene ruedas de
PyTorch. Son entornos de inferencia, no de entrenamiento.

Decidimos dos stacks: **servicio** sobre los toolboxes existentes, `llama.cpp` + GGUF, sin
trabajo previo; y **entrenamiento** en un contenedor nuevo con Python 3.12 y PyTorch de
las nightlies ROCm de TheRock, que produce un Adaptador como artefacto. Encaja con el
pipeline por etapas: cada etapa produce un artefacto que la siguiente lee, y ninguna
necesita las dependencias de la otra.

La separación no es una concesión: es lo que permite que el Modo Consulta esté en marcha
mientras el entorno de entrenamiento todavía no existe.

## Alternativa rechazada: Ollama

Ollama está instalado en la máquina y sería el camino cómodo, pero empaqueta el Adaptador
dentro de un modelo declarado en un `Modelfile`. Probar cinco Adaptadores serían cinco
modelos registrados y ninguna conmutación en caliente, lo que contradice el ADR-0002.
Se descarta a propósito, no por desconocimiento.

## Alternativa rechazada: reutilizar un toolbox existente para entrenar

Instalar PyTorch dentro de un toolbox de `llama.cpp` obligaría a bajar su Python de 3.14,
rompiendo la razón por la que ese toolbox funciona. El contenedor de entrenamiento es
nuevo y desechable.
