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
