FROM python:3.11-slim

# p7zip နဲ့ unrar/rar tool များ ထည့်သွင်းခြင်း
RUN apt-get update && apt-get install -y \
    p7zip-full \
    p7zip-rar \
    rar \
    unrar \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "bot.py"]
