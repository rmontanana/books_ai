"""Quien decide si una etapa tiene que correr, y la corre.

El criterio es un **recibo** por etapa: la huella de cada artefacto que consumio,
la de cada uno que produjo y la version de la etapa. Una etapa esta al dia cuando
lo que hay hoy en disco coincide con lo que dice su recibo. Como la huella de un
artefacto intermedio es a la vez salida de una etapa y entrada de la siguiente, un
cambio en el origen se propaga solo hasta donde llega.
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from books_ai.pipeline.errors import PipelineError
from books_ai.pipeline.fingerprint import Fingerprints
from books_ai.pipeline.pipeline import Pipeline
from books_ai.pipeline.stage import Stage


@dataclass(frozen=True)
class Receipt:
    """Lo que quedo registrado la ultima vez que una etapa corrio de verdad."""

    version: str
    inputs: dict[str, str]
    outputs: dict[str, str]

    @staticmethod
    def parse(raw: object) -> Receipt | None:
        """El recibo, o `None` si el fichero no tiene la forma esperada."""
        if not isinstance(raw, dict):
            return None
        version = raw.get("version")
        inputs = raw.get("inputs")
        outputs = raw.get("outputs")
        if not isinstance(version, str) or not isinstance(inputs, dict):
            return None
        if not isinstance(outputs, dict):
            return None
        return Receipt(
            version=version,
            inputs={str(k): str(v) for k, v in inputs.items()},
            outputs={str(k): str(v) for k, v in outputs.items()},
        )


@dataclass(frozen=True)
class StageStatus:
    """El veredicto sobre una etapa, sin ejecutarla."""

    stage: str
    fresh: bool
    reason: str


@dataclass(frozen=True)
class StageOutcome:
    """Lo que paso con una etapa en una ejecucion concreta."""

    stage: str
    reused: bool
    reason: str


class Runner:
    def __init__(self, pipeline: Pipeline, cache_dir: Path | None = None) -> None:
        self._pipeline = pipeline
        self._cache_dir = cache_dir or pipeline.root / ".cache"
        self._receipts_dir = self._cache_dir / "receipts"
        self._fingerprints = Fingerprints(self._cache_dir / "fingerprints.json")

    def status(self, names: Sequence[str] | None = None) -> list[StageStatus]:
        """El estado de cada etapa pedida, sin tocar nada."""
        elegidas = list(names) if names is not None else list(self._pipeline.stages)
        veredictos = []
        try:
            for nombre in elegidas:
                etapa = self._pipeline.stage_named(nombre)
                al_dia, motivo = self._is_fresh(etapa)
                veredictos.append(StageStatus(stage=nombre, fresh=al_dia, reason=motivo))
        finally:
            # Aunque solo se estuviera mirando, las huellas ya se han pagado.
            self._fingerprints.save()
        return veredictos

    def run(
        self,
        names: Sequence[str],
        *,
        force: bool = False,
        only: bool = False,
    ) -> list[StageOutcome]:
        """Ejecuta las etapas pedidas y, salvo `only`, las que necesitan por delante.

        `force` reejecuta todo el plan aunque los recibos digan que esta al dia.
        """
        plan = list(names) if only else self._plan(names)
        for nombre in plan:
            self._pipeline.stage_named(nombre)

        resultados = []
        try:
            for nombre in plan:
                etapa = self._pipeline.stage_named(nombre)
                al_dia, motivo = self._is_fresh(etapa)
                if al_dia and not force:
                    resultados.append(StageOutcome(stage=nombre, reused=True, reason=motivo))
                    continue
                self._execute(etapa)
                resultados.append(
                    StageOutcome(stage=nombre, reused=False, reason="forzada" if force else motivo)
                )
        finally:
            # Si una etapa revienta, lo ya calculado no se tira: la siguiente
            # pasada no vuelve a leer los 91 MB del Corpus para nada.
            self._fingerprints.save()
        return resultados

    def invalidate(self, name: str) -> list[str]:
        """Tira el recibo de una etapa y el de todas las que dependen de ella.

        Devuelve los nombres afectados, en orden de ejecucion.
        """
        self._pipeline.stage_named(name)
        alcanzadas = [name]
        pendientes = [name]
        while pendientes:
            actual = pendientes.pop()
            for dependiente in self._pipeline.dependents_of(actual):
                if dependiente not in alcanzadas:
                    alcanzadas.append(dependiente)
                    pendientes.append(dependiente)

        ordenadas = [n for n in self._topological_order() if n in alcanzadas]
        for nombre in ordenadas:
            self._receipt_path(nombre).unlink(missing_ok=True)
        return ordenadas

    def _execute(self, stage: Stage) -> None:
        contexto = self._pipeline.context_for(stage)
        entradas = self._input_digests(stage)

        for ruta in contexto.outputs.values():
            ruta.parent.mkdir(parents=True, exist_ok=True)
        try:
            stage.run(contexto)
        except PipelineError:
            raise
        except Exception as error:
            raise PipelineError(f"la etapa '{stage.name}' fallo: {error}") from error

        salidas: dict[str, str] = {}
        for nombre, ruta in contexto.outputs.items():
            self._fingerprints.forget(ruta)
            huella = self._fingerprints.of(ruta)
            if huella is None:
                raise PipelineError(
                    f"la etapa '{stage.name}' termino sin escribir su artefacto"
                    f" '{nombre}' en {ruta}"
                )
            salidas[nombre] = huella

        self._write_receipt(stage, entradas, salidas)

    def _is_fresh(self, stage: Stage) -> tuple[bool, str]:
        recibo = self._read_receipt(stage.name)
        if recibo is None:
            return False, "sin recibo"
        if recibo.version != stage.version:
            return False, f"la etapa cambio de version a '{stage.version}'"

        for nombre, ruta in self._pipeline.context_for(stage).outputs.items():
            huella = self._fingerprints.of(ruta)
            if huella is None:
                return False, f"falta el artefacto '{nombre}'"
            if recibo.outputs.get(nombre) != huella:
                return False, f"el artefacto '{nombre}' cambio fuera del pipeline"

        # Aqui no se levanta un error aunque falte una entrada: `status()` tiene
        # que poder informar de un pipeline a medias, no abortar al primer hueco.
        for nombre in stage.consumes:
            huella = self._fingerprints.of(self._pipeline.path_of(nombre))
            if huella is None:
                return False, f"falta la entrada '{nombre}'"
            if recibo.inputs.get(nombre) != huella:
                return False, f"cambio la entrada '{nombre}'"

        return True, "al dia"

    def _input_digests(self, stage: Stage) -> dict[str, str]:
        huellas: dict[str, str] = {}
        for nombre in stage.consumes:
            ruta = self._pipeline.path_of(nombre)
            huella = self._fingerprints.of(ruta)
            if huella is None:
                if self._pipeline.producer_of(nombre) is None:
                    raise PipelineError(
                        f"falta el artefacto de origen '{nombre}' que espera"
                        f" la etapa '{stage.name}': {ruta}"
                    )
                raise PipelineError(
                    f"falta el artefacto '{nombre}' que espera la etapa '{stage.name}':"
                    f" produce antes la etapa '{self._pipeline.producer_of(nombre)}'"
                )
            huellas[nombre] = huella
        return huellas

    def _plan(self, names: Sequence[str]) -> list[str]:
        """Las etapas pedidas mas sus dependencias, en orden topologico.

        Un ciclo lo detecta el orden topologico, no esta busqueda: aqui solo
        interesa a que se llega, no en que orden.
        """
        necesarias: set[str] = set()
        pendientes = list(names)
        while pendientes:
            nombre = pendientes.pop()
            if nombre in necesarias:
                continue
            necesarias.add(nombre)
            pendientes.extend(self._pipeline.dependencies_of(self._pipeline.stage_named(nombre)))
        return [n for n in self._topological_order() if n in necesarias]

    def _topological_order(self) -> list[str]:
        ordenadas: list[str] = []
        visitando: set[str] = set()

        def visitar(nombre: str, camino: tuple[str, ...]) -> None:
            if nombre in ordenadas:
                return
            if nombre in visitando:
                raise PipelineError(f"ciclo entre etapas: {' -> '.join((*camino, nombre))}")
            visitando.add(nombre)
            etapa = self._pipeline.stage_named(nombre)
            for dependencia in self._pipeline.dependencies_of(etapa):
                visitar(dependencia, (*camino, nombre))
            visitando.discard(nombre)
            ordenadas.append(nombre)

        for nombre in self._pipeline.stages:
            visitar(nombre, ())
        return ordenadas

    def _receipt_path(self, stage_name: str) -> Path:
        return self._receipts_dir / f"{stage_name}.json"

    def _read_receipt(self, stage_name: str) -> Receipt | None:
        ruta = self._receipt_path(stage_name)
        if not ruta.is_file():
            return None
        try:
            return Receipt.parse(json.loads(ruta.read_text(encoding="utf-8")))
        except (OSError, ValueError):
            return None

    def _write_receipt(self, stage: Stage, inputs: dict[str, str], outputs: dict[str, str]) -> None:
        self._receipts_dir.mkdir(parents=True, exist_ok=True)
        self._receipt_path(stage.name).write_text(
            json.dumps(
                {
                    "stage": stage.name,
                    "version": stage.version,
                    "inputs": inputs,
                    "outputs": outputs,
                },
                indent=2,
                sort_keys=True,
            ),
            encoding="utf-8",
        )
