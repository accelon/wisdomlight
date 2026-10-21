"""Build samples/jingang-2016/ from 李慧萍's 2016 thesis appendix.

Input (not in this repo):
  論文附錄(李慧萍0824版).docx

Usage:
  python tools/build_jingang_2016.py --appendix <appendix.docx> [--write]

Without --write it only prints statistics.
"""

import argparse
import json
import re
from collections import Counter
from pathlib import Path

from docx import Document
from docx.oxml.ns import qn
from docx.table import Table
from docx.text.paragraph import Paragraph

CN = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6,
      "七": 7, "八": 8, "九": 9, "十": 10, "十一": 11}

SECTION_TO_SUTRA = {1: 1, 2: 1, 3: 2, 4: 2, 5: 2, 6: 2, 7: 2, 8: 2, 9: 3, 10: 3, 11: 3}


def blocks(doc):
    for child in doc.element.body.iterchildren():
        if child.tag == qn("w:p"):
            yield Paragraph(child, doc)
        elif child.tag == qn("w:tbl"):
            yield Table(child, doc)


def cell_texts(row):
    return [" ".join(c.text.split()) for c in row.cells]


def clean(text):
    return re.sub(r"\s+", "", text or "")


def parse_range(text, prefix):
    m = re.match(rf"^{prefix}(\d+)-(\d+)\s*(.*)$", text, re.S)
    if not m:
        return None
    return int(m.group(1)), int(m.group(2)), clean(m.group(3))


def parse_id_label(text):
    m = re.match(r"^(\d+(?:-\d+)*)\s*(.*)$", text)
    if not m:
        return None
    return m.group(1), clean(m.group(2))


def section_index(paragraph):
    m = re.match(r"^([一二三四五六七八九十]+)、", paragraph)
    if not m:
        return None
    return CN.get(m.group(1))


def build(appendix_path):
    doc = Document(appendix_path)

    # --- appendix 5: section tables + node tables -------------------------
    sections = {}          # n -> {jiang_label, s_range, s_text, e_range}
    nodes = {}             # id -> {label, e_range, e_text, path}
    labels = {}            # id -> label (deepest occurrence)
    app = None
    section = None
    for b in blocks(doc):
        if isinstance(b, Paragraph):
            t = b.text.strip()
            m = re.match(r"^附錄([一二三四五六七八])", t)
            if m:
                app = m.group(1)
                continue
            if app == "五":
                n = section_index(t)
                if n:
                    section = n
            continue
        if app != "五" or not b.rows:
            continue
        rows = [cell_texts(r) for r in b.rows]
        header = " ".join(rows[0])
        is_section_table = "金剛經（S）" in header or any(c.startswith("S") for c in rows[0])
        if is_section_table:
            if section is None:
                continue
            for row in rows[1:]:
                s = next((x for x in row if re.match(r"^S\d+-\d+", x)), None)
                e = next((x for x in row if re.match(r"^E\d+-\d+", x)), None)
                if not s or not e:
                    continue
                sr = parse_range(s, "S")
                er = parse_range(e, "E")
                if not sr or not er:
                    continue
                # deepest non-empty label before S
                idx = row.index(s)
                label = next((x for x in reversed(row[:idx]) if x), "")
                sections[section] = {
                    "jiang_label": clean(label),
                    "s_start": sr[0], "s_end": sr[1], "s_text": sr[2],
                    "e_start": er[0], "e_end": er[1],
                }
        else:
            for row in rows[1:]:
                e = next((x for x in row if re.match(r"^E\d+-\d+", x)), None)
                if not e:
                    continue
                eidx = row.index(e)
                path = [x for x in row[:eidx] if x]
                if not path:
                    continue
                deepest = parse_id_label(path[-1])
                if not deepest:
                    continue
                nid, label = deepest
                er = parse_range(e, "E")
                if not er:
                    continue
                for p in path:
                    pl = parse_id_label(p)
                    if pl:
                        labels.setdefault(pl[0], pl[1])
                nodes[nid] = {
                    "label": label,
                    "e_start": er[0], "e_end": er[1], "e_text": er[2],
                    "path": [parse_id_label(p)[0] for p in path if parse_id_label(p)],
                }

    # Recompute E ranges from the transcribed text so that range length == text
    # length. The thesis's own E numbers are kept as e_start/e_end and compared
    # in checks.tsv.
    cum = 0
    for nid, nd in sorted(nodes.items(), key=lambda kv: kv[1]["e_start"]):
        nd["new_e_start"] = cum + 1
        cum += len(nd["e_text"])
        nd["new_e_end"] = cum

    # --- appendix 7: questions and answers --------------------------------
    questions = []
    answers = []
    app = None
    qsection = None
    current_q = None
    for b in blocks(doc):
        if isinstance(b, Paragraph):
            t = b.text.strip()
            m = re.match(r"^附錄([一二三四五六七八])", t)
            if m:
                app = m.group(1)
                continue
            if app == "七":
                n = section_index(t)
                if n:
                    qsection = n
            continue
        if app != "七" or qsection is None or not b.rows:
            continue
        for row in [cell_texts(r) for r in b.rows]:
            if not row or not row[0] or row[0].startswith("文義思考問題"):
                continue
            qtext = row[0]
            m = re.match(r"^(\d+)\.\s*(.*)$", qtext)
            if m:
                num = int(m.group(1))
                text = clean(m.group(2))
                same = (current_q is not None
                        and current_q["section"] == qsection
                        and current_q["order"] == num
                        and current_q["text"] == text)
                if not same:
                    current_q = {
                        "order": num,
                        "text": text,
                        "section": qsection,
                        "answers": [],
                    }
                    questions.append(current_q)
            if len(row) < 2:
                continue
            aid = parse_id_label(row[1])
            if not aid or current_q is None:
                continue
            current_q["answers"].append(aid[0])

    # --- derive anchors ---------------------------------------------------
    # top sections 1..11
    all_ids = set(nodes) | set(labels) | {str(i) for i in range(1, 12)}
    # make sure every prefix of every node id exists (some tables omit a parent row)
    for nid in list(nodes):
        parts = nid.split("-")
        for i in range(1, len(parts)):
            all_ids.add("-".join(parts[:i]))
    parents = {}
    for nid in all_ids:
        if "-" in nid:
            parents[nid] = nid.rsplit("-", 1)[0]
        else:
            parents[nid] = None

    def has_children(nid):
        return any(x != nid and x.startswith(nid + "-") for x in all_ids)

    def sort_key(nid):
        return tuple(int(x) for x in nid.split("-"))

    anchors = []
    anchors.append({"id": "jjn", "parent": "", "kind": "workgroup",
                    "label": "金剛般若波羅蜜經講義（江味農）", "order": 0, "note": "根"})
    anchors.append({"id": "vcpp", "parent": "", "kind": "workgroup",
                    "label": "金剛般若波羅蜜經（羅什譯；2011 版文字）", "order": 0, "note": "根"})
    sutra_labels = {1: "法會因由分第一", 2: "善現起請分第二", 3: "大乘正宗分第三"}
    for i in (1, 2, 3):
        anchors.append({"id": f"vcpp/{i}", "parent": "vcpp", "kind": "sutra",
                        "label": sutra_labels[i], "order": i, "note": "經文段"})
    # sutra ranges: S1-86, S87-273, S274-412
    sutra_bounds = {1: (1, 86), 2: (87, 273), 3: (274, 412)}

    for n in range(1, 12):
        s = sections[n]
        kids = [k for nid, k in nodes.items() if nid.startswith(f"{n}-")]
        e_note = (f"E{min(k['new_e_start'] for k in kids)}-{max(k['new_e_end'] for k in kids)}"
                  if kids else f"E{s['e_start']}-{s['e_end']}")
        anchors.append({"id": f"jjn/{n}", "parent": "jjn", "kind": "section",
                        "label": s["jiang_label"], "order": n,
                        "note": f"S{s['s_start']}-{s['s_end']}；{e_note}"})
    for nid in sorted([x for x in all_ids if "-" in x], key=sort_key):
        kind = "structure" if has_children(nid) else "unit"
        label = labels.get(nid) or nodes.get(nid, {}).get("label") or nid
        note = (f"E{nodes[nid]['new_e_start']}-{nodes[nid]['new_e_end']}"
                if nid in nodes else "結構節點")
        anchors.append({"id": f"jjn/{nid}", "parent": f"jjn/{nid.rsplit('-', 1)[0]}",
                        "kind": kind, "label": f"{nid} {label}".strip(),
                        "order": int(nid.split("-")[-1]), "note": note})

    # labels: 昭明 on sutra, 江味農 + 李慧萍 on commentary
    label_rows = []
    for i in (1, 2, 3):
        label_rows.append((f"vcpp/{i}", "zhaoming", sutra_labels[i], i,
                           "person:zhaoming", "PD", "表 3-3"))
    for n in range(1, 12):
        s = sections[n]
        label_rows.append((f"jjn/{n}", "jiang-weinong", s["jiang_label"], n,
                           "person:jiang-weinong", "PD", "表 3-4"))
        lee = labels.get(str(n), "")
        label_rows.append((f"jjn/{n}", "lee-huiping", f"{n} {lee}".strip(), n,
                           "person:lee-huiping", "CC-BY-SA-4.0", "附錄五"))
    for nid in sorted([x for x in all_ids if "-" in x], key=sort_key):
        label_rows.append((f"jjn/{nid}", "lee-huiping",
                           f"{nid} {labels.get(nid) or nid}".strip(),
                           int(nid.split("-")[-1]),
                           "person:lee-huiping", "CC-BY-SA-4.0", "附錄五"))

    # anchor_map: 11 section S spans + 193 unit E spans
    span_rows = []
    for n in range(1, 12):
        s = sections[n]
        span_rows.append((f"jjn/{n}", "JJN.2011", "char", s["s_start"], s["s_end"],
                          s["s_end"] - s["s_start"] + 1, s["s_text"]))
    for nid, nd in nodes.items():
        span_rows.append((f"jjn/{nid}", "JJN.2011", "char", nd["new_e_start"], nd["new_e_end"],
                          nd["new_e_end"] - nd["new_e_start"] + 1, nd["e_text"]))

    # sutra spans: concatenate section S text
    for i in (1, 2, 3):
        parts = [sections[n]["s_text"] for n in range(1, 12) if SECTION_TO_SUTRA[n] == i]
        start, end = sutra_bounds[i]
        span_rows.append((f"vcpp/{i}", "JJN.2011", "char", start, end, end - start + 1,
                          "".join(parts)))

    # checks: thesis E length vs transcribed text length, with recomputed ranges
    checks_rows = []
    for nid, nd in nodes.items():
        want = nd["e_end"] - nd["e_start"] + 1
        got = len(nd["e_text"])
        checks_rows.append((f"jjn/{nid}", nd["e_start"], nd["e_end"], want, got,
                            nd["new_e_start"], nd["new_e_end"], got,
                            "ok" if got == want else "adjusted",
                            "相符" if got == want else "論文 E 範圍與文字長度不符；已依文字重算"))

    works_rows = [
        ("JJN.2011", "江味農", "金剛般若波羅蜜經講義", "2011 修訂版（佛陀教育基金會）",
         "partial", "S1-412、E1-27904（依文字重算）", "PD",
         "江味農文本公有領域；引用時註明出處（頁 11–13、128–194）。"),
        ("JJN.B23", "江味農", "金剛般若波羅蜜經講義", "CBETA 大藏經補編 No.23",
         "full", "全文 36.5 萬字（sources/）", "non-commercial",
         "第二見證；標點與 2011 版不同，不可直接套用 E 字碼。"),
    ]

    # edges: jjn/n annotates vcpp/x
    edges = []
    for n in range(1, 12):
        edges.append((f"e-jjn-{n:04d}", f"jjn/{n}", "annotates", f"vcpp/{SECTION_TO_SUTRA[n]}",
                      "actor:me", "actor:me", "draft",
                      f"S{sections[n]['s_start']}-{sections[n]['s_end']}",
                      "江味農科判節點對應經文"))

    # questions / answers with ids
    qrows = []
    arows = []
    qid = 0
    aid = 0
    for q in questions:
        qid += 1
        q["id"] = f"q-{qid:04d}"
        qrows.append(q)
        for order, an in enumerate(q["answers"], 1):
            aid += 1
            if an in nodes:
                ev = f"E{nodes[an]['new_e_start']}-{nodes[an]['new_e_end']}"
            elif an.isdigit() and int(an) in sections:
                kids = [nd for nid, nd in nodes.items() if nid.startswith(an + "-")]
                ev = (f"E{min(k['new_e_start'] for k in kids)}-{max(k['new_e_end'] for k in kids)}"
                      if kids else "")
            else:
                kids = [nd for nid, nd in nodes.items() if nid.startswith(an + "-")]
                ev = (f"E{min(k['new_e_start'] for k in kids)}-{max(k['new_e_end'] for k in kids)}"
                      if kids else "")
            arows.append((f"a-{aid:04d}", q["id"], f"jjn/{an}", order, ev,
                          labels.get(an, "")))
    stats = {
        "sections": len(sections),
        "nodes": len(nodes),
        "anchors": len(anchors),
        "labels": len(label_rows),
        "spans": len(span_rows),
        "edges": len(edges),
        "questions": len(qrows),
        "answers": len(arows),
        "e_text_chars": sum(len(nd["e_text"]) for nd in nodes.values()),
        "s_text_chars": sum(len(s["s_text"]) for s in sections.values()),
        "depth": Counter(n.count("-") + 1 for n in nodes),
        "anchors_by_kind": Counter(a["kind"] for a in anchors),
    }
    return {
        "sections": sections, "nodes": nodes, "labels": labels,
        "anchors": anchors, "label_rows": label_rows, "span_rows": span_rows,
        "checks_rows": checks_rows, "works_rows": works_rows,
        "edges": edges, "questions": qrows, "answers": arows, "stats": stats,
    }


def write(out_dir, data):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    def tsv(name, header, rows):
        with open(out / name, "w", encoding="utf-8", newline="\n") as f:
            f.write("# " + "\t".join(header) + "\n")
            for r in rows:
                cells = [str(x).replace("\t", " ").replace("\n", " ") for x in r]
                f.write("\t".join(cells) + "\n")

    tsv("anchors.tsv", ["anchor", "parent", "kind", "label", "order", "note"],
        [(a["id"], a["parent"], a["kind"], a["label"], a["order"], a["note"]) for a in data["anchors"]])
    tsv("labels.tsv", ["anchor", "vocabulary", "label", "order", "said_by", "license", "source"],
        data["label_rows"])
    tsv("anchor_map.tsv", ["anchor", "edition", "space", "start", "end", "chars", "text"],
        data["span_rows"])
    tsv("edges.tsv", ["id", "from", "kind", "to", "said_by", "recorded_by", "status", "evidence", "note"],
        data["edges"])
    tsv("answers.tsv", ["id", "question", "anchor", "order", "evidence", "note"],
        data["answers"])
    tsv("checks.tsv", ["anchor", "thesis_start", "thesis_end", "thesis_chars",
                       "text_chars", "start", "end", "chars", "status", "note"],
        data["checks_rows"])
    tsv("works.tsv", ["edition", "author", "title", "basis", "extent", "covered", "license", "note"],
        data["works_rows"])

    with open(out / "questions.jsonl", "w", encoding="utf-8", newline="\n") as f:
        for q in data["questions"]:
            obj = {
                "schema": "question/0.1",
                "id": q["id"],
                "text": q["text"],
                "asked_by": "person:lee-huiping",
                "scope_anchor": f"jjn/{q['section']}",
                "order_in_section": q["order"],
                "status": "draft",
                "license": "CC-BY-SA-4.0",
                "source": "李慧萍 2016 論文附錄七",
                "date": "2026-10-21",
            }
            f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--appendix", default="論文附錄(李慧萍0824版).docx")
    ap.add_argument("--out", default="samples/jingang-2016")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    data = build(args.appendix)
    st = data["stats"]
    print("sections:", st["sections"])
    print("nodes:", st["nodes"], "depth:", dict(st["depth"]))
    print("anchors:", st["anchors"], dict(st["anchors_by_kind"]))
    print("labels:", st["labels"], "spans:", st["spans"], "edges:", st["edges"])
    print("questions:", st["questions"], "answers:", st["answers"])
    print("E text chars:", st["e_text_chars"], "(transcribed text; thesis says 27902)")
    print("S text chars:", st["s_text_chars"], "(expected 412)")

    # coverage (recomputed ranges)
    er = sorted((nd["new_e_start"], nd["new_e_end"]) for nd in data["nodes"].values())
    gaps = []
    prev = 0
    for s, e in er:
        if s != prev + 1:
            gaps.append((prev + 1, s - 1))
        prev = e
    print("E gaps:", gaps, "E end:", prev)
    sr = sorted((s["s_start"], s["s_end"]) for s in data["sections"].values())
    gaps = []
    prev = 0
    for s, e in sr:
        if s != prev + 1:
            gaps.append((prev + 1, s - 1))
        prev = e
    print("S gaps:", gaps, "S end:", prev)

    # answer anchors
    anchor_ids = {a["id"] for a in data["anchors"]}
    bad = [a for a in data["answers"] if a[2] not in anchor_ids]
    print("answers with unknown anchor:", len(bad), bad[:5])
    q_without = [q for q in data["questions"] if not q["answers"]]
    print("questions without answers:", len(q_without))

    # debug: expected 29 structure nodes
    d2p = {n.rsplit("-", 1)[0] for n in data["nodes"] if n.count("-") == 2}
    struct = {a["id"].split("/", 1)[1] for a in data["anchors"] if a["kind"] == "structure"}
    print("d2 parents:", len(d2p), "structure anchors:", len(struct),
          "missing:", sorted(d2p - struct), "extra:", sorted(struct - d2p))

    # debug: thesis E length vs transcribed text
    mism = []
    for nid, nd in data["nodes"].items():
        want = nd["e_end"] - nd["e_start"] + 1
        got = len(nd["e_text"])
        if got != want:
            mism.append((nid, want, got, nd["new_e_start"], nd["new_e_end"]))
    print("thesis E length mismatches:", len(mism))
    for m in mism[:10]:
        print("  ", m)

    # debug: answers per question
    counts = Counter(a[1] for a in data["answers"])
    print("answer count distribution:", Counter(counts.values()))

    if args.write:
        write(args.out, data)
        print("written to", args.out)


if __name__ == "__main__":
    main()
