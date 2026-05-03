from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import time

app = FastAPI()

# Add CORS middleware to allow requests from React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allow requests from React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/benchmark")
def run_benchmark():
    start = time.time()
    # placeholder: call agent here
    result = {"accuracy": 0.95, "latency": time.time() - start, "tokens": 120}
    return result