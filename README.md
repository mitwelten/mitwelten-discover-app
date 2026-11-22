# Mitwelten Discover App

https://discover.mitwelten.org/

## Setup

Requires Python 3.13.

```bash
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Configure Keycloak and the public URL in `.env` (or as environment variables):

```bash
KC_SERVER_URL=https://auth.your-domain.org/auth/
KC_CLIENT_ID=client-id
KC_REALM_NAME=realm
DOMAIN_NAME=http://localhost:8000
```

## Running

```bash
source .venv/bin/activate
./start-server.sh   # http://localhost:8000/app/
./run-tests.sh
```

## Dependency Upgrade Procedure

The image contains Python, the dependencies and the app code.

- [`requirements.in`](requirements.in): direct dependencies, edit this file when installing new packages
- [`requirements.txt`](requirements.txt): fully pinned lock file, generated from `requirements.in` (needs `uv`, see below)

1. Re-resolve all dependencies to their latest versions (for the Python version and platform of the image):

    ```bash
    uv pip compile requirements.in -o requirements.txt --python-version 3.13 --python-platform x86_64-manylinux_2_28 --upgrade
    ```

    To bump the Python version, change `FROM python:3.13-slim` in the [`Dockerfile`](Dockerfile) and `--python-version` above.

    Dash Mantine Components requires a specific React version, which is set with `_set_react_version` in [`src/main.py`](src/main.py).
    When it gets a major upgrade, check its [migration guide](https://www.dash-mantine-components.com/migration).

2. Test locally (see above): load the map, open a drawer of each data type, a note with images, and trigger a notification (e.g. *Add a new Note* while logged out).

3. Build, scan and push the image (`--pull` gets the latest base image with its security fixes):

    ```bash
    docker build --pull --platform linux/amd64 -t discover-app:test .
    trivy image --severity HIGH,CRITICAL --ignore-unfixed discover-app:test
    ```

    Push by tagging a release (`git tag <major.minor> && git push origin <major.minor>`; the GitHub workflow builds and pushes `<tag>` and `latest`),
    or manually with [`build-docker.sh`](build-docker.sh) `<tag>`.

4. On the server, pull and recreate the `mitwelten-discover` container.
