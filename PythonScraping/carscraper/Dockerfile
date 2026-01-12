# Використовуємо стабільну версію Python на базі Debian Bookworm
FROM python:3.11-slim-bookworm

WORKDIR /app

# 1. Встановлюємо мінімальні системні утиліти (для pip та збірки)
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# 2. Спочатку копіюємо requirements і ставимо бібліотеки Python
# Це дозволяє кешувати цей шар, щоб не перекачувати все при зміні коду
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3. ВАЖЛИВО: Встановлюємо Playwright браузери ТА системні залежності автоматично
# --with-deps встановлює всі ті бібліотеки (libgtk, libasound і т.д.), які у вас падали
RUN playwright install --with-deps chromium

# 4. Копіюємо весь код проекту
COPY . .

# Запуск
CMD ["python3", "scheduler.py"]