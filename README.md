# ParallaxLane v1.2

### Web-Based Online Examination and Proctoring System

## Overview

ParallaxLane is a full-stack web application designed to conduct online examinations with integrated monitoring and supervision. 
It ensures exam integrity by tracking user activity in real time and providing administrators with control and visibility over ongoing exams.

Version 1.2 improves system stability, corrects data flow issues, and ensures reliable real-time monitoring.

## System Description

### Backend System

The backend is built using Django and Django REST Framework. It is responsible for:
* User authentication using JWT
* Managing exams, questions, and attempts
* Handling answer submission and evaluation
* Logging violations and tracking risk scores
* Storing screenshots and monitoring data
* Providing APIs for admin monitoring and control


### Frontend System
The frontend is developed using Vue.js. It provides:
* Interactive user interface for candidates and administrators
* Exam interface with timer and controlled environment
* Real-time monitoring dashboard for admins
* API communication using Axios
* Routing and state handling for seamless navigation

## Usefulness
ParallaxLane is useful in scenarios where secure remote examinations are required:
* Enables online exams without physical supervision
* Helps detect suspicious behavior during tests
* Provides real-time monitoring for administrators
* Maintains a record of violations for post-exam review
* Reduces chances of malpractice in remote environments


## Key Features

### Authentication
* JWT-based authentication
* Role-based access (Admin / Candidate)

### Examination System
* Create and manage exams
* Timed exam sessions
* Automatic evaluation
* Attempt tracking

### Monitoring
* Tab switch detection
* Fullscreen exit tracking
* Copy and right-click detection
* Developer tools detection
* Camera and system health monitoring

### Violation Tracking
* Real-time logging
* Severity-based tracking
* Risk scoring

### Screenshot Capture
* Periodic webcam screenshots
* Linked to exam attempts
* Available in admin panel

### Admin Dashboard
* Live monitoring of candidates
* Status tracking (Active / Terminated)
* Violation count and risk score
* User-level details and screenshots
* Control actions for exam management

## Tech Stack

Backend

* Django
* Django REST Framework
* JWT Authentication

Frontend

* Vue.js (Composition API)
* Axios
* Vue Router

## System Architecture

```
Frontend (Vue)
     ↓ REST API
Backend (Django + DRF)
     ↓
Database
```

## Workflow

```
Login → Dashboard → Start Exam
                 ↓
        Monitoring Activated
                 ↓
        Violations Logged
                 ↓
        Exam Submission
                 ↓
        Results Generated
                 ↓
        Admin Review
```

## Project Structure

```
backend/
  accounts/
  exams/
  monitoring/
  admin_panel/

frontend/
  views/
  components/
  router/
  services/
```

## Setup

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Improvements in v1.2
* Fixed live monitoring synchronization
* Removed hardcoded dependencies
* Corrected API data flow
* Improved authentication handling
* Fixed dashboard state issues
* Optimized polling
* Improved routing

## Limitations
* Client-side monitoring can be bypassed
* Screenshot capture is periodic
* Rule-based detection system

## Future Scope
* AI-based detection
* WebSocket real-time monitoring
* Multi-exam tracking
* Advanced analytics

## Author
UMNG
