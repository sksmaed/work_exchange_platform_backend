# Deployment Guide (Docker + GitHub Actions)

This guide deploys the backend to a remote Linux server and enables automatic deployment when code is pushed to `main`.

## 1. Files added for production

- `docker-compose.prod.yml`
- `.env.production.example`
- `.github/workflows/deploy.yml`

## 2. Prepare server (one-time)

1. Install Docker and Docker Compose Plugin.
1. Clone this repository to your server, for example:

```sh
git clone <your-repo-url>
cd work_exchange_platform_backend
```

1. Copy environment template and edit secrets:

```sh
cp .env.production.example .env.production
```

1. (Optional) First manual start to verify (set APP_IMAGE first):

```sh
export APP_IMAGE=ghcr.io/<your-org>/<your-repo>:latest
docker compose -f docker-compose.prod.yml up -d
```

## 3. GitHub repository secrets

Create these secrets in GitHub Actions settings:

- `DEPLOY_HOST`: server IP or domain
- `DEPLOY_USER`: ssh user
- `DEPLOY_SSH_KEY`: private key content used by Actions to connect server
- `DEPLOY_PATH`: absolute path on server, e.g. `/home/ubuntu/work_exchange_platform_backend`
- `GHCR_USERNAME`: username for pulling image from ghcr.io
- `GHCR_TOKEN`: PAT with `read:packages`
- `ENV_PRODUCTION`: full content of `.env.production` (multi-line)

## 4. Auto deploy flow

When pushing to `main`:

1. GitHub Actions builds Docker image.
2. Image is pushed to `ghcr.io`.
3. Workflow connects to server via SSH.
4. Server pulls latest image and runs:

```sh
docker compose -f docker-compose.prod.yml up -d --remove-orphans
```

## 5. Notes

- Current app listens on port `8000`; place Nginx/Caddy in front for TLS in production.
- If PostgreSQL or Valkey is managed externally, update `.env.production` and `docker-compose.prod.yml` accordingly.
- The workflow is fully automatic; you no longer need manual `ssh -> git pull -> docker restart`.
