# mpc-vst-helm

Native VST2 port of the [Helm](https://tytel.org/helm/) polyphonic synthesizer for Akai MPC OS standalone devices (MPC Live, MPC One, MPC X, MPC Key, Force), built using [mpc-vst-plugins](https://github.com/sd88me/mpc-vst-plugins).

## Overview

Helm is a free, polyphonic synthesizer with:
- 32-voice polyphony
- 2 main oscillators with cross-modulation + 1 sub oscillator + noise
- Multi-mode resonant filter with key tracking and drive
- 3 LFOs, 3 envelopes (Amp, Filter, Mod)
- 32-step sequencer & arpeggiator
- Distortion, Reverb, Delay, and Stutter effects
- Extensive modulation routing

This port brings the full Helm synthesis engine directly into MPC OS as a native track instrument with custom touch screen UI and hardware Q-Link mapping.

The entire of the HELM engine is exposed here, with the caveat being that I have only exposed 8 modulation slots, however the plugin will load and run presets with more than 8 modulation connections.

# screenshots

## Presets
Allows you to browse through presets, you may add more under the preset folder in the plugin folder on the MPC.

<img width="1280" height="800" alt="image" src="https://github.com/user-attachments/assets/1743d001-89ab-4a8d-9606-e8a299f23eb4" />

## Performance control and mixer

<img width="1280" height="800" alt="image" src="https://github.com/user-attachments/assets/e930794f-51ff-41e2-b4fa-5b7932664777" />

## Oscillators
All 3 oscilators have all their parameters exposed. HELM is quite efficient too, so dont be afraid to turn up the unison voices for the oscillators, ive not got over 30% CPU usage even with a really thick supersaw.

<img width="1280" height="800" alt="image" src="https://github.com/user-attachments/assets/b537127a-22e6-4e21-b9f1-48e473c892b8" />

## Filter

<img width="1280" height="800" alt="image" src="https://github.com/user-attachments/assets/c2546832-f408-45bc-ba9e-d17248e67a7c" />

## Envelopes
These are drawn in real time, the [MPC Plaits plugin](https://github.com/poloq-instruments/mpc-vst-plaits) was used to help with this

<img width="1280" height="800" alt="image" src="https://github.com/user-attachments/assets/62e68117-2600-4d3d-90dc-0dc1b7eea446" />

## LFOs

<img width="1280" height="800" alt="image" src="https://github.com/user-attachments/assets/d8533798-e4e4-4836-bee1-8b8a86a1f7b7" />

## Step sequencer
All 32 steps that the desktop version of HELM can use. Depending on the lenght you have set, not all will be read. the Q links are mapped to the first 16 and second 16 steps respectively. 

<img width="1280" height="800" alt="image" src="https://github.com/user-attachments/assets/50614909-ccff-4e02-9b14-c1dcfc147117" />

## Mod matrix
8 Modulation slots with amount scaled to the parameter type (HELM internally routes based on the parameter type, but obviously thats not possible here as it would require dynamic assignment, instead the amount is scaled between the min and max of the target)

<img width="1280" height="800" alt="image" src="https://github.com/user-attachments/assets/c0bcbb6e-d7d8-4e0a-94e8-b34791edd48e" />

## FX

<img width="1280" height="800" alt="image" src="https://github.com/user-attachments/assets/19554b8d-9bd7-4d1c-bfe5-739801521e9e" />

# Notes
This was built with the assistance of AI, however there are multiple handmade changes to code, the UI etc...

# Installing
Install from the [MPC plugin catalog](https://sd88me.github.io/mpc-vst-plugins/), or manually build and install it, or download the release.

## Setup prior to install
SSH access is required, if you dont have it, the following steps can be used. This is easiest to do on WSL. 

### Prerequisites
- [mpcimg](https://github.com/TheKikGen/MPC-LiveXplore/tree/master/imgmaker/bin)
- usbipd-win `

1. download the latest MPC firmware USB image
2. Extract the rootfs from the image using the 










## License

GPL-3.0 (see `LICENSE`). Helm is copyright Matt Tytel.
