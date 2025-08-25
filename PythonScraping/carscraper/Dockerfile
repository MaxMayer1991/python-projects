FROM python:3.13-slim

LABEL org.opencontainers.image.authors="Maksym Plakushko <mplakushko@gmail.com>" \
      org.opencontainers.image.url="https://github.com/MaxMayer1991/carscraper" \
      org.opencontainers.image.description="Docker образ для Scrapy проєкту AutoriaScraper" \
      org.opencontainers.image.version="1.0.0"

# Встановлюємо системні залежності
RUN apt-get update && apt-get install -y \
    gnupg2 curl wget unzip xvfb \
    gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Додаємо ключ Google Chrome через gpg
RUN curl -fsSL https://dl.google.com/linux/linux_signing_key.pub \
    | gpg --dearmor -o /usr/share/keyrings/google-chrome-keyring.gpg

# Додаємо репозиторій Chrome
RUN echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome-keyring.gpg] \
    http://dl.google.com/linux/chrome/deb/ stable main" \
    > /etc/apt/sources.list.d/google-chrome.list

# Встановлюємо Google Chrome
RUN apt-get update && \
    apt-get install -y google-chrome-stable && \
    rm -rf /var/lib/apt/lists/*

# Встановлюємо ChromeDriver через новий JSON API
RUN CHROME_VERSION=$(google-chrome --product-version | cut -d. -f1-3) && \
    echo "Chrome version: $CHROME_VERSION" && \
    CHROMEDRIVER_VERSION=$(curl -s "https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_${CHROME_VERSION%%.*}") && \
    echo "ChromeDriver version: $CHROMEDRIVER_VERSION" && \
    wget -O /tmp/chromedriver.zip \
      "https://storage.googleapis.com/chrome-for-testing-public/${CHROMEDRIVER_VERSION}/linux64/chromedriver-linux64.zip" && \
    unzip /tmp/chromedriver.zip -d /tmp && \
    mv /tmp/chromedriver-linux64/chromedriver /usr/local/bin/ && \
    chmod +x /usr/local/bin/chromedriver && \
    rm -rf /tmp/chromedriver* && \
    chromedriver --version
# Встановлюємо робочий каталог
WORKDIR /app

# Копіюємо та встановлюємо залежності
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо весь проект
COPY . .

# Створюємо папки для логів і даних
RUN mkdir -p /app/logs /app/data && \
    chmod 755 /app/logs /app/data

# Встановлюємо змінні середовища для Chrome
ENV DISPLAY=:99
ENV PYTHONPATH=/app

# За замовчуванням запускаємо scheduler
CMD ["python3", "scheduler.py"]