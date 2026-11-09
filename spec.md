# SYSTEM SPECIFICATION: Budget-Aware Multi-Agent Orchestration Platform

## Architecture Constraints
- Language: Python
- Frontend: Streamlit
- Database: SQLite (Embedded)
- External APIs: Groq, Google AI Studio, OpenRouter (Keys managed via python-dotenv)

## Core Design Rules
1. Two-Stage Enforcement: Pre-dispatch cost estimation blocks unaffordable tasks; post-call reconciliation deducts actual tokens used.
2. Multiple-Choice Knapsack (MCKP): The router evaluates all possible model combinations across the DAG plan to maximize quality within the budget ceiling.
3. Append-Only Ledger: The `LEDGER` table must use SQLite triggers to strictly prohibit `UPDATE` or `DELETE` operations. All corrections must be appended as new rows.
4. Sequential Execution: Sub-tasks are executed in deterministic topological order. No parallel execution.

## Current Increment Focus
Read this specification and await instructions for the current development increment. Do not invent features outside the immediate requested scope.