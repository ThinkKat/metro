#!/bin/bash

case "$1" in
  start)
    echo "Starting FastAPI in production mode..."
    .venv/bin/python main.py & disown
    ;;
  terminate)
    echo "Stopping FastAPI server..."
    kill $(ps -ef | grep '.venv/bin/python\smain.py' | awk '{print $2}')
    ;;
  restart)
    echo "Restarting FastAPI server..."
    kill $(ps -ef | grep '.venv/bin/python\smain.py' | awk '{print $2}')
    .venv/bin/python main.py & disown
    ;;
  check)
    ps -ef | grep '.venv/bin/python\smain.py'
    ;;
  *)
    echo "Usage: $0 {dev|terminate|restart|check}"
    exit 1
    ;;
esac