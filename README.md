# School Data Management System

A comprehensive school data management application with a Django REST Framework backend and a modern React + Vite frontend.

## Tech Stack

### Backend
- **Framework**: Django 5.x with Django REST Framework
- **Database**: PostgreSQL
- **Authentication**: Token-based authentication with custom user model
- **Real-time**: Django Channels for WebSocket support
- **CORS**: django-cors-headers for frontend-backend communication
- **Configuration**: python-decouple for environment variable management

### Frontend
- **Framework**: React 19 with Vite
- **Styling**: TailwindCSS 4.x with Flowbite components
- **Routing**: React Router DOM 7.x
- **HTTP Client**: Axios
- **Icons**: React Icons

## Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL 14+
- pip (Python package manager)
- npm or yarn (Node package manager)

## Setup Instructions

### Backend Setup

1. **Navigate to the backend directory**:
   ```bash
   cd School_data
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install Python dependencies**:
   ```bash
   pip install -r ../requirements.txt
   ```

4. **Configure environment variables**:
   ```bash
   cp ../.env.example .env
   ```
   Edit the `.env` file with your database credentials and secret key.

5. **Run database migrations**:
   ```bash
   python manage.py migrate
   ```

6. **Create a superuser** (optional):
   ```bash
   python manage.py createsuperuser
   ```

7. **Start the Django development server**:
   ```bash
   python manage.py runserver
   ```
   The backend will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to the frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install Node dependencies**:
   ```bash
   npm install
   ```

3. **Start the Vite development server**:
   ```bash
   npm run dev
   ```
   The frontend will be available at `http://localhost:5173`

### Building for Production

**Frontend**:
```bash
cd frontend
npm run build
```

**Backend**:
```bash
cd School_data
python manage.py collectstatic
python manage.py runserver 0.0.0.0:8000
```

## Docker Deployment

### Using Docker Compose (Recommended)

1. **Ensure Docker and Docker Compose are installed**

2. **Configure environment variables**:
   ```bash
   cp .env.example .env
   ```

3. **Build and start all services**:
   ```bash
   docker-compose up --build
   ```

4. **Access the application**:
   - Frontend: `http://localhost:5173`
   - Backend API: `http://localhost:8000`
   - Admin Panel: `http://localhost:8000/admin`

5. **Stop the services**:
   ```bash
   docker-compose down
   ```

### Individual Docker Services

**Backend only**:
```bash
docker build -t school-data-backend .
docker run -p 8000:8000 --env-file .env school-data-backend
```

**Frontend only**:
```bash
cd frontend
docker build -t school-data-frontend .
docker run -p 5173:5173 school-data-frontend
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.

## Support

For support and questions, please open an issue in the repository.
