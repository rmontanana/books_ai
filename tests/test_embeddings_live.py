"""Comprobacion contra un llama-server de verdad.

Se salta si no hay uno levantado, para que la suite siga corriendo sin GPU. Para
ejecutarla:

    scripts/embeddings-server.sh &
    BOOKS_AI_EMBEDDINGS_URL=http://127.0.0.1:8081 uv run pytest tests/test_embeddings_live.py
"""

from __future__ import annotations

import os

import pytest

from books_ai.embeddings import EmbeddingsService

URL = os.environ.get("BOOKS_AI_EMBEDDINGS_URL")

pytestmark = pytest.mark.skipif(
    URL is None, reason="sin BOOKS_AI_EMBEDDINGS_URL: no hay Modelo de Embeddings servido"
)


@pytest.fixture
def servicio() -> EmbeddingsService:
    assert URL is not None
    return EmbeddingsService(URL)


def test_devuelve_un_vector_para_una_frase_en_castellano(servicio: EmbeddingsService) -> None:
    vector = servicio.embed_one("¿Cuántos enanos acompañan a Bilbo en su viaje?")
    assert len(vector) == 1024
    assert any(x != 0.0 for x in vector)


def test_los_vectores_vienen_normalizados(servicio: EmbeddingsService) -> None:
    vector = servicio.embed_one("Invernalia es la fortaleza de la Casa Stark.")
    assert sum(x * x for x in vector) == pytest.approx(1.0, abs=1e-3)


def test_lo_relacionado_queda_mas_cerca_que_lo_ajeno(servicio: EmbeddingsService) -> None:
    """La prueba de que el vector significa algo, no solo de que tiene el tamano correcto."""
    pregunta, respuesta, ajena = servicio.embed(
        [
            "¿Cuántos enanos acompañan a Bilbo en su viaje?",
            "Trece enanos partieron con Bilbo Bolsón desde Bolsón Cerrado.",
            "Invernalia es la fortaleza ancestral de la Casa Stark en el Norte.",
        ]
    )

    def coseno(a: list[float], b: list[float]) -> float:
        return sum(x * y for x, y in zip(a, b, strict=True))

    assert coseno(pregunta, respuesta) > coseno(pregunta, ajena) + 0.2
