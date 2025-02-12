#!/bin/bash

case "$1" in
  dev)
    echo "Starting FastAPI in development mode..."
    uvicorn main:app --host 127.0.0.1 --port 8001 --reload
    ;;
  start)
    echo "Starting FastAPI in production mode..."
    uvicorn main:app --host 0.0.0.0 --port 8000 --log-config log_conf.yaml & disown
    ;;
  terminate)
    echo "Stopping FastAPI server..."
    kill $(ps -ef | grep 'uvicorn\smain:app' | awk '{print $2}')
    ;;
  *)
    echo "Usage: $0 {dev|start|terminate}"
    exit 1
    ;;
esac