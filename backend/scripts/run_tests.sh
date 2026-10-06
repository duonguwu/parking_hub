#!/usr/bin/env bash
# Chạy pytest trong Docker (server không cài Python deps), dùng Mongo/Redis của infra stack.
# Dữ liệu test nằm trong DB riêng `parkinghub_test` (Redis DB 15) — không đụng dữ liệu thật.
# Usage: bash scripts/run_tests.sh [pytest args]
set -e
cd "$(dirname "$0")/.."
ENV_FILE=.env.production
MP=$(grep -E '^MONGO_PASSWORD=' $ENV_FILE | cut -d= -f2-)
RP=$(grep -E '^REDIS_PASSWORD=' $ENV_FILE | cut -d= -f2-)
docker run --rm --network host \
  -v "$PWD":/app -w /app \
  -v parkinghub-test-venv:/venv \
  -e UV_LINK_MODE=copy -e UV_PROJECT_ENVIRONMENT=/venv \
  -e TEST_MONGO_URI="mongodb://admin:${MP}@127.0.0.1:27017/parkinghub_test?authSource=admin" \
  -e TEST_REDIS_URL="redis://:${RP}@127.0.0.1:6379/15" -e COOKIE_SECURE=false \
  ghcr.io/astral-sh/uv:python3.12-bookworm-slim \
  sh -c "uv sync --frozen -q && uv run --frozen pytest ${*:-test -q}"
