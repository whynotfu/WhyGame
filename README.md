# WhyGame

WhyGame is a web platform where developers can publish their games and players can discover and play them online. The platform supports browser-based games such as Unity WebGL builds as well as downloadable versions. Players can launch games directly in the browser, explore new projects, and interact with the community.

The project demonstrates a full-stack web application with a backend API, database integration, file storage, and browser game hosting.

---

## Features

- User registration and authentication  
- Game publishing and management  
- Upload browser games (Unity WebGL)  
- Play games directly in the browser  
- Download games locally  
- Game pages with descriptions and metadata  
- Comments and ratings  
- Game catalog and discovery  

---

## Tech Stack

**Backend**
- Python
- Flask
- SQLAlchemy
- Flask-Migrate

**Database**
- PostgreSQL

**Frontend**
- HTML
- CSS
- JavaScript
- Jinja2

**Game Support**
- Unity WebGL builds

---

## Architecture

The project follows a three-tier architecture:

```
Frontend
|
| HTTP
|
Flask Backend (API)
|
SQLAlchemy ORM
|
PostgreSQL
```

Game builds are stored in a dedicated storage directory and served by the backend.

---

## Project Structure


## Goals

The goal of the project is to demonstrate:

- backend web development with Flask  
- REST API design  
- database modeling  
- file storage management  
- browser-based game hosting  

---

## Course Project Assignment

**Topic:** Development of a web platform for publishing and playing browser-based games (WhyGame)

**Student:** whynotfu  
**Group:** *(group number)*

### Development Tasks

1. **User authentication and authorization** — implement registration, login, and logout functionality using session-based or token-based authentication.

2. **Role-based access control** — define user roles (guest, registered user, game developer, administrator) and enforce permissions accordingly (e.g., only developers can publish games, only admins can delete any content).

3. **CRUD interface** — implement full create, read, update, and delete operations for the core entities: Users, Games, and Comments.

4. **Data aggregation and processing** — aggregate game statistics (total plays, average rating, number of downloads); provide a game catalog with filtering and sorting by genre, rating, and release date.

5. **File upload and download** — support uploading Unity WebGL game builds (zip archives with HTML/JS/WASM assets) and offering downloadable game packages for local play.

6. **Application entities (minimum 3):**
   - **User** — account data, role, profile information
   - **Game** — title, description, genre, build files, metadata
   - **Comment / Rating** — user feedback and numerical ratings per game

---

## Status

Project in active development.