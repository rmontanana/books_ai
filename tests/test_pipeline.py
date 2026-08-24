import json
from pathlib import Path

import pytest

from books_ai.pipeline import Pipeline, Runner, StageContext
from books_ai.pipeline.errors import PipelineError
from books_ai.pipeline.fingerprint import Fingerprints


def build_pipeline(root: Path, version: str = "1") -> tuple[Pipeline, list[str]]:
    """Two chained stages over a source file, recording every execution."""
    ejecutadas: list[str] = []
    pipeline = Pipeline(root)
    pipeline.source("fuente", "fuente.txt")
    pipeline.artifact("mayusculas", "artifacts/mayusculas.txt")
    pipeline.artifact("longitud", "artifacts/longitud.txt")

    @pipeline.stage("mayusculas", consumes=["fuente"], produces=["mayusculas"], version=version)
    def _mayusculas(ctx: StageContext) -> None:
        ejecutadas.append("mayusculas")
        ctx.outputs["mayusculas"].write_text(ctx.inputs["fuente"].read_text().upper())

    @pipeline.stage("longitud", consumes=["mayusculas"], produces=["longitud"])
    def _longitud(ctx: StageContext) -> None:
        ejecutadas.append("longitud")
        ctx.outputs["longitud"].write_text(str(len(ctx.inputs["mayusculas"].read_text())))

    return pipeline, ejecutadas


@pytest.fixture
def root(tmp_path: Path) -> Path:
    (tmp_path / "fuente.txt").write_text("hola")
    return tmp_path


def test_a_stage_declares_what_it_consumes_and_produces(root: Path) -> None:
    pipeline, _ = build_pipeline(root)
    etapa = pipeline.stages["longitud"]
    assert etapa.consumes == ("mayusculas",)
    assert etapa.produces == ("longitud",)


def test_running_a_stage_produces_its_artifact(root: Path) -> None:
    pipeline, ejecutadas = build_pipeline(root)
    Runner(pipeline).run(["mayusculas"])
    assert (root / "artifacts" / "mayusculas.txt").read_text() == "HOLA"
    assert ejecutadas == ["mayusculas"]


def test_a_stage_runs_separately_from_the_rest(root: Path) -> None:
    pipeline, ejecutadas = build_pipeline(root)
    Runner(pipeline).run(["mayusculas"])
    assert ejecutadas == ["mayusculas"]
    assert not (root / "artifacts" / "longitud.txt").exists()


def test_rerunning_an_unchanged_stage_reuses_the_cache(root: Path) -> None:
    pipeline, ejecutadas = build_pipeline(root)
    runner = Runner(pipeline)
    runner.run(["mayusculas"])
    outcomes = runner.run(["mayusculas"])
    assert ejecutadas == ["mayusculas"]
    assert [o.reused for o in outcomes] == [True]


def test_a_downstream_stage_pulls_its_upstream(root: Path) -> None:
    pipeline, ejecutadas = build_pipeline(root)
    Runner(pipeline).run(["longitud"])
    assert ejecutadas == ["mayusculas", "longitud"]
    assert (root / "artifacts" / "longitud.txt").read_text() == "4"


def test_changing_the_input_recomputes_the_stage_and_its_dependents(root: Path) -> None:
    pipeline, ejecutadas = build_pipeline(root)
    runner = Runner(pipeline)
    runner.run(["longitud"])
    ejecutadas.clear()

    (root / "fuente.txt").write_text("buenas tardes")
    runner.run(["longitud"])

    assert ejecutadas == ["mayusculas", "longitud"]
    assert (root / "artifacts" / "longitud.txt").read_text() == "13"


def test_invalidating_a_stage_forces_it_and_its_dependents(root: Path) -> None:
    pipeline, ejecutadas = build_pipeline(root)
    runner = Runner(pipeline)
    runner.run(["longitud"])
    ejecutadas.clear()

    assert runner.invalidate("mayusculas") == ["mayusculas", "longitud"]
    runner.run(["longitud"])

    assert ejecutadas == ["mayusculas", "longitud"]


def test_invalidating_a_stage_leaves_its_upstream_alone(root: Path) -> None:
    pipeline, ejecutadas = build_pipeline(root)
    runner = Runner(pipeline)
    runner.run(["longitud"])
    ejecutadas.clear()

    runner.invalidate("longitud")
    runner.run(["longitud"])

    assert ejecutadas == ["longitud"]


def test_a_deleted_output_is_rebuilt(root: Path) -> None:
    pipeline, ejecutadas = build_pipeline(root)
    runner = Runner(pipeline)
    runner.run(["mayusculas"])
    ejecutadas.clear()

    (root / "artifacts" / "mayusculas.txt").unlink()
    runner.run(["mayusculas"])

    assert ejecutadas == ["mayusculas"]


def test_a_new_stage_version_invalidates_the_cache(root: Path) -> None:
    pipeline, ejecutadas = build_pipeline(root)
    Runner(pipeline).run(["mayusculas"])

    otra, otras_ejecutadas = build_pipeline(root, version="2")
    Runner(otra).run(["mayusculas"])

    assert otras_ejecutadas == ["mayusculas"]


def test_force_reruns_a_fresh_stage(root: Path) -> None:
    pipeline, ejecutadas = build_pipeline(root)
    runner = Runner(pipeline)
    runner.run(["mayusculas"])
    runner.run(["mayusculas"], force=True)
    assert ejecutadas == ["mayusculas", "mayusculas"]


def test_status_reports_freshness_per_stage(root: Path) -> None:
    pipeline, _ = build_pipeline(root)
    runner = Runner(pipeline)
    runner.run(["mayusculas"])
    estado = {s.stage: s.fresh for s in runner.status()}
    assert estado == {"mayusculas": True, "longitud": False}


def test_a_missing_source_is_reported_not_swallowed(root: Path) -> None:
    pipeline, _ = build_pipeline(root)
    (root / "fuente.txt").unlink()
    with pytest.raises(PipelineError, match="fuente"):
        Runner(pipeline).run(["mayusculas"])


def test_a_stage_that_does_not_write_its_artifact_is_reported(root: Path) -> None:
    pipeline = Pipeline(root)
    pipeline.source("fuente", "fuente.txt")
    pipeline.artifact("vacio", "artifacts/vacio.txt")

    @pipeline.stage("vago", consumes=["fuente"], produces=["vacio"])
    def _vago(ctx: StageContext) -> None:
        return None

    with pytest.raises(PipelineError, match="vacio"):
        Runner(pipeline).run(["vago"])


def test_consuming_an_undeclared_artifact_is_reported(root: Path) -> None:
    pipeline = Pipeline(root)
    with pytest.raises(PipelineError, match="inexistente"):

        @pipeline.stage("rota", consumes=["inexistente"], produces=[])
        def _rota(ctx: StageContext) -> None:
            return None


def test_two_stages_cannot_produce_the_same_artifact(root: Path) -> None:
    pipeline, _ = build_pipeline(root)
    with pytest.raises(PipelineError, match="mayusculas"):

        @pipeline.stage("duplicada", consumes=["fuente"], produces=["mayusculas"])
        def _duplicada(ctx: StageContext) -> None:
            return None


def test_a_cycle_is_reported(root: Path) -> None:
    pipeline = Pipeline(root)
    pipeline.artifact("a", "artifacts/a.txt")
    pipeline.artifact("b", "artifacts/b.txt")

    @pipeline.stage("ida", consumes=["b"], produces=["a"])
    def _ida(ctx: StageContext) -> None:
        return None

    @pipeline.stage("vuelta", consumes=["a"], produces=["b"])
    def _vuelta(ctx: StageContext) -> None:
        return None

    with pytest.raises(PipelineError, match="[Cc]iclo"):
        Runner(pipeline).run(["ida"])


def test_an_unknown_stage_is_reported(root: Path) -> None:
    pipeline, _ = build_pipeline(root)
    with pytest.raises(PipelineError, match="fantasma"):
        Runner(pipeline).run(["fantasma"])


def test_status_reporta_pendiente_cuando_falta_una_entrada(root: Path) -> None:
    """Mirar el estado nunca revienta: para eso `Pipeline` solo declara."""
    pipeline, _ = build_pipeline(root)
    runner = Runner(pipeline)
    runner.run(["longitud"])

    (root / "artifacts" / "mayusculas.txt").unlink()
    estado = {s.stage: s.fresh for s in runner.status()}

    assert estado == {"mayusculas": False, "longitud": False}


def test_status_reporta_pendiente_cuando_falta_el_origen(root: Path) -> None:
    pipeline, _ = build_pipeline(root)
    runner = Runner(pipeline)
    runner.run(["mayusculas"])

    (root / "fuente.txt").unlink()
    assert [s.fresh for s in runner.status(["mayusculas"])] == [False]


def test_un_fallo_dentro_de_una_etapa_se_reporta_con_su_nombre(root: Path) -> None:
    pipeline = Pipeline(root)
    pipeline.source("fuente", "fuente.txt")
    pipeline.artifact("nada", "artifacts/nada.txt")

    @pipeline.stage("explosiva", consumes=["fuente"], produces=["nada"])
    def _explosiva(ctx: StageContext) -> None:
        raise TypeError("un artefacto con la forma de ayer")

    with pytest.raises(PipelineError, match="explosiva"):
        Runner(pipeline).run(["explosiva"])


def test_una_etapa_reescrita_con_el_mismo_tamano_no_se_da_por_igual(root: Path) -> None:
    """La memoria de huellas va contra (tamano, mtime); una salida recien
    reescrita no puede juzgarse con lo que se recordaba de antes."""
    pipeline = Pipeline(root)
    pipeline.source("fuente", "fuente.txt")
    pipeline.artifact("eco", "artifacts/eco.txt")

    @pipeline.stage("eco", consumes=["fuente"], produces=["eco"])
    def _eco(ctx: StageContext) -> None:
        ctx.outputs["eco"].write_text(ctx.inputs["fuente"].read_text().upper())

    runner = Runner(pipeline)
    runner.run(["eco"])

    (root / "fuente.txt").write_text("adio")  # mismo tamano que "hola"
    runner.run(["eco"])

    assert (root / "artifacts" / "eco.txt").read_text() == "ADIO"
    recibo = json.loads((root / ".cache" / "receipts" / "eco.json").read_text())
    assert recibo["outputs"]["eco"] == Fingerprints().of(root / "artifacts" / "eco.txt")
