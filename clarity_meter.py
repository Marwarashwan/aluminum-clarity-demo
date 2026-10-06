"""
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
