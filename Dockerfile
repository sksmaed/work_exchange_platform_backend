FROM python:3.13-slim

WORKDIR /app

# install uv 
RUN pip install --no-cache-dir uv

# copy requirements.txt
COPY ./requirements.txt .

# install dependencies
RUN uv pip install --system --no-cache-dir --upgrade pip setuptools wheel \
   && uv pip install --system --no-cache-dir -r requirements.txt

# copy the rest of the application code
COPY . .

# copy the entrypoint script
COPY docker-entrypoint/django-entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# expose the port the app runs on
EXPOSE 8000 

# set the entrypoint
ENTRYPOINT ["/entrypoint.sh"]

# set the command to run the application
CMD ["gunicorn", "config.asgi:application", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--workers", "4"]
