from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from benchmark_runner import run_benchmark
from equivalence import equivalent
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/benchmark")
def benchmark(problem: str = "2+2*3"):
    results = run_benchmark(problem)
    return results

@app.post("/equivalent")
def check_equivalence(payload: dict):
    a = payload["a"]
    b = payload["b"]
    return {"equivalent": equivalent(a, b)}