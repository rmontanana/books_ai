"""Las primeras dos etapas sobre el Corpus: inventario y resumen.

Son deliberadamente pequenas. Su trabajo aqui es dar al esqueleto de etapas algo
real que masticar -los PDF del Corpus- sin adelantar decisiones que pertenecen a
tickets posteriores: no hay Obras, ni Volumenes, ni Universos, ni Tipos de Texto
todavia, solo ficheros y paginas.
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader
from pypdf.errors import PyPdfError

from books_ai.pipeline import Pipeline, PipelineError, StageContext

CORPUS_POR_DEFECTO = "books"


@dataclass(frozen=True)
class FicheroDelCorpus:
    """Un PDF del Corpus tal y como esta en disco, antes de interpretarlo."""

    ruta: str
    paginas: int
    bytes: int


def inventariar(books_dir: Path) -> list[FicheroDelCorpus]:
    """Cada PDF bajo `books_dir`, con su cuenta de paginas, en orden estable."""
    encontrados = sorted(p for p in books_dir.rglob("*") if p.is_file() and _es_pdf(p))
    if not encontrados:
        raise PipelineError(f"no hay ningun PDF bajo {books_dir}")

    inventario = []
    for ruta in encontrados:
        inventario.append(
            FicheroDelCorpus(
                ruta=str(ruta.relative_to(books_dir)),
                paginas=_contar_paginas(ruta),
                bytes=ruta.stat().st_size,
            )
        )
    return inventario


def resumir(inventario: Sequence[FicheroDelCorpus]) -> str:
    """El inventario en un markdown legible, desglosado por carpeta."""
    por_carpeta: dict[str, list[FicheroDelCorpus]] = {}
    for fichero in inventario:
        carpeta = str(Path(fichero.ruta).parent)
        por_carpeta.setdefault(carpeta, []).append(fichero)

    total_paginas = sum(f.paginas for f in inventario)
    lineas = [
        "# Resumen del Corpus",
        "",
        f"{len(inventario)} ficheros, {total_paginas} paginas,"
        f" {_megas(sum(f.bytes for f in inventario))}.",
        "",
    ]
    for carpeta in sorted(por_carpeta):
        ficheros = por_carpeta[carpeta]
        lineas.append(
            f"## {carpeta} — {len(ficheros)} ficheros, {sum(f.paginas for f in ficheros)} paginas"
        )
        lineas.append("")
        lineas.append("| Fichero | Paginas | Tamano |")
        lineas.append("| --- | ---: | ---: |")
        for fichero in ficheros:
            nombre = Path(fichero.ruta).name
            lineas.append(f"| {nombre} | {fichero.paginas} | {_megas(fichero.bytes)} |")
        lineas.append("")
    return "\n".join(lineas)


def build_pipeline(root: Path, books_dir: Path | None = None) -> Pipeline:
    """El pipeline de la aplicacion tal y como esta hoy: dos etapas encadenadas."""
    pipeline = Pipeline(root)
    corpus = books_dir if books_dir is not None else root / CORPUS_POR_DEFECTO
    pipeline.source("corpus", str(_relativa(corpus, root)))
    pipeline.artifact("inventario", "artifacts/inventario.json")
    pipeline.artifact("resumen-corpus", "artifacts/resumen-corpus.md")

    @pipeline.stage("inventario", consumes=["corpus"], produces=["inventario"])
    def _inventario(ctx: StageContext) -> None:
        inventario = inventariar(ctx.inputs["corpus"])
        ctx.outputs["inventario"].write_text(
            json.dumps(
                {
                    "total_ficheros": len(inventario),
                    "total_paginas": sum(f.paginas for f in inventario),
                    "ficheros": [vars(f) for f in inventario],
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

    @pipeline.stage("resumen-corpus", consumes=["inventario"], produces=["resumen-corpus"])
    def _resumen(ctx: StageContext) -> None:
        crudo = json.loads(ctx.inputs["inventario"].read_text(encoding="utf-8"))
        inventario = [FicheroDelCorpus(**f) for f in crudo["ficheros"]]
        ctx.outputs["resumen-corpus"].write_text(resumir(inventario), encoding="utf-8")

    return pipeline


def _es_pdf(path: Path) -> bool:
    return path.suffix.lower() == ".pdf"


def _contar_paginas(ruta: Path) -> int:
    try:
        return len(PdfReader(ruta).pages)
    except (PyPdfError, OSError, ValueError) as error:
        raise PipelineError(f"no se pudo leer el PDF {ruta.name}: {error}") from error


def _relativa(objetivo: Path, root: Path) -> Path:
    try:
        return objetivo.resolve().relative_to(root.resolve())
    except ValueError:
        return objetivo.resolve()


def _megas(bytes_: int) -> str:
    return f"{bytes_ / 1_048_576:.1f} MB"
