# dag_validator.py

def validate_plan(tasks):
    """
    Validates that the AI-generated sub-task dependencies form a valid DAG.
    Expected format: [{'id': 1, 'depends_on': []}, {'id': 2, 'depends_on': [1]}]
    """
    graph = {task['id']: task.get('depends_on', []) for task in tasks}
    visited = set()
    path = set()

    def check_cycles(node):
        if node in path:
            return False, f"Cycle detected involving sub-task ID: {node}."
        if node in visited:
            return True, ""
        
        path.add(node)
        for dependency in graph.get(node, []):
            if dependency not in graph:
                return False, f"Sub-task {node} depends on a non-existent task {dependency}."
            
            is_valid, error_msg = check_cycles(dependency)
            if not is_valid:
                return False, error_msg
                
        path.remove(node)
        visited.add(node)
        return True, ""

    for task_id in graph:
        is_valid, error_msg = check_cycles(task_id)
        if not is_valid:
            return False, error_msg
            
    return True, "Plan is a valid DAG and safe for execution."


def get_execution_order(tasks):
    """
    Returns a list of task IDs in a valid execution order (Topological Sort).
    """
    graph = {task['id']: task.get('depends_on', []) for task in tasks}
    execution_order = []
    visited = set()

    def dfs(node):
        if node in visited:
            return
        visited.add(node)
        for dependency in graph.get(node, []):
            dfs(dependency)
        execution_order.append(node)

    for task_id in graph:
        dfs(task_id)
        
    return execution_order


# --- Quick Test ---
if __name__ == "__main__":
    valid_plan = [
        {'id': 1, 'depends_on': []},
        {'id': 2, 'depends_on': [1]},
        {'id': 3, 'depends_on': [2]}
    ]
    
    invalid_plan = [
        {'id': 1, 'depends_on': [2]},
        {'id': 2, 'depends_on': [1]}
    ]

    print("Testing Valid Plan:", validate_plan(valid_plan))
    print("Testing Invalid Plan:", validate_plan(invalid_plan))
    print("Execution Order:", get_execution_order(valid_plan))