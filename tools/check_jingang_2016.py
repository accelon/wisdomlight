"""Validate samples/jingang-2016/.

Checks:
  - anchors/labels/spans/edges/questions/answers parse and ids are unique
  - every parent/label/span/answer anchor exists
  - 193 unit E ranges cover 1-27902 without gaps
  - 11 section S ranges cover 1-412 without gaps
  - 151 questions, 278 answers; every question has an answer
  - question counts per section match the thesis (12, 41, 9, 2, 8, 3, 5, 3, 11, 33, 24)
"""

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
D = ROOT / "samples" / "jingang-2016"


def read_tsv(name):
    lines = (D / name).read_text(encoding="utf-8").splitlines()
    header = lines[0].lstrip("# ").split("\t")
    rows = []
    for line in lines[1:]:
        if not line.strip():
            continue
        rows.append(dict(zip(header, line.split("\t"))))
    return rows


def main():
    errors = []
    anchors = read_tsv("anchors.tsv")
    labels = read_tsv("labels.tsv")
    spans = read_tsv("anchor_map.tsv")
    edges = read_tsv("edges.tsv")
    answers = read_tsv("answers.tsv")
    checks = read_tsv("checks.tsv")
    works = read_tsv("works.tsv")
    questions = [json.loads(x) for x in (D / "questions.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]

    ids = [a["anchor"] for a in anchors]
    if len(ids) != len(set(ids)):
        errors.append("duplicate anchor ids")
    aset = set(ids)

    for a in anchors:
        if a["parent"] and a["parent"] not in aset:
            errors.append(f"missing parent: {a['anchor']} -> {a['parent']}")
    for l in labels:
        if l["anchor"] not in aset:
            errors.append(f"label for unknown anchor: {l['anchor']}")
    for s in spans:
        if s["anchor"] not in aset:
            errors.append(f"span for unknown anchor: {s['anchor']}")
    for e in edges:
        if e["from"] not in aset or e["to"] not in aset:
            errors.append(f"edge endpoint missing: {e['id']}")
    for a in answers:
        if a["anchor"] not in aset:
            errors.append(f"answer anchor missing: {a['id']}")

    qids = [q["id"] for q in questions]
    if len(qids) != len(set(qids)):
        errors.append("duplicate question ids")
    qset = set(qids)
    for a in answers:
        if a["question"] not in qset:
            errors.append(f"answer for unknown question: {a['id']}")

    units = [a for a in anchors if a["kind"] == "unit"]
    e_spans = [s for s in spans if s["anchor"] in {a["anchor"] for a in units}]
    er = sorted((int(s["start"]), int(s["end"])) for s in e_spans)
    prev = 0
    for start, end in er:
        if start != prev + 1:
            errors.append(f"E gap {prev + 1}-{start - 1}")
        prev = end
    e_end = prev
    if e_end != 27902:
        errors.append(f"E end {e_end} != 27902")

    s_spans = [s for s in spans if s["anchor"].startswith("jjn/") and s["anchor"].count("-") == 0]
    sr = sorted((int(s["start"]), int(s["end"])) for s in s_spans)
    prev = 0
    for start, end in sr:
        if start != prev + 1:
            errors.append(f"S gap {prev + 1}-{start - 1}")
        prev = end
    if prev != 412:
        errors.append(f"S end {prev} != 412")

    by_section = Counter(q["scope_anchor"] for q in questions)
    expected = {"jjn/1": 12, "jjn/2": 41, "jjn/3": 9, "jjn/4": 2, "jjn/5": 8,
                "jjn/6": 3, "jjn/7": 5, "jjn/8": 3, "jjn/9": 11, "jjn/10": 33, "jjn/11": 24}
    for sec, n in expected.items():
        if by_section.get(sec, 0) != n:
            errors.append(f"section {sec}: {by_section.get(sec, 0)} questions != {n}")

    aq = Counter(a["question"] for a in answers)
    no_answer = [q for q in questions if aq.get(q["id"], 0) == 0]
    if no_answer:
        errors.append(f"questions without answers: {len(no_answer)}")

    empty_labels = [l for l in labels if not l["label"].strip()]
    if empty_labels:
        errors.append(f"empty labels: {len(empty_labels)}")
    empty_evidence = [a for a in answers if not a["evidence"]]
    if empty_evidence:
        errors.append(f"answers without evidence: {len(empty_evidence)}")

    mism = [c for c in checks if c["status"] != "ok"]
    print(f"anchors {len(anchors)}  labels {len(labels)}  spans {len(spans)}  edges {len(edges)}")
    print(f"questions {len(questions)}  answers {len(answers)}  works {len(works)}")
    print(f"E spans {len(e_spans)}  E coverage 1-{e_end}")
    print(f"questions per section: {dict(sorted(by_section.items(), key=lambda kv: int(kv[0].split('/')[1])))}")
    print(f"answer count: {dict(sorted(Counter(aq.values()).items()))}")
    print(f"checks mismatches: {len(mism)}")
    for m in mism:
        print(f"  {m['anchor']} range={m['range_chars']} text={m['text_chars']}")
    if errors:
        print("ERRORS:")
        for e in errors:
            print(" -", e)
        sys.exit(1)
    print("OK")


if __name__ == "__main__":
    main()
