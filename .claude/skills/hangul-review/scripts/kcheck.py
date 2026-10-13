#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
kcheck.py — 한글 문장 기계 검사 (hangul-review 스킬)

무엇을 하나
  1) 검사:  끊어 내린 단문(R1·R2) · 이어 쓸 자리(R3) · 토막 문장(R4) · 과개행(R6)
            긴 문장 연쇄(R7) · 명사 조각(R8) · AI 상투어(A1) · 과장 수식(A2) · 자평(A3)
            번역투(A4) · 접속사 남발(A7) · 의인화·기계 주체(M3) · 상용 은유(M7)
            모호한 강도어 · 지시어 오프너(S2) · 말투 혼용(S4) · 시오체 · 오타(O1)
            외래어 표기(O2) · 표기 통일 · 작업 흔적(W7)
  2) 대조:  --compare <원본> <윤문본>  윤문이 만든 손상(P1·P2·P3·P4·P6·P8)을 찾는다

찍힌 자리는 판정이 아니라 사람이 볼 자리다. 개수를 0으로 맞추려고 문장을 고치지 않는다.
주어 누락·비유의 적절성·억지 연결(R5)은 기계가 못 본다 — 검수자가 본다.

사용
  python3 kcheck.py <파일|폴더> [...]          # .html .htm .md .txt
  python3 kcheck.py --compare 원본.html 윤문본.html
  python3 kcheck.py <대상> --json

종료 코드  0 = 🔴 없음 / 1 = 🔴 있음 / 2 = 실행 실패
표준 라이브러리만 쓴다 (설치 불필요, Windows·macOS 공통).
"""
import argparse
import difflib
import json
import os
import re
import sys
from collections import Counter
from html.parser import HTMLParser

HERE = os.path.dirname(os.path.abspath(__file__))
RULES = json.load(open(os.path.join(HERE, "rules.json"), encoding="utf-8"))
RH = RULES["rhythm"]

if os.name == "nt":  # Windows 콘솔 한글 깨짐 방지
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

COLOR = sys.stdout.isatty() and os.environ.get("NO_COLOR") is None
RED, YEL, DIM, GRN, OFF = (("\033[31m", "\033[33m", "\033[2m", "\033[32m", "\033[0m")
                           if COLOR else ("", "", "", "", ""))

HANGUL = re.compile(r"[가-힣]")
SKIP_DIRS = {"node_modules", ".git", "_review", ".claude", ".next", ".vercel", ".cache"}
EXTS = (".html", ".htm", ".md", ".txt")

# ── 텍스트 추출 ────────────────────────────────────────────────────────────
# kind: prose(본문 — 호흡 검사 대상) / label(제목·버튼·라벨·표 칸 — 호흡 검사 제외)
#       attr(alt·title·aria-label) / meta(title·description)

PROSE_TAGS = {"p", "blockquote", "dd", "li", "div", "section", "article", "main",
              "aside", "header", "footer", "body", "figure", "details"}
LABEL_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6", "button", "a", "label", "th", "td",
              "dt", "figcaption", "summary", "caption", "option", "legend", "title"}
LABEL_CONTAINERS = {"nav", "button", "a", "label", "select"}
SKIP_TAGS = {"script", "style", "noscript", "code", "pre", "svg", "template", "textarea"}
TEXT_ATTRS = ("alt", "title", "aria-label", "placeholder")


class _Extractor(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.skip = 0
        self.stack = []
        self.buf, self.line, self.kind, self.breaks = [], None, "prose", 0
        self.blocks = []

    def _kind_now(self):
        if any(t in LABEL_CONTAINERS for t in self.stack):
            return "label"
        for t in reversed(self.stack):
            if t in LABEL_TAGS:
                return "label"
            if t in PROSE_TAGS:
                return "prose"
        return "prose"

    def _flush(self):
        text = re.sub(r"\s+", " ", "".join(self.buf)).strip()
        if text and HANGUL.search(text) or (text and _has_placeholder(text)):
            self.blocks.append({"line": self.line or 0, "kind": self.kind,
                                "text": text, "breaks": self.breaks})
        self.buf, self.line, self.breaks = [], None, 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        for k in TEXT_ATTRS:
            v = (a.get(k) or "").strip()
            if v and (HANGUL.search(v) or _has_placeholder(v)):
                self.blocks.append({"line": self.getpos()[0], "kind": "attr",
                                    "text": v, "breaks": 0, "attr": k})
        if tag == "meta" and (a.get("name") or a.get("property") or "").lower() in (
                "description", "og:description", "og:title", "twitter:description"):
            v = (a.get("content") or "").strip()
            if v:
                self.blocks.append({"line": self.getpos()[0], "kind": "meta",
                                    "text": v, "breaks": 0})
        if tag in SKIP_TAGS:
            self.skip += 1
            return
        if tag == "br":
            self.breaks += 1
            self.buf.append(" ")
            return
        if tag in PROSE_TAGS or tag in LABEL_TAGS or tag in LABEL_CONTAINERS:
            self._flush()
            self.stack.append(tag)
            self.kind = self._kind_now()

    def handle_endtag(self, tag):
        if tag in SKIP_TAGS:
            self.skip = max(0, self.skip - 1)
            return
        if tag in PROSE_TAGS or tag in LABEL_TAGS or tag in LABEL_CONTAINERS:
            self._flush()
            if tag in self.stack:
                idx = len(self.stack) - 1 - self.stack[::-1].index(tag)
                del self.stack[idx:]
            self.kind = self._kind_now()

    def handle_data(self, data):
        if self.skip or not data.strip():
            return
        if self.line is None:
            self.line = self.getpos()[0]
        self.buf.append(data)

    def close(self):
        super().close()
        self._flush()


def extract(path):
    raw = open(path, encoding="utf-8", errors="replace").read()
    if path.lower().endswith((".html", ".htm")):
        ex = _Extractor()
        ex.feed(raw)
        ex.close()
        return ex.blocks, raw
    blocks, line = [], 1
    for chunk in re.split(r"\n[ \t]*\n", raw):
        start = line
        line += chunk.count("\n") + 2
        lines = [l for l in chunk.split("\n") if l.strip()]
        if not lines:
            continue
        first = lines[0].lstrip()
        if first.startswith("#") or first.startswith("|"):
            kind = "label"
        elif re.match(r"^([-*+]|\d+[.)])\s", first):
            for i, l in enumerate(lines):  # 목록 항목은 하나씩
                t = re.sub(r"^\s*([-*+]|\d+[.)])\s+", "", l).strip()
                if t:
                    blocks.append({"line": start + i, "kind": "label" if len(_sentences(t)) < 2 else "prose",
                                   "text": t, "breaks": 0})
            continue
        else:
            kind = "prose"
        text = re.sub(r"\s+", " ", chunk).strip()
        blocks.append({"line": start, "kind": kind, "text": text, "breaks": len(lines) - 1})
    return blocks, raw


# ── 문장 단위 도구 ──────────────────────────────────────────────────────────

def _sentences(text):
    text = re.sub(r"\.(?=[가-힣])", ". ", text)       # "했다.그래서" 도 경계로
    parts = re.split(r"(?<=[.!?…])\s+", text)
    return [p.strip() for p in parts if p.strip()]


def _clean(s):
    return s.strip().rstrip(".!?…\"'”’)").strip()


def _ending_kind(s):
    t = _clean(s)
    if t.endswith(("까요", "나요", "가요", "습니까", "을까", "ㄹ까")) or s.rstrip().endswith("?"):
        return "question"
    if t.endswith(("세요", "주세요", "십시오", "시죠", "봐요", "해요 ")):
        return "request"
    if t.endswith("습니다"):
        return "past" if len(t) > 3 and t[-4] in "았었였했" else "present"
    if t.endswith("니다"):
        return "present"
    if t.endswith("요"):
        return "past" if len(t) > 1 and t[-2] in "았었였했" else "present"
    if t.endswith("다"):
        return "past" if len(t) > 1 and t[-2] in "았었였했" else "present"
    return "other"


def _is_decl(s):
    return re.search(r"(다|요)[.!?…]?[\"'”’)]*$", s.strip()) is not None


VERB_END = set("다요죠까네지라자오게군데걸니나음함됨임봄")


def _noun_fragment(s):
    t = s.strip()
    if not t.endswith(".") or not HANGUL.search(t):
        return False
    core = _clean(t)
    return bool(core) and HANGUL.match(core[-1]) and core[-1] not in VERB_END and len(core) <= 20


KO_NUM = (r"(?<![가-힣])(?:한|두|세|네|다섯|여섯|일곱|여덟|아홉|열|열한|열두|스무|서른|마흔|쉰|첫)\s?"
          r"(?:곳|개|명|번|달|주|권|장|편|가지|차례|배|살|시|시간|해|군데|분|잔|벌|쪽|팀|건|작품|프로젝트|째|번째)")


def _has_placeholder(text):
    return any(re.search(p, text) for p in RULES["w7_placeholders"])


def _short(s, n):
    return s if len(s) <= n else s[: n - 1] + "…"


# ── 검사 ───────────────────────────────────────────────────────────────────

def check_blocks(blocks, raw):
    out = []

    def hit(b, rid, level, msg):
        out.append({"line": b["line"], "id": rid, "level": level, "msg": msg, "kind": b["kind"]})

    file_text = " ".join(b["text"] for b in blocks)

    for b in blocks:
        text, sents = b["text"], _sentences(b["text"])
        prose = b["kind"] == "prose" and len(sents) >= 2

        if prose:
            flagged = set()
            # R2 스타카토 — 25자 이하 3연속
            run = []
            for i, s in enumerate(sents + [""]):
                if s and HANGUL.search(s) and len(_clean(s)) <= RH["r2_max_len"]:
                    run.append(i)
                    continue
                if len(run) >= 3:
                    flagged.update(run)
                    hit(b, "R2", "error", "스타카토 — 25자 이하 %d연속: 「%s」" %
                        (len(run), " ".join(sents[j] for j in run)))
                run = []
            if len(sents) >= 3 and not flagged:
                avg = sum(len(_clean(s)) for s in sents) / len(sents)
                if avg < RH["r2_max_len"]:
                    flagged.update(range(len(sents)))
                    hit(b, "R2", "error", "스타카토 — 문장 %d개 평균 %.0f자: 「%s」" %
                        (len(sents), avg, _short(text, 70)))
            # R1 연속 단문 — 20자 이하 서술문 2연속 (김자매 기준과 같게)
            run = []
            for i, s in enumerate(sents + [""]):
                if s and i not in flagged and _is_decl(s) and len(_clean(s)) <= RH["r1_max_len"]:
                    run.append(i)
                    continue
                if len(run) >= 2:
                    flagged.update(run)
                    hit(b, "R1", "error", "연속 단문 — 짧은 서술문 %d개: 「%s」" %
                        (len(run), " ".join(sents[j] for j in run)))
                run = []
            # R3 이어 쓸 자리 / R4 토막
            for i in range(len(sents) - 1):
                a, c = sents[i], sents[i + 1]
                if i in flagged or i + 1 in flagged:
                    continue
                la, lc = len(_clean(a)), len(_clean(c))
                ka = _ending_kind(a)
                if ka not in ("past", "present") or ka != _ending_kind(c):
                    continue
                if la <= RH["r3_max_each"] and lc <= RH["r3_max_each"] and la + lc <= RH["r3_max_sum"]:
                    hit(b, "R3", "warn", "이어 쓸 자리 — 같은 종결 계열 두 문장: 「%s %s」 "
                        "(이어 읽는 게 나으면 한 문장으로. 관계가 없으면 억지로 잇지 않는다 · 강조용 끊음이면 그대로 — 개수를 0으로 맞추지 않는다)" % (a, c))
                elif len(sents) >= 3 and i >= 1 and la <= RH["r4_max_len"]:
                    hit(b, "R4", "warn", "토막 문장 — 문단 중간 단문: 「%s」 뒤 「%s」" %
                        (a, _short(c, 30)))
            # R7 긴 문장 연쇄
            run = 0
            for s in sents:
                run = run + 1 if len(_clean(s)) >= RH["r7_min_len"] else 0
                if run == 3:
                    hit(b, "R7", "warn", "60자 넘는 문장 3연속 — 한 문장이 여러 가지를 요약하고 있지 않은지")
            # R8 명사 조각
            for s in sents[:-1]:
                if _noun_fragment(s):
                    hit(b, "R8", "warn", "명사로 끊어 낸 조각 문장: 「%s」" % s)
            # S4 말투 혼용 (평서 '-다' 와 존댓말이 한 문단에)
            plain = [s for s in sents if re.search(r"[^니]다[.!]?$", _clean(s) + ".") and not _clean(s).endswith("니다")]
            polite = [s for s in sents if _clean(s).endswith(("니다", "요"))]
            if plain and polite:
                hit(b, "S4", "warn", "한 문단에 '-다'와 존댓말 혼용: 「%s」 / 「%s」" %
                    (_short(plain[0], 25), _short(polite[0], 25)))
            # S2 지시어로 연 첫 문장
            if re.match(r"^(이|그|이것|그것|이러한|그러한|이런|그런|여기서|이번)\s", sents[0]):
                hit(b, "S2", "warn", "문단 첫 문장이 지시어로 시작 — 가리키는 명사가 이 문단 안에 있는지: 「%s」" %
                    _short(sents[0], 40))
            # R6 과개행
            if b.get("breaks", 0) >= RH["r6_min_breaks"]:
                hit(b, "R6", "warn", "한 문단 안 줄바꿈 %d회 — 문장마다 줄을 끊고 있지 않은지" % b["breaks"])

        # ── 자리 불문 검사 ──
        for p in RULES["a1_cliche"]:
            m = re.search(p, text)
            if m:
                hit(b, "A1", "error", "AI 상투어 「%s」 — 지운다 · 문맥: %s" % (m.group(0), _short(text, 50)))
        for p in RULES["a3_self_praise"]:
            if p in text:
                hit(b, "A3", "warn", "자평 「%s」 — 판정 대신 근거 사실만" % p)
        for p in RULES["m3_personified"]:
            m = re.search(p, text)
            if m:
                hit(b, "M3", "warn", "의인화·기계 주체 「%s」 — 누가 무엇을 했는지로 · 문맥: %s" %
                    (m.group(0), _short(text, 50)))
        for w in RULES["m7_metaphor_words"]:
            if w in text:
                hit(b, "M7", "warn", "비유 후보 「%s」 — 가리키는 대상을 손으로 짚을 수 있는지 "
                    "(도메인 용어·감각 묘사·브랜드명이면 그대로) · 문맥: %s" % (w, _short(text, 50)))
        for w in RULES["m_vague_intensity"]:
            if w in text:
                hit(b, "M1", "warn", "모호한 강도어 「%s」 — 무슨 기준인지 본문이 답하는지" % w)
        for p in RULES["sipsio"]:
            if re.search(p, text):
                hit(b, "A", "warn", "명령조(시오체) — '~해 보세요'로")
        for wrong, right in RULES["o1_typos"].items():
            if wrong in text:
                hit(b, "O1", "error", "오타 「%s」 → 「%s」" % (wrong.strip(), right.strip()))
        for wrong, right in RULES["o2_loanwords"].items():
            if wrong in text:
                hit(b, "O2", "error", "표기 「%s」 → 「%s」 (브랜드 자체 표기면 예외)" % (wrong, right))
        if _has_placeholder(text):
            hit(b, "W7", "error", "작업 흔적이 화면에 남음: 「%s」" % _short(text, 40))
        if b["kind"] == "attr" and re.fullmatch(r"(이미지|사진|image|img)\s*\d*", text, re.I):
            hit(b, "W6", "warn", "alt가 '%s' — 보이는 것을 사실대로" % text)

    # ── 파일 단위 집계 ──
    fb = {"line": 0, "kind": "file"}
    hype = [(w, file_text.count(w)) for w in RULES["a2_hype"] if w in file_text]
    n_hype = sum(c for _, c in hype)
    if n_hype:
        hit(fb, "A2", "error" if n_hype >= 3 else "warn",
            "과장·추상 수식 %d회: %s" % (n_hype, ", ".join("%s×%d" % h for h in hype)))
    tr = []
    for p in RULES["a4_translationese"]:
        c = len(re.findall(p, file_text))
        if c:
            tr.append("%s×%d" % (p.replace("서?", "").replace("[다습]", "다"), c))
    if tr:
        hit(fb, "A4", "warn", "번역투 후보: " + ", ".join(tr) + " — 남발된 것만 손본다")
    all_sents = [s for b in blocks for s in _sentences(b["text"])]
    op = Counter()
    for s in all_sents:
        for w in RULES["a7_openers"]:
            if s.startswith(w + " ") or s.startswith(w + ","):
                op[w] += 1
    if sum(op.values()) >= 5:
        hit(fb, "A7", "warn", "문두 접속사 %d회: %s" % (sum(op.values()), dict(op)))
    commas = len(re.findall(r"(고|며|지만|면서|는데|어서|아서|해서),", file_text))
    if commas >= 6:
        hit(fb, "R", "warn", "연결어미 뒤 쉼표 %d회 — 대부분 지워도 된다" % commas)
    for pair in RULES["o2_pick_one"]:
        present = [w for w in pair if w in file_text]
        if len(present) > 1:
            hit(fb, "O", "warn", "표기 혼용 %s — 한 사이트 안에서 하나로" % "/".join(present))
    return out


# ── 대조 (윤문 반영 점검) ─────────────────────────────────────────────────

def compare(a_path, b_path):
    a_blocks, a_raw = extract(a_path)
    b_blocks, b_raw = extract(b_path)
    a_s = [re.sub(r"\s+", " ", s) for x in a_blocks for s in _sentences(x["text"])]
    b_s = [re.sub(r"\s+", " ", s) for x in b_blocks for s in _sentences(x["text"])]
    out = []

    def hit(rid, level, msg):
        out.append({"line": 0, "id": rid, "level": level, "msg": msg, "kind": "compare"})

    keep = sum(1 for s in a_s if s in set(b_s)) / max(1, len(a_s))
    a_txt, b_txt = " ".join(a_s), " ".join(b_s)
    sim = difflib.SequenceMatcher(None, a_txt, b_txt, autojunk=False).ratio()
    stats = {"원문 문장": len(a_s), "윤문 문장": len(b_s),
             "문장 유지율": "%.0f%%" % (keep * 100), "글자 유사도": "%.0f%%" % (sim * 100)}
    if keep < 0.7:
        hit("P8", "warn", "문장 유지율 %.0f%% — 70%% 미만이면 재작성. 중복 삭제(A6) 때문이면 출력에 밝힌다" % (keep * 100))

    # 새로 생긴 단문 연속·스타카토
    def rhythm_hits(blocks, raw):
        return {h["msg"] for h in check_blocks(blocks, raw) if h["id"] in ("R1", "R2")}
    new_rh = rhythm_hits(b_blocks, b_raw) - rhythm_hits(a_blocks, a_raw)
    for m in sorted(new_rh):
        hit("P1", "error", "윤문이 만든 끊어 내림 — " + m)

    # 새 비유 후보
    def metas(t):
        return {w for w in RULES["m7_metaphor_words"] if w in t}
    for w in sorted(metas(b_txt) - metas(a_txt)):
        hit("P3", "error", "원문에 없던 비유 후보 「%s」" % w)

    # 숫자·영문 고유명사·따옴표 인용
    def bag(rx, t):
        return Counter(re.findall(rx, t))
    for name, rx in (("숫자", r"\d[\d,.:%]*"), ("한글 수량", KO_NUM), ("영문", r"[A-Za-z][A-Za-z0-9&.\-]+"),
                     ("인용", r"[\"“「『]([^\"”」』]{2,})[\"”」』]")):
        ca, cb = bag(rx, a_txt), bag(rx, b_txt)
        gone, new = ca - cb, cb - ca
        if gone or new:
            hit("P6", "error", "%s 변경 — 사라짐 %s / 생김 %s" %
                (name, list(gone.elements())[:6], list(new.elements())[:6]))

    # 목소리 (구어 종결·질문형)
    def voice(sents):
        n = 0
        for s in sents:
            c = _clean(s)
            if s.rstrip().endswith("?") or any(c.endswith(v) for v in RULES["voice_markers"]):
                n += 1
        return n
    va, vb = voice(a_s), voice(b_s)
    stats["구어·질문 종결"] = "%d → %d" % (va, vb)
    if vb < va:
        hit("P4", "warn", "구어·질문 종결이 %d → %d로 줄었다 — 쓴 사람의 목소리가 눌렸는지" % (va, vb))

    # 과개행
    def breaks(raw, path):
        return len(re.findall(r"<br\s*/?>", raw, re.I)) if path.lower().endswith((".html", ".htm")) \
            else raw.count("\n")
    ba, bb = breaks(a_raw, a_path), breaks(b_raw, b_path)
    stats["줄바꿈"] = "%d → %d" % (ba, bb)
    if bb - ba >= 3 and bb > ba * 1.3:
        hit("P2", "error", "줄바꿈이 %d → %d로 늘었다 — 문단이 흩어졌는지" % (ba, bb))

    # 평균 문장 길이 급감
    la = sum(map(len, a_s)) / max(1, len(a_s))
    lb = sum(map(len, b_s)) / max(1, len(b_s))
    stats["평균 문장 길이"] = "%.0f → %.0f자" % (la, lb)
    if len(b_s) > len(a_s) * 1.25 and lb < la * 0.8:
        hit("P1", "warn", "문장 수 %d → %d, 평균 길이 %.0f → %.0f자 — 복문을 잘게 자르지 않았는지" %
            (len(a_s), len(b_s), la, lb))
    return out, stats


# ── 출력 ───────────────────────────────────────────────────────────────────

def collect(targets):
    files = []
    for t in targets:
        if os.path.isdir(t):
            for root, dirs, names in os.walk(t):
                dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith("._")]
                files += [os.path.join(root, n) for n in sorted(names)
                          if n.lower().endswith(EXTS) and not n.startswith("._")]
        elif os.path.isfile(t):
            files.append(t)
        else:
            print("파일 없음: %s" % t, file=sys.stderr)
            sys.exit(2)
    return files


def show(path, hits, stats=None):
    errs = [h for h in hits if h["level"] == "error"]
    warns = [h for h in hits if h["level"] == "warn"]
    head = (RED + "🔴 %d" % len(errs) + OFF) if errs else (GRN + "🔴 0" + OFF)
    print("%s  %s · 🟡 볼 자리 %d" % (path, head, len(warns)))
    if stats:
        print(DIM + "   " + " · ".join("%s %s" % kv for kv in stats.items()) + OFF)
    for h in errs + warns:
        mark = RED + "🔴" if h["level"] == "error" else YEL + "🟡"
        where = "%d행" % h["line"] if h["line"] else ("전체" if h["kind"] in ("file", "compare") else "-")
        print("   %s %-3s%s %-5s %s" % (mark, h["id"], OFF, where, h["msg"]))


def main():
    ap = argparse.ArgumentParser(description="한글 문장 기계 검사 (hangul-review)")
    ap.add_argument("targets", nargs="*")
    ap.add_argument("--compare", nargs=2, metavar=("원본", "윤문본"))
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    if a.compare:
        for p in a.compare:
            if not os.path.isfile(p):
                print("파일 없음: %s" % p, file=sys.stderr)
                sys.exit(2)
        hits, stats = compare(*a.compare)
        if a.json:
            print(json.dumps({"compare": a.compare, "stats": stats, "hits": hits}, ensure_ascii=False, indent=2))
        else:
            show("%s ↔ %s" % tuple(a.compare), hits, stats)
        sys.exit(1 if any(h["level"] == "error" for h in hits) else 0)

    if not a.targets:
        ap.print_help()
        sys.exit(2)
    results = {}
    for f in collect(a.targets):
        blocks, raw = extract(f)
        results[f] = check_blocks(blocks, raw)
    if a.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        for f, hits in results.items():
            show(f, hits)
        n_e = sum(1 for h in sum(results.values(), []) if h["level"] == "error")
        n_w = sum(1 for h in sum(results.values(), []) if h["level"] == "warn")
        print("\n합계: 파일 %d · 🔴 %d · 🟡 %d  — 찍힌 자리는 판정이 아니라 사람이 볼 자리다" %
              (len(results), n_e, n_w))
    sys.exit(1 if any(h["level"] == "error" for hs in results.values() for h in hs) else 0)


if __name__ == "__main__":
    main()
