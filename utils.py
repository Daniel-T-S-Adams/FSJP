"""
Utility functions for the FSJP solver.
Includes functions for saving and loading problem instances and results.
"""

import json
import os
import pickle
import numpy as np
import pandas as pd
from datetime import datetime


class NumpyEncoder(json.JSONEncoder):
    """JSON encoder that can handle NumPy types."""
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NumpyEncoder, self).default(obj)


def save_instance(instance, filename=None):
    """
    Save an FSJP instance to a JSON file.
    
    Args:
        instance: The FSJPInstance object to save
        filename: Optional filename, if None a default name will be generated
    
    Returns:
        The filename where the instance was saved
    """
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"instance_{instance.num_jobs}j_{instance.num_machines}m_{timestamp}.json"
    
    # Create output directory if it doesn't exist
    os.makedirs("instances", exist_ok=True)
    filepath = os.path.join("instances", filename)
    
    # Create serializable representation
    data = {
        'seed': instance.seed,
        'num_jobs': instance.num_jobs,
        'num_machines': instance.num_machines,
        'jobs': instance.jobs
    }
    
    # Save to file
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2, cls=NumpyEncoder)
    
    return filepath


def load_instance(filepath, instance_class):
    """
    Load an FSJP instance from a JSON file.
    
    Args:
        filepath: The file to load
        instance_class: The class to instantiate (FSJPInstance)
    
    Returns:
        An instance of the provided class
    """
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    # Create instance with the same seed
    instance = instance_class(seed=data['seed'], 
                            num_jobs=data['num_jobs'])
    
    # Override the generated jobs with the loaded ones
    instance.jobs = data['jobs']
    instance.num_machines = data['num_machines']
    
    return instance


def save_results(results, config_info, filename=None):
    """
    Save experiment results to a file.
    
    Args:
        results: Dictionary of algorithm results
        config_info: Dictionary with configuration information
        filename: Optional filename, if None a default name will be generated
    
    Returns:
        The filename where the results were saved
    """
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        num_jobs = config_info.get('num_jobs', 'X')
        filename = f"results_{num_jobs}j_{timestamp}.pkl"
    
    # Create output directory if it doesn't exist
    os.makedirs("results", exist_ok=True)
    filepath = os.path.join("results", filename)
    
    # Prepare data to save
    data = {
        'results': results,
        'config': config_info,
        'timestamp': datetime.now().isoformat()
    }
    
    # Save to file
    with open(filepath, 'wb') as f:
        pickle.dump(data, f)
    
    return filepath


def load_results(filepath):
    """
    Load experiment results from a file.
    
    Args:
        filepath: The file to load
    
    Returns:
        A dictionary with the loaded data
    """
    with open(filepath, 'rb') as f:
        data = pickle.load(f)
    
    return data


def export_results_to_csv(results, config_info, filename=None):
    """
    Export experiment results to CSV format.
    
    Args:
        results: Dictionary of algorithm results
        config_info: Dictionary with configuration information
        filename: Optional filename, if None a default name will be generated
    
    Returns:
        The filename where the CSV was saved
    """
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        num_jobs = config_info.get('num_jobs', 'X')
        filename = f"results_{num_jobs}j_{timestamp}.csv"
    
    # Create output directory if it doesn't exist
    os.makedirs("results", exist_ok=True)
    filepath = os.path.join("results", filename)
    
    # Prepare data for DataFrame
    data = []
    for alg_name, alg_results in results.items():
        for i, result in enumerate(alg_results):
            data.append({
                'algorithm': alg_name,
                'seed': config_info.get('random_seed_base', 0) + i,
                'makespan': result['makespan'],
                'execution_time': result['execution_time']
            })
    
    # Create DataFrame and save to CSV
    df = pd.DataFrame(data)
    df.to_csv(filepath, index=False)
    
    return filepath


def validate_solution(instance, solution):
    """
    Validate if a solution is feasible.
    
    A solution is valid if:
    1. All operations of all jobs are scheduled
    2. Operations of each job are scheduled in the correct order
    3. No machine processes multiple operations at the same time
    
    Args:
        instance: The FSJPInstance for which the solution was generated
        solution: The solution dictionary containing the schedule
        
    Returns:
        tuple: (is_valid, error_message) where is_valid is a boolean and 
               error_message is None if valid or a description of the violation
    """
    schedule = solution.get('schedule', [])
    
    # 1. Check if all operations are scheduled
    scheduled_ops = set()
    for op in schedule:
        op_key = (op['job_id'], op['operation_id'])
        scheduled_ops.add(op_key)
    
    total_required_ops = 0
    for job_id, job in enumerate(instance.jobs):
        total_required_ops += len(job['operations'])
        for op_id in range(len(job['operations'])):
            if (job_id, op_id) not in scheduled_ops:
                return False, f"Operation {op_id} of job {job_id} is not scheduled"
    
    if len(scheduled_ops) != total_required_ops:
        return False, "Schedule contains duplicate operations"
    
    # 2. Check if operations of each job are scheduled in the correct order
    for job_id in range(instance.num_jobs):
        # Get all operations of this job in the schedule
        job_ops = [op for op in schedule if op['job_id'] == job_id]
        job_ops.sort(key=lambda x: x['operation_id'])
        
        for i in range(1, len(job_ops)):
            if job_ops[i-1]['completion_time'] > job_ops[i]['start_time']:
                return False, f"Operation {job_ops[i]['operation_id']} of job {job_id} starts before previous operation completes"
    
    # 3. Check if no machine processes multiple operations at the same time
    for machine_id in range(instance.num_machines):
        # Get all operations on this machine
        machine_ops = [op for op in schedule if op['machine'] == machine_id]
        
        # Sort by start time
        machine_ops.sort(key=lambda x: x['start_time'])
        
        for i in range(1, len(machine_ops)):
            if machine_ops[i-1]['completion_time'] > machine_ops[i]['start_time']:
                return False, f"Operations on machine {machine_id} overlap in time"
    
    return True, None 