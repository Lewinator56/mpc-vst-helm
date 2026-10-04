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

def generate_adsr_strips(slot=120, frames=128, color=(56, 197, 197, 255), fill_bg=(24, 29, 34, 255)):
    top = 10
    bottom = slot - 10
    
    def y_level(l):
        return bottom - (bottom - top) * l
        
    def time_width(n):
        return slot * max(0.03, n ** 0.4)
        
    def curve_pts(x0, w, falling, steps=24):
        k = 4.0
        pts = []
        for i in range(steps + 1):
            t = i / float(steps)
            v = (1.0 - math.exp(-k * t)) / (1.0 - math.exp(-k))
            y = y_level(1.0 - v if falling else v)
            pts.append((x0 + t * w, y))
        return pts

    layers = ("attack", "decay", "sustain", "release", "below", "above")
    for layer in layers:
        im = Image.new("RGBA", (slot, slot * frames), (0, 0, 0, 0))
        dr = ImageDraw.Draw(im)
        for i in range(frames):
            n = i / float(frames - 1)
            y_off = i * slot
            
            if layer == "attack":
                w = time_width(n)
                x0 = slot - w
                c_pts = curve_pts(x0, w, False)
                pts = [(0, y_off + y_level(0))] + [(p[0], y_off + p[1]) for p in c_pts]
                dr.line(pts, fill=color, width=3)
            elif layer == "decay":
                w = time_width(n)
                c_pts = curve_pts(0, w, True)
                full_curve = [(p[0], y_off + p[1]) for p in c_pts] + [(slot, y_off + y_level(0))]
                poly = full_curve + [(slot, y_off + slot), (0, y_off + slot)]
                dr.polygon(poly, fill=fill_bg)
                dr.line(full_curve, fill=color, width=3)
            elif layer == "sustain":
                y = y_off + y_level(n)
                dr.line([(0, y), (slot, y)], fill=color, width=3)
            elif layer == "below":
                y = y_off + y_level(n)
                dr.rectangle([0, y + 2, slot, y_off + slot], fill=fill_bg)
            elif layer == "release":
                w = time_width(n)
                c_pts = curve_pts(0, w, True)
                full_curve = [(p[0], y_off + p[1]) for p in c_pts] + [(slot, y_off + y_level(0))]
                poly = full_curve + [(slot, y_off), (0, y_off)]
                dr.polygon(poly, fill=fill_bg)
                dr.line(full_curve, fill=color, width=3)
            elif layer == "above":
                y = y_off + y_level(n)
                dr.rectangle([0, y_off, slot, max(y_off, y - 2)], fill=fill_bg)
                
        out_path = os.path.join(IMG_DIR, f"env_{layer}.png")
        im.save(out_path)
        print(f"Generated ADSR filmstrip {out_path} ({slot}x{slot * frames})")

def generate_filter_filmstrip(w=520, h=120, frames=128):
    im = Image.new("RGBA", (w, h * frames), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    
    for i in range(frames):
        t = i / float(frames - 1)
        y_off = i * h
        
        # Screen panel
        dr.rounded_rectangle([0, y_off, w - 1, y_off + h - 1], radius=6, fill=BG_COLOR, outline=BORDER_COLOR, width=1)
        
        # Grid lines
        for gx in range(40, w - 20, 50):
            dr.line([(gx, y_off + 8), (gx, y_off + h - 8)], fill=GRID_COLOR, width=1)
        dr.line([(10, y_off + h // 2), (w - 10, y_off + h // 2)], fill=GRID_COLOR, width=1)
        
        # Dynamic filter response curve
        cutoff_x = 24 + t * (w - 48)
        pts = []
        for x in range(16, w - 16):
            dx = (x - cutoff_x) / 32.0
            resonance = math.exp(-(dx * dx) * 0.9) * 26.0
            rolloff = 1.0 / (1.0 + math.exp(dx * 2.8))
            y_val = (y_off + h - 16) - (rolloff * (h - 46) + resonance)
            y_clamped = max(y_off + 8, min(y_off + h - 10, y_val))
            pts.append((x, y_clamped))
            
        poly = [(pts[0][0], y_off + h - 10)] + pts + [(pts[-1][0], y_off + h - 10)]
        dr.polygon(poly, fill=(CYAN_ACCENT[0], CYAN_ACCENT[1], CYAN_ACCENT[2], 30))
        draw_wave(dr, pts, color=CYAN_ACCENT, width=3)
        
    out_path = os.path.join(IMG_DIR, "filter_curve.png")
    im.save(out_path)
    print(f"Generated filter filmstrip {out_path} ({w}x{h * frames})")

def generate_step_fader_strip(w=74, h=360, frames=45):
    im = Image.new("RGBA", (w, h * frames), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    
    for i in range(frames):
        t = i / float(frames - 1)
        y_off = i * h
        
        # Step column background (dark graphite)
        dr.rectangle([0, y_off, w - 1, y_off + h - 1], fill=(26, 28, 33, 255), outline=(16, 17, 20, 255), width=1)
        
        # Horizontal subtle grid lines
        for gy in range(40, h - 20, 40):
            dr.line([(4, y_off + gy), (w - 5, y_off + gy)], fill=(34, 37, 44, 255), width=1)
            
        bar_y = int(y_off + (1.0 - t) * (h - 20) + 8)
        
        # Fill below step value (dark grey/gunmetal fill)
        if bar_y < y_off + h - 8:
            dr.rectangle([3, bar_y, w - 4, y_off + h - 6], fill=(42, 46, 56, 255))
            
        # Glowing green horizontal indicator bar
        glow_bar = (GREEN_ACCENT[0], GREEN_ACCENT[1], GREEN_ACCENT[2], 80)
        dr.rounded_rectangle([2, bar_y - 2, w - 3, bar_y + 7], radius=2, fill=glow_bar)
        dr.rounded_rectangle([3, bar_y, w - 4, bar_y + 5], radius=2, fill=(38, 231, 100, 255))
        
    out_path = os.path.join(IMG_DIR, "step_fader.png")
    im.save(out_path)
    print(f"Generated step fader filmstrip {out_path} ({w}x{h * frames})")

def generate_mixer_fader_strip(w=56, h=200, frames=80):
    im = Image.new("RGBA", (w, h * frames), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    
    for i in range(frames):
        t = i / float(frames - 1)
        y_off = i * h
        
        # Fader well
        dr.rounded_rectangle([6, y_off + 4, w - 7, y_off + h - 5], radius=4, fill=(16, 18, 22, 255), outline=(35, 39, 48, 255), width=1)
        
        # Value position
        bar_y = int(y_off + (1.0 - t) * (h - 24) + 10)
        
        # Fill from bottom up
        if bar_y < y_off + h - 8:
            dr.rounded_rectangle([9, bar_y, w - 10, y_off + h - 8], radius=2, fill=(210, 216, 228, 255))
            
        # Top white cap
        dr.rounded_rectangle([4, max(y_off + 4, bar_y - 4), w - 5, min(y_off + h - 4, bar_y + 5)], radius=3, fill=(245, 250, 255, 255), outline=(59, 240, 255, 255), width=1)
        
    out_path = os.path.join(IMG_DIR, "mixer_fader.png")
    im.save(out_path)
    print(f"Generated mixer fader filmstrip {out_path} ({w}x{h * frames})")

def main():
    generate_waveforms(w=280, h=120)
    generate_adsr_strips(slot=120, frames=128, color=(56, 197, 197, 255), fill_bg=(24, 29, 34, 255))
    generate_filter_filmstrip(w=520, h=120, frames=128)
    generate_step_fader_strip(w=74, h=360, frames=45)
    generate_mixer_fader_strip(w=56, h=200, frames=80)
    generate_envelope_curve("amp", GOLD_ACCENT, w=380, h=72)
    generate_envelope_curve("fil", CYAN_ACCENT, w=380, h=72)
    generate_envelope_curve("mod", GREEN_ACCENT, w=380, h=72)

if __name__ == "__main__":
    main()

