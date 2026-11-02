"""Reads the UBU student-survey report (Unidad Técnica de Calidad, one page per subject)."""
import io
import re

import pdfplumber

ITEMS_PRESENCIAL = ["2", "3", "4", "5", "6", "7", "8", "9", "11"]
ITEMS_ONLINE = ["2", "3", "4", "5", "6", "7", "8", "9", "10"]
PAIR = re.compile(r"N:\s*(\d+)\s*Media:\s*(\d+,\d+)")
LABEL = re.compile(r"(?<![\d,])(G|\d{1,2})\.(?=\s*[A-ZÁÉÍÓÚa-z])")


def _num(s):
    return float(s.replace(",", "."))


def _rows(chars, xmin, tol=4.0):
    rows = []
    for c in sorted(chars, key=lambda c: (round(c["top"]), c["x0"])):
        if c["x0"] < xmin or not c["text"].strip():
            continue
        for r in rows:
            if abs(r["top"] - c["top"]) < tol:
                r["chars"].append(c)
                break
        else:
            rows.append({"top": c["top"], "chars": [c]})
    out = []
    for r in rows:
        cs = sorted(r["chars"], key=lambda c: c["x0"])
        s, xs, last = "", [], None
        for c in cs:
            if last is not None and c["x0"] - last > 2.5:
                s += " "
                xs.append(None)
            s += c["text"]
            xs.append(c["x0"])
            last = c["x1"]
        out.append({"top": r["top"], "text": s, "xs": xs})
    return out


def leer_informe(data: bytes) -> dict:
    out = {"asignatura": "", "titulacion": "", "curso": "", "modalidad": "presencial",
           "matriculados": None, "respondidas": None, "participacion": None, "items": {}}
    with pdfplumber.open(io.BytesIO(data)) as pdf:
        page = pdf.pages[0]
        text = page.extract_text() or ""
        rows = _rows(page.chars, xmin=page.width * 0.18)

    def grab(pat, conv=str):
        m = re.search(pat, text)
        return conv(m.group(1).strip()) if m else None

    out["asignatura"] = grab(r"Asignatura:\s*(.+)") or ""
    out["titulacion"] = grab(r"Titulaci[oó]n:\s*(.+)") or ""
    out["curso"] = grab(r"Curso:\s*(\d+)") or ""
    out["matriculados"] = grab(r"Matriculados:\s*(\d+)", int)
    out["respondidas"] = grab(r"respondidas:\s*(\d+)", int)
    out["participacion"] = grab(r"Participaci[oó]n sobre matriculados:\s*(\d+,\d+)", _num)
    if re.search(r"DOCENCIA EN MODALIDAD (ONLINE|SEMIPRESENCIAL|NO PRESENCIAL)", text, re.I):
        out["modalidad"] = "online"

    labels, means = [], []
    for r in rows:
        for m in LABEL.finditer(r["text"]):
            x = next((v for v in r["xs"][m.start():] if v is not None), None)
            if x is not None:
                labels.append((x, r["top"], m.group(1)))
        for m in PAIR.finditer(r["text"]):
            x = next((v for v in r["xs"][m.start():] if v is not None), None)
            if x is not None:
                means.append((x, r["top"], _num(m.group(2))))
    for x, y, v in means:
        cand = [l for l in labels if 0 < y - l[1] < 45 and abs(l[0] - (x - 17)) < 30]
        if cand:
            lab = max(cand, key=lambda l: l[1])
            out["items"][lab[2]] = v
    return out


def media_items(inf: dict):
    keys = ITEMS_ONLINE if inf["modalidad"] == "online" else ITEMS_PRESENCIAL
    vals = [inf["items"][k] for k in keys if k in inf["items"]]
    return (sum(vals) / len(vals), len(vals)) if vals else (None, 0)
