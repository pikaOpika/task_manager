# TaskFlow

A task management web application built with Django. Organize teams, track tasks, and manage projects.

## Features

- Task creation with priority, deadline, and assignees
- Project and team management
- Join request system for projects
- Worker profiles with photos
- Task filtering and search

## Setup

**1. Clone the repository**
```
git clone <repository-url>
cd task_manager
```

**2. Create and activate a virtual environment**
```
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux
```

**3. Install dependencies**
```
pip install -r requirements.txt
```

**4. Apply migrations**
```
python manage.py migrate
```

**5. Create a superuser (optional)**
```
python manage.py createsuperuser
```

**6. Run the development server**
```
python manage.py runserver
```

Open your browser at `http://127.0.0.1:8000`

## Database Schema

```mermaid
erDiagram
    Position {
        int id
        string name
    }
    TaskType {
        int id
        string name
    }
    Worker {
        int id
        string username
        string slug
        image image
        int position_id FK
    }
    Task {
        int id
        string name
        text description
        date deadline
        bool is_completed
        string priority
        string slug
        int task_type_id FK
        int project_id FK
    }
    Project {
        int id
        string name
        text description
        string slug
        int created_by_id FK
    }
    Team {
        int id
        string name
        string slug
        int project_id FK
        int created_by_id FK
    }
    JoinRequest {
        int id
        string status
        datetime created_at
        int project_id FK
        int from_user_id FK
    }

    Worker }o--o| Position : "has position"
    Task }o--o| TaskType : "has type"
    Task }o--o| Project : "belongs to"
    Task }o--o{ Worker : "assignees"
    Project ||--o{ Team : "has teams"
    Project }o--|| Worker : "created by"
    Team }o--o{ Worker : "members"
    Team }o--|| Worker : "created by"
    JoinRequest }o--|| Project : "request for"
    JoinRequest }o--|| Worker : "request from"
```
