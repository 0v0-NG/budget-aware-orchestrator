# mckp_router.py
import itertools

def estimate_subtask_cost(subtask, model):
    """
    Calculates estimated cost based on token estimates and model pricing (per 1,000 tokens).
    """
    tokens_in = subtask.get('est_tokens_in', 500)
    tokens_out = subtask.get('est_tokens_out', 300)
    
    cost_in = (tokens_in / 1000.0) * model['input_price']
    cost_out = (tokens_out / 1000.0) * model['output_price']
    return round(cost_in + cost_out, 6)


def solve_mckp_routing(subtasks, models, budget_cap):
    """
    Evaluates all model assignments across sub-tasks to maximize quality within budget_cap.
    Returns: (is_feasible, best_assignment, total_est_cost, total_quality, message)
    """
    if not subtasks or not models:
        return False, None, 0.0, 0.0, "Missing sub-tasks or candidate models."

    best_quality = -1.0
    best_cost = float('inf')
    best_assignment = None

    # Generate all possible combinations of models for the given sub-tasks
    for combination in itertools.product(models, repeat=len(subtasks)):
        total_cost = 0.0
        total_quality = 0.0
        current_assignment = {}

        for subtask, model in zip(subtasks, combination):
            est_cost = estimate_subtask_cost(subtask, model)
            task_type = subtask.get('task_type', 'general')
            quality = model.get('quality_scores', {}).get(task_type, 0.5)

            total_cost += est_cost
            total_quality += quality
            current_assignment[subtask['id']] = {
                'model_id': model['model_id'],
                'identifier': model['identifier'],
                'est_cost': est_cost,
                'quality': quality
            }

        # Stage 1 Enforcement: Must fit strictly within the budget cap
        if total_cost <= budget_cap:
            # Maximize quality; break ties by choosing the cheaper option
            if (total_quality > best_quality) or (
                total_quality == best_quality and total_cost < best_cost
            ):
                best_quality = total_quality
                best_cost = round(total_cost, 6)
                best_assignment = current_assignment

    if best_assignment is None:
        return (
            False,
            None,
            0.0,
            0.0,
            f"Pre-dispatch block: No model combination fits within the ${budget_cap} budget cap."
        )

    return (
        True,
        best_assignment,
        best_cost,
        round(best_quality, 2),
        "Optimal routing plan found."
    )


# --- Quick Test ---
if __name__ == "__main__":
    sample_models = [
        {
            'model_id': 1,
            'identifier': 'llama-3.1-8b-instant (Cheap)',
            'input_price': 0.0001,
            'output_price': 0.0002,
            'quality_scores': {'extraction': 0.75, 'reasoning': 0.60}
        },
        {
            'model_id': 2,
            'identifier': 'llama-3.3-70b-versatile (Premium)',
            'input_price': 0.0008,
            'output_price': 0.0012,
            'quality_scores': {'extraction': 0.90, 'reasoning': 0.95}
        }
    ]

    sample_subtasks = [
        {'id': 1, 'task_type': 'extraction', 'est_tokens_in': 1000, 'est_tokens_out': 500},
        {'id': 2, 'task_type': 'reasoning', 'est_tokens_in': 1000, 'est_tokens_out': 500}
    ]

    print("--- Test 1: Moderate Budget ($0.0020) ---")
    feasible, plan, cost, quality, msg = solve_mckp_routing(sample_subtasks, sample_models, budget_cap=0.0020)
    print(f"Status: {feasible} | Cost: ${cost} | Quality: {quality} | {msg}")
    if plan:
        for task_id, details in plan.items():
            print(f"  Sub-task {task_id} -> {details['identifier']} (Est Cost: ${details['est_cost']})")

    print("\n--- Test 2: Impossible Budget ($0.0001) ---")
    feasible2, _, _, _, msg2 = solve_mckp_routing(sample_subtasks, sample_models, budget_cap=0.0001)
    print(f"Status: {feasible2} | {msg2}")