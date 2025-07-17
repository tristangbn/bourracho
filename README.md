# Bourracho

Welcome to bourracho repository where tech-enjoyers meet techno-kiffers!

## Prerequisites

Before you begin, ensure you have the following installed:

- **Node.js** (v18 or higher) - [Download here](https://nodejs.org/)
- **Python** (3.11 or higher) - [Download here](https://python.org/)
- **uv** (Python package manager) - [Install with](https://docs.astral.sh/uv/getting-started/installation/): `pip install uv`

## Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd bourracho
```

### 2. Backend Setup

Navigate to the backend directory and set up the Django environment:

```bash
cd backend

# Install dependencies using uv
uv sync

# Run database migrations
uv run manage.py migrate

# Create a superuser (optional)
uv run manage.py createsuperuser

# Start the development server
uv run manage.py runserver
```

The Django backend will be available at `http://localhost:8000`

### 3. Frontend Setup

In a new terminal, navigate to the frontend directory:

```bash
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

The React frontend will be available at `http://localhost:5173`

## Development Scripts

### Backend Scripts

```bash
cd backend

# Run the development server
uv run manage.py runserver

# Run tests
uv run pytest

# Create and apply migrations
uv run manage.py makemigrations
uv run manage.py migrate

# Access Django admin
uv run manage.py createsuperuser
```

### Frontend Scripts

```bash
cd frontend

# Start development server
npm run dev

# Start development server with host access (for mobile testing)
npm run dev:host

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint

# Fix linting issues
npm run lint:fix

# Format code
npm run format

# Check code formatting
npm run format:check
```

## Project Structure

```text
bourracho/
├── backend/                 # Django backend
│   ├── bourracho/          # Main Django app
│   ├── conversations_api/  # Conversations API
│   ├── manage.py           # Django management script
│   └── requirements.txt    # Python dependencies
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── hooks/          # Custom React hooks
│   │   └── lib/            # Utility functions
│   └── package.json        # Node.js dependencies
└── README.md
```

## API Documentation

Once the backend is running, you can access:

- **Django Admin**: `http://localhost:8000/admin/`
- **API Documentation**: `http://localhost:8000/api/docs/`

## Troubleshooting

### Common Issues

1. **Port already in use**: If port 8000 or 5173 is already in use, you can specify a different port:

   - Backend: `uv run manage.py runserver 8001`
   - Frontend: `npm run dev -- --port 3000`

2. **Database issues**: If you encounter database errors, try:

   ```bash
   cd backend
   uv run manage.py migrate --run-syncdb
   ```

3. **Node modules issues**: If frontend dependencies are corrupted:

   ```bash
   cd frontend
   rm -rf node_modules package-lock.json
   npm install
   ```

## Contributing

1. Create a feature branch
2. Make your changes
3. Run tests and linting
4. Submit a pull request

For more details, see [CONTRIBUTING.md](CONTRIBUTING.md).
