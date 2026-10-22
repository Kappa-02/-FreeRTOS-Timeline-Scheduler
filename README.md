# Deterministic Timeline Scheduler for FreeRTOS

A **five-person university project** extending the bundled FreeRTOS kernel with a time-triggered scheduling policy for **hard and soft real-time tasks**.

Developed for **Operating Systems for Embedded Systems**, **Politecnico di Torino**, academic year **2025–2026**, **Group 36**. The implementation was developed collaboratively.

## Overview

The scheduler selects tasks from a statically configured timeline rather than relying solely on the default priority policy:

- **Hard real-time (HRT):** execution is restricted to configured windows; unfinished work stops running when its window expires.
- **Soft real-time (SRT):** tasks use available time within their configured windows and can be preempted by HRT tasks.
- **Major-frame repetition:** task contexts are reset at the major-frame boundary to restart the cyclic schedule.
- **Early-completion slack:** an HRT task that finishes early can release time for SRT execution.
- **Priority-mode regression:** setting `configUSE_TIMELINE=0` selects the retained priority-based code path.
- **Configuration tooling:** a Python utility validates window definitions and emits a C schedule table and example task bodies.

The supplied target is an **ARM Cortex-M3**, emulated with QEMU's **MPS2-AN385** machine. The bundled kernel reports version **`V11.1.0+`**.

### Team

- Lorenzo Giandomenico
- Alessandro Minutoli
- Mattia Giosa
- Federico Capitani
- Ludovico Rigotti

See the [project report](docs/project-report.pdf) for the original design, implementation details and discussion. The public copy retains all five authors; student registration numbers have been removed.

## Technical focus

**C · FreeRTOS kernel modification · real-time scheduling · task-context reset · preemption · semaphore handling · ARM cross-compilation · QEMU · Python code generation · CI**

The main implementation points are `FreeRTOS-Kernel/tasks.c`, the task API in `include/task.h`, and the configuration interface in `include/timeline.h`.

## Build and run

### Requirements

- Linux, GNU Make and an **Arm GNU embedded toolchain** providing `arm-none-eabi-gcc` and `arm-none-eabi-size`.
- Newlib for the embedded target.
- `qemu-system-arm`.
- Python **3.10 or later** for the test runner and configuration tools; no third-party Python packages are required.

For Debian/Ubuntu:

```bash
sudo apt-get update
sudo apt-get install --no-install-recommends make gcc-arm-none-eabi libnewlib-arm-none-eabi qemu-system-arm python3
```

### Timeline demo

From the repository root:

```bash
make -C Demo clean
make -C Demo all
make -C Demo qemu_start
```

QEMU stays running because the firmware is cyclic. Exit with **Ctrl+A, then X**. UART messages are printed in the terminal.

### Default priority scheduler

```bash
make -C DemoPriority clean
make -C DemoPriority all
make -C DemoPriority qemu_start
```

### Individual timeline scenario

Choose a test number from 1 to 8. Always rebuild after changing it:

```bash
make -C DemoTest clean
make -C DemoTest all EXTRA_CFLAGS="-DTEST_NUMBER=3"
make -C DemoTest qemu_start
```

## Automated verification

```bash
python3 -m unittest discover -s tests -v
python3 scripts/run_tests.py
```

The first command tests JSON validation and result parsing. The second rebuilds and runs the priority scenario and eight timeline scenarios, writing build logs, UART logs and `summary.json` under `artifacts/`.

The runner accepts the expected timeout of continuously running firmware only when a success result is present. A failure marker, a kernel/QEMU fault, an unexpected exit or a missing result fails the scenario, even if `PASSED` also appears elsewhere in the output.

| Scenario | Behaviour exercised |
| --- | --- |
| Priority | Retained default scheduling mode |
| 1 | Overlapping HRT windows |
| 2 | Adjacent windows and preemption |
| 3 | HRT preemption of SRT work |
| 4 | Start-time consistency |
| 5 | Five sequential HRT tasks, checked independently per major frame |
| 6 | Deadline overrun handling |
| 7 | Semaphore release across frame boundaries |
| 8 | Polling through shared state |

To run a subset or change the host timeout:

```bash
python3 scripts/run_tests.py --cases priority,3,6 --timeout 5
```

These are regression and demonstration scenarios on an emulator. They are not a formal timing proof or validation on physical hardware. See [validation notes](docs/VALIDATION.md) for the environment, publication changes and limits.

## Generate an application from JSON

```bash
mkdir -p artifacts
python3 Tools/scheduler_generator.py -c Tools/system_config.json -o artifacts/generated_main.c
make -C Demo clean
make -C Demo all MAIN_SOURCE=../artifacts/generated_main.c
make -C Demo qemu_start
```

The generator checks task identifiers, window bounds, HARD-window overlaps and the fraction of the major frame reserved for HARD windows. It emits placeholder workloads; application-specific task logic must be supplied separately.

The supplied kernel and demo configuration use a **1000-tick major frame** and a **1000 Hz tick rate**. The generator requires these values because it emits task tables, not kernel or tick configuration. [Tool documentation](Tools/README.md) describes the JSON fields and limitations.

## Repository layout

```text
FreeRTOS-Timeline-Scheduler/
├── FreeRTOS-Kernel/          # Bundled kernel and the group's timeline implementation
├── Demo/                    # Timeline application and generated-main build option
├── DemoPriority/            # Priority-mode regression application
├── DemoTest/                # Eight original timeline scenarios
├── Tools/                   # JSON schedule validation and C generation
├── scripts/run_tests.py     # Shared QEMU test runner
├── tests/                   # Python regression tests
├── docs/
│   ├── project-report.pdf
│   ├── VALIDATION.md
│   └── legacy/              # Original GitLab Runner setup, retained for reference
├── .github/workflows/       # GitHub Actions test workflow
├── .gitlab-ci.yml           # Shared-runner entry point for a configured GitLab runner
├── Dockerfile              # Optional local toolchain environment
└── LICENSE
```

## CI and optional container environment

The GitHub workflow installs the cross toolchain and QEMU, runs the Python and firmware scenarios, builds a generated application, and uploads the logs. The GitLab entry point uses the same runner and expects its build dependencies to be installed.

For a local container environment:

```bash
docker build -t freertos-timeline .
docker run --rm -v "$PWD:/workspace" freertos-timeline
```

The root Dockerfile needs no GitLab registration. The original runner recipe is kept under `docs/legacy/gitlab-runner/` as historical project material.

## Licence and upstream attribution

The original project's [GNU GPL v3 licence](LICENSE) is retained. The bundled upstream FreeRTOS code retains its [MIT licence](FreeRTOS-Kernel/LICENSE.md) and existing copyright notices. Existing per-file notices are preserved.
