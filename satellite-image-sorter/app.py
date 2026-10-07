"""
app.py

Backend application module for Satellite Image Sorter & Organizer.
Replaces the legacy Streamlit frontend with the decoupled FastAPI backend application.
Allows running via either `uvicorn main:app` or `uvicorn app:app`.
"""

from main import app

if __name__ == "__main__":
    import uvicorn
    from config import HOST, PORT

    uvicorn.run("main:app", host=HOST, port=PORT, reload=True)
