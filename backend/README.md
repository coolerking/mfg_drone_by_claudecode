# MFG Drone Backend API

Tello EDU drone automatic tracking system backend implementation using FastAPI.

## Development Setup

This project uses [uv](https://docs.astral.sh/uv/) for Python package management.

### Prerequisites

- Python 3.12 or later
- uv package manager

### Installation

1. Install dependencies:
```bash
uv sync
```

2. Activate the virtual environment:
```bash
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate  # Windows
```

3. Run the development server:
```bash
uv run uvicorn main:app --reload
```

### Development Tools

- Linting: `uv run ruff check`
- Formatting: `uv run black .`
- Type checking: `uv run mypy .`
- Testing: `uv run pytest`

## Project Structure

```
backend/
├── main.py                 # FastAPI application entry point
├── routers/               # API route handlers
│   ├── connection.py      # Drone connection management
│   ├── flight_control.py  # Flight control endpoints
│   ├── movement.py        # Basic movement endpoints
│   ├── advanced_movement.py # Advanced movement control
│   ├── camera.py          # Camera operations
│   ├── sensors.py         # Sensor data endpoints
│   ├── settings.py        # Settings management
│   ├── mission_pad.py     # Mission pad functionality
│   ├── tracking.py        # Object tracking
│   └── model.py           # AI model management
├── models/                # Pydantic models
│   ├── requests.py        # Request models
│   └── responses.py       # Response models
├── services/              # Business logic
│   └── drone_service.py   # Drone control service
├── dependencies.py        # Dependency injection
└── tests/                 # Test files
```