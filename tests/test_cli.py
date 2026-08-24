from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner
from pypdf import PdfWriter

from books_ai.cli import main


@pytest.fixture
def proyecto(tmp_path: Path) -> Path:
    libro = tmp_path / "books" / "GOT" / "Juego de tronos.pdf"
    libro.parent.mkdir(parents=True)
    escritor = PdfWriter()
    escritor.add_blank_page(width=200, height=200)
    with libro.open("wb") as fichero:
        escritor.write(fichero)
    return tmp_path


def correr(proyecto: Path, *args: str) -> str:
    resultado = CliRunner().invoke(main, ["--root", str(proyecto), *args])
    assert resultado.exit_code == 0, resultado.output
    return resultado.output


def test_list_muestra_las_etapas_y_su_estado(proyecto: Path) -> None:
    salida = correr(proyecto, "pipeline", "list")
    assert "inventario" in salida
    assert "resumen-corpus" in salida
    assert "pendiente" in salida


def test_run_produce_el_artefacto(proyecto: Path) -> None:
    correr(proyecto, "pipeline", "run", "inventario")
    inventario = json.loads((proyecto / "artifacts" / "inventario.json").read_text())
    assert inventario["total_paginas"] == 1


def test_run_repetido_dice_que_reusa(proyecto: Path) -> None:
    correr(proyecto, "pipeline", "run", "inventario")
    salida = correr(proyecto, "pipeline", "run", "inventario")
    assert "al dia" in salida


def test_run_sin_etapas_corre_el_pipeline_entero(proyecto: Path) -> None:
    correr(proyecto, "pipeline", "run")
    assert (proyecto / "artifacts" / "resumen-corpus.md").exists()


def test_invalidate_arrastra_a_las_dependientes(proyecto: Path) -> None:
    correr(proyecto, "pipeline", "run")
    salida = correr(proyecto, "pipeline", "invalidate", "inventario")
    assert "inventario" in salida
    assert "resumen-corpus" in salida


def test_un_error_del_pipeline_sale_como_fallo_no_como_traza(tmp_path: Path) -> None:
    (tmp_path / "books").mkdir()
    resultado = CliRunner().invoke(main, ["--root", str(tmp_path), "pipeline", "run"])
    assert resultado.exit_code != 0
    assert "PDF" in resultado.output
    assert "Traceback" not in resultado.output


def test_una_etapa_desconocida_sale_como_fallo(proyecto: Path) -> None:
    resultado = CliRunner().invoke(main, ["--root", str(proyecto), "pipeline", "run", "fantasma"])
    assert resultado.exit_code != 0
    assert "fantasma" in resultado.output


def test_se_niega_a_correr_si_el_sistema_de_ficheros_no_es_utf8(
    proyecto: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Un locale heredado corrompe los nombres de Obra acentuados en silencio."""
    monkeypatch.setattr("sys.getfilesystemencoding", lambda: "ISO-8859-1")
    resultado = CliRunner().invoke(main, ["--root", str(proyecto), "pipeline", "run"])
    assert resultado.exit_code != 0
    assert "UTF-8" in resultado.output
    assert "Traceback" not in resultado.output
