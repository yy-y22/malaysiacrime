# Official Python 2.7 slim image
FROM python:2.7-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /malaysiacrime

# Install core runtime dependencies
COPY requirements.txt /malaysiacrime/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . /malaysiacrime/

EXPOSE 8000

# Ensure settings.py and SQLite DB exist even when ./:/app is mounted, then run server
CMD ["sh", "-c", "cp -n settings_default.py settings.py && python manage.py syncdb --noinput && python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]