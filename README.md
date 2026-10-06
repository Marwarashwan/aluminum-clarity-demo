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

```python
clarity_meter.py - live "clarity score" from a webcam, for the EGA clarification /
precipitation / filtration demo.

WHAT IT DOES
------------
Points your laptop's webcam at a clear cup/beaker and shows a big live number +
gauge bar on screen: how clear (vs cloudy) the liquid currently looks. Exactly the
same idea as the gear-inspector project - a camera automatically measuring
something instead of a person eyeballing it - just measuring "clarity" instead of
tooth count.

HOW IT MEASURES CLARITY
------------------------
It looks at a small box in the middle of the frame (where you'll position the cup)
and measures how much fine detail/contrast is visible there, using a standard
blur-detection technique (variance of the Laplacian - the same trick used for
autofocus "is this in focus" checks). A clear liquid lets you see sharp detail
through it (the background pattern, bubbles, the far side of the cup); a cloudy
liquid scatters light and blurs all of that out. More visible detail = higher
score = clearer.

SETUP FOR THE DEMO
-------------------
1. Put something with a clear PATTERN behind where the cup will sit - a sheet of
   paper with text or a grid works great, printed and taped to the table behind the
   cup. Plain blank backgrounds give a weak signal (there's no detail to blur out in
   the first place).
2. Good steady lighting. Avoid the camera auto-adjusting exposure/focus mid-demo if
   you can (some webcam apps let you lock focus/exposure - check beforehand).
3. Run this script, position the empty/clear cup inside the on-screen box, then
   press C to calibrate ("this is 100% clear"). Do this once before the audience
   arrives, with the actual cup and liquid you'll start with.
4. During the demo, just do your physical steps - the number reacts on its own.

USAGE
-----
    python3 clarity_meter.py
        -> opens your default webcam (camera index 0)

    python3 clarity_meter.py --camera 1
        -> use a different camera (e.g. a USB webcam instead of a laptop's own)

CONTROLS (while the window is focused)
----------------------------------------
    C   calibrate - sets whatever is in the box RIGHT NOW as the 100% clear baseline
    R   reset calibration (back to raw/uncalibrated numbers)
    Q   quit

IMPORTANT - PRACTICE THIS BEFORE THE REAL SESSION
----------------------------------------------------
Live demos in front of an audience are risky - lighting, camera angle, and glare
all affect this. Run through your exact demo (same cup, same liquids, same spot in
the room) at least once beforehand, and have the plain physical demo (just showing
the liquid clearing/clouding/filtering by eye) as your fallback if anything looks
wrong on the day. The number is a bonus layer, not the whole demo.
"""
import argparse
import collections

import cv2
import numpy as np

# --- Tunables -----------------------------------------------------------------
ROI_FRACTION = 0.35      # the measurement box is this fraction of the frame's
                          # shorter side, centred in the frame
SMOOTHING_FRAMES = 8      # live number is averaged over this many recent frames,
                          # to stop it jittering frame-to-frame
BAR_WIDTH = 420
BAR_HEIGHT = 40


def get_roi_box(frame_shape):
    h, w = frame_shape[:2]
    side = int(ROI_FRACTION * min(h, w))
    cx, cy = w // 2, h // 2
    x0, y0 = cx - side // 2, cy - side // 2
    return x0, y0, side, side


def compute_clarity_raw(frame_bgr, box):
    """Variance of the Laplacian inside `box` - higher = more visible fine detail
    = clearer liquid. This is a relative/arbitrary-scale number on its own; the
    calibration step turns it into a 0-100%-ish "clarity score" people can read.
    """
    x, y, w, h = box
    roi = frame_bgr[y:y + h, x:x + w]
    if roi.size == 0:
        return 0.0
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    return float(cv2.Laplacian(gray, cv2.CV_64F).var())


def draw_overlay(frame, box, raw_value, baseline, history):
    x, y, w, h = box
    smoothed = float(np.mean(history)) if history else raw_value

    if baseline is not None and baseline > 1e-6:
        # Raw Laplacian-variance ratio drops off much faster than a liquid actually
        # LOOKS like it's clearing (tested against a simulated gradual settle) - the
        # square root of the ratio tracks the real "how much has it cleared" far
        # better, so the on-screen number moves at a pace that matches what the
        # audience sees instead of snapping to ~0% early and jumping at the end.
        ratio = max(0.0, smoothed) / baseline
        pct = 100.0 * ratio ** 0.5
        label = f"Clarity: {pct:.0f}%"
        frac = max(0.0, min(1.0, pct / 100.0))
    else:
        label = f"Raw signal: {smoothed:.0f}  (press C to calibrate)"
        frac = max(0.0, min(1.0, smoothed / 300.0))   # rough uncalibrated scale

    if frac > 0.66:
        color = (0, 200, 0)        # green - clear
    elif frac > 0.33:
        color = (0, 200, 255)      # amber - medium
    else:
        color = (0, 0, 220)        # red - cloudy

    # measurement box
    cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
    cv2.putText(frame, "place cup here", (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    # big label
    cv2.putText(frame, label, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.1, color, 3)

    # gauge bar
    bx, by = 20, 70
    cv2.rectangle(frame, (bx, by), (bx + BAR_WIDTH, by + BAR_HEIGHT), (80, 80, 80), 2)
    fill_w = int(BAR_WIDTH * frac)
    cv2.rectangle(frame, (bx, by), (bx + fill_w, by + BAR_HEIGHT), color, -1)

    cv2.putText(frame, "[C] calibrate   [R] reset   [Q] quit", (20, frame.shape[0] - 15),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)
    return frame


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--camera", type=int, default=0, help="camera index (default 0)")
    args = ap.parse_args()

    cap = cv2.VideoCapture(args.camera)
    if not cap.isOpened():
        print(f"Could not open camera {args.camera}. Try --camera 1, or check nothing "
              "else (Zoom, another app) is already using the webcam.")
        return

    baseline = None
    history = collections.deque(maxlen=SMOOTHING_FRAMES)
    print(__doc__)
    print("Window open - click it to focus, then use C / R / Q.")

    while True:
        ok, frame = cap.read()
        if not ok:
            print("Lost the camera feed - stopping.")
            break
        frame = cv2.flip(frame, 1)   # mirror, feels more natural facing the camera
        box = get_roi_box(frame.shape)
        raw = compute_clarity_raw(frame, box)
        history.append(raw)
        frame = draw_overlay(frame, box, raw, baseline, history)
        cv2.imshow("Clarity-O-Meter", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('c'):
            baseline = float(np.mean(history)) if history else raw
            print(f"Calibrated: current reading ({baseline:.0f}) is now 100% clear.")
        elif key == ord('r'):
            baseline = None
            print("Calibration reset - showing raw signal again.")

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
```
