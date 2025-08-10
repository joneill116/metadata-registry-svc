from fastapi import FastAPI

app = FastAPI(title="Metadata Registry Service")

@app.get("/healthz")
def health_check():
    return {"status": "ok"}
