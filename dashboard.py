# app.py
import sqlite3
import pandas as pd
import streamlit as st
from dag_validator import validate_plan, get_execution_order
from mckp_router import solve_mckp_routing
from api_client import execute_prompt

st.set_page_config(page_title="Budget-Aware AI Orchestrator", layout="wide")
st.title("Budget-Aware AI Task Orchestrator")

# Sidebar Configuration
st.sidebar.header("Stage 1: Budget Controls")
budget_cap = st.sidebar.slider(
    "Maximum Budget Cap ($)", 
    min_value=0.0001, 
    max_value=0.0050, 
    value=0.0020, 
    step=0.0001,
    format="$%.4f"
)
budget_level = st.sidebar.selectbox("Budget Tier", ["Strict", "Standard", "Flexible"])

task_prompt = st.text_input("Enter High-Level Task:", "Analyze Q3 financial report and calculate trends")

if st.button("Run Orchestrator (Simulation Mode)", type="primary"):
    conn = sqlite3.connect('orchestrator.db')
    cursor = conn.cursor()

    # 1. Create Run Record
    cursor.execute(
        "INSERT INTO RUN (task, budget_level, cap, status) VALUES (?, ?, ?, ?)",
        (task_prompt, budget_level, budget_cap, "IN_PROGRESS")
    )
    run_id = cursor.lastrowid

    # 2. Mock Sub-tasks & Multi-Provider Candidate Models
    subtasks = [
        {'id': 1, 'task_type': 'extraction', 'description': 'Extract key metrics from text', 'est_tokens_in': 500, 'est_tokens_out': 200, 'depends_on': []},
        {'id': 2, 'task_type': 'reasoning', 'description': 'Calculate trends based on metrics', 'est_tokens_in': 800, 'est_tokens_out': 400, 'depends_on': [1]}
    ]

    models = [
        {'model_id': 1, 'identifier': 'llama-3.1-8b-instant', 'provider': 'groq', 'input_price': 0.0001, 'output_price': 0.0002, 'quality_scores': {'extraction': 0.80, 'reasoning': 0.60}},
        {'model_id': 2, 'identifier': 'gemini-1.5-flash', 'provider': 'gemini', 'input_price': 0.0003, 'output_price': 0.0006, 'quality_scores': {'extraction': 0.85, 'reasoning': 0.80}},
        {'model_id': 3, 'identifier': 'llama-3.3-70b-versatile', 'provider': 'groq', 'input_price': 0.0008, 'output_price': 0.0012, 'quality_scores': {'extraction': 0.90, 'reasoning': 0.95}}
    ]

    # 3. Validate DAG
    is_valid, dag_msg = validate_plan(subtasks)
    if not is_valid:
        st.error(f"DAG Validation Failed: {dag_msg}")
    else:
        exec_order = get_execution_order(subtasks)
        st.success(f"DAG Validated | Topological Execution Order: {exec_order}")

        # 4. Solve MCKP Routing
        feasible, plan, est_cost, quality, route_msg = solve_mckp_routing(subtasks, models, budget_cap)
        
        if not feasible:
            st.error(route_msg)
            cursor.execute("UPDATE RUN SET status = 'FAILED_BUDGET' WHERE run_id = ?", (run_id,))
            conn.commit()
        else:
            col1, col2, col3 = st.columns(3)
            col1.metric("Run ID", f"#{run_id}")
            col2.metric("Total Estimated Cost", f"${est_cost:.5f}")
            col3.metric("Total Quality Score", f"{quality}")

            # 5. Execute and Record in Ledger
            for task_id in exec_order:
                task_def = next(t for t in subtasks if t['id'] == task_id)
                assignment = plan[task_id]
                model_obj = next(m for m in models if m['model_id'] == assignment['model_id'])

                response = execute_prompt(model_obj['provider'], model_obj['identifier'], task_def['description'])

                with st.expander(f"Sub-task {task_id}: {task_def['description']} -> {model_obj['identifier']}", expanded=True):
                    st.write(f"**Provider:** {model_obj['provider'].upper()} | **Est. Cost:** ${assignment['est_cost']:.5f} | **Quality:** {assignment['quality']}")
                    st.code(response)

                cursor.execute('''
                    INSERT INTO LEDGER 
                    (run_id, subtask_id, model_id, attempt, est_cost, input_price, output_price, decision, reason)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    run_id, task_id, model_obj['model_id'], 1, assignment['est_cost'],
                    model_obj['input_price'], model_obj['output_price'], "SUCCESS", "Simulated execution via UI"
                ))

            cursor.execute("UPDATE RUN SET status = 'COMPLETED' WHERE run_id = ?", (run_id,))
            conn.commit()

    conn.close()

# Display Live Append-Only Ledger from SQLite
st.subheader("Append-Only SQLite Audit Ledger (NFR3)")
conn = sqlite3.connect('orchestrator.db')
ledger_df = pd.read_sql_query("SELECT ledger_id, run_id, subtask_id, model_id, est_cost, decision, reason, created_at FROM LEDGER ORDER BY ledger_id DESC", conn)
conn.close()
st.dataframe(ledger_df, use_container_width=True)