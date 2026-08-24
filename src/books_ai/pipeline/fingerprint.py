"""Huellas de contenido para los artefactos del pipeline.

La huella de un artefacto es el sha256 de su contenido: es lo que decide si una
etapa tiene que rehacer su trabajo. Calcularla sobre los 92 MB del Corpus en cada
arranque seria caro, asi que se memoriza contra `(tamano, mtime)` y solo se relee
el fichero cuando alguno de los dos cambia.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

_BLOQUE = 1 << 20


class Fingerprints:
    """Huellas de contenido, memorizadas contra el `stat()` de cada fichero."""

    def __init__(self, cache_path: Path | None = None) -> None:
        self._cache_path = cache_path
        self._memo: dict[str, list[object]] = {}
        self._sucio = False
        if cache_path is not None and cache_path.exists():
            try:
                cargado = json.loads(cache_path.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                cargado = {}
            if isinstance(cargado, dict):
                # La cache es una optimizacion, no una fuente de verdad: una entrada
                # con otra forma se descarta y se recalcula, nunca revienta el arranque.
                self._memo = {
                    str(k): list(v)
                    for k, v in cargado.items()
                    if isinstance(v, list) and len(v) == 3
                }

    def of(self, path: Path) -> str | None:
        """La huella del fichero o directorio, o `None` si no existe."""
        if path.is_dir():
            return self._of_directory(path)
        if not path.is_file():
            return None
        return self._of_file(path)

    def save(self) -> None:
        """Vuelca la memoria a disco, si se configuro un fichero de cache."""
        if self._cache_path is None or not self._sucio:
            return
        self._cache_path.parent.mkdir(parents=True, exist_ok=True)
        self._cache_path.write_text(
            json.dumps(self._memo, indent=2, sort_keys=True), encoding="utf-8"
        )
        self._sucio = False

    def forget(self, path: Path) -> None:
        """Olvida lo memorizado de una ruta que se acaba de reescribir.

        La memoria va contra `(tamano, mtime)`, y hay sistemas de ficheros cuya
        resolucion de mtime es mas gruesa que el hueco entre escribir un
        artefacto y volver a medirlo. Sin esto, una reescritura del mismo tamano
        podria devolver la huella anterior y colarse en el recibo.
        """
        self._memo.pop(str(path.resolve()), None)

    def _of_file(self, path: Path) -> str:
        stat = path.stat()
        clave = str(path.resolve())
        recordado = self._memo.get(clave)
        if recordado is not None and recordado[:2] == [stat.st_size, stat.st_mtime_ns]:
            return str(recordado[2])

        digest = hashlib.sha256()
        with path.open("rb") as fichero:
            while bloque := fichero.read(_BLOQUE):
                digest.update(bloque)
        huella = digest.hexdigest()

        self._memo[clave] = [stat.st_size, stat.st_mtime_ns, huella]
        self._sucio = True
        return huella

    def _of_directory(self, path: Path) -> str:
        digest = hashlib.sha256()
        for hijo in sorted(p for p in path.rglob("*") if p.is_file()):
            digest.update(str(hijo.relative_to(path)).encode())
            digest.update(b"\0")
            digest.update(self._of_file(hijo).encode())
            digest.update(b"\0")
        return digest.hexdigest()
