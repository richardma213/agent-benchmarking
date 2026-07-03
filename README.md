# BenchSym

A symbolic‑math benchmarking platform built with FastAPI, LM Studio, and Hugging Face Router for multi‑agent Qwen inference, featuring automated SymPy equivalence checking across 100+ integrals.

---

## About

SymBench is a lightweight evaluation framework for symbolic‑math LLMs. It runs multiple agents on a shared set of integrals, normalizes their outputs, and verifies correctness using SymPy. The system supports both local inference (LM Studio) and cloud‑based inference (Hugging Face Router), enabling reproducible comparisons across different model backends.

---

## Tools Used

- **FastAPI** — backend service for routing, orchestration, and evaluation  
- **LM Studio** — local inference for Qwen 3–7B models  
- **Hugging Face Router** — cloud inference fallback / multi‑backend support  
- **SymPy** — symbolic parsing, normalization, and equivalence checking  
- **Python** — core logic, evaluation pipeline, and agent harness  
- **Vite / TypeScript (optional)** — lightweight frontend for running test batches  

---

## Development Process

1. **Problem Set Design**  
   - Curated 100+ integrals and symbolic expressions for evaluation  
   - Standardized formatting for ingestion and reproducibility  

2. **Backend Architecture**  
   - Built a FastAPI service to coordinate multi‑agent inference  
   - Added endpoints for running batches, checking equivalence, and exporting results  

3. **Agent Integration**  
   - Connected LM Studio for local Qwen inference  
   - Added Hugging Face Router for cloud‑based model execution  
   - Unified both into a consistent multi‑agent workflow  

4. **Equivalence Engine**  
   - Implemented SymPy‑based parsing, simplification, and symbolic comparison  
   - Added normalization rules to handle constants, formatting differences, and special functions  

5. **Benchmark Harness**  
   - Automated text‑file ingestion  
   - Logged outputs, errors, and correctness results  
   - Produced reproducible evaluation runs for model comparison  

---

## Why This Project Matters

SymBench provides a practical way to evaluate symbolic‑math LLMs beyond raw text comparison. By enforcing SymPy‑verified equivalence and supporting multiple inference backends, it offers a reliable foundation for benchmarking correctness, consistency, and model behavior on mathematically rigorous tasks.

---

## Future Work

- Add support for more model families (LLaMA, DeepSeek, Mistral)  
- Expand the problem set beyond integrals (ODEs, algebraic simplification, limits)  
- Add a dashboard for visualizing correctness and failure modes  
- Integrate caching and batch scheduling for large‑scale runs  

---

## Repo Status

Actively maintained. More documentation and examples coming soon.
