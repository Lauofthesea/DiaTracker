
# ML Diabetes Tracker

A comprehensive web application that combines machine learning-based diabetes risk prediction with nutritional tracking capabilities.

## Features

- **Diabetes Risk Prediction**: ML-powered assessment using health metrics
- **Food Database**: Comprehensive nutritional information and allergen data
- **Meal Tracking**: Log food intake with real-time nutritional calculations
- **Analytics Dashboard**: Visualize nutritional trends and health insights
- **User Profiles**: Manage health data and dietary preferences
- **Responsive Design**: Works on desktop, tablet, and mobile devices

## Technology Stack

### Backend
- **Framework**: Python FastAPI
- **Database**: PostgreSQL 18 + pgcrypto extension
- **ML**: scikit-learn, pandas, numpy
- **Authentication**: JWT tokens + bcrypt password hashing

### Frontend
- **Framework**: React 18+ with TypeScript
- **Build Tool**: Vite
- **UI Components**: shadcn/ui + Tailwind CSS
- **State Management**: Zustand
- **Charts**: Recharts
- **HTTP Client**: Axios

### Prerequisites

- Node.js 18+
- Python 3.11+
- PostgreSQL 14+
- Docker & Docker Compose (optional)

### COPY / CLONE MUNA REPO TO RUN

1. **Clone the repository**
```bash
git clone <repository-url>
cd ml-diabetes-tracker
```

2. **Start with Docker (Recommended)**
```bash
docker-compose up
```

3. **Or run manually:**

   **Backend:**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   python scripts/init_db.py
   uvicorn main:app --reload
   ```

   **Frontend:**
   ```bash
   npm install
   npm run dev
   ```

4. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000

## Project Structure

```
ml-diabetes-tracker/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── core/           # Configuration
│   │   ├── db/             # Database setup
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   └── services/       # Business logic
│   ├── alembic/            # Database migrations
│   ├── scripts/            # Utility scripts
│   ├── tests/              # Backend tests
│   └── main.py            # Application entry point
├── src/                    # React frontend
│   ├── app/               # Main application
│   ├── components/        # UI components
│   ├── styles/           # CSS and styling
│   └── test/             # Frontend tests
├── .kiro/                 # Kiro specifications
├── docker-compose.yml     # Development environment
└── README.md             # This file
```

### Backend Development

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest

# Run with hot reload
uvicorn main:app --reload

# Create database migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head
```

### Frontend Development

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Run tests
npm test

# Build for production
npm run build
```

## Security & Compliance

- **HIPAA Compliance**: Encrypted data at rest and in transit
- **Authentication**: JWT tokens with secure password hashing
- **Data Protection**: AES-256 encryption for sensitive fields
- **Input Validation**: Comprehensive request validation

// CREATED BY: BSIT3B - GROUP 1 //
## CONTRIBUTORS ## 

**Calvi, Fairudz L.**
**Fernandez, Rhimand Niño M.**
**Hadjula, Gandykhan C. - Developer**
**Hipolito, Micheal Laurence T. - Developer**
**Kalayakan, Mohammad Alhussain L.**
**Vega, Ashley Faye M.**
**Zamora, Renan F.**
