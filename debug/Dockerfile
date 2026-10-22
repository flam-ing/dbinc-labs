FROM python:3.13-slim
WORKDIR /app
RUN useradd --create-home learner && mkdir /data && chown learner:learner /data
COPY app.py ./
COPY static ./static
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 GUESTBOOK_HOST=0.0.0.0 GUESTBOOK_DB=/data/guestbook.sqlite3
USER learner
EXPOSE 8000
CMD ["python", "app.py"]
