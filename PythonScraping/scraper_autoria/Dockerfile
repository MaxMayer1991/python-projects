FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

WORKDIR /app

# Об'єднуємо оновлення і встановлення тільки того, чого немає в базовому образі
# Базовий образ playwright вже має Python, pip, і купу ліб для браузера
RUN apt-get update && apt-get install -y \
    openssh-server \
    postgresql-client \
    tzdata \
    # Інші бібліотеки (libnss3, libatk і т.д.) вже є в playwright install-deps або в самому образі
    && rm -rf /var/lib/apt/lists/*

# Налаштування SSH
RUN mkdir -p /var/run/sshd && \
    echo 'root:root' | chpasswd && \
    sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Playwright
# Встановлюємо лише браузер (deps вже є, або якщо треба - розкоментуйте install-deps)
RUN playwright install firefox
# RUN playwright install-deps # Спробуйте закоментувати це, якщо зависає, часто це зайве для цього образу

COPY . .

EXPOSE 22

CMD service ssh start && python3 scheduler.py