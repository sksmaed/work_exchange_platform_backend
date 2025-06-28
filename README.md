# work_for_exchange_system_backend

work for exchange system backend in Django

## How to Start to Develop

1. Install `uv` and `Python 3.13` via the Python package manager.

    For Windows:

    ```sh
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    ```

    For Linux and macOS:

    ```sh
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

    Install Python 3.13 (actually Python 3.13.5 will be installed):

    ```sh
    uv python install 3.13
    ```

2. Create a virtual environment and activate it:

    ```sh
    uv venv --python 3.13
    .venv\Scripts\activate
    ```

3. Set up the `dotenv/.env` file

4. Build and run the docker container:

    ```sh
    docker-compose --env-file dotenv/.env up --build -d
    ```

5. For the first time running the backend system, you need to create a superuser.

    ```sh
    docker-compose exec app python manage.py createsuperuser
    ```

6. visit <http:localhost:8000> and login to Django admin system.
