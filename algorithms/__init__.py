"""
Algorithms package for FSJP (Flexible Shop Job Problem) solvers.
This package contains various algorithms for solving FSJP instances.
"""

from importlib import import_module
import os
import json

def load_algorithms():
    """
    Load all enabled algorithms from config.json.
    
    Returns:
        dict: Dictionary of algorithm name to algorithm function
    """
    # Load configuration
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    algorithms = {}
    
    # Get enabled algorithms from config
    for alg_name, enabled in config['algorithms'].items():
        if not enabled:
            continue
        
        try:
            # Dynamically import the algorithm module
            module_name = f"algorithms.{alg_name}"
            module = import_module(module_name)
            
            # Get the main algorithm function
            if hasattr(module, alg_name):
                algorithms[alg_name] = getattr(module, alg_name)
            else:
                print(f"Warning: Algorithm module '{alg_name}' does not contain the '{alg_name}' function")
        except ImportError:
            print(f"Warning: Cannot import algorithm '{alg_name}'. Make sure the file exists in the algorithms directory.")
    
    return algorithms


def run_algorithm(name, instance):
    """
    Run a specific algorithm on the given instance.
    
    Args:
        name: Name of the algorithm to run
        instance: FSJPInstance to run the algorithm on
        
    Returns:
        dict: Result of the algorithm containing at least 'makespan' and 'schedule'
    """
    import time
    
    # Load algorithms
    algorithms = load_algorithms()
    
    if name not in algorithms:
        return {"makespan": float('inf'), "error": f"Unknown algorithm: {name}"}
    
    # Run the algorithm with timing
    start_time = time.time()
    
    try:
        result = algorithms[name](instance)
    except Exception as e:
        result = {"makespan": float('inf'), "error": f"Error running {name}: {str(e)}"}
    
    execution_time = time.time() - start_time
    
    # Add execution time to result
    if isinstance(result, dict):
        result['execution_time'] = execution_time
    else:
        # If the algorithm didn't return a dict, create one
        result = {
            "makespan": float('inf'),
            "error": f"Algorithm {name} didn't return a valid result",
            "execution_time": execution_time
        }
    
    return result 