# GramAI phase 1: verified knowledge safety

1. Keep a private full MySQL backup. Do not commit the dump or credentials.
2. Close GramAI. Pull the updated code. Open 001_verified_knowledge.sql in MySQL Workbench, connect to the existing server and execute the entire script. The script targets gramai_db; adjust USE only if your database has a different name.
3. Check the three counts at the end. On the supplied baseline, 13 legacy records and 13 pending imports, 0 available verified schemes are expected. The legacy review queue will be reopened for records not already pending.
4. Restart GramAI. Ask about pensions and PM-KISAN: until verified data is published, the application must respond that verified information is unavailable. Old FAQs and cached answers must not be used; recent questions are re-asked. The sync button and legacy approve/correct actions are disabled. Rejection retains the original scheme.
5. If migration errors occur, stop and report the error. MySQL DDL commits implicitly; the script is additive and can be rerun after correcting the error. Do not import the full backup over a working database as a routine migration.

The schema stores pending imports, source registrations, scheme revisions, evidence and aliases. The view exposes only active, current, unexpired published revisions with six evidence fields and enabled source hosts. It is a structural safeguard, not an automated factual verification system. Source registration and publication are intentionally not enabled in the application until the next phase. No verified scheme facts are seeded. Existing query logs, FAQ, cached responses and admin accounts are preserved. Historical success metrics are not accuracy scores. Alias retrieval, real synchronization, translation validation, jurisdiction-aware retrieval, NLP improvements and the evidence editor remain future work. The initial 35-point retrieval cutoff is provisional and requires evaluation.

Run on a disposable database copy first where possible. The supplied dump must remain private.
