# scripts

## `gen-diagrams.py`

Generates the intro diagrams for the partials module:

```bash
python3 scripts/gen-diagrams.py images/
```

Writes `images/what-is-a-template-{1,2,3}.svg` and
`images/what-is-a-partial-{1,2,3,4}.svg`. Edit the script, never the SVGs.

Both sets share `CANVAS_W` and `FS`, so code lands at the same size on a slide
whichever diagram is showing. Stages within a set share coordinates, so
advancing a slide only adds — the one exception is the template box in the
partials set, which shrinks as markup moves out of it, on purpose.

There is no background rectangle: the diagrams sit on the slide background.
Note this differs from `images/html-template-partials.svg` and the other
older figures, which carry a grey `#ececec` backdrop.

Colour vocabulary:

| Colour | Means |
|---|---|
| teal `#14625d` | a value that came from the document |
| amber `#8a5a00` | the part being extracted, and the call it leaves behind |
| purple `#6a4c93` | a partial you supplied |
| grey `#555` | boilerplate |

Each SVG carries `<title>` and `<desc>`. The slide `fig-alt` is copied from
`<desc>`, so if you change a diagram, re-copy it.
