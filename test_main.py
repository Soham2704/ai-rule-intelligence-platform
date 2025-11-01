from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "AI Rule Intelligence Platform - Test Deployment"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "AI Rule Test"}

@app.get("/docs")
def read_docs():
    return {"message": "API Documentation Endpoint"}