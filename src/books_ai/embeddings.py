"""El Modelo de Embeddings, servido por `llama-server`.

El Modo Consulta habla con el modelo por HTTP y nunca lo carga en proceso: es lo
que mantiene la consulta libre de PyTorch (ADR-0003) y permite cambiar de Modelo
de Embeddings sin tocar el pipeline.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import httpx


class EmbeddingsError(RuntimeError):
    """El servicio de embeddings no dio un vector utilizable."""


class EmbeddingsService:
    """Cliente del endpoint `/v1/embeddings` de `llama-server`."""

    def __init__(self, base_url: str, *, timeout: float = 120.0) -> None:
        self.base_url = base_url.rstrip("/")
        self._timeout = timeout

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        """Un vector por texto, en el mismo orden en que entraron."""
        if not texts:
            return []

        try:
            respuesta = httpx.post(
                f"{self.base_url}/v1/embeddings",
                json={"input": list(texts)},
                timeout=self._timeout,
            )
        except httpx.HTTPError as error:
            raise EmbeddingsError(
                f"no se pudo hablar con el servicio de embeddings en {self.base_url}: {error}"
            ) from error

        if respuesta.status_code != httpx.codes.OK:
            raise EmbeddingsError(
                f"el servicio de embeddings respondio {respuesta.status_code}:"
                f" {_mensaje_de_error(respuesta)}"
            )

        return _vectores(respuesta, esperados=len(texts))

    def embed_one(self, text: str) -> list[float]:
        """El vector de un solo texto."""
        return self.embed([text])[0]

    def dimension(self) -> int:
        """La dimension que devuelve el modelo servido ahora mismo."""
        return len(self.embed_one("dimension"))


def _mensaje_de_error(respuesta: httpx.Response) -> str:
    try:
        cuerpo = respuesta.json()
    except ValueError:
        return respuesta.text.strip()[:200]
    if isinstance(cuerpo, dict):
        error = cuerpo.get("error")
        if isinstance(error, dict) and "message" in error:
            return str(error["message"])
        if isinstance(error, str):
            return error
    return respuesta.text.strip()[:200]


def _vectores(respuesta: httpx.Response, *, esperados: int) -> list[list[float]]:
    try:
        cuerpo = respuesta.json()
    except ValueError as error:
        raise EmbeddingsError(
            f"respuesta ilegible del servicio de embeddings: {respuesta.text.strip()[:200]}"
        ) from error

    if not isinstance(cuerpo, dict) or not isinstance(cuerpo.get("data"), list):
        raise EmbeddingsError(f"respuesta sin lista 'data': {str(cuerpo)[:200]}")

    entradas: list[Any] = cuerpo["data"]
    if len(entradas) != esperados:
        raise EmbeddingsError(
            f"se pidieron {esperados} vectores y el servicio devolvio {len(entradas)}"
        )

    vectores: list[list[float]] = [[] for _ in range(esperados)]
    for posicion, entrada in enumerate(entradas):
        if not isinstance(entrada, dict):
            raise EmbeddingsError(f"entrada de 'data' que no es un objeto: {str(entrada)[:200]}")
        indice = entrada.get("index", posicion)
        if not isinstance(indice, int) or not 0 <= indice < esperados:
            raise EmbeddingsError(f"indice fuera de rango en la respuesta: {indice!r}")
        vectores[indice] = _vector(entrada.get("embedding"))

    dimensiones = {len(v) for v in vectores}
    if len(dimensiones) > 1:
        raise EmbeddingsError(
            f"el servicio mezclo vectores de dimension distinta: {sorted(dimensiones)}"
        )
    return vectores


def _vector(crudo: Any) -> list[float]:
    if not isinstance(crudo, list) or not crudo:
        raise EmbeddingsError(f"vector vacio o ausente en la respuesta: {str(crudo)[:200]}")
    if isinstance(crudo[0], list):
        raise EmbeddingsError(
            "el servicio devolvio un vector por token en vez de uno por texto:"
            " arranca llama-server con --pooling cls (o mean) para el Modelo de Embeddings"
        )
    try:
        return [float(x) for x in crudo]
    except (TypeError, ValueError) as error:
        raise EmbeddingsError(f"vector con valores no numericos: {str(crudo)[:200]}") from error
