# Judging VM: linux/amd64, 4 GB RAM, 2 vCPU, CPU-only.
# Build (add --platform linux/amd64 on Apple Silicon):
#   docker build --platform linux/amd64 -t <registry>/amd-track1:latest .
FROM python:3.11-slim

WORKDIR /app

# A small 2-3B 4-bit GGUF for the free local path. Override at build with:
#   --build-arg MODEL_URL=https://huggingface.co/.../model.gguf
ARG MODEL_URL=https://huggingface.co/bartowski/Qwen2.5-3B-Instruct-GGUF/resolve/main/Qwen2.5-3B-Instruct-Q4_K_M.gguf

COPY requirements.txt .
# Compile llama-cpp-python from source against glibc (the prebuilt CPU wheels are
# musl-linked and won't load on this Debian base). GGML_NATIVE=OFF + AVX2 keeps the
# binary portable to the grading CPU instead of the build machine's instruction set.
# Build tools are purged afterwards to keep the image small.
RUN apt-get update && apt-get install -y --no-install-recommends build-essential cmake \
 && CMAKE_ARGS="-DGGML_NATIVE=OFF -DGGML_AVX2=ON -DGGML_OPENMP=OFF" pip install --no-cache-dir -r requirements.txt \
 && apt-get purge -y build-essential cmake && apt-get autoremove -y \
 && rm -rf /var/lib/apt/lists/*

# Bake the model in so the container is self-contained and ready fast (<60s).
ADD ${MODEL_URL} /models/local.gguf

COPY agent/ agent/

ENV LOCAL_MODEL_PATH=/models/local.gguf \
    LLAMA_THREADS=2

# One-shot batch: read /input/tasks.json -> answer -> write /output/results.json -> exit.
CMD ["python", "-m", "agent.run"]
