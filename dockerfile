FROM python:3.11-alpine
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app
COPY etc/req.txt .
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install -r req.txt
COPY . .
CMD ["./run-app.sh"]