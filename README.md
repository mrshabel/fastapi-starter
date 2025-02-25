# 🚀 FastAPI Production Starter

Bored out of countless hours spent repeatedly setting up new projects, this template is my solution to the "not another project setup" syndrome. It's a carefully crafted FastAPI starter that comes with everything you need to go from idea to production, without the usual headaches.

## 💡 Why This Template?

Ever found yourself:

-   Spending days setting up the same project structure... again?
-   Copying authentication code from your last project?
-   Wondering about the "right way" to structure your FastAPI app?
-   Needing to add monitoring but not sure where to start?

Yeah, me too. That's exactly why this template exists. It's opinionated where it matters, flexible where you need it, and comes with batteries included.

## 📌 Features

-   **🔄 Modular CRUD System** – Reusable base for all entities
-   **🔑 OAuth Authentication** – Google login included, extendable to other providers
-   **📄 Auto-generated OpenAPI Docs** – `/docs` and `/redoc`
-   **📦 Docker Support** – Preconfigured `Dockerfile` & `docker-compose`
-   **🗄️ SQLModel ORM** – A hybrid of SQLAlchemy and Pydantic
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

### 5️⃣ Start the Application

```sh
./run.sh
```

### 6️⃣ Access API Documentation

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
2. **Modify the entity model & schema**
3. **Adjust the repository logic**

This ensures consistency across all API resources while reducing development time.

### Base CRUD Endpoints

-   **POST** `/items/` – Create a new entity
-   **GET** `/items/` – Retrieve all entities
-   **GET** `/items/{id}/` – Retrieve a single entity by ID
-   **PATCH** `/items/{id}/` – Update an entity
-   **DELETE** `/items/{id}/` – Delete an entity

## 🔑 Authentication

### OAuth2 Login (Google & Other Providers)

-   **Google OAuth support is built-in** and **easily extensible** to other providers.
-   Supports **OAuth2 Authorization Code Flow** .

#### Authentication Endpoints

-   **POST** `/auth/signup` – Register a new user
-   **POST** `/auth/login` – Log in to get a JWT token
-   **POST** `/auth/login/access-token` – Get OAuth access token
-   **GET** `/auth/{provider}/init` – Initiate OAuth login with Google or another provider
-   **GET** `/auth/{provider}/callback` – Handle OAuth callback

#### Extending OAuth to New Providers

To add a new provider (e.g., GitHub, Facebook, etc.), modify the `OAuthProvider` schema and update the authentication flow in the **auth service** .

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

## 🎯 Contributing

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/feature-name`)
3. **Commit changes** (`git commit -m "feat: add feature"`)
4. **Push to branch** (`git push origin feature/feature-name`)
5. **Open a Pull Request**

## 🔮 Future Updates

| Feature Proposal          | Status         |
| ------------------------- | -------------- |
| API Gateway support       | ⏳ In Progress |
| IaC support               | 🚀 Planned     |
| Async task queue (Celery) | ⏳ In Progress |
| Tests support             | ⏳ In Progress |

## 📜 License

This project is licensed under the **MIT License**
