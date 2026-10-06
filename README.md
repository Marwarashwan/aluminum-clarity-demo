# aluminum-clarity-demo

A live webcam demo that measures how clear (vs. cloudy) a liquid looks, in real time. Built for EGA's **"Open Stage – Meet AL"** STEM session, to make the clarification → precipitation → filtration stages of the Bayer process (how bauxite ore becomes alumina) visible and interactive for an audience.

---

## What it does

Point a laptop webcam at a clear cup/beaker. The script watches a box in the middle of the frame and shows a live number + color-coded gauge bar on screen for how clear the liquid currently is — no manual judging, no "does this look clear enough yet" guessing. The number reacts on its own as you do the physical demo in front of people.

## How it measures clarity

It looks at how much fine visual detail is visible *through* the liquid — using a standard computer-vision technique called **Laplacian variance** (the same math used in camera autofocus systems to detect "is this in focus"). Put something with a visible pattern (text, a grid) behind the cup:

- **Clear liquid** → you can see that pattern sharply → high score
- **Cloudy liquid** → light scatters, the pattern blurs out → low score

Press **C** once at the start, with your starting (clearest or cloudiest, whichever you begin with) liquid in frame, to calibrate that as the 100% reference point — everything else is measured relative to it.

## Controls

| Key | Action |
|---|---|
| `C` | Calibrate — sets the current reading as the 100% baseline |
| `R` | Reset calibration (back to raw numbers) |
| `Q` | Quit |

## Running it

```bash
pip install opencv-python
python3 clarity_meter.py

# or, to use a different camera:
python3 clarity_meter.py --camera 1
```

## Demo setup tips

- Tape a printed pattern (text, a grid, anything with visible detail) to the table **behind** where the cup will sit. A plain blank background gives the camera nothing to measure — cloudiness has no visible "detail" to blur out in the first place.
- Use steady, consistent lighting. If your webcam app lets you lock focus/exposure, do it — auto-adjustment mid-demo can throw the number off.
- **Do a full dry run** with your actual cup, your actual liquids, in the actual room, before presenting to an audience. Live camera demos are sensitive to lighting and angle in ways that are hard to predict from a desk test.
- The number is a *supporting* layer, not the whole demo — the physical change (mud settling, crystals forming, liquid passing through a filter) should read clearly by eye on its own, in case the camera read-out glitches.

## Suggested demo flow

| Bayer process stage | What you do physically | What the meter shows |
|---|---|---|
| **Clarification** | Start with muddy water (stands in for the leftover red mud after digestion); let it settle, or add a pinch of alum to speed it up | Clarity score climbs as solids settle out |
| **Precipitation** | A supersaturated solution (sodium acetate is a safe, dramatic choice) — seed it with one crystal and it fills with solid crystals in seconds | Clarity score drops suddenly — a fast, dramatic visual |
| **Filtration** | Pour the crystal slurry through a coffee filter into a clean cup | Clarity score jumps back up — crystals stayed behind in the filter |

---

## Skills and concepts this project uses

- **Computer vision fundamentals** — reading a live video stream frame-by-frame with OpenCV (`cv2.VideoCapture`), rather than working from a single static photo
- **Edge/blur detection** — the Laplacian operator measures how sharply brightness changes across an image; its variance is a well-established proxy for "how much fine detail is present," which is what autofocus systems use to detect blur
- **Signal processing** — smoothing noisy frame-to-frame readings with a moving average, and choosing a response curve (square root of the raw ratio) so the on-screen number matches how a human eye actually perceives gradual clearing, instead of snapping to near-zero too early
- **Calibration against a reference** — same principle as the gear project's real-world scale factor: a single reference measurement turns an arbitrary raw number into something meaningful (there, pixels → millimeters; here, raw signal → a 0-100% clarity score)
- **Real-time UI feedback** — drawing an overlay (text, a gauge bar, color coding) directly onto a live video feed with OpenCV's drawing functions

## Relation to the gear-inspection project

This project and `industrial-quality-inspection` (the gear/bearing inspector) are **separate, unrelated applications** — one looks at liquids in real time through a webcam, the other analyzes still photos of mechanical parts — but they share the same underlying idea and a lot of the same technique:

> **A camera can measure something automatically and precisely, instead of a person estimating it by eye.**

Specifically, they share:
- The same core library (OpenCV) and the same category of technique: turning an image into a small set of meaningful numbers (there: tooth count, radii, bore ratio; here: a clarity score)
- The same "calibrate against one known reference, then everything else is measured relative to it" pattern
- The same engineering discipline: validate the measurement logic against **synthetic test cases you control** before trusting it on a real camera/real photo — both projects were built and debugged this way, not just written and hoped to work
- The same honest-about-limitations approach: both explicitly document what conditions they were tested under and where they're likely to struggle (there: angled/non-flat gear photos; here: lighting changes, glare, cameras with auto-exposure)

In short: the gear inspector was the first project to prove out "measure something automatically with a camera instead of eyeballing it" as a working approach — this project reuses that same approach on a completely different problem, for a STEM outreach context instead of an engineering inspection context.
