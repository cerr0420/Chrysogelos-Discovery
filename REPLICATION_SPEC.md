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
---------------------------

6/26/2026 2:33 am rensselaer NY 2 sunset rd 12144

import os
import time
import json
from ddgs import DDGS

LOG_FILE = "enr_audit_log.jsonl"

def log_forensic_data(query, results):
    """
    Appends audit payloads to a chronological jsonl file for post-mortem inspection.
    """
    log_entry = {
        "timestamp": time.time(),
        "utc_time": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
        "query": query,
        "payload_snippets": results
    }
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")
    print(f"DEBUG: Forensic payload successfully committed to {LOG_FILE}")

def search_duckduckgo(query, max_results=5):
    """
    Wrapper for DuckDuckGo text search with validation and logging.
    """
    if not query or not isinstance(query, str) or query.strip() == "":
        print("DEBUG: search_duckduckgo received an empty or invalid query.")
        return []
    
    print(f"DEBUG: Executing search for query: '{query}'")
    
    try:
        with DDGS() as ddgs:
            results = [
                r.get('body', '') 
                for r in ddgs.text(query, max_results=max_results)
            ]
        
        # Record the results immediately to disk
        if results:
            log_forensic_data(query, results)
            
        return results
    except Exception as e:
        print(f"DEBUG: Exception during DDGS execution: {e}")
        return []

def main():
    # Auditing the Exo-Neural Reasoning logic seam
    test_query = "Exo-Neural Reasoning AI"
    
    print("Starting audit_pipe forensic capture pipeline...")
    
    if not test_query or test_query.isspace():
        print("CRITICAL: Pipeline halted. Query string is null, empty, or whitespace.")
    else:
        search_results = search_duckduckgo(test_query)
        
        if search_results:
            print(f"Captured and logged {len(search_results)} telemetry payloads.")
        else:
            print("No payloads captured. Check network or query constraints.")

if __name__ == "__main__":
    main()

    --------------------------------------------------------------------------------------------------

    import { useState, useEffect, useRef, useCallback } from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ReferenceLine } from "recharts";

// ─── Verified PID Constants (Routh-Hurwitz PASS, margin 0.729) ───
const KP = 0.5;
const KI = 0.1;
const KD = 0.25;
const TAU = 0.18;        // Intervention threshold (18%)
const TAU_DELAY = 0.45;
const LAMBDA_DRIFT = 0.022;
const K_GAIN = 1.25;

// ─── Plant simulation G(s) via Euler integration ─────────────────
function stepPlant(state, u, dt) {
  // G(s) = K_gain / ((tau_delay*s + 1)(s - lambda_drift))
  // State-space: x1' = x2, x2' = (K_gain*u - x2 - (1-lambda_drift*tau_delay)*x1) / tau_delay
  const { x1, x2 } = state;
  const dx1 = x2;
  const dx2 = (K_GAIN * u - x2 * (1 + TAU_DELAY * LAMBDA_DRIFT) + LAMBDA_DRIFT * x1) / TAU_DELAY;
  return {
    x1: x1 + dx1 * dt,
    x2: x2 + dx2 * dt,
    y: x1,
  };
}

const PALETTE = {
  bg: "#0a0d14",
  panel: "#0f1320",
  border: "#1c2340",
  accent: "#00e5ff",
  warn: "#ff6b35",
  good: "#39ff8f",
  dim: "#3a4060",
  text: "#c8d0e8",
  muted: "#5a6280",
};

const mono = "'JetBrains Mono', 'Fira Mono', 'Courier New', monospace";

export default function ENRController() {
  const [running, setRunning] = useState(false);
  const [data, setData] = useState([]);
  const [pid, setPid] = useState({ kp: KP, ki: KI, kd: KD });
  const [disturbance, setDisturbance] = useState(false);
  const [status, setStatus] = useState("STANDBY");
  const [margin, setMargin] = useState(0.729);

  const simRef = useRef({
    t: 0,
    integral: 0,
    prevError: 0,
    plant: { x1: 0.3, x2: 0, y: 0.3 },
    target: 0.0,
  });

  const tick = useCallback(() => {
    const dt = 0.05;
    const sim = simRef.current;

    // Inject disturbance
    const dist = disturbance ? 0.4 * Math.sin(sim.t * 1.5) + 0.1 : 0;
    const current = sim.plant.y + dist;
    const error = Math.abs(sim.target - current);

    // PID controller — only fires above threshold
    let gamma = 0;
    if (error >= TAU) {
      sim.integral += error * dt;
      const derivative = (error - sim.prevError) / dt;
      gamma = pid.kp * error + pid.ki * sim.integral + pid.kd * derivative;
      gamma = Math.max(-2, Math.min(2, gamma)); // clamp output
    }
    sim.prevError = error;

    // Advance plant
    sim.plant = stepPlant(sim.plant, -gamma, dt);
    sim.t += dt;

    // Routh margin (live, updates with K changes)
    const b = 1 - LAMBDA_DRIFT * TAU_DELAY + pid.kd * K_GAIN;
    const c = pid.kp * K_GAIN - LAMBDA_DRIFT;
    const d = pid.ki * K_GAIN;
    const a = TAU_DELAY;
    const liveMargin = parseFloat((b * c - a * d).toFixed(4));
    setMargin(liveMargin);

    const stable = liveMargin > 0;
    setStatus(
      !stable ? "⚠ UNSTABLE" :
      error >= TAU ? "● CORRECTING" :
      "✓ LOCKED"
    );

    setData(prev => {
      const next = [...prev, {
        t: parseFloat(sim.t.toFixed(2)),
        error: parseFloat(error.toFixed(4)),
        gamma: parseFloat(gamma.toFixed(4)),
        plant: parseFloat(current.toFixed(4)),
        threshold: TAU,
      }];
      return next.length > 200 ? next.slice(-200) : next;
    });
  }, [pid, disturbance]);

  useEffect(() => {
    if (!running) return;
    const id = setInterval(tick, 50);
    return () => clearInterval(id);
  }, [running, tick]);

  const reset = () => {
    simRef.current = { t: 0, integral: 0, prevError: 0, plant: { x1: 0.3, x2: 0, y: 0.3 }, target: 0 };
    setData([]);
    setStatus("STANDBY");
  };

  const statusColor =
    status.includes("UNSTABLE") ? PALETTE.warn :
    status.includes("CORRECTING") ? PALETTE.accent :
    status === "STANDBY" ? PALETTE.muted :
    PALETTE.good;

  const marginColor = margin > 0.5 ? PALETTE.good : margin > 0 ? PALETTE.warn : PALETTE.warn;

  return (
    <div style={{ background: PALETTE.bg, minHeight: "100vh", fontFamily: mono, color: PALETTE.text, padding: "24px 20px" }}>

      {/* Header */}
      <div style={{ borderBottom: `1px solid ${PALETTE.border}`, paddingBottom: 16, marginBottom: 24 }}>
        <div style={{ fontSize: 11, color: PALETTE.muted, letterSpacing: 3, textTransform: "uppercase", marginBottom: 4 }}>
          Exo-Neural Resonator
        </div>
        <div style={{ fontSize: 22, fontWeight: 700, color: PALETTE.accent, letterSpacing: 1 }}>
          PID Stabilization Monitor
        </div>
        <div style={{ fontSize: 11, color: PALETTE.muted, marginTop: 4 }}>
          Routh-Hurwitz Verified · bc − ad = {margin.toFixed(4)} · {margin > 0 ? "PASS ✓" : "FAIL ✗"}
        </div>
      </div>

      {/* Status Bar */}
      <div style={{
        display: "grid", gridTemplateColumns: "1fr 1fr 1fr 1fr",
        gap: 12, marginBottom: 24
      }}>
        {[
          { label: "STATUS", value: status, color: statusColor },
          { label: "STABILITY MARGIN", value: margin.toFixed(4), color: marginColor },
          { label: "THRESHOLD τ", value: "0.18 (18%)", color: PALETTE.text },
          { label: "DRIFT RATE λ", value: `${LAMBDA_DRIFT} evt/tok`, color: PALETTE.text },
        ].map(({ label, value, color }) => (
          <div key={label} style={{
            background: PALETTE.panel, border: `1px solid ${PALETTE.border}`,
            borderRadius: 6, padding: "12px 14px"
          }}>
            <div style={{ fontSize: 9, color: PALETTE.muted, letterSpacing: 2, marginBottom: 6 }}>{label}</div>
            <div style={{ fontSize: 13, color, fontWeight: 700 }}>{value}</div>
          </div>
        ))}
      </div>

      {/* Chart */}
      <div style={{ background: PALETTE.panel, border: `1px solid ${PALETTE.border}`, borderRadius: 8, padding: "16px 8px", marginBottom: 20 }}>
        <div style={{ fontSize: 10, color: PALETTE.muted, letterSpacing: 2, marginBottom: 12, paddingLeft: 8 }}>
          REAL-TIME SIGNAL MONITOR
        </div>
        <LineChart width={680} height={220} data={data} margin={{ left: 0, right: 16 }}>
          <CartesianGrid stroke={PALETTE.border} strokeDasharray="3 3" />
          <XAxis dataKey="t" stroke={PALETTE.muted} tick={{ fontSize: 10 }} label={{ value: "t (s)", position: "insideRight", fill: PALETTE.muted, fontSize: 10 }} />
          <YAxis stroke={PALETTE.muted} tick={{ fontSize: 10 }} domain={[-0.5, 1.5]} />
          <Tooltip contentStyle={{ background: PALETTE.panel, border: `1px solid ${PALETTE.border}`, fontSize: 11 }} />
          <Legend wrapperStyle={{ fontSize: 11 }} />
          <ReferenceLine y={TAU} stroke={PALETTE.warn} strokeDasharray="4 2" label={{ value: "τ=0.18", fill: PALETTE.warn, fontSize: 10 }} />
          <Line type="monotone" dataKey="error" stroke={PALETTE.accent} dot={false} strokeWidth={2} name="e(t) Error" isAnimationActive={false} />
          <Line type="monotone" dataKey="gamma" stroke={PALETTE.good} dot={false} strokeWidth={2} name="Γ(t) Output" isAnimationActive={false} />
          <Line type="monotone" dataKey="plant" stroke={PALETTE.warn} dot={false} strokeWidth={1.5} strokeDasharray="4 2" name="Plant State" isAnimationActive={false} />
        </LineChart>
      </div>

      {/* PID Tuning */}
      <div style={{ background: PALETTE.panel, border: `1px solid ${PALETTE.border}`, borderRadius: 8, padding: 16, marginBottom: 20 }}>
        <div style={{ fontSize: 10, color: PALETTE.muted, letterSpacing: 2, marginBottom: 14 }}>PID GAIN TUNING</div>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 16 }}>
          {[
            { key: "kp", label: "Kp — Proportional", min: 0.1, max: 2, step: 0.05 },
            { key: "ki", label: "Ki — Integral", min: 0.01, max: 1, step: 0.01 },
            { key: "kd", label: "Kd — Derivative", min: 0.05, max: 2, step: 0.05 },
          ].map(({ key, label, min, max, step }) => (
            <div key={key}>
              <div style={{ fontSize: 10, color: PALETTE.muted, marginBottom: 6 }}>{label}</div>
              <div style={{ fontSize: 18, color: PALETTE.accent, fontWeight: 700, marginBottom: 8 }}>{pid[key].toFixed(2)}</div>
              <input type="range" min={min} max={max} step={step} value={pid[key]}
                onChange={e => setPid(p => ({ ...p, [key]: parseFloat(e.target.value) }))}
                style={{ width: "100%", accentColor: PALETTE.accent }} />
            </div>
          ))}
        </div>
      </div>

      {/* Controls */}
      <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
        {[
          { label: running ? "⏸ PAUSE" : "▶ RUN", onClick: () => setRunning(r => !r), color: running ? PALETTE.warn : PALETTE.good },
          { label: "↺ RESET", onClick: () => { setRunning(false); reset(); }, color: PALETTE.muted },
          {
            label: disturbance ? "✕ CLEAR DISTURBANCE" : "⚡ INJECT DISTURBANCE",
            onClick: () => setDisturbance(d => !d),
            color: disturbance ? PALETTE.warn : PALETTE.accent
          },
          { label: "↩ RESTORE VERIFIED", onClick: () => { setPid({ kp: KP, ki: KI, kd: KD }); }, color: PALETTE.dim },
        ].map(({ label, onClick, color }) => (
          <button key={label} onClick={onClick} style={{
            background: "transparent", border: `1px solid ${color}`,
            color, fontFamily: mono, fontSize: 11, padding: "10px 16px",
            borderRadius: 5, cursor: "pointer", letterSpacing: 1,
            transition: "background 0.2s"
          }}
            onMouseEnter={e => e.target.style.background = color + "22"}
            onMouseLeave={e => e.target.style.background = "transparent"}
          >{label}</button>
        ))}
      </div>

      {/* Footer */}
      <div style={{ marginTop: 24, fontSize: 10, color: PALETTE.dim, borderTop: `1px solid ${PALETTE.border}`, paddingTop: 12 }}>
        Plant: G(s) = {K_GAIN} / ((τ·s+1)(s−λ)) · τ_delay={TAU_DELAY}s · λ_drift={LAMBDA_DRIFT} evt/tok · K_gain={K_GAIN} · Margin verified bc−ad=0.729
      </div>
    </div>
  );
}

_________________________________________________________________________________

