#!/usr/bin/env python3
"""Generate the intro diagrams for the partials module.

    python3 scripts/gen-diagrams.py images/

Writes what-is-a-template-{1,2,3}.svg and what-is-a-partial-{1,2,3,4}.svg.

Both sets share CANVAS_W and FS, so text lands at the same size on a slide
whichever diagram is showing. Stages within a set share coordinates, so a
click only ever adds. No background rect: these sit on the slide background.

Colour vocabulary:
    teal    a value that came from the document
    amber   the part being extracted, and the call it leaves behind
    purple  a partial you supplied
    grey    boilerplate
"""
import html as _html
import pathlib
import sys

MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'DejaVu Sans Mono', monospace"
SANS = "-apple-system, system-ui, 'Segoe UI', Roboto, sans-serif"

CANVAS_W = 1300
FS, LH = 24, 34                 # code size and line height, shared by both sets
CH = FS * 0.6                   # monospace advance width
PAD_T, PAD_B, PAD_X = 40, 24, 26
LABEL_GAP = 14                  # baseline of a label above its box

TEAL, AMBER, PURPLE, GREY = "#14625d", "#8a5a00", "#6a4c93", "#555"
INK, MUTE = "#222", "#777"


def esc(t):
    return _html.escape(t, quote=False)


def _runs(text, base):
    """Split {teal}/{amber}-marked text into (chunk, colour) runs."""
    cur, rest, chars = base, text, []
    while rest:
        for tag, col in (("{teal}", TEAL), ("{amber}", AMBER)):
            if rest.startswith(tag):
                cur = base if cur == col else col
                rest = rest[len(tag):]
                break
        else:
            chars.append((rest[0], cur))
            rest = rest[1:]
    out, buf, bufc = [], "", None
    for ch, c in chars:
        if c != bufc and buf:
            out.append((buf, bufc))
            buf = ""
        buf += ch
        bufc = c
    if buf:
        out.append((buf, bufc))
    return out


def code(x, y, text, base=GREY):
    n = len(text) - len(text.lstrip(" "))
    if n:                        # SVG collapses leading space
        text = " " * n + text[n:]
    spans = "".join(
        esc(t) if c == base else f'<tspan fill="{c}" font-weight="bold">{esc(t)}</tspan>'
        for t, c in _runs(text, base))
    return f'    <text x="{x}" y="{y}">{spans}</text>'


def box_h(nlines):
    return PAD_T + LH * (nlines - 1) + PAD_B


def box(x, y, w, lines, fill="#ffffff", stroke="#333", sw=4, dash=False,
        base=GREY, h=None):
    h = h if h is not None else box_h(len(lines))
    d = ' stroke-dasharray="7 5"' if dash else ''
    out = [f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" '
           f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>',
           f'  <g font-family="{MONO}" font-size="{FS}" fill="{base}">']
    out += [code(x + PAD_X, y + PAD_T + i * LH, ln, base)
            for i, ln in enumerate(lines)]
    out.append('  </g>')
    return "\n".join(out)


def caption(x, y, name, note=None, right=None, color=INK, note_color=MUTE):
    out = [f'  <text x="{x}" y="{y}" font-family="{MONO}" font-size="26" '
           f'font-weight="bold" fill="{color}">{esc(name)}</text>']
    if note:
        out.append(f'  <text x="{right}" y="{y}" text-anchor="end" '
                   f'font-family="{SANS}" font-size="22" fill="{note_color}">'
                   f'{esc(note)}</text>')
    return "\n".join(out)


def head(w, h, title, desc):
    return "\n".join([
        '<?xml version="1.0" encoding="UTF-8" standalone="no"?>',
        '<svg xmlns="http://www.w3.org/2000/svg"',
        f'     viewBox="0 0 {w} {h}"',
        '     role="img"',
        '     aria-labelledby="svg-title svg-desc">',
        f'  <title id="svg-title">{esc(title)}</title>',
        f'  <desc id="svg-desc">{esc(desc)}</desc>',
        ''])


# ===================================================================== #
#  what-is-a-template : document -> output -> the template that did it   #
# ===================================================================== #
T_LX, T_LW = 40, 390
T_RX, T_RW = 680, 580
T_JOIN = 560                                   # x of the connector elbow

QMD = ["---", "title: {teal}Hello{teal}", "---", "",
       "{teal}Hello **world**!{teal}"]
TPL = ["<html>", "<head>", "<title>{teal}$title${teal}</title>", "</head>",
       "<body>", "{teal}$body${teal}", "</body>", "</html>"]
OUT = ["<html>", "<head>", "<title>{teal}Hello{teal}</title>", "</head>",
       "<body>", "{teal}<p>Hello <strong>world</strong>!</p>{teal}",
       "</body>", "</html>"]

T_QMD_Y, T_QMD_H = 48, box_h(len(QMD))
T_TPL_Y, T_TPL_H = T_QMD_Y + T_QMD_H + 52, box_h(len(TPL))
T_OUT_H = box_h(len(OUT))
T_OUT_Y = (T_QMD_Y + T_TPL_Y + T_TPL_H) // 2 - T_OUT_H // 2
T_H = T_TPL_Y + T_TPL_H + 24

T_DESC = {
    1: ("A Quarto document",
        "One box, labelled hello.qmd, your content, holding a short Quarto "
        "document: a YAML header setting title to Hello, then the line Hello "
        "asterisk asterisk world asterisk asterisk exclamation mark. The value "
        "Hello and the body line are teal."),
    2: ("A document renders to output",
        "The document on the left, with a connector stepping down from it, "
        "labelled render, arrowing into hello.html on the right: a full HTML "
        "page of which only two parts are teal, Hello inside the title "
        "element and a paragraph reading Hello world. Everything else is grey, "
        "and nothing yet explains where it came from."),
    3: ("A template is boilerplate with named holes",
        "The same figure with template.html revealed below the document, its "
        "connector joining the render line. The template is HTML boilerplate "
        "with two teal placeholders, dollar title dollar inside the title "
        "element and dollar body dollar inside the body. They line up with the "
        "two teal parts of the output, and the grey boilerplate lines up with "
        "the grey output."),
}


def template_svg(stage):
    t, d = T_DESC[stage]
    s = [head(CANVAS_W, T_H, t, d)]
    s.append(caption(T_LX, T_QMD_Y - LABEL_GAP, "hello.qmd", "your content",
                     T_LX + T_LW))
    s.append(box(T_LX, T_QMD_Y, T_LW, QMD))

    if stage >= 3:
        s.append(caption(T_LX, T_TPL_Y - LABEL_GAP, "template.html",
                         "the template", T_LX + T_LW))
        s.append(box(T_LX, T_TPL_Y, T_LW, TPL))

    if stage >= 2:
        qmid = T_QMD_Y + T_QMD_H // 2
        jmid = T_OUT_Y + T_OUT_H // 2
        s.append(f'  <g stroke="{MUTE}" stroke-width="3" fill="none">')
        s.append(f'    <path d="M {T_LX+T_LW} {qmid} L {T_JOIN} {qmid} L {T_JOIN} {jmid}"/>')
        if stage >= 3:
            tmid = T_TPL_Y + T_TPL_H // 2
            s.append(f'    <path d="M {T_LX+T_LW} {tmid} L {T_JOIN} {tmid} L {T_JOIN} {jmid}"/>')
        s.append(f'    <path d="M {T_JOIN} {jmid} L {T_RX-42} {jmid}"/>')
        s.append('  </g>')
        s.append(f'  <path d="M {T_RX-20} {jmid} L {T_RX-44} {jmid-11} '
                 f'L {T_RX-44} {jmid+11} Z" fill="{MUTE}"/>')
        s.append(f'  <text x="{T_JOIN-16}" y="{jmid+7}" text-anchor="end" '
                 f'font-family="{SANS}" font-size="22" fill="{MUTE}">render</text>')
        s.append(caption(T_RX, T_OUT_Y - LABEL_GAP, "hello.html", "the output",
                         T_RX + T_RW))
        s.append(box(T_RX, T_OUT_Y, T_RW, OUT))

    s.append('\n</svg>')
    return "\n".join(s) + "\n"


# ===================================================================== #
#  what-is-a-partial : carve -> extract -> generalise -> override        #
# ===================================================================== #
P_LX, P_LW = 40, 400
P_RX, P_RW = 660, 560

MONOLITH = ["<html>", "<head>", "<title>{teal}$title${teal}</title>", "</head>",
            "<body>", "<header>", "  <h1>{teal}$title${teal}</h1>",
            "  <p>{teal}$author${teal}</p>", "</header>", "{teal}$body${teal}",
            "</body>", "</html>"]
ONE_OUT = ["<html>", "<head>", "<title>{teal}$title${teal}</title>", "</head>",
           "<body>", "{amber}$title-block.html()${amber}", "{teal}$body${teal}",
           "</body>", "</html>"]
ALL_OUT = ["<html>", "<head>", "{amber}$metadata.html()${amber}",
           "{amber}$styles.html()${amber}", "</head>", "<body>",
           "{amber}$title-block.html()${amber}", "{amber}$toc.html()${amber}",
           "{teal}$body${teal}", "</body>", "</html>"]
PART_Q = ["<header>", "  <h1>{teal}$title${teal}</h1>",
          "  <p>{teal}$author${teal}</p>", "</header>"]
PART_MINE = ["<header>", "  <h1>{teal}$title${teal}</h1>",
             "  <p>{teal}$subtitle${teal}</p>", "  <p>{teal}$author${teal}</p>",
             "</header>"]

P_BOX_Y = 48
P_BOX_H = box_h(len(MONOLITH))                 # tallest stage, sets the canvas
P_Q_Y, P_Q_H = 48, box_h(len(PART_Q))
P_M_Y, P_M_H = P_Q_Y + P_Q_H + 62, box_h(len(PART_MINE))
P_H = max(P_BOX_Y + P_BOX_H, P_M_Y + P_M_H) + 24

P_DESC = {
    1: ("One file holds the whole page",
        "A box labelled template.html, one file, holding a small but complete "
        "HTML template: html, head, a title element with the teal dollar title "
        "dollar, then a body containing a header element with an h1 of dollar "
        "title dollar and a paragraph of dollar author dollar, then dollar "
        "body dollar. The header element and its two indented lines are ringed "
        "in an amber dashed box, annotated: this part is the title block."),
    2: ("The title block moves into its own file",
        "The same template.html box, with the header markup gone and the amber "
        "call dollar title-block dot html parens dollar in its place. A "
        "connector runs from that call to a new box on the right, labelled "
        "title-block.html, the file it names, holding the header element with "
        "an h1 of the teal dollar title dollar and a paragraph of the teal "
        "dollar author dollar. Its tags are annotated raw HTML and its "
        "placeholders annotated variables."),
    3: ("Quarto does this for every part",
        "The same figure, with the rest of the template also replaced by amber "
        "calls: dollar metadata dot html parens dollar and dollar styles dot "
        "html parens dollar in the head, and dollar toc dot html parens dollar "
        "beside the title-block call in the body. Only dollar body dollar, in "
        "teal, and the literal html, head and body tags remain."),
    4: ("Your file is used instead",
        "The same figure with Quarto's title-block.html box faded to grey and "
        "a second box below it drawn with a purple dashed border, labelled "
        "title-block.html, yours. It holds the same header element plus an "
        "extra paragraph containing the teal dollar subtitle dollar. The "
        "connector from the call now points at your box."),
}


def partial_svg(stage):
    t, d = P_DESC[stage]
    lines = {1: MONOLITH, 2: ONE_OUT, 3: ALL_OUT, 4: ALL_OUT}[stage]
    s = [head(CANVAS_W, P_H, t, d)]
    s.append(caption(P_LX, P_BOX_Y - LABEL_GAP, "template.html",
                     "one file" if stage == 1 else "calls other files",
                     P_LX + P_LW))
    s.append(box(P_LX, P_BOX_Y, P_LW, lines))   # sizes to content: it shrinks as parts move out

    if stage == 1:                              # ring the region we will lift
        ry = P_BOX_Y + PAD_T + 5 * LH - 25
        rh = LH * 4
        s.append(f'  <rect x="{P_LX+14}" y="{ry}" width="{P_LW-28}" height="{rh}" '
                 f'rx="6" fill="none" stroke="{AMBER}" stroke-width="2.5" '
                 f'stroke-dasharray="7 5"/>')
        s.append(f'  <text x="{P_LX+P_LW+34}" y="{ry+rh//2-4}" font-family="{SANS}" '
                 f'font-size="24" fill="{AMBER}">this part is the</text>')
        s.append(f'  <text x="{P_LX+P_LW+34}" y="{ry+rh//2+26}" font-family="{SANS}" '
                 f'font-size="24" font-weight="bold" fill="{AMBER}">title block</text>')

    if stage >= 2:
        faded = stage == 4
        call_i = 5 if stage == 2 else 6         # index of the title-block call
        cy = P_BOX_Y + PAD_T + call_i * LH - 8
        ty = (P_Q_Y + P_Q_H // 2) if not faded else (P_M_Y + P_M_H // 2)
        col = GREY if not faded else PURPLE
        s.append(f'  <g stroke="{col}" stroke-width="3" fill="none">')
        s.append(f'    <path d="M {P_LX+P_LW} {cy} L 560 {cy} L 560 {ty} L {P_RX-42} {ty}"/>')
        s.append('  </g>')
        s.append(f'  <path d="M {P_RX-20} {ty} L {P_RX-44} {ty-11} '
                 f'L {P_RX-44} {ty+11} Z" fill="{col}"/>')

        s.append(caption(P_RX, P_Q_Y - LABEL_GAP, "title-block.html",
                         "Quarto's" if faded else "the file it names",
                         P_RX + P_RW, color="#aaa" if faded else INK,
                         note_color="#aaa" if faded else MUTE))
        qlines = PART_Q if not faded else [l.replace("{teal}", "") for l in PART_Q]
        s.append(box(P_RX, P_Q_Y, P_RW, qlines,
                     fill="#f7f7f7" if faded else "#ffffff",
                     stroke="#ccc" if faded else "#333",
                     sw=2 if faded else 4, base="#aaa" if faded else GREY))
        if stage in (2, 3):
            s.append(f'  <text x="{P_RX+P_RW-24}" y="{P_Q_Y+PAD_T-4}" '
                     f'text-anchor="end" font-family="{SANS}" font-size="22" '
                     f'fill="{MUTE}">raw HTML</text>')
            s.append(f'  <text x="{P_RX+P_RW-24}" y="{P_Q_Y+PAD_T+LH-4}" '
                     f'text-anchor="end" font-family="{SANS}" font-size="22" '
                     f'fill="{TEAL}">variables</text>')

    if stage == 4:
        s.append(caption(P_RX, P_M_Y - LABEL_GAP, "title-block.html", "yours",
                         P_RX + P_RW, color="#4a3268", note_color=PURPLE))
        s.append(box(P_RX, P_M_Y, P_RW, PART_MINE, fill="#ece9f5",
                     stroke=PURPLE, sw=3, dash=True, base="#4a3268"))

    s.append('\n</svg>')
    return "\n".join(s) + "\n"


if __name__ == "__main__":
    out = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "images")
    for n in (1, 2, 3):
        (out / f"what-is-a-template-{n}.svg").write_text(template_svg(n))
        print("wrote", f"what-is-a-template-{n}.svg")
    for n in (1, 2, 3, 4):
        (out / f"what-is-a-partial-{n}.svg").write_text(partial_svg(n))
        print("wrote", f"what-is-a-partial-{n}.svg")
