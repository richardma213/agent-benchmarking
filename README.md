## About

BenchSym is a lightweight evaluation system for symbolic‑math LLMs. It runs multiple agents on a shared set of calculus problems, parses and normalizes their outputs, and checks correctness using SymPy. The platform supports both local inference (LM Studio) and cloud‑based inference (Hugging Face Router), enabling reproducible comparisons across different Qwen model backends.

---
## Tools Used

- **FastAPI** — backend routing, orchestration, and evaluation  
- **SymPy** — symbolic parsing, simplification, and equivalence checking  
- **LM Studio** — local inference for Qwen 3–7B models  
- **Hugging Face Router** — cloud inference fallback / multi‑backend support  
- **Python** — evaluation pipeline and agent harness  

---
## Sample UI Run
![Dashboard](./images/demo1.png)
![Dashboard](./images/demo2.png)

## Development Process

I began by building two agents: ml_agent, which solves problems directly through LLM inference, and math_agent, which uses an LLM parser to convert expressions into SymPy‑compatible syntax for symbolic evaluation. After that, I developed an automated benchmarking pipeline that loads problems from JSON files, runs both agents, and validates outputs using LLM‑assisted checking and regex parsing. This workflow eliminated manual testing and made it easy to run large batches of problems quickly. For testing, a set of 60+ calculus tasks was generated, ran through the automated pipeline, and then checked for any inaccuracies. Final results are generated automatically by the pipeline and averaged.

## Results & Findings

BenchSym was used to benchmark two agents across four evaluation runs (Qwen 3B and Qwen 7B).  
Below are the **final combined averages** across all trials:

### **math_agent**
- **Accuracy:** 89.5%  
- **Avg latency:** 1288.41 ms  
- **Total tokens:** 5641.25  

### **ml_agent**
- **Accuracy:** 64.65%  
- **Avg latency:** 2255.27 ms  
- **Total tokens:** 6184.25  

### **Overall Trial Stats**
- **Correct answers:** 77.125%  
- **Total tokens:** 11825.25  
- **Avg tokens/trial:** 168.57  
- **Avg latency:** 1771.84 ms  

### **Key Improvements**
- **∼38% higher accuracy**  
- **∼43% lower latency**  
- **∼9% fewer tokens**  

These results show that structured symbolic‑math agents, combined with normalization and SymPy verification, can significantly outperform direct model computation on calculus tasks.

---

## Why This Project Matters

Symbolic‑math tasks require more than text matching — they require structural correctness. BenchSym provides a reproducible way to evaluate LLMs on mathematically rigorous problems using symbolic equivalence rather than raw string comparison. This makes it a practical tool for studying model reliability, consistency, and reasoning behavior.

---

## Future Work

- Support additional model families (LLaMA, DeepSeek, Mistral)  
- Expand beyond calculus (ODEs, algebraic simplification, limits)  
- Add a dashboard for visualizing correctness and failure modes  
- Integrate caching and batch scheduling for large‑scale runs  

---

## Repo Status

Actively maintained. More documentation and examples coming soon.
