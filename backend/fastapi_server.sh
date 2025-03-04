#!/bin/bash

case "$1" in
  dev)
    echo "Starting FastAPI in development mode..."
    .venv/bin/uvicorn main:app --host 127.0.0.1 --port 8001 --reload --log-config log_conf_dev.yaml
    ;;
  start)
    echo "Starting FastAPI in production mode..."
    .venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000 --log-config log_conf.yaml & disown
    ;;
  terminate)
    echo "Stopping FastAPI server..."
    kill $(ps -ef | grep 'uvicorn\smain:app\s--host\s127.0.0.1\s--port\s8000' | awk '{print $2}')
    ;;
  restart)
    echo "Restarting FastAPI server..."
    kill $(ps -ef | grep 'uvicorn\smain:app\s--host\s127.0.0.1\s--port\s8000' | awk '{print $2}')
    .venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000 --log-config log_conf.yaml & disown
    ;;
  *)
    echo "Usage: $0 {dev|start|terminate|restart}"
    exit 1
    ;;
esac