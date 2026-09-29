"""Preparación de lotes cegados, validación de etiquetas, acuerdo y adjudicación."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from . import blinding
from .config import ANNOT, INTERIM, load
from .wikidump import SYN_DIR

CATS = {
    "final": ["FELIZ", "AGRIDULCE", "AMBIGUO", "TRAGICO", "NO_CLASIFICABLE"],
    "supervivencia": ["SOBREVIVE", "MUERE", "MIXTO", "NO_CLARO"],
    "objetivo": ["LOGRADO", "PARCIAL", "NO_LOGRADO", "NO_CLARO"],
    "relaciones": ["FORTALECIDAS", "MIXTAS", "ROTAS", "NO_APLICA", "NO_CLARO"],
    "justicia_narrativa": ["SI", "PARCIAL", "NO", "NO_APLICA", "NO_CLARO"],
    "tono_cierre": ["ESPERANZA", "ALIVIO", "CONEXION", "RESIGNACION", "DESESPERANZA", "NO_CLARO"],
}
ITEMS = ["agencia", "cambio", "vinculos", "futuro"]
BOOLS = ["describe_final", "reconocida"]
ORDINAL_FINAL = ["FELIZ", "AGRIDULCE", "AMBIGUO", "TRAGICO"]  # orden de valencia para kappa ponderada
KEY_DIR = INTERIM / "keys"


def load_synopsis(tconst: str) -> dict | None:
    p = SYN_DIR / f"{tconst}.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def synopsis_ok(tconst: str, min_words: int) -> bool:
    rec = load_synopsis(tconst)
    return bool(rec and rec.get("text") and len(rec["text"].split()) >= min_words)


def make_batches(films: pd.DataFrame, stage: str, batch_size: int = 40) -> pd.DataFrame:
    """Crea lotes cegados en annotation/batches/{stage}/ y la clave id→tconst en data/interim/keys/.

    `films` necesita columnas tconst, primaryTitle, originalTitle, enwiki_url.
    """
    cfg = load()
    seed, maxw = cfg["project"]["seed"], cfg["sinopsis"]["max_palabras_anotacion"]
    out_dir = ANNOT / "batches" / stage
    out_dir.mkdir(parents=True, exist_ok=True)
    KEY_DIR.mkdir(parents=True, exist_ok=True)
    recs = []
    for r in films.itertuples():
        syn = load_synopsis(r.tconst)
        titles = blinding.title_variants(r.primaryTitle, r.originalTitle,
                                         r.enwiki_url.rsplit("/wiki/", 1)[-1] if isinstance(r.enwiki_url, str) else None)
        text = blinding.mask(syn["text"], titles)
        text, trunc = blinding.truncate_words(text, maxw)
        recs.append({"id": blinding.blind_id(r.tconst, seed), "tconst": r.tconst, "sinopsis": text,
                     "palabras_originales": len(syn["text"].split()), "truncada": trunc})
    df = pd.DataFrame(recs).sort_values("id").reset_index(drop=True)  # orden por id cegado = mezcla cohortes
    df["batch"] = [f"{stage}_{i // batch_size + 1:02d}" for i in range(len(df))]
    for b, g in df.groupby("batch"):
        with open(out_dir / f"{b}.jsonl", "w", encoding="utf-8") as fh:
            for x in g.itertuples():
                fh.write(json.dumps({"id": x.id, "sinopsis": x.sinopsis}, ensure_ascii=False) + "\n")
    df[["id", "tconst", "batch", "palabras_originales", "truncada"]].to_csv(KEY_DIR / f"{stage}_key.csv", index=False)
    return df


def _coerce_item(v):
    if v is None or (isinstance(v, str) and v.strip().lower() in ("", "null", "na", "none")):
        return np.nan
    v = float(v)
    if v not in (-2, -1, 0, 1, 2):
        raise ValueError(f"ítem fuera de rango: {v}")
    return v


def validate_record(rec: dict) -> list[str]:
    errs = []
    if not isinstance(rec.get("id"), str):
        errs.append("id ausente")
    for k, allowed in CATS.items():
        if rec.get(k) not in allowed:
            errs.append(f"{k}={rec.get(k)!r} no permitido")
    for k in ITEMS:
        try:
            _coerce_item(rec.get(k))
        except (TypeError, ValueError):
            errs.append(f"{k}={rec.get(k)!r} fuera de escala")
    for k in BOOLS:
        if not isinstance(rec.get(k), bool):
            errs.append(f"{k} no booleano")
    if rec.get("confianza") not in (1, 2, 3):
        errs.append("confianza no válida")
    return errs


def load_labels(paths: list[Path], annotator: str) -> tuple[pd.DataFrame, list[str]]:
    rows, errors = [], []
    for p in paths:
        for ln, line in enumerate(Path(p).read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError as e:
                errors.append(f"{p.name}:{ln} JSON inválido: {e}")
                continue
            errs = validate_record(rec)
            if errs:
                errors.append(f"{p.name}:{ln} {rec.get('id')}: {'; '.join(errs)}")
                continue
            for k in ITEMS:
                rec[k] = _coerce_item(rec.get(k))
            rec["annotator"] = annotator
            rows.append(rec)
    df = pd.DataFrame(rows)
    if not df.empty and df["id"].duplicated().any():
        dups = df.loc[df["id"].duplicated(), "id"].tolist()
        errors.append(f"ids duplicados: {dups[:10]}")
        df = df.drop_duplicates("id", keep="first")
    return df, errors


def vision_score(df: pd.DataFrame, min_items: int = 3) -> pd.Series:
    vals = df[ITEMS].astype(float)
    ok = vals.notna().sum(axis=1) >= min_items
    return vals.mean(axis=1).where(ok)


def pair(a: pd.DataFrame, b: pd.DataFrame) -> pd.DataFrame:
    return a.merge(b, on="id", suffixes=("_A", "_B"), how="outer", indicator=True)


def disagreements(pr: pd.DataFrame, item_gap: int = 3) -> pd.DataFrame:
    """Películas que requieren adjudicación: cualquier categórica distinta o ítem con diferencia ≥ item_gap."""
    mask = pd.Series(False, index=pr.index)
    for k in CATS:
        mask |= pr[f"{k}_A"] != pr[f"{k}_B"]
    for k in ITEMS:
        mask |= (pr[f"{k}_A"] - pr[f"{k}_B"]).abs() >= item_gap
        mask |= pr[f"{k}_A"].isna() ^ pr[f"{k}_B"].isna()
    return pr[mask & (pr["_merge"] == "both")]


def make_adjudication_batch(pr: pd.DataFrame, stage: str, batch_texts: dict[str, str], seed: int,
                            batch_size: int = 40) -> pd.DataFrame:
    """Lotes para el adjudicador: sinopsis + dos etiquetas anónimas (orden X/Y aleatorizado por película)."""
    rng = np.random.default_rng(seed)
    dis = disagreements(pr)
    out_dir = ANNOT / "batches" / f"{stage}_adjudicacion"
    out_dir.mkdir(parents=True, exist_ok=True)
    fields = list(CATS) + ITEMS + ["nota"]
    rows = []
    for i, r in enumerate(dis.itertuples(index=False)):
        rd = r._asdict()
        la = {k: rd[f"{k}_A"] for k in fields}
        lb = {k: rd[f"{k}_B"] for k in fields}
        for d in (la, lb):
            for k in ITEMS:
                d[k] = None if pd.isna(d[k]) else int(d[k])
        swap = bool(rng.integers(0, 2))
        x, y = (lb, la) if swap else (la, lb)
        diff = [k for k in list(CATS) + ITEMS
                if not (la[k] == lb[k] or (k in ITEMS and la[k] is not None and lb[k] is not None
                                            and abs(la[k] - lb[k]) < 3))]
        rows.append({"id": rd["id"], "sinopsis": batch_texts[rd["id"]], "etiqueta_X": x, "etiqueta_Y": y,
                     "campos_en_desacuerdo": diff, "_swap": swap, "_batch": f"{stage}_adj_{i // batch_size + 1:02d}"})
    df = pd.DataFrame(rows)
    for b, g in df.groupby("_batch") if not df.empty else []:
        with open(out_dir / f"{b}.jsonl", "w", encoding="utf-8") as fh:
            for rec in g.drop(columns=["_swap", "_batch"]).to_dict("records"):
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    if not df.empty:
        df[["id", "_swap", "_batch"]].to_csv(KEY_DIR / f"{stage}_adjudicacion_key.csv", index=False)
    return df


def finalize(pr: pd.DataFrame, adj: pd.DataFrame | None) -> pd.DataFrame:
    """Etiqueta final: acuerdo → valor común; desacuerdo categórico → adjudicador;
    ítems → media de A y B salvo que difieran ≥3 (o uno sea nulo), en cuyo caso decide el adjudicador."""
    both = pr[pr["_merge"] == "both"].copy()
    adj = adj.set_index("id") if adj is not None and not adj.empty else pd.DataFrame()
    out = pd.DataFrame({"id": both["id"].values})
    src = []
    for k in CATS:
        vals, s = [], []
        for r in both.itertuples(index=False):
            a, b = getattr(r, f"{k}_A"), getattr(r, f"{k}_B")
            if a == b:
                vals.append(a)
                s.append("acuerdo")
            elif r.id in adj.index and k in adj.columns and pd.notna(adj.at[r.id, k]):
                vals.append(adj.at[r.id, k])
                s.append("adjudicado")
            else:
                vals.append(None)
                s.append("sin_resolver")
        out[k] = vals
        out[f"{k}_fuente"] = s
    for k in ITEMS:
        vals = []
        for r in both.itertuples(index=False):
            a, b = getattr(r, f"{k}_A"), getattr(r, f"{k}_B")
            if pd.notna(a) and pd.notna(b) and abs(a - b) < 3:
                vals.append((a + b) / 2)
            elif r.id in adj.index and k in adj.columns:
                v = adj.at[r.id, k]
                vals.append(np.nan if v is None or pd.isna(v) else float(v))
            else:
                vals.append(np.nan)
        out[k] = vals
    for k in BOOLS:
        out[f"{k}_A"] = both[f"{k}_A"].values
        out[f"{k}_B"] = both[f"{k}_B"].values
    out["reconocida"] = both["reconocida_A"].values | both["reconocida_B"].values
    out["describe_final"] = both["describe_final_A"].values & both["describe_final_B"].values
    out["vision_vida"] = vision_score(out)
    return out


def validate_adjudication(path: Path, batch_path: Path) -> list[str]:
    """Comprueba que cada línea resuelve exactamente los campos en desacuerdo con valores permitidos."""
    need = {}
    for line in Path(batch_path).read_text(encoding="utf-8").splitlines():
        if line.strip():
            d = json.loads(line)
            need[d["id"]] = set(d["campos_en_desacuerdo"])
    errs, seen = [], set()
    for ln, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            d = json.loads(line)
        except json.JSONDecodeError as e:
            errs.append(f"línea {ln}: JSON inválido ({e})")
            continue
        i = d.get("id")
        if i not in need:
            errs.append(f"línea {ln}: id desconocido {i}")
            continue
        seen.add(i)
        missing = need[i] - set(d)
        if missing:
            errs.append(f"{i}: faltan {sorted(missing)}")
        for k in need[i] & set(d):
            v = d[k]
            if k in CATS and v not in CATS[k]:
                errs.append(f"{i}: {k}={v!r} no permitido")
            if k in ITEMS and v is not None and v not in (-2, -1, 0, 1, 2):
                errs.append(f"{i}: {k}={v!r} fuera de escala")
    for i in set(need) - seen:
        errs.append(f"{i}: sin adjudicar")
    return errs
