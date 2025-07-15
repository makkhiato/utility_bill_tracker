# Utility Bill Tracker – Backend API

This is the **backend REST API** for the Utility Bill Tracker app, built with Flask. It handles authentication, bill management, user settings, and automatic notifications.

---

## Tech Stack

- **Flask** (REST API)
- **Flask-JWT-Extended** (JWT Auth)
- **SQLAlchemy** (ORM)
- **Flask-APScheduler** (Scheduled jobs for notifications)
- **SQLite** (default local DB)

---

## Setup Instructions

### 1. Clone the repository

```
git clone https://github.com/yourusername/utility-bill-tracker.git
cd utility-bill-tracker
```

### 2. Create virtual environment

```
python -m venv venv
source venv/bin/activate # On Windows: venv/Scripts/activate
```

### 3. Install dependencies

```
pip install -r requirements.txt
```

### 4. Create .env file
*Update values in .env*
```
cp .env.example .env
```

### 5. Initialize the database
*The database and tables will be auto-created on app startup.*

*Seed test data:*
```
python seed.py
```

### 6. Run the development server

```
flask run
```

---

## API Endpoints

### Notes

- All authenticated routes require the `Authorization: Bearer <access_token>` header except `/login` and `/register`.
- Base URL: `http://localhost:5000/api`

### Auth

| Method | Endpoint    | Description                             |
|--------|-------------|-----------------------------------------|
| POST   | `/register` | Register a new user                     |
| POST   | `/login`    | Login and receive access/refresh tokens |
| POST   | `/refresh`  | Get a new access token                  |

### User Settings

| Method | Endpoint    | Description                     |
|--------|-------------|---------------------------------|
| GET    | `/settings` | Get current user's settings     |
| PUT    | `/settings` | Update user settings            |
| PUT    | `/user`     | Update user profile information |

### Bills

| Method | Endpoint      | Description                                 |
|--------|---------------|---------------------------------------------|
| GET    | `/bills`      | Get bills (supports pagination/filter/sort) |
| POST   | `/bills`      | Add new bill                                |
| GET    | `/bills/<id>` | Get bill by ID                              |
| PUT    | `/bills/<id>` | Update bill by ID                           |
| DELETE | `/bills/<id>` | Delete bill by ID                           |

### Analytics

| Method | Endpoint               | Description                                 |
|--------|------------------------|---------------------------------------------|
| GET    | `/analytics`           | Get summary of bills for the last 6 months  |
| GET    | `/analytics/predict`   | Predict upcoming bills based on past bills  |
| GET    | `/analytics/breakdown` | Get summary of breakdown of bills over time |

### Notification

| Method | Endpoint                                   | Description                            |
|--------|--------------------------------------------|----------------------------------------|
| GET    | `/notification`                            | Get all notifications for current user |
| PUT    | `/notification/<int:notification_id>/seen` | Mark a specific notification as seen   |
| DELETE | `/notification/<int:notification_id>`      | Delete a specific notification         |


---

## Project Structure (backend)
```
utility_bill_tracker/
└── backend/
    │
    ├── app/
    │   ├── routes/
    │   │   ├── __init__.py
    │   │   ├── analytics_route.py
    │   │   ├── auth_routes.py
    │   │   ├── bill_routes.py
    │   │   ├── notifications_route.py
    │   │   └── user_routes.py
    │   ├── utils/
    │   │   ├── auth.py
    │   │   └── scheduled_notif.py
    │   ├── __init__.py
    │   ├── config.py
    │   ├── extensions.py
    │   └── models.py
    ├── .env.example
    ├── .gitignore
    ├── README.md
    ├── requirements.txt
    ├── run.py
    ├── seed.py
    └── utility_bill_tracker_api.postman_collection.json
```

---

## Development and Testing

- Use **Postman** or **Thunder Client** to test routes
- Call `/api/refresh` to get new access token when the current one expires

---

## Environment Variables
```
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret-key
DATABASE_URL=sqlite:///database.db
```
