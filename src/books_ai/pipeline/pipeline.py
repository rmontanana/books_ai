"""La declaracion del pipeline: artefactos, etapas y quien produce que."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from pathlib import Path

from books_ai.pipeline.errors import PipelineError
from books_ai.pipeline.stage import Stage, StageContext, StageFn


class Pipeline:
    """El grafo declarado: nombres de artefacto, rutas y etapas que los enlazan.

    Solo declara. No decide si algo esta al dia ni ejecuta nada: de eso se ocupa
    `Runner`, que es lo que permite listar el pipeline sin tocar el disco.
    """

    def __init__(self, root: Path) -> None:
        self.root = Path(root)
        self._paths: dict[str, Path] = {}
        self._sources: set[str] = set()
        self._producers: dict[str, str] = {}
        self.stages: dict[str, Stage] = {}

    def artifact(self, name: str, relative_path: str) -> None:
        """Declara un artefacto que produce alguna etapa."""
        self._declare(name, relative_path)

    def source(self, name: str, relative_path: str) -> None:
        """Declara un artefacto de origen: entra al pipeline, nadie lo produce."""
        self._declare(name, relative_path)
        self._sources.add(name)

    def stage(
        self,
        name: str,
        *,
        consumes: Sequence[str],
        produces: Sequence[str],
        version: str = "1",
    ) -> Callable[[StageFn], StageFn]:
        """Registra una etapa. Se usa como decorador sobre su cuerpo."""

        def register(run: StageFn) -> StageFn:
            if name in self.stages:
                raise PipelineError(f"la etapa '{name}' ya esta declarada")
            for artefacto in (*consumes, *produces):
                if artefacto not in self._paths:
                    raise PipelineError(
                        f"la etapa '{name}' declara el artefacto '{artefacto}', sin declarar"
                    )
            for artefacto in produces:
                if artefacto in self._sources:
                    raise PipelineError(
                        f"la etapa '{name}' produce '{artefacto}', declarado como origen"
                    )
                duena = self._producers.get(artefacto)
                if duena is not None:
                    raise PipelineError(
                        f"'{artefacto}' ya lo produce la etapa '{duena}';"
                        f" '{name}' no puede producirlo tambien"
                    )
            self.stages[name] = Stage(
                name=name,
                consumes=tuple(consumes),
                produces=tuple(produces),
                run=run,
                version=version,
            )
            for artefacto in produces:
                self._producers[artefacto] = name
            return run

        return register

    def path_of(self, artifact: str) -> Path:
        """La ruta absoluta de un artefacto declarado."""
        try:
            return self._paths[artifact]
        except KeyError:
            raise PipelineError(f"artefacto '{artifact}' sin declarar") from None

    def producer_of(self, artifact: str) -> str | None:
        """La etapa que produce el artefacto, o `None` si es de origen."""
        return self._producers.get(artifact)

    def is_source(self, artifact: str) -> bool:
        return artifact in self._sources

    def stage_named(self, name: str) -> Stage:
        try:
            return self.stages[name]
        except KeyError:
            raise PipelineError(f"etapa '{name}' desconocida") from None

    def context_for(self, stage: Stage) -> StageContext:
        return StageContext(
            inputs={nombre: self.path_of(nombre) for nombre in stage.consumes},
            outputs={nombre: self.path_of(nombre) for nombre in stage.produces},
        )

    def dependencies_of(self, stage: Stage) -> list[str]:
        """Las etapas que producen lo que esta consume, sin repetir."""
        vistas: list[str] = []
        for artefacto in stage.consumes:
            productora = self._producers.get(artefacto)
            if productora is not None and productora not in vistas:
                vistas.append(productora)
        return vistas

    def dependents_of(self, name: str) -> list[str]:
        """Las etapas que consumen algo producido por esta."""
        producidos = set(self.stage_named(name).produces)
        return [
            otra.name for otra in self.stages.values() if producidos.intersection(otra.consumes)
        ]

    def _declare(self, name: str, relative_path: str) -> None:
        if name in self._paths:
            raise PipelineError(f"el artefacto '{name}' ya esta declarado")
        self._paths[name] = self.root / relative_path
