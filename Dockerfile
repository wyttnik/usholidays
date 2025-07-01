FROM python:3.12.9-slim

RUN pip install uv

WORKDIR /app

COPY requirements.lock ./

RUN uv pip install --no-cache --system -r requirements.lock

COPY prestart.sh ./
COPY src/usholidays ./

ENTRYPOINT [ "./prestart.sh" ]

CMD [ "python", "main.py" ]
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]