# Judging VM runs linux/amd64. Build with:
#   docker build --platform linux/amd64 -t <registry>/amd-track1:latest .
# (the --platform flag matters only if you build on Apple Silicon.)
FROM --platform=linux/amd64 python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY agent/ agent/

# One-shot batch: read /input/tasks.json -> answer via Fireworks -> write
# /output/results.json -> exit. Not a long-running server.
CMD ["python", "-m", "agent.run"]
