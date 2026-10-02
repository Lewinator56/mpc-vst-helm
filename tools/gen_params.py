#!/usr/bin/env python3
"""Generate params.json for mpc-vst-helm including all Helm parameters,
preset selection, and an 8-slot modulation matrix.
"""
import json
import os

SOURCES = [
    "None",
    "Mono LFO 1",
    "Mono LFO 2",
    "Poly LFO",
    "Step Sequencer",
    "Amp Envelope",
    "Filter Envelope",
    "Mod Envelope",
    "Random",
    "Velocity",
    "Key Track",
    "Mod Wheel",
    "Pitch Wheel",
    "Aftertouch"
]

DESTINATIONS = [
    "None",
    "Filter Cutoff",
    "Filter Resonance",
    "Filter Drive",
    "Filter Blend",
    "Filter Env Depth",
    "Osc 1 Waveform",
    "Osc 1 Transpose",
    "Osc 1 Tune",
    "Osc 1 Volume",
    "Osc 1 Unison Detune",
    "Osc 2 Waveform",
    "Osc 2 Transpose",
    "Osc 2 Tune",
    "Osc 2 Volume",
    "Osc 2 Unison Detune",
    "Cross Modulation",
    "Osc Feedback Amount",
    "Sub Waveform",
    "Sub Shuffle",
    "Sub Volume",
    "Noise Volume",
    "Master Volume",
    "Distortion Drive",
    "Distortion Mix",
    "Delay Frequency",
    "Delay Feedback",
    "Delay Dry/Wet",
    "Reverb Feedback",
    "Reverb Damping",
    "Reverb Dry/Wet",
    "Stutter Frequency",
    "Stutter Softness",
    "Formant X",
    "Formant Y",
    "Mono LFO 1 Rate",
    "Mono LFO 1 Amp",
    "Mono LFO 2 Rate",
    "Mono LFO 2 Amp",
    "Poly LFO Rate",
    "Poly LFO Amp",
    "Step Rate",
    "Amp Attack",
    "Amp Decay",
    "Amp Sustain",
    "Amp Release",
    "Filter Attack",
    "Filter Decay",
    "Filter Sustain",
    "Filter Release",
    "Mod Attack",
    "Mod Decay",
    "Mod Sustain",
    "Mod Release"
]

WAVEFORMS_13 = [
    "Sine", "Triangle", "Square", "Saw Up", "Saw Down",
    "3 Step", "4 Step", "8 Step", "3 Pyramid", "5 Pyramid", "9 Pyramid",
    "Sample & Hold", "Sample & Glide"
]

WAVEFORMS_11 = WAVEFORMS_13[:11]

SYNCED_FREQS = [
    "32/1", "16/1", "8/1", "4/1", "2/1", "1/1",
    "1/2", "1/4", "1/8", "1/16", "1/32", "1/64"
]

FREQ_SYNC_STYLES = ["Seconds", "Tempo", "Tempo Dot", "Tempo Trip"]
RETRIGGER_STYLES = ["Free", "Retrigger", "Playhead"]
OFF_ON = ["Off", "On"]
FILTER_STYLES = ["12dB", "24dB", "Shelf"]
FILTER_SHELVES = ["Low Shelf", "Band Shelf", "High Shelf"]
ARP_PATTERNS = ["Up", "Down", "Up-Down", "As Played", "Random"]
DISTORTION_TYPES = ["Soft Clip", "Hard Clip", "Linear Fold", "Sine Fold"]
PORTAMENTO_TYPES = ["Always", "Legato", "Off"]


def build_params():
    params = []

    # 1. Preset Navigation
    params.extend([
        {
            "key": "preset",
            "name": "Preset",
            "min": 0,
            "max": 300,
            "default": 0,
            "display": "int",
            "type": "stepper"
        },
        {
            "key": "preset_prev",
            "name": "Prev Preset",
            "min": 0,
            "max": 1,
            "momentary": True,
            "step_of": "preset",
            "step_delta": -1
        },
        {
            "key": "preset_next",
            "name": "Next Preset",
            "min": 0,
            "max": 1,
            "momentary": True,
            "step_of": "preset",
            "step_delta": 1
        },
        {
            "key": "patch_name",
            "name": "Patch Name",
            "display": "string",
            "type": "readout"
        },
        {
            "key": "folder_name",
            "name": "Category",
            "display": "string",
            "type": "readout"
        },
        {
            "key": "author",
            "name": "Author",
            "display": "string",
            "type": "readout"
        }
    ])

    # 2. Master / Global
    params.extend([
        {"key": "volume", "name": "Master Volume", "min": 0.0, "max": 1.414, "default": 0.707},
        {"key": "polyphony", "name": "Polyphony", "min": 1, "max": 16, "default": 6, "display": "int", "unit": "v"},
        {"key": "legato", "name": "Legato", "options": OFF_ON, "default": 0},
        {"key": "portamento", "name": "Portamento", "min": -9.0, "max": -1.0, "default": -7.0, "unit": "s/oct"},
        {"key": "portamento_type", "name": "Portamento Type", "options": PORTAMENTO_TYPES, "default": 0},
        {"key": "pitch_bend_range", "name": "Pitch Bend Range", "min": 0, "max": 48, "default": 2, "display": "int", "unit": "st"},
        {"key": "velocity_track", "name": "Velocity Track", "min": -1.0, "max": 1.0, "default": 0.0, "unit": "%"}
    ])

    # 3. Oscillators
    params.extend([
        # Osc 1
        {"key": "osc_1_waveform", "name": "Osc 1 Wave", "options": WAVEFORMS_11, "default": 4},
        {"key": "osc_1_transpose", "name": "Osc 1 Transpose", "min": -48, "max": 48, "default": 0, "display": "int", "unit": "st"},
        {"key": "osc_1_tune", "name": "Osc 1 Tune", "min": -1.0, "max": 1.0, "default": 0.0, "unit": "ct"},
        {"key": "osc_1_volume", "name": "Osc 1 Volume", "min": 0.0, "max": 1.0, "default": 0.548},
        {"key": "osc_1_unison_voices", "name": "Osc 1 Unison Voices", "min": 1, "max": 15, "default": 1, "display": "int", "unit": "v"},
        {"key": "osc_1_unison_detune", "name": "Osc 1 Unison Detune", "min": 0.0, "max": 100.0, "default": 10.0, "unit": "ct"},
        {"key": "unison_1_harmonize", "name": "Osc 1 Harmonize", "options": OFF_ON, "default": 0},

        # Cross mod & Feedback
        {"key": "cross_modulation", "name": "Cross Mod", "min": 0.0, "max": 0.5, "default": 0.0, "unit": "%"},
        {"key": "osc_feedback_amount", "name": "Feedback Amount", "min": -1.0, "max": 1.0, "default": 0.0, "unit": "%"},
        {"key": "osc_feedback_transpose", "name": "Feedback Transpose", "min": -24, "max": 24, "default": 0, "display": "int", "unit": "st"},
        {"key": "osc_feedback_tune", "name": "Feedback Tune", "min": -1.0, "max": 1.0, "default": 0.0, "unit": "ct"},

        # Osc 2
        {"key": "osc_2_waveform", "name": "Osc 2 Wave", "options": WAVEFORMS_11, "default": 4},
        {"key": "osc_2_transpose", "name": "Osc 2 Transpose", "min": -48, "max": 48, "default": 0, "display": "int", "unit": "st"},
        {"key": "osc_2_tune", "name": "Osc 2 Tune", "min": -1.0, "max": 1.0, "default": 0.0, "unit": "ct"},
        {"key": "osc_2_volume", "name": "Osc 2 Volume", "min": 0.0, "max": 1.0, "default": 0.548},
        {"key": "osc_2_unison_voices", "name": "Osc 2 Unison Voices", "min": 1, "max": 15, "default": 1, "display": "int", "unit": "v"},
        {"key": "osc_2_unison_detune", "name": "Osc 2 Unison Detune", "min": 0.0, "max": 100.0, "default": 10.0, "unit": "ct"},
        {"key": "unison_2_harmonize", "name": "Osc 2 Harmonize", "options": OFF_ON, "default": 0},

        # Sub & Noise
        {"key": "sub_waveform", "name": "Sub Wave", "options": WAVEFORMS_11, "default": 2},
        {"key": "sub_octave", "name": "Sub Octave Down", "options": OFF_ON, "default": 0},
        {"key": "sub_shuffle", "name": "Sub Shuffle", "min": 0.0, "max": 1.0, "default": 0.0, "unit": "%"},
        {"key": "sub_volume", "name": "Sub Volume", "min": 0.0, "max": 1.0, "default": 0.0},
        {"key": "noise_volume", "name": "Noise Volume", "min": 0.0, "max": 1.0, "default": 0.0}
    ])

    # 4. Filter
    params.extend([
        {"key": "filter_on", "name": "Filter On", "options": OFF_ON, "default": 1},
        {"key": "filter_style", "name": "Filter Style", "options": FILTER_STYLES, "default": 0},
        {"key": "filter_shelf", "name": "Filter Shelf", "options": FILTER_SHELVES, "default": 0},
        {"key": "cutoff", "name": "Cutoff", "min": 28.0, "max": 127.0, "default": 80.0, "unit": "st"},
        {"key": "resonance", "name": "Resonance", "min": 0.0, "max": 1.0, "default": 0.5, "unit": "%"},
        {"key": "filter_drive", "name": "Filter Drive", "min": -12.0, "max": 20.0, "default": 0.0, "unit": "dB"},
        {"key": "filter_blend", "name": "Filter Blend", "min": 0.0, "max": 2.0, "default": 0.0},
        {"key": "fil_env_depth", "name": "Filter Env Depth", "min": -128.0, "max": 128.0, "default": 0.0, "unit": "st"},
        {"key": "keytrack", "name": "Key Track", "min": -1.0, "max": 1.0, "default": 0.0, "unit": "%"},

        # Formant filter
        {"key": "formant_on", "name": "Formant On", "options": OFF_ON, "default": 0},
        {"key": "formant_x", "name": "Formant X", "min": 0.0, "max": 1.0, "default": 0.5},
        {"key": "formant_y", "name": "Formant Y", "min": 0.0, "max": 1.0, "default": 0.5}
    ])

    # 5. Envelopes
    params.extend([
        # Amp Env
        {"key": "amp_attack", "name": "Amp Attack", "min": 0.0, "max": 4.0, "default": 0.1, "unit": "s"},
        {"key": "amp_decay", "name": "Amp Decay", "min": 0.0, "max": 4.0, "default": 1.5, "unit": "s"},
        {"key": "amp_sustain", "name": "Amp Sustain", "min": 0.0, "max": 1.0, "default": 1.0},
        {"key": "amp_release", "name": "Amp Release", "min": 0.0, "max": 4.0, "default": 0.3, "unit": "s"},

        # Filter Env
        {"key": "fil_attack", "name": "Filter Attack", "min": 0.0, "max": 4.0, "default": 0.0, "unit": "s"},
        {"key": "fil_decay", "name": "Filter Decay", "min": 0.0, "max": 4.0, "default": 1.5, "unit": "s"},
        {"key": "fil_sustain", "name": "Filter Sustain", "min": 0.0, "max": 1.0, "default": 0.5},
        {"key": "fil_release", "name": "Filter Release", "min": 0.0, "max": 4.0, "default": 1.5, "unit": "s"},

        # Mod Env
        {"key": "mod_attack", "name": "Mod Attack", "min": 0.0, "max": 4.0, "default": 0.0, "unit": "s"},
        {"key": "mod_decay", "name": "Mod Decay", "min": 0.0, "max": 4.0, "default": 1.5, "unit": "s"},
        {"key": "mod_sustain", "name": "Mod Sustain", "min": 0.0, "max": 1.0, "default": 0.5},
        {"key": "mod_release", "name": "Mod Release", "min": 0.0, "max": 4.0, "default": 1.5, "unit": "s"}
    ])

    # 6. LFOs
    params.extend([
        # Mono LFO 1
        {"key": "mono_lfo_1_waveform", "name": "Mono LFO 1 Wave", "options": WAVEFORMS_13, "default": 0},
        {"key": "mono_lfo_1_amplitude", "name": "Mono LFO 1 Amp", "min": -1.0, "max": 1.0, "default": 1.0},
        {"key": "mono_lfo_1_frequency", "name": "Mono LFO 1 Rate", "min": -7.0, "max": 6.0, "default": 1.0, "unit": "s"},
        {"key": "mono_lfo_1_sync", "name": "Mono LFO 1 Sync", "options": FREQ_SYNC_STYLES, "default": 1},
        {"key": "mono_lfo_1_tempo", "name": "Mono LFO 1 Tempo", "options": SYNCED_FREQS, "default": 6},
        {"key": "mono_lfo_1_retrigger", "name": "Mono LFO 1 Retrigger", "options": RETRIGGER_STYLES, "default": 2},

        # Mono LFO 2
        {"key": "mono_lfo_2_waveform", "name": "Mono LFO 2 Wave", "options": WAVEFORMS_13, "default": 0},
        {"key": "mono_lfo_2_amplitude", "name": "Mono LFO 2 Amp", "min": -1.0, "max": 1.0, "default": 1.0},
        {"key": "mono_lfo_2_frequency", "name": "Mono LFO 2 Rate", "min": -7.0, "max": 6.0, "default": 1.0, "unit": "s"},
        {"key": "mono_lfo_2_sync", "name": "Mono LFO 2 Sync", "options": FREQ_SYNC_STYLES, "default": 1},
        {"key": "mono_lfo_2_tempo", "name": "Mono LFO 2 Tempo", "options": SYNCED_FREQS, "default": 7},
        {"key": "mono_lfo_2_retrigger", "name": "Mono LFO 2 Retrigger", "options": RETRIGGER_STYLES, "default": 2},

        # Poly LFO
        {"key": "poly_lfo_waveform", "name": "Poly LFO Wave", "options": WAVEFORMS_13, "default": 0},
        {"key": "poly_lfo_amplitude", "name": "Poly LFO Amp", "min": -1.0, "max": 1.0, "default": 1.0},
        {"key": "poly_lfo_frequency", "name": "Poly LFO Rate", "min": -7.0, "max": 6.0, "default": 1.0, "unit": "s"},
        {"key": "poly_lfo_sync", "name": "Poly LFO Sync", "options": FREQ_SYNC_STYLES, "default": 1},
        {"key": "poly_lfo_tempo", "name": "Poly LFO Tempo", "options": SYNCED_FREQS, "default": 7}
    ])

    # 7. Step Sequencer & Arpeggiator
    params.extend([
        # Step Sequencer controls
        {"key": "num_steps", "name": "Num Steps", "min": 1, "max": 32, "default": 8, "display": "int"},
        {"key": "step_smoothing", "name": "Step Smoothing", "min": 0.0, "max": 0.5, "default": 0.0},
        {"key": "step_frequency", "name": "Step Rate", "min": -5.0, "max": 6.0, "default": 2.0, "unit": "s"},
        {"key": "step_sequencer_sync", "name": "Step Sync", "options": FREQ_SYNC_STYLES, "default": 1},
        {"key": "step_sequencer_tempo", "name": "Step Tempo", "options": SYNCED_FREQS, "default": 7},
        {"key": "step_sequencer_retrigger", "name": "Step Retrigger", "options": RETRIGGER_STYLES, "default": 2},

        # Arpeggiator controls
        {"key": "arp_on", "name": "Arp On", "options": OFF_ON, "default": 0},
        {"key": "arp_pattern", "name": "Arp Pattern", "options": ARP_PATTERNS, "default": 0},
        {"key": "arp_octaves", "name": "Arp Octaves", "min": 1, "max": 4, "default": 1, "display": "int", "unit": "oct"},
        {"key": "arp_gate", "name": "Arp Gate", "min": 0.0, "max": 1.0, "default": 0.5, "unit": "%"},
        {"key": "arp_frequency", "name": "Arp Rate", "min": -1.0, "max": 4.0, "default": 2.0, "unit": "s"},
        {"key": "arp_sync", "name": "Arp Sync", "options": FREQ_SYNC_STYLES, "default": 1},
        {"key": "arp_tempo", "name": "Arp Tempo", "options": SYNCED_FREQS, "default": 9}
    ])

    # 8. Effects
    params.extend([
        # Distortion
        {"key": "distortion_on", "name": "Distortion On", "options": OFF_ON, "default": 0},
        {"key": "distortion_type", "name": "Distortion Type", "options": DISTORTION_TYPES, "default": 0},
        {"key": "distortion_drive", "name": "Distortion Drive", "min": -30.0, "max": 30.0, "default": 0.0, "unit": "dB"},
        {"key": "distortion_mix", "name": "Distortion Mix", "min": 0.0, "max": 1.0, "default": 1.0},

        # Delay
        {"key": "delay_on", "name": "Delay On", "options": OFF_ON, "default": 0},
        {"key": "delay_frequency", "name": "Delay Time", "min": -2.0, "max": 5.0, "default": 2.0, "unit": "s"},
        {"key": "delay_sync", "name": "Delay Sync", "options": FREQ_SYNC_STYLES, "default": 1},
        {"key": "delay_tempo", "name": "Delay Tempo", "options": SYNCED_FREQS, "default": 9},
        {"key": "delay_feedback", "name": "Delay Feedback", "min": -1.0, "max": 1.0, "default": 0.4, "unit": "%"},
        {"key": "delay_dry_wet", "name": "Delay Mix", "min": 0.0, "max": 1.0, "default": 0.5, "unit": "%"},

        # Reverb
        {"key": "reverb_on", "name": "Reverb On", "options": OFF_ON, "default": 0},
        {"key": "reverb_feedback", "name": "Reverb Feedback", "min": 0.8, "max": 1.0, "default": 0.9, "unit": "%"},
        {"key": "reverb_damping", "name": "Reverb Damping", "min": 0.0, "max": 1.0, "default": 0.5},
        {"key": "reverb_dry_wet", "name": "Reverb Mix", "min": 0.0, "max": 1.0, "default": 0.5, "unit": "%"},

        # Stutter
        {"key": "stutter_on", "name": "Stutter On", "options": OFF_ON, "default": 0},
        {"key": "stutter_frequency", "name": "Stutter Time", "min": 0.0, "max": 7.0, "default": 3.0, "unit": "s"},
        {"key": "stutter_sync", "name": "Stutter Sync", "options": FREQ_SYNC_STYLES, "default": 1},
        {"key": "stutter_tempo", "name": "Stutter Tempo", "options": SYNCED_FREQS, "default": 8},
        {"key": "stutter_softness", "name": "Stutter Softness", "min": 0.0, "max": 1.0, "default": 0.2, "unit": "%"},
        {"key": "stutter_resample_frequency", "name": "Resample Time", "min": -7.0, "max": 4.0, "default": 1.0, "unit": "s"},
        {"key": "stutter_resample_sync", "name": "Resample Sync", "options": FREQ_SYNC_STYLES, "default": 1},
        {"key": "stutter_resample_tempo", "name": "Resample Tempo", "options": SYNCED_FREQS, "default": 6}
    ])

    # 9. Modulation Matrix (8 Slots)
    for slot in range(1, 9):
        params.extend([
            {
                "key": f"mod_{slot}_source",
                "name": f"Mod {slot} Source",
                "options": SOURCES,
                "default": 0
            },
            {
                "key": f"mod_{slot}_dest",
                "name": f"Mod {slot} Dest",
                "options": DESTINATIONS,
                "default": 0
            },
            {
                "key": f"mod_{slot}_amount",
                "name": f"Mod {slot} Depth",
                "min": -1.0,
                "max": 1.0,
                "default": 0.0,
                "unit": "%"
            }
        ])

    sections = [
        {
            "label": "Main & Presets",
            "keys": ["preset", "preset_prev", "preset_next", "patch_name", "folder_name", "author", "volume", "polyphony", "legato", "portamento", "portamento_type", "pitch_bend_range", "velocity_track"]
        },
        {
            "label": "Oscillator 1",
            "keys": ["osc_1_waveform", "osc_1_transpose", "osc_1_tune", "osc_1_volume", "osc_1_unison_voices", "osc_1_unison_detune", "unison_1_harmonize", "cross_modulation"]
        },
        {
            "label": "Oscillator 2",
            "keys": ["osc_2_waveform", "osc_2_transpose", "osc_2_tune", "osc_2_volume", "osc_2_unison_voices", "osc_2_unison_detune", "unison_2_harmonize", "osc_feedback_amount", "osc_feedback_transpose", "osc_feedback_tune"]
        },
        {
            "label": "Sub & Noise",
            "keys": ["sub_waveform", "sub_octave", "sub_shuffle", "sub_volume", "noise_volume"]
        },
        {
            "label": "Filter",
            "keys": ["filter_on", "filter_style", "filter_shelf", "cutoff", "resonance", "filter_drive", "filter_blend", "fil_env_depth", "keytrack", "formant_on", "formant_x", "formant_y"]
        },
        {
            "label": "Amp Envelope",
            "keys": ["amp_attack", "amp_decay", "amp_sustain", "amp_release"]
        },
        {
            "label": "Filter Envelope",
            "keys": ["fil_attack", "fil_decay", "fil_sustain", "fil_release"]
        },
        {
            "label": "Mod Envelope",
            "keys": ["mod_attack", "mod_decay", "mod_sustain", "mod_release"]
        },
        {
            "label": "Mono LFO 1",
            "keys": ["mono_lfo_1_waveform", "mono_lfo_1_amplitude", "mono_lfo_1_frequency", "mono_lfo_1_sync", "mono_lfo_1_tempo", "mono_lfo_1_retrigger"]
        },
        {
            "label": "Mono LFO 2",
            "keys": ["mono_lfo_2_waveform", "mono_lfo_2_amplitude", "mono_lfo_2_frequency", "mono_lfo_2_sync", "mono_lfo_2_tempo", "mono_lfo_2_retrigger"]
        },
        {
            "label": "Poly LFO",
            "keys": ["poly_lfo_waveform", "poly_lfo_amplitude", "poly_lfo_frequency", "poly_lfo_sync", "poly_lfo_tempo"]
        },
        {
            "label": "Arpeggiator",
            "keys": ["arp_on", "arp_pattern", "arp_octaves", "arp_gate", "arp_frequency", "arp_sync", "arp_tempo"]
        },
        {
            "label": "Step Sequencer",
            "keys": ["num_steps", "step_smoothing", "step_frequency", "step_sequencer_sync", "step_sequencer_tempo", "step_sequencer_retrigger"]
        },
        {
            "label": "Distortion",
            "keys": ["distortion_on", "distortion_type", "distortion_drive", "distortion_mix"]
        },
        {
            "label": "Stutter",
            "keys": ["stutter_on", "stutter_frequency", "stutter_sync", "stutter_tempo", "stutter_softness", "stutter_resample_frequency", "stutter_resample_sync", "stutter_resample_tempo"]
        },
        {
            "label": "Delay & Reverb",
            "keys": ["delay_on", "delay_frequency", "delay_sync", "delay_tempo", "delay_feedback", "delay_dry_wet", "reverb_on", "reverb_feedback", "reverb_damping", "reverb_dry_wet"]
        },
        {
            "label": "Mod Matrix 1-4",
            "keys": ["mod_1_source", "mod_1_dest", "mod_1_amount", "mod_2_source", "mod_2_dest", "mod_2_amount", "mod_3_source", "mod_3_dest", "mod_3_amount", "mod_4_source", "mod_4_dest", "mod_4_amount"]
        },
        {
            "label": "Mod Matrix 5-8",
            "keys": ["mod_5_source", "mod_5_dest", "mod_5_amount", "mod_6_source", "mod_6_dest", "mod_6_amount", "mod_7_source", "mod_7_dest", "mod_7_amount", "mod_8_source", "mod_8_dest", "mod_8_amount"]
        }
    ]

    return params, sections


if __name__ == "__main__":
    params, sections = build_params()
    data = {
        "name": "Helm",
        "params": params,
        "sections": sections
    }
    out_path = os.path.join(os.path.dirname(__file__), "..", "params.json")
    with open(out_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Wrote {len(params)} parameters across {len(sections)} sections to {out_path}")
