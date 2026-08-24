"""El Modo Consulta no puede depender de PyTorch (ADR-0003).

El entrenamiento vive en otro stack y en otro contenedor. Si PyTorch se cuela en
el entorno de consulta, la separacion se ha roto y nadie se entera hasta que hay
que reproducir el servicio en una maquina limpia.
"""

from __future__ import annotations

import importlib.util
import re
import tomllib
from pathlib import Path

import pytest

PROHIBIDAS = ("torch", "torchvision", "torchaudio", "transformers", "accelerate")


def test_el_entorno_de_consulta_no_trae_pytorch() -> None:
    presentes = [nombre for nombre in PROHIBIDAS if importlib.util.find_spec(nombre) is not None]
    assert presentes == []


def nombre_de(dependencia: str) -> str:
    """El nombre a secas, sea cual sea el operador: `torch<3`, `torch~=2`, `torch[cuda]`."""
    return re.split(r"[<>=!~\[@;\s]", dependencia, maxsplit=1)[0].strip().lower()


@pytest.mark.parametrize(
    "declarada",
    [
        "torch",
        "torch==2.5",
        "torch>=2.5",
        "torch<3",
        "torch~=2.5",
        "torch[cuda]",
        "torch @ http://x",
    ],
)
def test_el_guardia_reconoce_cualquier_forma_de_declarar_torch(declarada: str) -> None:
    assert nombre_de(declarada) in PROHIBIDAS


def test_ninguna_dependencia_declarada_es_de_la_pista_de_entrenamiento() -> None:
    proyecto = tomllib.loads(
        (Path(__file__).parent.parent / "pyproject.toml").read_text(encoding="utf-8")
    )
    declaradas = proyecto["project"]["dependencies"]
    assert [d for d in declaradas if nombre_de(d) in PROHIBIDAS] == []
