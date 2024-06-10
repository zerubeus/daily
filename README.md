## Architecture Overview

### Project Structure

The project utilizes a modular and scalable architecture with the following key components:

- **FastAPI**: For building and handling API requests.
- **PostgreSQL**: For relational database management and persistent data storage.
- **Redis**: For caching and temporary storage of activation codes.
- **Docker**: For containerization and managing services using Docker Compose.
- **HTTP Basic Authentication**: For securing endpoints and verifying user credentials.

### run the API

```bash
docker compose up -d
```

### run the tests

```bash
docker compose exec api pytest
```

### API documentation

visit http://localhost:8000/docs

