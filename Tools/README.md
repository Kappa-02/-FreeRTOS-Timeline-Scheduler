# Schedule configuration and C generation

`scheduler_generator.py` validates a JSON schedule and emits a C application using `TimelineTaskConfig_t` and `vConfigureScheduler`. It uses only the Python standard library.

From the repository root:

```bash
mkdir -p artifacts
python3 Tools/scheduler_generator.py -c Tools/system_config.json -o artifacts/generated_main.c
make -C Demo clean
make -C Demo all MAIN_SOURCE=../artifacts/generated_main.c
make -C Demo qemu_start
```

Stop QEMU with Ctrl+A, then X.

## Supported configuration

| Field | Meaning |
| --- | --- |
| `system_name` | Label printed by the generated application |
| `timeline_period` | Must be `1000`, matching the bundled kernel's fixed major frame |
| `tick_rate_hz` | Must be `1000`, matching the bundled demos' `FreeRTOSConfig.h` |
| `tasks` | Non-empty task list |
| `name` | Unique C identifier |
| `type` | `HARD` or `SOFT` |
| `start_tick`, `end_tick` | Integer window boundaries, with `0 <= start < end <= 1000` |
| `stack_size` | Positive stack size in words; defaults to `128` |

HARD windows must not overlap. SOFT windows may overlap HARD windows because SOFT execution is preemptible. The reported HARD utilisation is the fraction of the major frame reserved by configured windows; it is **not measured CPU load or a WCET schedulability proof**.

The generator creates task tables and placeholder workloads. It does not change the kernel period, tick configuration or implement sensor/actuator drivers. Invalid configurations and output-write failures return a nonzero process status.

`generated_main.c` is the original generated example retained from the group project. Use `artifacts/generated_main.c` for local regeneration to keep build output separate from tracked source.
