# Automated Resume Shortlister

A Django-based web application that helps recruiters efficiently manage job postings and automatically shortlist candidates based on resume matching using Natural Language Processing (NLP).

## Features

- **Smart Resume Parsing**: Automatically extracts key information from resumes including skills, experience, and education
- **Intelligent Matching**: Uses NLP to match candidates with job descriptions based on content similarity and specific requirements
- **Role-Based Access**:
  - **Recruiters**: Post jobs, view matched candidates, manage applications
  - **Candidates**: Upload resumes, view matched jobs, track applications
  - **Administrators**: Monitor platform analytics, manage users

## Technology Stack

- Python 3.8+
- Django 5.0.2
- PostgreSQL
- Bootstrap 5
- Chart.js for analytics
- spaCy for NLP
- scikit-learn for text processing

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <repository-url>
cd AutomatedResumeShortlister
```

### 2. Create and Activate Virtual Environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm
```

### 4. Environment Setup
Create a `.env` file in the project root with the following content:
```
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=postgres://user:password@localhost:5432/resume_shortlister
```

### 5. Database Setup
```bash
# Create PostgreSQL database
createdb resume_shortlister

# Run migrations
python manage.py migrate
```

### 6. Create Superuser
```bash
python manage.py createsuperuser
```

### 7. Run Development Server
```bash
python manage.py runserver
```

The application will be available at `http://localhost:8000`

## Project Structure

```
AutomatedResumeShortlister/
├── jobs/                   # Job posting and matching functionality
├── resumes/               # Resume upload and parsing
├── users/                 # User authentication and profiles
├── dashboard/             # Role-specific dashboards
├── matching/             # NLP matching algorithms
├── templates/            # HTML templates
├── static/               # Static files (CSS, JS, images)
└── manage.py            # Django management script
```

## Usage

1. **Admin Setup**:
   - Access the admin interface at `/admin`
   - Create user roles (Recruiter, Candidate)
   - Monitor platform analytics

2. **Recruiter Flow**:
   - Create job postings with requirements
   - View matched candidates
   - Manage applications

3. **Candidate Flow**:
   - Upload resume
   - View matched jobs
   - Apply to positions
   - Track application status

## Development

- Run tests: `python manage.py test`
- Check code style: `flake8`
- Generate migrations: `python manage.py makemigrations`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 