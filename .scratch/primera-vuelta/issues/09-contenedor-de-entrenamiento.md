# 09 — Contenedor de entrenamiento

**What to build:** Un contenedor en el que se puede entrenar un LoRA sobre la GPU y ver
que la pérdida baja. No entrena nada útil todavía: demuestra que el entorno existe y
funciona, que es el único riesgo real de toda la pista de fine tuning.

**Blocked by:** None — can start immediately.

**Status:** ready-for-agent

- [ ] Contenedor nuevo, no un toolbox de `llama.cpp` reutilizado: bajar su Python 3.14 rompería lo que ya funciona
- [ ] Python 3.12 con PyTorch de las nightlies ROCm de TheRock para `gfx1151`
- [ ] La GPU se detecta desde dentro del contenedor
- [ ] Un LoRA de juguete entrena de principio a fin y la pérdida baja
- [ ] Queda anotado el reparto de memoria efectivo: la BIOS asigna la mayor parte a la GPU y deja ~30 GiB al sistema
- [ ] Queda anotado el riesgo de que `uv` o `pip` reinstalen ruedas CUDA por encima de las ROCm, y cómo se evita
