from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "healthy", "message": "RVC service running"}

@app.post("/runsync")
def process(request: dict):
    return {"status": "success", "output": "RVC handler working", "input": request}

if __name__ == "__main__":
    print("Starting RVC service on port 8000...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
