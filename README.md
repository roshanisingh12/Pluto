=# SATIQ --- Satellite Image Sorter & Organizer

SATIQ is a satellite-image cataloging and organization project with a
**React + Vite + TypeScript** frontend and a **FastAPI** backend. It
brings image-related workflows together with search, filtering, sorting,
statistics, export/organization utilities, and demonstrations of data
structures and algorithms.

> **Project status:** Local development and testing. Deployment to
> Vercel and Render should be done only after the frontend, backend, and
> their API connection have been verified locally.

## Technology Stack

-   **Frontend:** React, TypeScript, Vite, Tailwind CSS
-   **Backend:** Python, FastAPI, Uvicorn, Pydantic
-   **Supporting libraries:** Pillow, python-multipart
-   **API documentation:** FastAPI Swagger UI

## Repository Structure

``` text
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
│   ├── sample_images/          # Sample image assets, if present
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

-   Image upload and image catalog workflows
-   Image metadata and dataset-related operations
-   Sorting and searching endpoints
-   Filtering and statistics
-   Benchmarking and export/organization utilities
-   DSA endpoints and implementations, including sorting, searching, and
    a separate-chaining hash table

The available frontend screens and supported actions depend on the
current implementation. Use the API documentation to confirm the backend
routes available in your local checkout.

## Prerequisites

Install:

-   [Node.js](https://nodejs.org/) and npm
-   [Python](https://www.python.org/downloads/) 3.13 or a compatible
    Python version

Check your installations:

``` powershell
node --version
npm --version
python --version
```

The commands below assume the repository is located at `C:\PLUTO\Pluto`.
If yours is in another location, adjust the paths.

## Run SATIQ Locally

Start the frontend and backend in **two separate terminals**. Keep both
terminals running while using the app.

### 1. Start the frontend

``` powershell
cd C:\PLUTO\Pluto\frontend
npm run dev
```

Open the local URL printed by Vite. It is commonly:

``` text
http://localhost:5173
```

If npm reports that dependencies are missing, install them from the
frontend directory:

``` powershell
npm install
```

Then run `npm run dev` again.

### 2. Start the backend

In a second terminal:

``` powershell
cd C:\PLUTO\Pluto\satellite-image-sorter
python -m uvicorn main:app --reload
```

The API is commonly available at:

``` text
http://127.0.0.1:8000
```

Open the interactive API documentation:

``` text
http://127.0.0.1:8000/docs
```

Alternative documentation is available at `/redoc` when enabled by the
application.

If Python reports missing packages, install the backend requirements
from the backend directory:

``` powershell
python -m pip install -r requirements.txt
```

Then start Uvicorn again. If you use a virtual environment, activate it
before installing packages or launching the server.

### Stop the servers

Press `Ctrl+C` in each terminal to stop its server.

## Configuration

Configuration files are provided as examples:

-   `frontend/.env.example`
-   `satellite-image-sorter/.env.example`

Review these files and the associated configuration code before changing
environment values. Use local environment files for machine-specific
settings, keep secrets out of Git, and never commit API keys or
credentials.

The frontend must point to the correct local API base URL. Check the
frontend environment example and API client code to confirm the exact
variable name and expected URL format before changing it. The backend
CORS configuration must allow the local frontend origin.

## Testing Checklist

After both servers start, verify the following in the browser:

-   [ ] The frontend loads without a blank screen.
-   [ ] The backend starts without import or configuration errors.
-   [ ] `/docs` opens and lists the available API endpoints.
-   [ ] Frontend requests reach the backend successfully.
-   [ ] Upload and image-related operations work with valid image files.
-   [ ] Search, sorting, filtering, statistics, and other implemented
    features work.
-   [ ] Browser developer tools and both terminals show no unresolved
    errors.

Test one feature at a time. If a feature fails, record the browser
error, request URL/status, and relevant terminal output before changing
code.

## Test Data

A sample CSV named `satiq_test_satellite_images.csv` may be used to test
a CSV-import or catalog feature **only if the application supports that
format and schema**. The supplied example data is synthetic; its file
paths are illustrative and do not point to real satellite images. It
cannot replace actual image files when testing image decoding, metadata
extraction, or image processing.

If the CSV import rejects the file, inspect the implementation or API
schema to determine the expected columns and format rather than assuming
every CSV structure is supported.

## API Documentation

When the backend is running, use:

-   Swagger UI: `http://127.0.0.1:8000/docs`
-   ReDoc: `http://127.0.0.1:8000/redoc`

These pages describe the routes registered by the running backend. Use
them to inspect request parameters, accepted data formats, and response
schemas.

## Troubleshooting

**`npm` is not recognized** - Install Node.js, reopen PowerShell, and
check `node --version` and `npm --version`.

**Frontend dependencies are missing** - Run `npm install` inside
`frontend/`, then retry `npm run dev`.

**`No module named uvicorn` or another Python import error** - Activate
your intended Python environment and run
`python -m pip install -r requirements.txt` from
`satellite-image-sorter/`.

**Port 5173 or 8000 is already in use** - Stop the process already using
the port or configure a different port. If you change a port, ensure the
frontend API configuration and backend CORS settings still match.

**Frontend loads but API calls fail** - Confirm the backend is running,
inspect the failed request in browser developer tools, verify the
frontend API base URL, and check `CORS_ORIGINS` in
`satellite-image-sorter/config.py`.

**Backend starts but a feature fails** - Check the route in `/docs`,
confirm the request matches its schema, and inspect the backend terminal
for the traceback.

## Deployment Roadmap

Deployment is planned after local verification:

1.  Run and test the frontend and backend locally.
2.  Confirm the production API URL and environment-variable
    requirements.
3.  Deploy the FastAPI backend to Render.
4.  Verify the deployed API and configure CORS for the production
    frontend origin.
5.  Deploy the React + Vite frontend to Vercel with the production API
    URL.
6.  Test the deployed application end to end.

Do not assume local `.env` values, local file paths, uploaded files, or
development-server settings will work in production. Review file
storage, secrets, CORS, build settings, and service startup commands
before deployment.

## Contributing / Safe Changes

-   Keep frontend and backend changes scoped to the feature being worked
    on.
-   Avoid committing `.env` files, secrets, uploaded private data, or
    generated build artifacts.
-   Run the application and relevant tests after making changes.
-   Preserve existing Python, DSA, and service functionality when
    modifying the frontend or backend.

------------------------------------------------------------------------

**SATIQ** --- Satellite Image Sorter & Organizer
