# PLUTO — Satellite Image Sorter & Organizer

PLUTO is a satellite-image cataloging and organization project with a **React + Vite + TypeScript** frontend and a **FastAPI** backend. It brings image-related workflows together with search, filtering, sorting, statistics, export/organization utilities, and demonstrations of data structures and algorithms.

> **Project status:** Local development and testing. Deployment to Vercel and Render should be done only after the frontend, backend, and their API connection have been verified locally.

## Technology Stack

- **Frontend:** React, TypeScript, Vite, Tailwind CSS
- **Backend:** Python, FastAPI, Uvicorn, Pydantic
- **Supporting libraries:** Pillow, python-multipart
- **API documentation:** FastAPI Swagger UI

## Repository Structure

```text
Pluto/
├── frontend/                  # React + Vite web application
│   ├── public/
│   ├── src/
│   ├── .env.example
│   ├── package.json
│   └── vite.config.ts
├── satellite-image-sorter/    # FastAPI backend
│   ├── api/                   # API route modules
│   ├── dsa/                   # Data structures and algorithms
│   ├── models/                # Schemas and models
│   ├── services/              # Application services
│   ├── tests/                 # Tests
│   ├── sample_images/         # Sample image assets, if present
│   ├── uploads/                # Upload workspace
│   ├── utils/
│   ├── app.py                 # Alternate backend entry point
│   ├── main.py                # FastAPI application entry point
│   ├── config.py
│   ├── requirements.txt
│   └── .env.example
├── .gitignore
└── README.md
```

## Features

The backend code is organized around these capabilities:

- Image upload and image catalog workflows
- Image metadata and dataset-related operations
- Sorting and searching endpoints
- Filtering and statistics
- Benchmarking and export/organization utilities
- DSA endpoints and implementations, including sorting, searching, and a separate-chaining hash table

The available frontend screens and supported actions depend on the current implementation. Use the API documentation to confirm the backend routes available in your local checkout.

## Prerequisites

Install:

- [Node.js](https://nodejs.org/) and npm
- [Python](https://www.python.org/downloads/) 3.13 or a compatible Python version

Check your installations:

```powershell
node --version
npm --version
python --version
```

The commands below assume the repository is located at `C:\PLUTO\Pluto`. If yours is in another location, adjust the paths.

## Run PLUTO Locally

Start the frontend and backend in **two separate terminals**. Keep both terminals running while using the app.

### 1. Start the frontend

```powershell
cd C:\PLUTO\Pluto\frontend
npm run dev
```

Open the local URL printed by Vite. It is commonly:

```text
http://localhost:5173
```

If npm reports that dependencies are missing, install them from the frontend directory:

```powershell
npm install
```

Then run `npm run dev` again.

### 2. Start the backend

In a second terminal:

```powershell
cd C:\PLUTO\Pluto\satellite-image-sorter
python -m uvicorn main:app --reload
```

The API is commonly available at:

```text
http://127.0.0.1:8000
```

Open the interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

Alternative documentation is available at `/redoc` when enabled by the application.

If Python reports missing packages, install the backend requirements from the backend directory:

```powershell
python -m pip install -r requirements.txt
```

Then start Uvicorn again. If you use a virtual environment, activate it before installing packages or launching the server.

### Stop the Servers

Press `Ctrl+C` in each terminal to stop its server.

## Configuration

Configuration files are provided as examples:

- `frontend/.env.example`
- `satellite-image-sorter/.env.example`

Review these files and the associated configuration code before changing environment values. Use local environment files for machine-specific settings, keep secrets out of Git, and never commit API keys or credentials.

The frontend must point to the correct local API base URL. Check the frontend environment example and API client code to confirm the exact variable name and expected URL format before changing it. The backend CORS configuration must allow the local frontend origin.

## Testing Checklist

After both servers start, verify the following in the browser:

- [ ] The frontend loads without a blank screen.
- [ ] The backend starts without import or configuration errors.
- [ ] `/docs` opens and lists the available API endpoints.
- [ ] Frontend requests reach the backend successfully.
- [ ] Upload and image-related operations work with valid image files.
- [ ] Search, sorting, filtering, statistics, and other implemented features work.
- [ ] Browser developer tools and both terminals show no unresolved errors.

Test one feature at a time. If a feature fails, record the browser error, request URL/status, and relevant terminal output before changing code.

## Test Data

A sample CSV named `pluto_test_satellite_images.csv` may be used to test a CSV-import or catalog feature **only if the application supports that format and schema**. The supplied example data is synthetic; its file paths are illustrative and do not point to real satellite images. It cannot replace actual image files when testing image decoding, metadata extraction, or image processing.

If the CSV import rejects the file, inspect the implementation or API schema to determine the expected columns and format rather than assuming every CSV
