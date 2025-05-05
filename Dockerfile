FROM python:3.12.7 AS base
WORKDIR /usr/local/app
ENV TZ=Asia/Seoul
COPY ./backend .
RUN pip install --no-cache-dir -r requirements.txt
VOLUME ["/usr/local/app/assets"]

FROM base AS collect
CMD ["python", "-m", "services.collect.main"]

FROM base AS fastapi
EXPOSE 8000
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--log-config", "api/log_conf.yaml"]
