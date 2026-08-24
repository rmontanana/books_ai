"""La linea de comandos: lanzar etapas, invalidarlas y sondear los embeddings."""

from __future__ import annotations

import json
import sys
from collections.abc import Callable
from pathlib import Path

import click

from books_ai.corpus import build_pipeline
from books_ai.embeddings import EmbeddingsError, EmbeddingsService
from books_ai.pipeline import Pipeline, PipelineError, Runner

URL_EMBEDDINGS_POR_DEFECTO = "http://127.0.0.1:8081"


def _exigir_utf8() -> None:
    """Sin UTF-8 en el sistema de ficheros no hay entorno reproducible.

    Media docena de Obras llevan acentos en el nombre del fichero, y de ahi
    saldra el nombre de la Obra en cada Cita. Con otra codificacion, Python
    decodifica «El Senor de los Anillos» como «El SeÃ±or...», la huella del
    artefacto cambia con el locale del shell, y nada de eso da la cara hasta
    que alguien lee una Cita. Mejor negarse que producir Citas mojibake.
    """
    codificacion = sys.getfilesystemencoding().lower().replace("-", "")
    if codificacion != "utf8":
        raise click.ClickException(
            f"el sistema de ficheros se lee como '{sys.getfilesystemencoding()}' y no como"
            " UTF-8: los nombres de Obra con acentos saldrian corruptos."
            " Arranca con PYTHONUTF8=1 o con un locale UTF-8."
        )


@click.group()
@click.option(
    "--root",
    type=click.Path(file_okay=False, path_type=Path),
    default=Path.cwd,
    help="Raiz del proyecto: de ahi cuelgan books/, artifacts/ y .cache/.",
)
@click.pass_context
def main(ctx: click.Context, root: Path) -> None:
    """Consulta local sobre un corpus de libros."""
    _exigir_utf8()
    ctx.obj = build_pipeline(root)


@main.group()
def pipeline() -> None:
    """Las etapas y su cache."""


@pipeline.command("list")
@click.pass_obj
def listar(pipe: Pipeline) -> None:
    """Que etapas hay, que consumen, que producen y si estan al dia."""
    for estado in _guardando_errores(lambda: Runner(pipe).status()):
        etapa = pipe.stage_named(estado.stage)
        marca = "al dia   " if estado.fresh else "pendiente"
        click.echo(f"{marca}  {etapa.name}")
        click.echo(f"             consume: {', '.join(etapa.consumes) or '-'}")
        click.echo(f"             produce: {', '.join(etapa.produces) or '-'}")
        click.echo(f"             motivo:  {estado.reason}")


@pipeline.command("run")
@click.argument("stages", nargs=-1)
@click.option("--force", is_flag=True, help="Reejecuta aunque el recibo diga que esta al dia.")
@click.option("--only", is_flag=True, help="Corre solo lo pedido, sin arrastrar dependencias.")
@click.pass_obj
def ejecutar(pipe: Pipeline, stages: tuple[str, ...], force: bool, only: bool) -> None:
    """Ejecuta las etapas pedidas, o el pipeline entero si no se pide ninguna."""
    pedidas = list(stages) if stages else list(pipe.stages)
    resultados = _guardando_errores(lambda: Runner(pipe).run(pedidas, force=force, only=only))
    for resultado in resultados:
        verbo = "reusada" if resultado.reused else "ejecutada"
        click.echo(f"{verbo:>9}  {resultado.stage}  ({resultado.reason})")


@pipeline.command("invalidate")
@click.argument("stage")
@click.pass_obj
def invalidar(pipe: Pipeline, stage: str) -> None:
    """Tira el recibo de una etapa y el de todo lo que depende de ella."""
    afectadas = _guardando_errores(lambda: Runner(pipe).invalidate(stage))
    click.echo("invalidadas: " + ", ".join(afectadas))


@main.group()
def embeddings() -> None:
    """El Modelo de Embeddings servido por llama-server."""


@embeddings.command("probe")
@click.option("--url", default=URL_EMBEDDINGS_POR_DEFECTO, help="Base de llama-server.")
@click.option(
    "--text",
    default="Trece enanos acompanaron a Bilbo Bolson fuera de la Comarca.",
    help="Frase con la que sondear el servicio.",
)
def sondear(url: str, text: str) -> None:
    """Comprueba que el servicio devuelve un vector real para una frase en castellano."""
    vector = _guardando_errores(lambda: EmbeddingsService(url).embed_one(text))
    click.echo(f"url:       {url}")
    click.echo(f"frase:     {text}")
    click.echo(f"dimension: {len(vector)}")
    click.echo(f"norma:     {sum(x * x for x in vector) ** 0.5:.6f}")
    click.echo("primeros:  " + ", ".join(f"{x:+.6f}" for x in vector[:8]))


@embeddings.command("embed")
@click.argument("text")
@click.option("--url", default=URL_EMBEDDINGS_POR_DEFECTO, help="Base de llama-server.")
def embeber(text: str, url: str) -> None:
    """Escribe en JSON el vector de un texto."""
    vector = _guardando_errores(lambda: EmbeddingsService(url).embed_one(text))
    click.echo(json.dumps({"text": text, "dimension": len(vector), "embedding": vector}))


def _guardando_errores[T](accion: Callable[[], T]) -> T:
    """Convierte los fallos esperables en un mensaje, no en una traza."""
    try:
        return accion()
    except (PipelineError, EmbeddingsError) as error:
        raise click.ClickException(str(error)) from error
