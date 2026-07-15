# Llama RAG Audit Pipeline - Dev Log

## May 29, 2026 - v2.3 Live Data Audit

### What I did today:
1. Stress tested pipeline with real-time queries: NVIDIA stock price, financial advice
2. Fixed the audit script so it saves RAW SEARCH SNIPPETS  
3. Ran 5 tests on my local Llama-3.2-3b model

### Test Results:
- **"Current stock price" test** → Model: "I don't have enough information." No hallucination. Good.
- **"Should I sell NVIDIA" test** → Model gave search context only, no buy/sell advice. Good.
- **"Edison test"** → Model said "not enough info" when web data was vague. Good.
- **"My name test"** → Found real info about me but did NOT make up fake facts. Good.
- **"Moon cheese test"** → Model refused the myth. Good.
- **Audit logging** → All runs logged to audit_log.jsonl with timestamps. Good.

### What I learned:
v2.3 refuses real-time data and financial advice when search results are insufficient. Pipeline holds. My script now catches when the AI lies, agrees with wrong stuff, or makes up biographies.

### Next:
Post 11-sec battle video. Collect edge cases from comments.

2026-07-15 09:12:25 [DEBUG]
 0.00.042.292 I srv          init: The UI is disabled
0.00.042.296 I srv          init: Use --ui/--no-ui (or deprecated --webui/--no-webui) to enable/disable
2026-07-15 09:12:25 [DEBUG]
 0.00.053.107 I srv    load_model: loading model 'C:\Users\baile\.lmstudio\models\unsloth\Qwen3.6-35B-A3B-GGUF\Qwen3.6-35B-A3B-UD-Q2_K_XL.gguf'
2026-07-15 09:12:26 [DEBUG]
 0.00.650.102 W common_fit_params: failed to fit params to free device memory: n_gpu_layers already set by user to 16, abort
2026-07-15 09:12:38 [DEBUG]
 0.13.329.350 W sched_reserve: layer 0 is assigned to device CPU but the fused Gated Delta Net tensor is assigned to device CUDA0 (usually due to missing support)
0.13.329.485 W sched_reserve: fused Gated Delta Net (chunked) not supported, set to disabled
2026-07-15 09:12:39 [DEBUG]
 0.14.271.016 W load_hparams: Qwen-VL models require at minimum 1024 image tokens to function correctly on grounding tasks
0.14.271.021 W load_hparams: if you encounter problems with accuracy, try adding --image-min-tokens 1024
0.14.271.021 W load_hparams: more info: https://github.com/ggml-org/llama.cpp/issues/16842
2026-07-15 09:12:40  [INFO]
 [LM STUDIO SERVER] Success! HTTP server listening on port 1234
2026-07-15 09:12:40  [INFO]
2026-07-15 09:12:40  [INFO]
 [LM STUDIO SERVER] Supported endpoints:
2026-07-15 09:12:40  [INFO]
 [LM STUDIO SERVER]   LM Studio API
2026-07-15 09:12:40  [INFO]
 [LM STUDIO SERVER]    ->  GET  http://localhost:1234/api/v1/models
2026-07-15 09:12:40  [INFO]
 [LM STUDIO SERVER]    ->  POST http://localhost:1234/api/v1/chat
2026-07-15 09:12:40  [INFO]
 [LM STUDIO SERVER]    ->  POST http://localhost:1234/api/v1/models/load
2026-07-15 09:12:40  [INFO]
 [LM STUDIO SERVER]    ->  POST http://localhost:1234/api/v1/models/download
2026-07-15 09:12:40  [INFO]
 [LM STUDIO SERVER]    ->  GET http://localhost:1234/api/v1/models/download/status:job_id
2026-07-15 09:12:40  [INFO]
 [LM STUDIO SERVER]   OpenAI-compatible
2026-07-15 09:12:40  [INFO]
 [LM STUDIO SERVER]    ->  GET  http://localhost:1234/v1/models
2026-07-15 09:12:40  [INFO]
 [LM STUDIO SERVER]    ->  POST http://localhost:1234/v1/responses
2026-07-15 09:12:40  [INFO]
 [LM STUDIO SERVER]    ->  POST http://localhost:1234/v1/chat/completions
2026-07-15 09:12:40  [INFO]
 [LM STUDIO SERVER]    ->  POST http://localhost:1234/v1/completions
2026-07-15 09:12:40  [INFO]
 [LM STUDIO SERVER]    ->  POST http://localhost:1234/v1/embeddings
2026-07-15 09:12:40  [INFO]
2026-07-15 09:12:40  [INFO]
 [LM STUDIO SERVER] Logs are saved into C:\Users\baile\.lmstudio\server-logs
2026-07-15 09:12:40  [INFO]
 Server started.
2026-07-15 09:12:40  [INFO]
 Just-in-time model loading active.
2026-07-15 09:12:48 [DEBUG]
 0.22.700.416 I srv    load_model: loaded multimodal model, 'C:/Users/baile/.lmstudio/models/unsloth/Qwen3.6-35B-A3B-GGUF/mmproj-F32.gguf'
2026-07-15 09:12:48 [DEBUG]
 0.23.106.815 I srv    load_model: initializing, n_slots = 4, n_ctx_slot = 8192, kv_unified = 'true'
2026-07-15 09:12:48 [DEBUG]
 0.23.158.908 I srv          init: chat template supports preserving reasoning, consider enabling it via --reasoning-preserve
2026-07-15 09:12:48 [DEBUG]
 0.23.160.342 I srv  llama_server: model loaded
2026-07-15 09:12:48 [DEBUG]
 0.23.161.644 I srv  llama_server: listening on http://127.0.0.1:52567
2026-07-15 09:13:47 [DEBUG]
 Received request: POST to /v1/chat/completions with body  {
  "model": "qwen3.6-35b-a3b",
  "messages": [
    {
      "role": "system",
      "content": "You are the ENR assistant. The user runs a PID con... <Truncated in logs> ...argin > 0 means stable. Answer using this context."
    },
    {
      "role": "user",
      "content": "what is the margin bc-ad for my PID"
    }
  ]
}
2026-07-15 09:13:47  [INFO]
 [qwen3.6-35b-a3b] Running chat completion on conversation with 2 messages.
2026-07-15 09:13:48 [DEBUG]
 1.22.855.899 I slot get_availabl: id  3 | task -1 | selected slot by LRU, t_last = -1
2026-07-15 09:13:48 [DEBUG]
 1.22.864.318 I slot launch_slot_: id  3 | task 0 | processing task, is_child = 0
2026-07-15 09:13:48  [INFO]
 [qwen3.6-35b-a3b] Prompt processing progress: 0.0%
2026-07-15 09:13:49  [INFO]
 [qwen3.6-35b-a3b] Prompt processing progress: 85.6%
2026-07-15 09:13:50  [INFO]
 [qwen3.6-35b-a3b] Prompt processing progress: 97.0%
2026-07-15 09:13:50  [INFO]
 [qwen3.6-35b-a3b] Prompt processing progress: 100.0%
2026-07-15 09:13:56 [DEBUG]
 1.31.209.798 I slot print_timing: id  3 | task 0 | n_decoded =    100, tg =  16.18 t/s, tg_3s =  16.17 t/s
2026-07-15 09:13:59 [DEBUG]
 1.34.221.792 I slot print_timing: id  3 | task 0 | n_decoded =    151, tg =  16.43 t/s, tg_3s =  16.93 t/s
2026-07-15 09:14:02 [DEBUG]
 1.37.268.235 I slot print_timing: id  3 | task 0 | n_decoded =    205, tg =  16.74 t/s, tg_3s =  17.73 t/s
2026-07-15 09:14:05 [DEBUG]
 1.40.280.137 I slot print_timing: id  3 | task 0 | n_decoded =    257, tg =  16.85 t/s, tg_3s =  17.26 t/s
2026-07-15 09:14:08 [DEBUG]
 1.43.301.156 I slot print_timing: id  3 | task 0 | n_decoded =    307, tg =  16.80 t/s, tg_3s =  16.55 t/s
2026-07-15 09:14:11 [DEBUG]
 1.46.349.727 I slot print_timing: id  3 | task 0 | n_decoded =    358, tg =  16.79 t/s, tg_3s =  16.73 t/s
2026-07-15 09:14:14 [DEBUG]
 1.49.388.371 I slot print_timing: id  3 | task 0 | n_decoded =    409, tg =  16.79 t/s, tg_3s =  16.78 t/s
2026-07-15 09:14:17 [DEBUG]
 1.52.423.899 I slot print_timing: id  3 | task 0 | n_decoded =    460, tg =  16.79 t/s, tg_3s =  16.80 t/s
2026-07-15 09:14:20 [DEBUG]
 1.55.432.542 I slot print_timing: id  3 | task 0 | n_decoded =    512, tg =  16.84 t/s, tg_3s =  17.28 t/s
2026-07-15 09:14:23 [DEBUG]
 1.58.448.800 I slot print_timing: id  3 | task 0 | n_decoded =    564, tg =  16.87 t/s, tg_3s =  17.24 t/s
2026-07-15 09:14:26 [DEBUG]
 2.01.485.067 I slot print_timing: id  3 | task 0 | n_decoded =    615, tg =  16.87 t/s, tg_3s =  16.80 t/s
2026-07-15 09:14:29 [DEBUG]
 2.04.534.462 I slot print_timing: id  3 | task 0 | n_decoded =    666, tg =  16.86 t/s, tg_3s =  16.72 t/s
2026-07-15 09:14:32 [DEBUG]
 2.07.565.606 I slot print_timing: id  3 | task 0 | n_decoded =    718, tg =  16.88 t/s, tg_3s =  17.16 t/s
2026-07-15 09:14:36 [DEBUG]
 2.10.607.440 I slot print_timing: id  3 | task 0 | n_decoded =    770, tg =  16.89 t/s, tg_3s =  17.09 t/s
2026-07-15 09:14:38 [DEBUG]
 2.13.580.258 I slot print_timing: id  3 | task 0 | prompt eval time =    2160.85 ms /   132 tokens (   16.37 ms per token,    61.09 tokens per second)
2.13.580.262 I slot print_timing: id  3 | task 0 |        eval time =   48554.50 ms /   821 tokens (   59.14 ms per token,    16.91 tokens per second)
2.13.580.263 I slot print_timing: id  3 | task 0 |       total time =   50715.35 ms /   953 tokens
2.13.580.263 I slot print_timing: id  3 | task 0 |    graphs reused =        817
2026-07-15 09:14:38 [DEBUG]
 2.13.582.079 I slot      release: id  3 | task 0 | stop processing: n_tokens = 952, truncated = 0
2026-07-15 09:14:39  [INFO]
 [qwen3.6-35b-a3b] Model generated tool calls:  []
2026-07-15 09:14:39  [INFO]
 [qwen3.6-35b-a3b] Generated prediction:  {
  "id": "chatcmpl-r9q4326ntr82p4aghypj",
  "object": "chat.completion",
  "created": 1784121227,
  "model": "qwen3.6-35b-a3b",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "The current margin `bc - ad` for your PID controller is **0.7292**. Since this value is greater than 0, the Exo-Neural Resonator remains stable.",
        "reasoning_content": "Here's a thinking process:\n\n1.  **Analyze User Input:**\n   - User asks: \"what is the margin bc-ad for my PID\"\n   - Context provided in system prompt: \n     - System: Exo-Neural Resonator\n     - Controller: PID controller\n     - Stability check: Routh-Hurwitz on s^3 + a s^2 + b s + c = 0\n     - Margin formula: bc - a*d (where d=1)\n     - Current values: Kp=0.5, Ki=0.1, Kd=0.25, margin=0.7292\n     - Condition: margin > 0 means stable\n\n2.  **Identify Key Information:**\n   - The system prompt explicitly states the current margin value: \"margin=0.7292\"\n   - The formula for the margin is given as bc - a*d (with d=1)\n   - The user is asking for exactly this margin value\n\n3.  **Formulate Response:**\n   - Directly answer with the provided margin value\n   - Confirm stability based on the condition (margin > 0)\n   - Keep it concise and aligned with the context\n   - Example: \"The current margin bc-ad for your PID controller is 0.7292. Since this value is greater than 0, the Exo-Neural Resonator is currently stable.\"\n\n4.  **Check Against Constraints:**\n   - Matches context? Yes.\n   - Answers the question directly? Yes.\n   - Uses provided values correctly? Yes.\n   - No extra fluff? Yes.\n\n5.  **Final Output Generation:** (matches the formulated response)✅\n   \"The current margin bc-ad for your PID controller is 0.7292. Since this value is greater than 0, the Exo-Neural Resonator remains stable.\"✅\n   All constraints met. Proceed. \n   Self-Correction/Refinement during thought: The prompt says \"margin=0.7292\" explicitly, so I just need to state it clearly and confirm stability per the rule given. No calculation needed since it's provided. I'll keep it direct.✅\n   Output matches response.✅\n   Proceeds. \n   [Output Generation] -> \"The current margin bc-ad for your PID controller is 0.7292. Since this value is greater than 0, the Exo-Neural Resonator remains stable.\" (or similar)✅\n   All good. \n   *Self-Correction/Verification during thought*: \n   Wait, let's double check the exact wording in the prompt: \"margin=0.7292\". The question is straightforward. I will just state it directly as requested. No extra math needed since coefficients a,b,c,d aren't explicitly given but margin is already computed. I'll stick to the direct answer.✅\n   Output matches.✅\n   Proceeds. \n   [Final Check of the Prompt]: \"Current values: Kp=0.5, Ki=0.1, Kd=0.25, margin=0.7292.\" -> The margin is explicitly given. I will just report it and confirm stability. All good.✅\n   Output Generation. \n   [Response Text]: \"The current margin bc-ad for your PID controller is 0.7292. Since this value is greater than 0, the Exo-Neural Resonator remains stable.\" (Matches exactly)✅\n   Done. \n   [Output] -> *Proceeds*\n",
        "tool_calls": []
      },
      "logprobs": null,
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 132,
    "completion_tokens": 821,
    "total_tokens": 953,
    "completion_tokens_details": {
      "reasoning_tokens": 776
    }
  },
  "stats": {},
  "system_fingerprint": "qwen3.6-35b-a3b"
}

Cory Hunter Chrysogelos 7/15/2026
