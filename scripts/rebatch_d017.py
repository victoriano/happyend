"""Reorganización única de lotes tras la corrección D-017 (ver scripts/README.md). Ejecutado el 2026-09-29."""
import glob
import json
import shutil
from pathlib import Path

import pandas as pd

import finales.annotation as A

cat = pd.read_csv("data/interim/catalog.csv").set_index("tconst")
sample = pd.read_csv("data/derived/muestra_principal.csv")
films = cat.loc[sample.tconst.unique(), ["primaryTitle", "originalTitle", "enwiki_url"]].reset_index()
orig_dir, tmp = A.ANNOT, Path("data/interim/tmp_annot")
tmp.mkdir(exist_ok=True)
A.ANNOT = tmp
newdf = A.make_batches(films, "principal", batch_size=50)
A.ANNOT = orig_dir
newtext = dict(zip(newdf.id, newdf.sinopsis))
old = {}
for i in range(1, 11):
    f = f"annotation/batches/principal/principal_{i:02d}.jsonl"
    for line in open(f):
        d = json.loads(line)
        old[d["id"]] = (d["sinopsis"], Path(f).stem)
keep = {i for i, (t, b) in old.items() if newtext.get(i) == t}
changed = {i for i, (t, b) in old.items() if i in newtext and newtext[i] != t}
dropped = {i for i in old if i not in newtext}
pending = sorted(set(newtext) - keep)
for f in glob.glob("annotation/batches/principal/principal_1[1-9].jsonl") + glob.glob("annotation/batches/principal/principal_2*.jsonl"):
    Path(f).unlink()
batch_of = {i: old[i][1] for i in keep}
for j in range(0, len(pending), 50):
    name = f"principal_{11 + j // 50:02d}"
    with open(f"annotation/batches/principal/{name}.jsonl", "w", encoding="utf-8") as fh:
        for i in pending[j:j + 50]:
            fh.write(json.dumps({"id": i, "sinopsis": newtext[i]}, ensure_ascii=False) + "\n")
            batch_of[i] = name
key = newdf[["id", "tconst", "palabras_originales", "truncada"]].copy()
key["batch"] = key.id.map(batch_of)
key[["id", "tconst", "batch", "palabras_originales", "truncada"]].to_csv("annotation/claves/principal_key.csv", index=False)
log = pd.DataFrame([{"id": i, "lote_v1": old[i][1], "motivo": "texto de sinopsis corregido (D-017): se reanota"} for i in sorted(changed)]
                   + [{"id": i, "lote_v1": old[i][1], "motivo": "fuera de la muestra tras corrección (D-017): etiqueta descartada"} for i in sorted(dropped)])
log.to_csv("reports/tables/reanotacion_correccion_sinopsis.csv", index=False)
for ann in ("A", "B"):
    for f in glob.glob(f"annotation/labels/principal/{ann}/*.jsonl"):
        lines = [x for x in open(f).read().splitlines() if x.strip()]
        good = [x for x in lines if json.loads(x)["id"] in keep]
        bad = [x for x in lines if json.loads(x)["id"] not in keep]
        if bad:
            Path(f"annotation/labels/principal_obsoletas/{ann}").mkdir(parents=True, exist_ok=True)
            open(f"annotation/labels/principal_obsoletas/{ann}/{Path(f).name}", "w").write("\n".join(bad) + "\n")
            open(f, "w").write("\n".join(good) + "\n")
shutil.rmtree(tmp)
