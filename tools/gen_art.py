#!/usr/bin/env python3
"""Generates visual display assets for Helm Touch UI on MPC:
- 13 waveform display diagrams (Sine, Tri, Square, Saw Up/Down, Steps, Pyramids, S&H, S&Glide)
- ADSR envelope curves (Amp, Filter, Mod)
- Filter frequency response curve
- Step sequencer pattern grid
"""
import os
import math
import numpy as np
from PIL import Image, ImageDraw

IMG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "images")
os.makedirs(IMG_DIR, exist_ok=True)

# Helm Palette
BG_COLOR = (24, 23, 28)
BORDER_COLOR = (45, 43, 52)
GRID_COLOR = (35, 34, 42)
CYAN_ACCENT = (59, 240, 255)
GOLD_ACCENT = (255, 176, 32)
GREEN_ACCENT = (76, 255, 138)
PURPLE_ACCENT = (200, 110, 255)

def create_screen(w, h, bg=BG_COLOR, border=BORDER_COLOR):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    # Rounded bezel background
    dr.rounded_rectangle([0, 0, w - 1, h - 1], radius=8, fill=bg, outline=border, width=2)
    # Subtle center grid line
    dr.line([(10, h // 2), (w - 10, h // 2)], fill=GRID_COLOR, width=1)
    for gx in range(40, w - 20, 40):
        dr.line([(gx, 10), (gx, h - 10)], fill=GRID_COLOR, width=1)
    return im, dr

def draw_wave(dr, points, color=CYAN_ACCENT, width=3):
    # Draw glow line
    glow_color = (color[0], color[1], color[2], 70)
    for offset in range(-2, 3):
        if offset != 0:
            glow_pts = [(p[0], p[1] + offset) for p in points]
            dr.line(glow_pts, fill=glow_color, width=width + 2)
    # Draw main line
    dr.line(points, fill=color, width=width)

def generate_waveforms(w=260, h=110):
    mid_y = h / 2.0
    amp = (h / 2.0) - 18.0
    x_start = 14
    x_end = w - 14
    x_span = x_end - x_start
    n_pts = 200

    for idx in range(13):
        im, dr = create_screen(w, h)
        pts = []
        for i in range(n_pts):
            t = i / float(n_pts - 1)  # 0 to 1 across 2 full cycles
            cycles = 2.0
            phase = (t * cycles) % 1.0

            if idx == 0:  # Sine
                val = math.sin(t * cycles * 2.0 * math.pi)
            elif idx == 1:  # Triangle
                val = 4.0 * abs(phase - 0.5) - 1.0
            elif idx == 2:  # Square
                val = 1.0 if phase < 0.5 else -1.0
            elif idx == 3:  # Saw Up
                val = 2.0 * phase - 1.0
            elif idx == 4:  # Saw Down
                val = 1.0 - 2.0 * phase
            elif idx == 5:  # 3 Step
                val = (math.floor(phase * 3.0) / 1.0) - 1.0
            elif idx == 6:  # 4 Step
                val = (math.floor(phase * 4.0) / 1.5) - 1.0
            elif idx == 7:  # 8 Step
                val = (math.floor(phase * 8.0) / 3.5) - 1.0
            elif idx == 8:  # 3 Pyramid
                p = (phase * 2.0) if phase < 0.5 else (2.0 - phase * 2.0)
                val = (math.floor(p * 3.0) / 1.0) - 1.0
            elif idx == 9:  # 5 Pyramid
                p = (phase * 2.0) if phase < 0.5 else (2.0 - phase * 2.0)
                val = (math.floor(p * 5.0) / 2.0) - 1.0
            elif idx == 10:  # 9 Pyramid
                p = (phase * 2.0) if phase < 0.5 else (2.0 - phase * 2.0)
                val = (math.floor(p * 9.0) / 4.0) - 1.0
            elif idx == 11:  # Sample & Hold
                # 8 discrete steps across the width
                step_idx = int(t * 8)
                pseudo_rand = math.sin(step_idx * 133.7) * 0.9
                val = pseudo_rand
            elif idx == 12:  # Sample & Glide
                step_idx = t * 6
                s0 = math.sin(int(step_idx) * 133.7) * 0.9
                s1 = math.sin((int(step_idx) + 1) * 133.7) * 0.9
                frac = step_idx - int(step_idx)
                smooth = frac * frac * (3.0 - 2.0 * frac)
                val = s0 + (s1 - s0) * smooth

            px = x_start + t * x_span
            py = mid_y - (val * amp)
            pts.append((px, py))

        color = CYAN_ACCENT if idx < 11 else GOLD_ACCENT
        draw_wave(dr, pts, color=color, width=3)
        out_path = os.path.join(IMG_DIR, f"wave_{idx}.png")
        im.save(out_path)
    print("Generated 13 waveform images.")

def generate_envelope_curve(name, color, w=380, h=74):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    dr.rounded_rectangle([0, 0, w - 1, h - 1], radius=6, fill=BG_COLOR, outline=BORDER_COLOR, width=1)
    
    # ADSR Envelope curve
    # Points: start (0, h-10) -> attack peak (w*0.2, 10) -> decay to sustain (w*0.45, h*0.45) -> sustain end (w*0.75, h*0.45) -> release end (w-15, h-10)
    pts = [
        (16, h - 12),
        (int(w * 0.22), 14),
        (int(w * 0.46), int(h * 0.42)),
        (int(w * 0.74), int(h * 0.42)),
        (w - 18, h - 12)
    ]
    # Smooth line
    smooth_pts = []
    for i in range(len(pts) - 1):
        p0, p1 = pts[i], pts[i+1]
        for t in range(25):
            frac = t / 24.0
            # Hermite/Bezier-like smooth interp
            sx = p0[0] + (p1[0] - p0[0]) * frac
            sy = p0[1] + (p1[1] - p0[1]) * (frac * frac * (3 - 2 * frac))
            smooth_pts.append((sx, sy))
            
    # Fill under curve
    poly = [(smooth_pts[0][0], h - 12)] + smooth_pts + [(smooth_pts[-1][0], h - 12)]
    dr.polygon(poly, fill=(color[0], color[1], color[2], 30))
    draw_wave(dr, smooth_pts, color=color, width=2)
    
    # Markers for A, D, S, R
    dr.line([(pts[1][0], 10), (pts[1][0], h - 10)], fill=GRID_COLOR, width=1)
    dr.line([(pts[2][0], 10), (pts[2][0], h - 10)], fill=GRID_COLOR, width=1)
    dr.line([(pts[3][0], 10), (pts[3][0], h - 10)], fill=GRID_COLOR, width=1)
    
    out_path = os.path.join(IMG_DIR, f"env_{name}.png")
    im.save(out_path)
    print(f"Generated {out_path}")

def generate_filter_curve(w=560, h=100):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    dr.rounded_rectangle([0, 0, w - 1, h - 1], radius=8, fill=BG_COLOR, outline=BORDER_COLOR, width=2)
    
    # Draw frequency response curve (low-pass with resonant peak)
    pts = []
    for x in range(16, w - 16):
        t = (x - 16) / float(w - 32)
        # Lowpass filter response approximation with resonance bump around t=0.55
        freq = t * 4.0 - 2.0
        # Peak at t=0.55
        cutoff = 0.55
        dist = t - cutoff
        resonance = math.exp(-(dist * 12.0) ** 2) * 26.0
        rolloff = 1.0 / (1.0 + math.exp((t - cutoff) * 14.0))
        y_val = (h - 22) - (rolloff * (h - 48) + resonance)
        y_clamped = max(12, min(h - 12, y_val))
        pts.append((x, y_clamped))
        
    poly = [(pts[0][0], h - 12)] + pts + [(pts[-1][0], h - 12)]
    dr.polygon(poly, fill=(CYAN_ACCENT[0], CYAN_ACCENT[1], CYAN_ACCENT[2], 35))
    draw_wave(dr, pts, color=CYAN_ACCENT, width=3)
    
    out_path = os.path.join(IMG_DIR, "filter_curve.png")
    im.save(out_path)
    print(f"Generated {out_path}")

def generate_step_grid(w=580, h=100):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    dr.rounded_rectangle([0, 0, w - 1, h - 1], radius=8, fill=BG_COLOR, outline=BORDER_COLOR, width=2)
    
    # 16 step bars
    n_steps = 16
    pad = 14
    avail_w = w - 2 * pad
    step_w = (avail_w - (n_steps - 1) * 4) / n_steps
    
    # Pre-defined rhythmic pattern heights
    pattern = [0.9, 0.3, 0.6, 0.4, 0.85, 0.2, 0.7, 0.5, 1.0, 0.4, 0.65, 0.35, 0.8, 0.5, 0.9, 0.6]
    for i, val in enumerate(pattern):
        bx = pad + i * (step_w + 4)
        bar_h = val * (h - 28)
        by = h - 14 - bar_h
        # Bar glow fill
        dr.rounded_rectangle([bx, by, bx + step_w, h - 14], radius=3, fill=(GOLD_ACCENT[0], GOLD_ACCENT[1], GOLD_ACCENT[2], 180), outline=GOLD_ACCENT, width=1)
        
    out_path = os.path.join(IMG_DIR, "step_grid.png")
    im.save(out_path)
    print(f"Generated {out_path}")

def main():
    generate_waveforms(w=280, h=120)
    generate_envelope_curve("amp", GOLD_ACCENT, w=380, h=72)
    generate_envelope_curve("fil", CYAN_ACCENT, w=380, h=72)
    generate_envelope_curve("mod", GREEN_ACCENT, w=380, h=72)
    generate_filter_curve(w=560, h=110)
    generate_step_grid(w=580, h=110)

if __name__ == "__main__":
    main()
