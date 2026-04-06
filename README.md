# work_for_exchange_system_backend

work for exchange system backend in Django

## How to Start to Develop

1. Install `uv` and `Python 3.13` via the Python package manager.
  For Windows:
    For Linux and macOS:
    Install Python 3.13 (actually Python 3.13.5 will be installed):
2. Create a virtual environment and activate it:
  ```sh
    uv venv --python 3.13
    .venv\Scripts\activate
  ```
3. Set up the `.env` file
4. Build and run the docker container:
  ```sh
    docker-compose up --build -d
  ```
5. synchronize the packages for this project.
  ```sh
    uv sync
  ```
6. Apply migrations to database.
  ```sh
    python manage.py migrate
  python manage.py runserver   

  ```
7. visit [http:localhost:8000](http:localhost:8000) and login to Django admin system.

## Note

- For the first time setting up Django service, you should create the superuser

    ```sh
    python manage.py createsuperuser
    ```

## Production Deployment

- See `docs/deployment_guide.md` for Docker-based server deployment and GitHub Actions auto deployment setup.
