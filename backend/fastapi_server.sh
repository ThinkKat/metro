#!/bin/bash

case "$1" in
  dev)
    echo "Starting FastAPI in development mode..."
    /home/cathink8210/projects/metro/backend/.venv/bin/uvicorn main:app --host 127.0.0.1 --port 8001 --reload --log-config log_conf_dev.yaml
    ;;
  start)
    echo "Starting FastAPI in production mode..."
    /home/cathink8210/projects/metro/backend/.venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --log-config log_conf.yaml & disown
    ;;
  terminate)
    echo "Stopping FastAPI server..."
    kill $(ps -ef | grep 'uvicorn\smain:app' | awk '{print $2}')
    ;;
  restart)
    echo "Restarting FastAPI server..."
    kill $(ps -ef | grep 'uvicorn\smain:app' | awk '{print $2}') && /home/cathink8210/projects/metro/backend/.venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --log-config log_conf.yaml & disown
    ;;
  *)
    echo "Usage: $0 {dev|start|terminate}"
    exit 1
    ;;
esac