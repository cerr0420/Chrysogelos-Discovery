# Llama RAG Audit Pipeline - Dev Log

## May 29, 2026 - v2.3 Done

### What I did today:
1. Fixed the audit script so it saves RAW SEARCH SNIPPETS
2. Ran 3 tests on my local Llama-3.2-3b model

### Test Results:
- **Edison test** → Model said "not enough info" when web data was vague. Good.
- **My name test** → Found real info about me but did NOT make up fake facts. Good.
- **Moon cheese test** → Model refused the myth. Good.

### What I learned:
My script now catches when the AI lies, agrees with wrong stuff, or makes up biographies.

### Next:
Try it on stock tickers next.
