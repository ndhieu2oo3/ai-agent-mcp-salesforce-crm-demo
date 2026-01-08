#!/bin/bash
set -e

echo "======================================"
echo " AI Agent MCP Demo - Run Script"
echo "======================================"

# -------- CONFIG --------
ENV_NAME="agent-demo"
PYTHON_VERSION="3.10"
MODEL_PATH="./model/Qwen3-4B-Instruct-2507"
MODEL_NAME="Qwen3-4B-Instruct-2507"
VLLM_PORT=8001
APP_PORT=8000
CUDA_DEVICE=1
# ------------------------

echo "[1/6] Checking conda environment..."

if ! conda info --envs | grep -q "$ENV_NAME"; then
  echo "Conda env not found. Creating $ENV_NAME..."
  conda create -n $ENV_NAME python=$PYTHON_VERSION -y
else
  echo "Conda env $ENV_NAME already exists."
fi

echo "[2/6] Activating conda environment..."
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate $ENV_NAME

echo "[3/6] Installing dependencies..."
pip install --upgrade pip
pip install -r ./requirements.txt > ./log/install.log 2>&1
echo "Dependencies installed."

echo "[4/6] Running setup script..."
python3 ./set_up.py

echo "[5/6] Starting vLLM server..."

set +e
curl -s http://localhost:$VLLM_PORT/v1/models > /dev/null
VLLM_RUNNING=$?
set -e

if [ $VLLM_RUNNING -eq 0 ]; then
  echo "vLLM server is already running on port $VLLM_PORT. Reusing it."
else
  echo "vLLM not running. Starting new vLLM server..."

  CUDA_VISIBLE_DEVICES=$CUDA_DEVICE \
  python3 -m vllm.entrypoints.openai.api_server \
    --model $MODEL_PATH \
    --served-model-name $MODEL_NAME \
    --port $VLLM_PORT \
    --gpu-memory-utilization 0.8 \
    --max-model-len 1000 \
    > ./log/vllm.log 2>&1 &

  VLLM_PID=$!
  echo "vLLM started (PID=$VLLM_PID)"
  echo "Waiting for vLLM to be ready..."
  sleep 10
fi

echo "[6/6] Starting Agent application..."
python3 -m app.main &

APP_PID=$!
echo "======================================"
echo " Demo is running"
echo "--------------------------------------"
echo " LLM API   : http://localhost:$VLLM_PORT"
echo " Agent UI  : http://localhost:$APP_PORT"
echo " vLLM log  : vllm.log"
echo "--------------------------------------"
echo " Press Ctrl+C to stop"
echo "======================================"

trap "echo 'Stopping...'; kill $VLLM_PID $APP_PID" SIGINT SIGTERM
wait
