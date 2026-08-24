"""Que es una etapa: lo que consume, lo que produce y como se ejecuta."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class StageContext:
    """Las rutas ya resueltas que recibe el cuerpo de una etapa.

    Una etapa no sabe donde viven sus artefactos ni como se decide si tiene que
    correr: solo lee de `inputs` y escribe en `outputs`.
    """

    inputs: Mapping[str, Path]
    outputs: Mapping[str, Path]


StageFn = Callable[[StageContext], None]


@dataclass(frozen=True)
class Stage:
    """Una etapa del pipeline y su declaracion de artefactos.

    `version` forma parte de la huella: subirla invalida la cache de la etapa
    aunque su entrada no haya cambiado, que es como se propaga un cambio de
    logica que los datos no delatan.
    """

    name: str
    consumes: tuple[str, ...]
    produces: tuple[str, ...]
    run: StageFn
    version: str = "1"
