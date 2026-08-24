from __future__ import annotations

import json
from pathlib import Path

import pytest
from pypdf import PdfWriter

from books_ai.corpus import build_pipeline, inventariar, resumir
from books_ai.pipeline import PipelineError, Runner


def escribir_pdf(destino: Path, paginas: int) -> None:
    destino.parent.mkdir(parents=True, exist_ok=True)
    escritor = PdfWriter()
    for _ in range(paginas):
        escritor.add_blank_page(width=200, height=200)
    with destino.open("wb") as fichero:
        escritor.write(fichero)


@pytest.fixture
def books(tmp_path: Path) -> Path:
    raiz = tmp_path / "books"
    escribir_pdf(raiz / "GOT" / "Juego de tronos.pdf", paginas=3)
    escribir_pdf(raiz / "GOT" / "Choque de reyes.pdf", paginas=5)
    escribir_pdf(raiz / "La Tierra Media" / "El Hobbit.pdf", paginas=2)
    return raiz


def test_el_inventario_recoge_cada_pdf_con_sus_paginas(books: Path) -> None:
    inventario = inventariar(books)
    paginas = {f.ruta: f.paginas for f in inventario}
    assert paginas == {
        "GOT/Choque de reyes.pdf": 5,
        "GOT/Juego de tronos.pdf": 3,
        "La Tierra Media/El Hobbit.pdf": 2,
    }


def test_el_inventario_sale_ordenado_y_no_depende_del_orden_del_disco(books: Path) -> None:
    rutas = [f.ruta for f in inventariar(books)]
    assert rutas == sorted(rutas)


def test_el_inventario_ignora_lo_que_no_es_pdf(books: Path) -> None:
    (books / "GOT" / "notas.txt").write_text("no es una Obra")
    assert all(f.ruta.endswith(".pdf") for f in inventariar(books))


def test_un_pdf_ilegible_se_reporta_en_vez_de_contarse_como_cero(books: Path) -> None:
    (books / "GOT" / "roto.pdf").write_bytes(b"esto no es un PDF")
    with pytest.raises(PipelineError, match="roto.pdf"):
        inventariar(books)


def test_un_corpus_sin_pdfs_se_reporta(tmp_path: Path) -> None:
    vacio = tmp_path / "books"
    vacio.mkdir()
    with pytest.raises(PipelineError, match="ning[uú]n PDF"):
        inventariar(vacio)


def test_el_resumen_totaliza_ficheros_y_paginas(books: Path) -> None:
    resumen = resumir(inventariar(books))
    assert "3 ficheros" in resumen
    assert "10 p" in resumen


def test_el_resumen_desglosa_por_carpeta(books: Path) -> None:
    resumen = resumir(inventariar(books))
    assert "GOT" in resumen
    assert "La Tierra Media" in resumen


def test_las_dos_etapas_producen_sus_artefactos(tmp_path: Path, books: Path) -> None:
    pipeline = build_pipeline(tmp_path, books_dir=books)
    Runner(pipeline).run(["resumen-corpus"])

    inventario = json.loads((tmp_path / "artifacts" / "inventario.json").read_text())
    assert inventario["total_paginas"] == 10
    assert len(inventario["ficheros"]) == 3
    assert (tmp_path / "artifacts" / "resumen-corpus.md").read_text().startswith("#")


def test_anadir_una_obra_recalcula_las_dos_etapas(tmp_path: Path, books: Path) -> None:
    pipeline = build_pipeline(tmp_path, books_dir=books)
    runner = Runner(pipeline)
    runner.run(["resumen-corpus"])

    escribir_pdf(books / "La Tierra Media" / "El Silmarillion.pdf", paginas=7)
    resultados = runner.run(["resumen-corpus"])

    assert [r.reused for r in resultados] == [False, False]
    inventario = json.loads((tmp_path / "artifacts" / "inventario.json").read_text())
    assert inventario["total_paginas"] == 17


def test_sin_cambios_no_se_rehace_nada(tmp_path: Path, books: Path) -> None:
    pipeline = build_pipeline(tmp_path, books_dir=books)
    runner = Runner(pipeline)
    runner.run(["resumen-corpus"])
    resultados = runner.run(["resumen-corpus"])
    assert [r.reused for r in resultados] == [True, True]
