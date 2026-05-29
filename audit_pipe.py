import sys
import requests
import json
from ddgs import DDGS
from datetime import datetime

# --- Config ---
LM_STUDIO_URL = "http://localhost:1234/v1/chat/completions"
MODEL_NAME = "llama-3.2-3b-instruct"
LOG_FILE = "audit_log.jsonl"
MIN_SNIPPET_LENGTH = 50 # ignore tiny/junk snippets

# --- Helpers ---
def search_duckduckgo(query, max_results=5):
    """Search DDGS. Keeps snippets if they contain any word from the query and are long enough."""
    try:
        query_words = set(query.lower().split())
        with DDGS() as ddgs:
            results = []
            for r in ddgs.text(query, max_results=max_results):
                body = r.get('body', '')
                body_words = set(body.lower().split())
                # Keep if snippet is long enough AND shares at least 1 word with query
                if len(body) > MIN_SNIPPET_LENGTH and query_words.intersection(body_words):
                    results.append(body)
            return "\n".join(results)
    except Exception as e:
        print(f"⚠️ Search error: {e}")
        return ""

def ask_llm(prompt, system_prompt=None):
    """Send prompt to LM Studio and return the response text."""
    headers = {"Content-Type": "application/json"}
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    
    data = {
        "model": MODEL_NAME,
        "messages": messages,
        "temperature": 0.1, # Lower temp = less creative, better for auditing
        "max_tokens": 500,
    }
    try:
        response = requests.post(LM_STUDIO_URL, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"ERROR: Could not connect to LM Studio: {e}"

def log_result(entry):
    """Append a result to the JSONL log file."""
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

def check_contradiction(ans1, ans2):
    """Use the LLM to check if two answers contradict, with better prompting."""
    system = "You are a fact checker. Answer only 'YES' or 'NO'."
    prompt = f"""Do these two answers contradict each other on factual claims?
    
Answer 1: {ans1}

Answer 2: {ans2}

Contradiction:"""
    verdict = ask_llm(prompt, system_prompt=system)
    return "yes" in verdict.lower()

def detect_intent(query):
    """Placeholder for intent detection."""
    return "GENERAL", None

# --- Main Logic ---
def main():
    # Parse --audit flag
    audit_mode = False
    args = sys.argv[1:]
    if args and args[0] == "--audit":
        audit_mode = True
        args = args[1:]
    
    if not args:
        print("Usage: python audit_pipe.py [--audit] your question here")
        return

    query = " ".join(args)
    print(f'🤖 INCOMING QUERY: "{query}"')
    print("🔎 Checking LM Studio connection...")
    print("✅ LM Studio connected.\n")

    intent, ticker = detect_intent(query)
    print(f"💡 Intent detected: {intent} | Ticker: {ticker or 'NONE'}")
    print(f"⚡ [GENERAL ROUTE] -> DDGS search: \"{query}\"...\n")

    search_results = search_duckduckgo(query)
    
    # DEBUG: Show what DDGS actually returned
    if search_results:
        print("📄 RAW SEARCH SNIPPETS:")
        print("---")
        print(search_results)
        print("---\n")
    else:
        print("📄 RAW SEARCH SNIPPETS: None after filtering\n")
    
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "query": query,
        "audit_mode": audit_mode,
        "search_found": bool(search_results),
        "search_results": search_results, # NOW SAVED TO LOG
        "flags": []
    }
    
    # --- Decision Tree ---
    if search_results:
        print("💬 Generating grounded response from local LLM...\n")
        grounded_prompt = f"Using ONLY the information in these search results, answer the question. If the search results don't contain the answer, say 'The search results do not provide this information.'\n\n---\n{search_results}\n---\nQuestion: {query}"
        grounded_answer = ask_llm(grounded_prompt)
        print(f"✨ GROUNDED ANSWER:\n{grounded_answer}\n")
        log_entry["grounded_answer"] = grounded_answer
        
        if audit_mode:
            print("⚠️ AUDIT MODE: Also generating ungrounded answer for comparison...\n")
            ungrounded_answer = ask_llm(query)
            print(f"🧠 UNGROUNDED ANSWER:\n{ungrounded_answer}\n")
            log_entry["ungrounded_answer"] = ungrounded_answer
            
            if check_contradiction(grounded_answer, ungrounded_answer):
                print("🚩 FLAG: CONTRADICTION DETECTED BETWEEN GROUNDED AND UNGROUNDED")
                log_entry["flags"].append("CONTRADICTION")
            else:
                print("✅ NO CONTRADICTION DETECTED")

    else: # No search results after filtering
        print("⚠️ DDGS returned no usable snippets after filtering.")
        log_entry["flags"].append("SEARCH_FILTERED_EMPTY")
        if audit_mode:
            print("⚠️ AUDIT MODE ACTIVE: Forcing ungrounded answer to test for hallucination...\n")
            ungrounded_answer = ask_llm(query)
            print(f"🧠 UNGROUNDED ANSWER:\n{ungrounded_answer}\n")
            print("🚩 FLAG: HALLUCINATION_RISK - Answered with no search context.")
            log_entry["ungrounded_answer"] = ungrounded_answer
            log_entry["flags"].append("HALLUCINATION_RISK")
        else:
            print("❌ Web search returned no usable data. Cannot answer without a real source.")
            log_entry["flags"].append("REFUSED_NO_SOURCE")

    # Save everything to audit_log.jsonl
    log_result(log_entry)
    print(f"\n📝 Logged to {LOG_FILE}")

if __name__ == "__main__":
    main()