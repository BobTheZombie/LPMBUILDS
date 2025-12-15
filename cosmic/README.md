# COSMIC packaging notes

This repository now includes LPM build scripts for key COSMIC desktop components:

- `cosmic-comp`: Wayland compositor built on `wlroots` with PipeWire screen casting support.
- `cosmic-panel`: Panel and dock implementation.
- `cosmic-settings`: Graphical settings utility.
- `cosmic-launcher`: Application launcher.
- `cosmic-greeter`: Login and lock screen greeter for the session.

## Source references
All component sources are pulled directly from the upstream Pop!_OS COSMIC repositories using the `epoch-1.0.0` tag:

- https://github.com/pop-os/cosmic-comp
- https://github.com/pop-os/cosmic-panel
- https://github.com/pop-os/cosmic-settings
- https://github.com/pop-os/cosmic-launcher
- https://github.com/pop-os/cosmic-greeter

## Build and dependency guidance

Each build script:

- Declares the Rust toolchain (`rust`, `cargo`, `clang`) and GNOME stack (`gtk4`, `libadwaita`) that the upstream crates expect.
- Pulls in Wayland dependencies such as `wlroots`, `wayland-protocols`, `libxkbcommon`, `libinput`, and PipeWire where appropriate.
- Runs `cargo fetch --locked` followed by `cargo vendor vendor` in `prepare()` to lock the crate set for reproducible, offline builds against system libraries.
- Leaves `PATCHES` empty; no downstream fixes are currently required for system libraries, but the array is ready for future compatibility adjustments.

## Recommended meta package

Install `cosmic-session` to pull in the full desktop experience in one transaction. The meta package depends on the compositor, panel, settings app, launcher, and greeter while also recommending the Wayland stack pieces (`wlroots`, `pipewire`) needed to run the session.
