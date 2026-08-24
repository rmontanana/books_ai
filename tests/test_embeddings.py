from __future__ import annotations

import json
import threading
from collections.abc import Callable, Iterator
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any

import pytest

from books_ai.embeddings import EmbeddingsError, EmbeddingsService

Responder = Callable[[dict[str, Any]], tuple[int, str]]


def serve(responder: Responder) -> Iterator[str]:
    """Un llama-server de mentira, para no depender de que haya uno levantado."""

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self) -> None:  # noqa: N802 - lo impone BaseHTTPRequestHandler
            longitud = int(self.headers.get("Content-Length", "0"))
            peticion = json.loads(self.rfile.read(longitud) or b"{}")
            estado, cuerpo = responder(peticion)
            crudo = cuerpo.encode()
            self.send_response(estado)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(crudo)))
            self.end_headers()
            self.wfile.write(crudo)

        def log_message(self, *args: Any) -> None:
            return None

    servidor = HTTPServer(("127.0.0.1", 0), Handler)
    hilo = threading.Thread(target=servidor.serve_forever, daemon=True)
    hilo.start()
    try:
        yield f"http://127.0.0.1:{servidor.server_port}"
    finally:
        servidor.shutdown()
        servidor.server_close()


def embeddings_ok(vectores: list[list[float]]) -> Responder:
    def responder(peticion: dict[str, Any]) -> tuple[int, str]:
        entrada = peticion["input"]
        textos = entrada if isinstance(entrada, list) else [entrada]
        cuerpo = {
            "object": "list",
            "model": "bge-m3",
            "data": [
                {"object": "embedding", "index": i, "embedding": vectores[i]}
                for i in range(len(textos))
            ],
        }
        return 200, json.dumps(cuerpo)

    return responder


@pytest.fixture
def base_url(request: pytest.FixtureRequest) -> Iterator[str]:
    responder: Responder = request.param
    yield from serve(responder)


@pytest.mark.parametrize("base_url", [embeddings_ok([[0.1, 0.2, 0.3]])], indirect=True)
def test_devuelve_un_vector_para_una_frase_en_castellano(base_url: str) -> None:
    servicio = EmbeddingsService(base_url)
    vector = servicio.embed_one("Trece enanos acompanan a Bilbo")
    assert vector == [0.1, 0.2, 0.3]


@pytest.mark.parametrize(
    "base_url", [embeddings_ok([[1.0, 0.0], [0.0, 1.0], [0.5, 0.5]])], indirect=True
)
def test_conserva_el_orden_de_los_textos(base_url: str) -> None:
    servicio = EmbeddingsService(base_url)
    vectores = servicio.embed(["uno", "dos", "tres"])
    assert vectores == [[1.0, 0.0], [0.0, 1.0], [0.5, 0.5]]


def test_una_lista_vacia_no_llega_a_llamar_al_servicio() -> None:
    servicio = EmbeddingsService("http://127.0.0.1:1")
    assert servicio.embed([]) == []


@pytest.mark.parametrize("base_url", [embeddings_ok([[1.0, 0.0]])], indirect=True)
def test_la_dimension_sale_del_propio_servicio(base_url: str) -> None:
    servicio = EmbeddingsService(base_url)
    assert servicio.dimension() == 2


def _error(estado: int, cuerpo: str) -> Responder:
    def responder(peticion: dict[str, Any]) -> tuple[int, str]:
        return estado, cuerpo

    return responder


@pytest.mark.parametrize(
    "base_url", [_error(500, json.dumps({"error": {"message": "sin modelo"}}))], indirect=True
)
def test_un_error_del_servicio_se_reporta_con_su_mensaje(base_url: str) -> None:
    servicio = EmbeddingsService(base_url)
    with pytest.raises(EmbeddingsError, match="sin modelo"):
        servicio.embed_one("hola")


@pytest.mark.parametrize("base_url", [_error(200, "no soy json")], indirect=True)
def test_una_respuesta_ilegible_se_reporta(base_url: str) -> None:
    servicio = EmbeddingsService(base_url)
    with pytest.raises(EmbeddingsError, match="respuesta"):
        servicio.embed_one("hola")


@pytest.mark.parametrize(
    "base_url",
    [_error(200, json.dumps({"object": "list", "data": []}))],
    indirect=True,
)
def test_faltar_vectores_se_reporta_en_vez_de_devolver_de_menos(base_url: str) -> None:
    servicio = EmbeddingsService(base_url)
    with pytest.raises(EmbeddingsError, match="1"):
        servicio.embed(["hola"])


def _sin_pooling() -> Responder:
    """llama-server con `--pooling none` devuelve un vector por token, no uno por texto."""

    def responder(peticion: dict[str, Any]) -> tuple[int, str]:
        cuerpo = {
            "object": "list",
            "data": [{"index": 0, "embedding": [[0.1, 0.2], [0.3, 0.4]]}],
        }
        return 200, json.dumps(cuerpo)

    return responder


@pytest.mark.parametrize("base_url", [_sin_pooling()], indirect=True)
def test_un_servidor_sin_pooling_se_detecta_y_se_explica(base_url: str) -> None:
    servicio = EmbeddingsService(base_url)
    with pytest.raises(EmbeddingsError, match="pooling"):
        servicio.embed_one("hola")


def _dimension_inconsistente() -> Responder:
    def responder(peticion: dict[str, Any]) -> tuple[int, str]:
        cuerpo = {
            "object": "list",
            "data": [
                {"index": 0, "embedding": [0.1, 0.2]},
                {"index": 1, "embedding": [0.1, 0.2, 0.3]},
            ],
        }
        return 200, json.dumps(cuerpo)

    return responder


@pytest.mark.parametrize("base_url", [_dimension_inconsistente()], indirect=True)
def test_dimensiones_dispares_se_reportan(base_url: str) -> None:
    servicio = EmbeddingsService(base_url)
    with pytest.raises(EmbeddingsError, match="dimension"):
        servicio.embed(["uno", "dos"])


def _desordenado() -> Responder:
    def responder(peticion: dict[str, Any]) -> tuple[int, str]:
        cuerpo = {
            "object": "list",
            "data": [
                {"index": 1, "embedding": [0.0, 1.0]},
                {"index": 0, "embedding": [1.0, 0.0]},
            ],
        }
        return 200, json.dumps(cuerpo)

    return responder


@pytest.mark.parametrize("base_url", [_desordenado()], indirect=True)
def test_se_reordena_por_indice_no_por_orden_de_llegada(base_url: str) -> None:
    servicio = EmbeddingsService(base_url)
    assert servicio.embed(["uno", "dos"]) == [[1.0, 0.0], [0.0, 1.0]]
