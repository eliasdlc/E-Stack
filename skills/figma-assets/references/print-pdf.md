# Print PDF from a Figma export

Used for the ConoceRD brochure (5 Oct) and the 5x7 in card (12 Oct). The
Figma frame is built at 1 px = 1 pt and already contains the bleed, so the
export's page is trim + 2 x bleed. For a 5x7 in card with 3 mm (8.5 pt)
bleed: 377 x 521 pt page, trim box inset 8.5 pt.

1. Export each face: `download_assets` with `defaultFormat: pdf`, then
   `curl -sL -o face.pdf "https://www.figma.com/api/mcp/asset/<id>.pdf"`.
2. Install the tool in a scratch venv (it is not on the system):
   `python3 -m venv /tmp/print/venv && /tmp/print/venv/bin/pip -q install pikepdf`.
3. Build two files from the faces, in order (front, back):
   - `...-sangrado.pdf` (the one that normally goes to the printer): MediaBox and BleedBox are the whole page, TrimBox is inset by the bleed.
   - `...-marcas.pdf`: a larger page (slug of about 27 pt per side) with the face placed in the middle and hairline crop marks drawn outside the bleed, at the trim lines.

The script below ran on pikepdf 10.17 with two blank 377 x 521 pt faces (2
pages each, boxes as described, marks at the four corners). Keep the source
PDFs open until both files are saved: pikepdf destroys their pages when the
source object is released.

```python
import pikepdf
from pikepdf import Pdf, Name, Array, Dictionary

W, H, B = 377, 521, 8.5            # page with bleed, bleed
faces = [Pdf.open(f) for f in ["face-1.pdf", "face-2.pdf"]]   # keep them open until both files are saved

out = Pdf.new()
for src in faces:
    out.pages.append(src.pages[0])
for p in out.pages:
    p.obj['/MediaBox'] = Array([0, 0, W, H]); p.obj['/BleedBox'] = Array([0, 0, W, H])
    p.obj['/TrimBox'] = Array([B, B, W - B, H - B])
out.save("piece-imprenta-sangrado.pdf")

S = 27                              # slug around the bleed for the marks
mk = Pdf.new()
for src in faces:
    page = mk.add_blank_page(page_size=(W + 2 * S, H + 2 * S))
    form = mk.copy_foreign(src.pages[0].as_form_xobject())
    page.obj['/Resources'] = Dictionary(XObject=Dictionary(Face=form))
    xs, ys, g = [S + B, S + W - B], [S + B, S + H - B], 3
    ops = [f"q 1 0 0 1 {S} {S} cm /Face Do Q", "q 0.25 w 1 1 1 1 K"]   # CMYK registration black
    for x in xs:
        ops += [f"{x} 0 m {x} {S - B - g} l S", f"{x} {S + H + B + g} m {x} {H + 2 * S} l S"]
    for y in ys:
        ops += [f"0 {y} m {S - B - g} {y} l S", f"{S + W + B + g} {y} m {W + 2 * S} {y} l S"]
    ops.append("Q")
    page.obj['/Contents'] = mk.make_stream("\n".join(ops).encode())
    page.obj['/BleedBox'] = Array([S, S, S + W, S + H]); page.obj['/TrimBox'] = Array([S + B, S + B, S + W - B, S + H - B])
mk.save("piece-imprenta-marcas.pdf")
```

Checks that were run on the 12 Oct card and should be repeated: page count,
trim size exactly 5 x 7 in (`pdfinfo -box`), all content inside the safe zone
(5 mm from the trim), `pdffonts` lists embedded fonts, and `pdftoppm` renders
of every page looked at by eye. Earlier versions of the PDFs move to a
`versiones/<n>/` folder next to the new ones.
