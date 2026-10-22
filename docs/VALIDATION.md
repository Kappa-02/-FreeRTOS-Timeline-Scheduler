# Validation and publication notes

## Local environment

Validation date: **22 October 2026**.

- Native Linux execution.
- Arm embedded GCC **16.2.0**.
- QEMU **11.1.2**, `mps2-an385`, `cortex-m3`.
- Python **3.14** for the configuration and runner tests.

## Scope of verification

- The original priority application and eight timeline scenarios were built and executed in QEMU.
- The stricter shared runner rejects mixed success/failure output, faults, missing results and unexpected process exits.
- Python tests exercise configuration rejection and runner verdicts.
- The C application generated from `Tools/system_config.json` was cross-compiled through `Demo/Makefile` using `MAIN_SOURCE`.

Generated logs are local build artefacts under `artifacts/`; CI uploads its own logs on each run. The GitHub workflow has not been represented as remotely passing before its first actual execution. The optional Docker image has not been built during this local validation.

## Changes made when preparing this portfolio copy

- Replaced the long historical README with setup, architecture, examples and team attribution.
- Preserved all bundled kernel source bytes and upstream copyright/licence files.
- Added a shared QEMU runner and GitHub workflow; the GitLab entry point calls the same runner.
- Removed a misleading `TEST PASSED` print from the deadline test's failure branch.
- Corrected scenario 5's fixture: its former 100-tick delay occupied its entire 100-tick slot, leaving no margin for dispatch and UART output. This intermittently failed the first frame. It now uses 80 ticks, checks completion order, and resets its completion count at each report so later frames cannot mask a failure.
- Added JSON schema checks needed to produce compilable task declarations, guarded the fixed kernel timing parameters, and made output-write errors fail the generator command.
- Added `MAIN_SOURCE` to the timeline demo build so a generated application can be compiled without overwriting the hand-written demo.
- Collected the report under `docs/`, removing student registration numbers from the public copy while retaining all author names.

## Limits

The scenarios provide practical regression coverage, not exhaustive verification of scheduler behaviour. Workloads include demonstration delays and UART output, so results depend on the selected emulator/toolchain and test parameters. Existing compile warnings remain visible in the build logs.

Task-context reset does not automatically restore arbitrary shared/global application data. Application state and resource policies still need to be designed for the cyclic task model. Window feasibility and reserved-window utilisation do not establish WCET bounds or prove schedulability on physical hardware.
