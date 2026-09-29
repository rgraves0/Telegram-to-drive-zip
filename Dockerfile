FROM python:3.11-slim

# non-free repository များ ဖွင့်ပြီး CLI Archiving Tools ထည့်သွင်းခြင်း
RUN echo "deb http://deb.debian.org/debian bookworm contrib non-free non-free-firmware" >> /etc/apt/sources.list && \
    apt-get update && apt-get install -y --no-install-recommends \
    p7zip-full \
    unar \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "bot.py"]
