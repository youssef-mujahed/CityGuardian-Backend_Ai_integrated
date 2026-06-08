#  CityGuardian - AI Emergency Response System
##  About The Project

**CityGuardian** is an AI-powered backend system for emergency response and smart traffic management. It helps reduce emergency response time by:

-  **Severity Prediction** - ML model predicts accident severity (1-3)
-  **Smart Routing** - Calculates fastest route to hospital with live traffic
-  **SMS Alerts** - Instant emergency notifications via SMS
-  **Role-Based Access** - Admin dashboard + Citizen mobile app

##  Built With

- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Relational database
- **SQLAlchemy** - ORM for database operations
- **JWT + bcrypt** - Authentication & security
- **scikit-learn** - ML model for severity prediction
- **OpenRouteService** - Route calculation API
- **MoceanAPI** - SMS delivery service

##  Database Schema

| Table | Description |
|-------|-------------|
| `users` | Admin & citizen accounts |
| `incidents` | Accident reports |
| `incident_updates` | Status change history |
| `hospitals` | Hospital locations |
| `routes` | Calculated emergency routes |
| `risk_zones` | High-risk areas |
| `predictions` | ML prediction results |

## 🔗 API Endpoints 

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/login` | Login with mobile + password |
| GET | `/api/v1/auth/me` | Get current user profile |

### Incidents
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/incidents` | Report an accident |
| GET | `/api/v1/incidents` | Get all incidents (admin) |
| GET | `/api/v1/incidents/active` | Get active incidents |
| PUT | `/api/v1/incidents/{id}` | Update incident status |

### Routing
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/routes/hospitals` | Get all hospitals |
| POST | `/api/v1/routes/to-hospital` | Get route + ETA |

### ML Prediction
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/risk/predict` | Predict risk score |
| POST | `/api/v1/risk/severity` | Predict accident severity |

### SMS
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/sms/send` | Send SMS (admin) |
| POST | `/api/v1/sms/emergency` | Send emergency alert |

##  Getting Started

### Prerequisites

- Python 3.12+
- PostgreSQL 16+
- Git

### Installation

**1. Clone the repository**
```bash
git clone https://github.com/youssef-mujahed/CityGuardian-Backend_Ai_integrated.git
cd CityGuardian-Backend_Ai_integrated
