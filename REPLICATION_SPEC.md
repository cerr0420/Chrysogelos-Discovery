# REPLICATION_SPEC.md

## 1. System Requirements & Dependencies
To run the `audit_pipe.py` test harness, ensure the following environment is configured:

* **Python Version**: 3.10+
* **Essential Libraries**: 
    * `requests`: For API interactions.
    * `duckduckgo-search`: For real-time grounding verification.
    * `jsonlines`: For structured logging of audit results.
* **Setup**: Clone the `Chrysogelos-Discovery` repository and run `pip install -r requirements.txt` (if applicable) or install the above dependencies manually.

## 2. LM Studio & Model Configuration
To achieve the documented behavioral outputs, your local LLM environment should be configured as follows:

* **Model**: [Specify Model Name Here] (e.g., Llama-3-8B-Instruct or equivalent)
* **Temperature**: 0.0 (Recommended for reproducibility of logical contradictions)
* **Context Window**: 8192 tokens (or higher)
* **System Prompt**: Use the default system prompt established in `audit_pipe.py`.

## 3. Execution Protocol
To initiate the audit pipeline:

1.  Launch **LM Studio** and start your local server.
2.  Open your terminal in the `Chrysogelos-Discovery` directory.
3.  Run the pipeline command: 
    `python audit_pipe.py --mode=audit --target=[model_endpoint]`
4.  Use the standardized trigger prompts included in `audit_pipe.py` to target the "Epistemic Authority Inversion" behavior.

## 4. Expected Output
The script generates an `audit_log.jsonl` file. Each entry should contain:
* `timestamp`: ISO 8601 format.
* `input_prompt`: The trigger used.
* `llm_response`: The model's raw output.
* `grounded_status`: Boolean (True/False based on search results).
* `contradiction_flag`: Boolean (Flagged if contradiction is detected).

## 5. Epistemic Verification
**Status: UNVERIFIED BEHAVIORAL TEST FRAMEWORK**
This repository contains tools and artifacts documenting a reproducible LLM behavior class referred to by the author as "Epistemic Authority Inversion." 

* This is NOT a peer-reviewed scientific classification.
* This is NOT proof of a novel architectural failure mode.
* This IS a working test harness for documenting observed behavior vs. user interpretation.

Adding replication specification 
import sys
import time
import requests
import json
from ddgs import DDGS
from datetime import datetime

# --- Omega Monitor integration ---
from omega_monitor import Message, OmegaMonitor, StabilityState
_omega = OmegaMonitor()

# --- Config ---
LM_STUDIO_URL = "http://localhost:1234/v1/chat/completions"
MODEL_NAME = "deepseek/deepseek-r1-0528-qwen3-8b"
LOG_FILE = "audit_log.jsonl"
MIN_SNIPPET_LENGTH = 50

# --- Helper Functions ---
def ask_llm(prompt, system_prompt=None, diagnostic_notes=None):
    headers = {"Content-Type": "application/json"}
    messages = []
    
    # Inject metacognitive diagnostics if present
    if diagnostic_notes:
        meta_instruction = (
            f"\n[DIAGNOSTIC FEEDBACK]: Your previous response was unstable due to: {diagnostic_notes}. "
            "Critically analyze why these issues occurred and generate a corrected response "
            "that eliminates these specific logical or factual flaws."
        )
        system_prompt = (system_prompt or "You are a helpful assistant.") + meta_instruction

    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    
    data = {
        "model": MODEL_NAME,
        "messages": messages,
        "temperature": 0.1,
        "max_tokens": 1500,
    }
    try:
        response = requests.post(LM_STUDIO_URL, headers=headers, json=data, timeout=120)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"ERROR: Could not connect to LM Studio: {e}"

def run_omega(query: str, answer: str, label: str, log_entry: dict) -> None:
    history = [Message(role="user", content=query)]
    msg = Message(role="assistant", content=answer)
    result = _omega.evaluate(msg, history)
    _omega.last_result = result # Store state for the pipeline loop

    key = f"omega_{label}"
    log_entry[key] = {"score": result.omega, "state": result.state.value, "flags": result.drift_reasons}
    
    icon = {StabilityState.STABLE: "🟢", StabilityState.WATCHFUL: "🟡", StabilityState.UNSTABLE: "🟠", StabilityState.COLLAPSED: "🔴"}[result.state]
    print(f"{icon} Ω [{label.upper()}]: {result.omega:.3f} → {result.state.value}")
    
    if result.unstable:
        log_entry["flags"].append(f"OMEGA_UNSTABLE_{label.upper()}")

def search_duckduckgo(query, max_results=5):
    # ... (Keep your existing search logic) ...
    with DDGS() as ddgs:
        results = [r.get('body', '') for r in ddgs.text(query, max_results=max_results) 
                   if len(r.get('body', '')) > MIN_SNIPPET_LENGTH]
        return "\n".join(results)

# --- Main Logic ---
def main():
    args = sys.argv[1:]
    query = " ".join(args)
    
    # 1. Define log_entry at the very top so it exists for the entire function
    log_entry = {
        "timestamp": time.time(),
        "query": query,
        "final_answer": "Pending",
        "stability_score": 0.0,
        "flags": []
    }
    
    # 2. Initialize answer variable
    answer = "No query processed" 
    
    search_results = search_duckduckgo(query)
    
    # Decision Tree with Metacognitive Loop
    if search_results:
        grounded_prompt = f"Using ONLY the information in these search results, answer the question. \n\n---\n{search_results}\n---\nQuestion: {query}"
        
        # Primary Attempt
        answer = ask_llm(grounded_prompt) 
        log_entry["final_answer"] = answer
        run_omega(query, answer, "initial", log_entry)
        
        # Correction Gate
        if _omega.last_result.unstable:
            reasons = " | ".join(_omega.last_result.drift_reasons)
            print(f"\n⚠️ METACONTEXT: Stability compromised ({reasons}). Initiating correction...")
            
            # Recursive pass
            answer = ask_llm(grounded_prompt, diagnostic_notes=reasons)
            log_entry["corrected_answer"] = answer
            run_omega(query, answer, "corrected", log_entry)
        
        print(f"✨ FINAL ANSWER:\n{answer}\n")
    
    # 3. Write to log
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")

if __name__ == "__main__":
    main()
