"""
Results management module for FSJP.
Handles structured saving of experiment results.
"""

import os
import json
import pandas as pd
from datetime import datetime
from utils import validate_solution, NumpyEncoder
import numpy as np

class ResultsManager:
    """
    Manager for saving FSJP experiment results in a structured format.
    
    Results are saved in the following structure:
    results/
        [test_name]/
            results.json                # Combined config and results summary
            instances.json              # All problem instances used in the test
            [algorithm_name]/
                solutions.json          # Contains all solutions for each seed
                validations.csv         # Contains validation results for each seed
    """
    
    def __init__(self, test_name):
        """
        Initialize a results manager.
        
        Args:
            test_name: Name of the test/experiment
        """
        self.test_name = test_name
        self.base_dir = os.path.join("results", test_name)
        
        # Ensure base directory exists
        os.makedirs(self.base_dir, exist_ok=True)
    
    def get_algorithm_dir(self, algorithm_name):
        """Get the directory for a specific algorithm."""
        alg_dir = os.path.join(self.base_dir, algorithm_name)
        os.makedirs(alg_dir, exist_ok=True)
        return alg_dir
    
    def save_instances(self, instances):
        """
        Save all problem instances used in this test run.
        
        Args:
            instances: List of problem instances
            
        Returns:
            Path to the saved file
        """
        filepath = os.path.join(self.base_dir, "instances.json")
        
        # Transform instances to a serializable format
        instances_data = {}
        for i, instance in enumerate(instances):
            instances_data[str(instance.seed)] = {
                'seed': instance.seed,
                'num_jobs': instance.num_jobs,
                'num_machines': instance.num_machines,
                'jobs': instance.jobs
            }
        
        with open(filepath, 'w') as f:
            json.dump(instances_data, f, indent=2, cls=NumpyEncoder)
        
        return filepath
    
    def save_solutions(self, algorithm_name, solutions):
        """
        Save all solutions for an algorithm.
        
        Args:
            algorithm_name: Name of the algorithm
            solutions: List of solutions, one per seed
            
        Returns:
            Path to the saved file
        """
        alg_dir = self.get_algorithm_dir(algorithm_name)
        filepath = os.path.join(alg_dir, "solutions.json")
        
        # Transform solutions to a dictionary indexed by seed
        solutions_dict = {}
        for i, solution in enumerate(solutions):
            seed = solution.get('seed', i)
            solutions_dict[str(seed)] = solution
        
        with open(filepath, 'w') as f:
            json.dump(solutions_dict, f, indent=2, cls=NumpyEncoder)
        
        return filepath
    
    def save_validations(self, algorithm_name, instances, solutions):
        """
        Save validation results for an algorithm.
        
        Args:
            algorithm_name: Name of the algorithm
            instances: List of problem instances, one per seed
            solutions: List of solutions, one per seed
            
        Returns:
            Path to the saved file
        """
        alg_dir = self.get_algorithm_dir(algorithm_name)
        filepath = os.path.join(alg_dir, "validations.csv")
        
        # Create validation data
        validations = []
        for i, (instance, solution) in enumerate(zip(instances, solutions)):
            seed = solution.get('seed', instance.seed)
            is_valid, error_msg = validate_solution(instance, solution)
            makespan = solution.get('makespan', float('inf'))
            
            validations.append({
                'seed': seed,
                'is_valid': is_valid,
                'makespan': makespan,
                'error_message': error_msg
            })
        
        # Save to CSV
        df = pd.DataFrame(validations)
        df.to_csv(filepath, index=False)
        
        return filepath
    
    def save_results_summary(self, config, algorithms, results):
        """
        Save a combined config and results summary.
        
        Args:
            config: Configuration dictionary
            algorithms: List of algorithm names
            results: Dictionary of algorithm results
            
        Returns:
            Path to the saved file
        """
        filepath = os.path.join(self.base_dir, "results.json")
        
        # Create combined configuration and summary
        results_data = {
            'test_name': self.test_name,
            'timestamp': datetime.now().isoformat(),
            'configuration': config,
            'algorithm_results': {}
        }
        
        for alg_name in algorithms:
            if alg_name not in results:
                continue
                
            alg_results = results[alg_name]
            makespans = [r['makespan'] for r in alg_results]
            times = [r['execution_time'] for r in alg_results]
            
            # Calculate standard deviations
            makespan_std = np.std(makespans) if len(makespans) > 1 else 0
            time_std = np.std(times) if len(times) > 1 else 0
            
            results_data['algorithm_results'][alg_name] = {
                'avg_makespan': sum(makespans) / len(makespans),
                'min_makespan': min(makespans),
                'max_makespan': max(makespans),
                'makespan_std': makespan_std,
                'avg_time': sum(times) / len(times),
                'time_std': time_std
            }
        
        with open(filepath, 'w') as f:
            json.dump(results_data, f, indent=2, cls=NumpyEncoder)
        
        return filepath
    
    def save_all_results(self, config, instances, results):
        """
        Save all results in the structured format.
        
        Args:
            config: Configuration dictionary
            instances: List of problem instances, one per seed
            results: Dictionary of algorithm results
            
        Returns:
            Dictionary of saved file paths
        """
        algorithms = list(results.keys())
        
        # Save all instances used in this test run
        instances_path = self.save_instances(instances)
        
        # Save combined results and configuration
        results_summary_path = self.save_results_summary(config, algorithms, results)
        
        saved_files = {
            'results_summary': results_summary_path,
            'instances': instances_path
        }
        
        for alg_name, alg_results in results.items():
            # Add seed information to each solution if not present
            for i, solution in enumerate(alg_results):
                if 'seed' not in solution:
                    solution['seed'] = instances[i].seed
            
            # Save solutions and validations
            saved_files[f"{alg_name}_solutions"] = self.save_solutions(alg_name, alg_results)
            saved_files[f"{alg_name}_validations"] = self.save_validations(alg_name, instances, alg_results)
        
        return saved_files 