# Automated Resume Shortlister - Technical Documentation

## Overview

The Automated Resume Shortlister is a Django-based web application designed to streamline the recruitment process by automatically matching candidate resumes with job requirements using Natural Language Processing (NLP). This document provides detailed technical information about the system's architecture, components, and implementation.

## System Architecture

### Technology Stack

- **Backend Framework**: Django 5.0.2
- **Database**: PostgreSQL
- **Frontend**: Bootstrap 5, Chart.js
- **NLP Processing**: spaCy 3.7.4
- **Task Queue**: Celery 5.3.6 with Redis
- **Document Processing**: python-docx, PyPDF2
- **Data Visualization**: matplotlib, plotly
- **Form Handling**: django-crispy-forms with crispy-bootstrap5

### Core Components

1. **User Management (`users/`)**
   - Role-based authentication (Admin, Recruiter, Candidate)
   - User profiles and permissions
   - Session management

2. **Job Management (`jobs/`)**
   - Job posting creation and management
   - Requirement specification
   - Application tracking

3. **Resume Processing (`resumes/`)**
   - Resume upload and parsing
   - Information extraction
   - Document format handling (PDF, DOCX)

4. **Matching Engine (`matching/`)**
   - NLP-based resume analysis
   - Job-candidate matching algorithms
   - Similarity scoring

5. **Dashboard (`dashboard/`)**
   - Role-specific views
   - Analytics and reporting
   - Application status tracking

## Detailed Component Documentation

### Resume Processing

The system supports multiple document formats and uses specialized libraries for parsing:
- PDF files: PyPDF2
- DOCX files: python-docx
- Text extraction and cleaning
- Information extraction using spaCy

### Matching Algorithm

The matching process involves several steps:
1. Text preprocessing
2. Feature extraction
3. Similarity calculation
4. Score normalization
5. Ranking and shortlisting

### Task Queue System

Celery is used for handling asynchronous tasks:
- Resume parsing
- Matching calculations
- Email notifications
- Report generation

## API Documentation

### Authentication Endpoints

- `/api/auth/login/` - User login
- `/api/auth/register/` - User registration
- `/api/auth/logout/` - User logout

### Job Management Endpoints

- `/api/jobs/` - CRUD operations for job postings
- `/api/jobs/{id}/applications/` - Job applications management
- `/api/jobs/{id}/matches/` - Get matched candidates

### Resume Management Endpoints

- `/api/resumes/` - Resume upload and management
- `/api/resumes/{id}/parse/` - Resume parsing
- `/api/resumes/{id}/matches/` - Get matching jobs

## Database Schema

### Key Models

1. **User**
   - id
   - username
   - email
   - role
   - profile_data

2. **Job**
   - id
   - title
   - description
   - requirements
   - status
   - created_by

3. **Resume**
   - id
   - user
   - file_path
   - parsed_data
   - upload_date

4. **Application**
   - id
   - job
   - candidate
   - status
   - match_score

## Deployment Guide

### Production Setup

1. **Environment Configuration**
   - Set DEBUG=False
   - Configure production database
   - Set up static file serving
   - Configure email settings

2. **Server Requirements**
   - Python 3.8+
   - PostgreSQL
   - Redis
   - Nginx/Apache
   - Gunicorn

3. **Security Considerations**
   - SSL/TLS configuration
   - Database security
   - File upload restrictions
   - Rate limiting

## Performance Optimization

### Caching Strategy

- Redis for session storage
- Template fragment caching
- Query result caching
- Static file caching

### Database Optimization

- Index optimization
- Query optimization
- Connection pooling
- Regular maintenance

## Monitoring and Maintenance

### Logging

- Application logs
- Error tracking
- Performance metrics
- User activity logs

### Backup Strategy

- Database backups
- File system backups
- Configuration backups
- Recovery procedures

## Troubleshooting Guide

### Common Issues

1. **Resume Parsing Issues**
   - Check file format support
   - Verify file permissions
   - Check storage space

2. **Matching Algorithm Issues**
   - Verify NLP model loading
   - Check input data quality
   - Monitor performance metrics

3. **Performance Issues**
   - Check server resources
   - Monitor database performance
   - Review caching configuration

## Future Enhancements

1. **Planned Features**
   - Advanced analytics dashboard
   - Machine learning improvements
   - Mobile application
   - API enhancements

2. **Technical Improvements**
   - Microservices architecture
   - Containerization
   - CI/CD pipeline
   - Automated testing

## Contributing Guidelines

### Development Workflow

1. Fork the repository
2. Create feature branch
3. Follow coding standards
4. Write tests
5. Submit pull request

### Code Standards

- PEP 8 compliance
- Docstring documentation
- Type hints
- Test coverage requirements

## License

This project is licensed under the MIT License. See the LICENSE file for details. 
