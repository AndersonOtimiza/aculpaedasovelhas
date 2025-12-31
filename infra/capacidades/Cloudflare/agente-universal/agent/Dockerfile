FROM python:3.11-slim

# Dependencias de sistema para HTTP, Playwright e CLI
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl git ca-certificates build-essential libssl-dev libffi-dev python3-dev \
    wget unzip fonts-liberation xvfb libnss3 libatk1.0-0 libatk-bridge2.0-0 \
    libxkbcommon0 libdrm2 libgbm1 libxcomposite1 libxdamage1 libxrandr2 libasound2 \
    openssh-client jq \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -U pip \
 && pip install --no-cache-dir -r /app/requirements.txt

# Instala navegadores Playwright (Chromium)
RUN python -m playwright install --with-deps chromium

COPY app /app/app

# Instala Node.js e npm
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
RUN apt-get install -y nodejs

# Instala dependências do agente Node.js para que possa ser chamado pelo agente Python
COPY package.json /app/
COPY package-lock.json /app/
COPY wp-intelligent-agent.js /app/
COPY .env.op /app/
RUN npm install

ENV PYTHONUNBUFFERED=1
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
