from app import app
import os
import uvicorn

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))  # Default to port 8000 if PORT env variable is not set
    workers = int(os.getenv("WORKERS", 4))  # Default to 1 worker if WORKERS env variable is not set
    uvicorn.run(app, host="0.0.0.0", port=port, workers=workers)
