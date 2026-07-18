# 1. Download a tiny, empty Linux computer with Python 3.13 pre-installed
FROM python:3.13-slim

# 2. Tell Linux not to buffer text (so print statements show up immediately)
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# 3. Create a folder inside the Linux box called /app
WORKDIR /app

# 4. Copy ONLY your requirements.txt from your Mac into the Linux box
COPY requirements.txt /app/

# 5. Install the Python packages inside the Linux box
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy the rest of your project (all your code) into the Linux box
COPY . /app/