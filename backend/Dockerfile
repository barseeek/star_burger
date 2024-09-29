FROM python:3.10
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . /app
RUN SECRET_KEY=something python manage.py collectstatic --noinput

CMD ["python", "-m", "gunicorn", "-b", "0.0.0.0:8080", "star_burger.wsgi:application"]
