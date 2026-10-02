# Vendored Upstream: Helm Polyphonic Synthesizer

- **Upstream Repository**: https://github.com/mtytel/helm
- **Commit**: `abdedd527e6e1cf86636f0f1e8a3e75b06ed166a`
- **Date**: 2018-07-08
- **Author**: Matt Tytel
- **License**: GNU General Public License v3.0 (see `LICENSE`)

## Vendored Components

1. **`src/dsp/mopo/`** (from `mopo/src/`):
   - Pure C++ modular polyphonic synthesizer library.
   - Includes oscillators, ladder/SVF/biquad filters, envelopes, LFOs, arpeggiator, delay, reverb, distortion, stutter, step generator, and routing infrastructure.
   - Zero JUCE or platform-specific GUI dependencies.

2. **`src/dsp/synthesis/`** (from `src/synthesis/`):
   - Helm-specific synth modules: `HelmEngine`, `HelmVoiceHandler`, `HelmLfo`, `HelmOscillators`, `FixedPointOscillator`, `DcFilter`, `ResonanceCancel`, `PeakMeter`, `TriggerRandom`, `ValueSwitch`.
   - Pure C++ DSP.

3. **`src/dsp/common/`** (from `src/common/`):
   - `helm_common.h` and `helm_common.cpp`: Contains the ~115 parameter definitions (`ValueDetailsLookup::parameter_list`), option strings, and parameter metadata.

4. **`patches/Factory Presets/`** (from `patches/Factory Presets/`):
   - Factory presets organized by category (`Arp`, `Bass`, `Chip`, `Harsh`, `Keys`, `Lead`, `Pad`, `Percussion`, `SFX`).

## Local Modifications

- Clean import from upstream commit `abdedd527e6e1cf86636f0f1e8a3e75b06ed166a`.
- All GUI, JUCE library code (`JuceLibraryCode/`, `JUCE/`), VST/AU wrapper code, and build files (`Makefile`, `.jucer`) excluded in favor of `mpc-vst-plugins` wrapper and TUI skinning.
