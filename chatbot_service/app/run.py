import uvicorn, os, sys

PROJECT_ROOT = os.path.dirname(os.path.abspath(os.path.join(__file__, "..")))
sys.path.insert(0, PROJECT_ROOT)

if __name__ == "__main__":
    uvicorn.run(
        "app.api.main:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    )
