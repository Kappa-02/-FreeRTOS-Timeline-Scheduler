FROM debian:bookworm-slim
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       make python3 gcc-arm-none-eabi libnewlib-arm-none-eabi qemu-system-arm \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /workspace
CMD ["python3", "scripts/run_tests.py"]
