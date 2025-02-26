# 🚀 FastAPI Starter

This repo contains are starter template for FastAPI applications. The project structure may feel a bit opionionated where it matters, but it's flexible enough and follows the repository pattern.

## 💡Motivation

I found myself spending countless hours to setup my FastAPI projects over and over again whenever i needed to run a production-grade application. Authentication, Databases, and other features became a pain to repeatedly setup so I decided to create this template to take away the effort and time wasted.

## 📌 Features

-   **🔄 Modular CRUD System** – Reusable base for all entities
-   **🔑 OAuth Authentication** – Google login included, extendable to other providers
-   **📄 Auto-generated OpenAPI Docs** – `/docs` and `/redoc`
-   **📦 Docker Support** – Preconfigured `Dockerfile` & `docker-compose`
-   **🗄️ SQLModel ORM** – A hybrid of SQLAlchemy and Pydantic, all your models and schemas as one entity
-   **🛠️ Background Tasks** – Async task execution support
-   **🔒 JWT-Based Authentication** – Secure access control
-   **✅ Pre-configured Linting & Formatting** – Uses `ruff`

## 📂 Project Structure

```
fastapi-starter/
│── data/                      # Data storage
│── docker-compose.yaml        # Docker setup
│── docker-compose.override.yaml
│── Dockerfile                 # Containerization
│── Makefile                   # Task automation
│── pyproject.toml             # Dependency management
│── README.md                  # Documentation
│── run.sh                     # Script to start the application
│── uv.lock                    # Dependency lock file
│── src/                       # Application source code
│   ├── api/                   # API route definitions
│   ├── core/                  # Core configurations & settings
│   ├── models/                # Database models using SQLModel
│   ├── repositories/          # Database interaction logic
│   ├── services/              # Business logic
│   ├── utils/                 # Utility functions
│   ├── main.py                # Application entry point
│   ├── __init__.py
│   ├── __pycache__/
```

## 🚀 Installation & Setup

### 1️⃣ Clone the Repository

```sh
git clone https://github.com/yourusername/fastapi-starter.git
cd fastapi-starter
```

### 2️⃣ Set Up a Virtual Environment with `uv`

```sh
uv venv .venv
source .venv/bin/activate  # On macOS/Linux
.venv\Scripts\activate     # On Windows
```

### 3️⃣ Install Dependencies

```sh
uv sync
```

### 4️⃣ Set Up Pre-commit Hooks

```sh
pre-commit install
```

**Why?** This ensures comprehensive checks **before commits** to maintain code quality.

### 5️⃣ Generate Self-Signed Certificates

```bash
make certs
```

### 6️⃣ Start the Application

```sh
./run.sh
```

### 7️⃣ Access API Documentation

-   📜 OpenAPI: [http://localhost:8000/docs](http://localhost:8000/docs)
-   📜 Redoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## 🔄 Detaching from the Original Repo

If you cloned this repo but want to use it as your own **without linking to ours** , run:

```sh
rm -rf .git
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

## 🏗️ CRUD System

The `items` endpoints serve as a **base template for all CRUD-like entities** . To add a new resource, simply:

1. **Copy the `items` endpoints**
2. **Modify the entity models**
3. **Adjust the repository and service logic**
4. **Register the endpoint in the base router**

This ensures consistency across all API resources while reducing development time.

### 🔑 Authentication

### Authentication Endpoints

-   **POST** `/auth/signup` – Register a new user
-   **POST** `/auth/login` – Log in to get a JWT token
-   **POST** `/auth/login/access-token` – Get OAuth access token
-   **GET** `/auth/{provider}/init` – Initiate OAuth login with Google or another provider. Visit OAuth provider developer page to obtain details.
-   **GET** `/auth/{provider}/callback` – Handle OAuth callback. Set callback url to `https://`

## 🐳 Running with Docker

```sh
docker-compose up --build
```

## 🛠️ Development

### Running Linting & Formatting (`ruff`)

```sh
ruff check
# fix linting issues
ruff check --fix
ruff format
```

## Deployment

### Nginx Setup

1. Generate ssl certificates with a trusted certificates authority or use a self-signed certificate by running the oppenssl command below

    ```sh
    openssl req -x509 -noenc -days 365 -newkey rsa:2048 -keyout nginx/certs/server.key -out nginx/certs/server.crt
    ```

    The certificates will be generated and placed in the `nginx` directory. However, place these in the `/etc/ssl` directory during deployment.

2. Uncomment the line that rewrites the http request to port 8443 since it wont be needed in production.
3. Copy the nginx configuration to `/etc/nginx/sites-available` to run the nginx server.
   `NB: this stressful configuration won't really be needed after integrating an IaaC tool, lol😅`

Get to know more about ssl certificates [here](https://www.digitalocean.com/community/tutorials/how-to-create-a-self-signed-ssl-certificate-for-nginx-in-ubuntu-20-04-1 "Creating Self-Signed Certificates").
