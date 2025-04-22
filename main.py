"""
Main runner for FSJP (Flexible Shop Job Problem) experiments.
This script generates problem instances and runs selected algorithms.
"""

import random
import time
import json
import numpy as np
import os
from utils import save_instance, load_instance, save_results, export_results_to_csv
from algorithms import run_algorithm
from results_manager import ResultsManager
from visualize_results import generate_runtime_chart, generate_makespan_chart

# Load configuration
with open('config.json', 'r') as f:
    CONFIG = json.load(f)

class FSJPInstance:
    """Class representing a single FSJP instance."""
    
    def __init__(self, seed, num_jobs=None):
        """Initialize a new FSJP instance with the given parameters."""
        self.seed = seed
        random.seed(seed)
        np.random.seed(seed)
        
        # Use values from config unless overridden
        self.num_jobs = num_jobs if num_jobs is not None else CONFIG['difficulty_parameters']['num_jobs']
        
        # Calculate number of machines based on scaling law
        self.num_machines = max(1, int(self.num_jobs ** CONFIG['fixed_parameters']['machine_scaling_exponent']))
        
        # Generate jobs
        self.jobs = self._generate_jobs()
        
    def _generate_jobs(self):
        """Generate a set of jobs with operations and machine assignments."""
        jobs = []
        
        for job_id in range(self.num_jobs):
            # Determine number of operations for this job
            ops_range = CONFIG['fixed_parameters']['operations_per_job']
            num_operations = random.randint(ops_range[0], ops_range[1])
            
            # Generate operations for this job
            operations = []
            for op_id in range(num_operations):
                # Determine flexibility (number of machines that can process this operation)
                flex_range = CONFIG['fixed_parameters']['flexibility']
                flexibility = random.randint(flex_range[0], 
                                           min(flex_range[1], self.num_machines))
                
                # Select which machines can process this operation
                eligible_machines = random.sample(range(self.num_machines), flexibility)
                
                # Generate processing time for this operation (same across all machines)
                # Use operation_duration range if provided, otherwise use default range
                if 'operation_duration' in CONFIG['fixed_parameters']:
                    duration_range = CONFIG['fixed_parameters']['operation_duration']
                    processing_time = random.uniform(duration_range[0], duration_range[1])
                else:
                    processing_time = random.uniform(10, 100)
                
                # Create dictionary of processing times (same value for all eligible machines)
                processing_times = {machine: processing_time for machine in eligible_machines}
                
                operations.append({
                    'operation_id': op_id,
                    'eligible_machines': eligible_machines,
                    'processing_times': processing_times
                })
            
            jobs.append({
                'job_id': job_id,
                'operations': operations
            })
        
        return jobs
    
    def __str__(self):
        """Return a string representation of the FSJP instance."""
        return (f"FSJP Instance (seed={self.seed}): "
                f"{self.num_jobs} jobs, {self.num_machines} machines")


def main():
    """Main function to run the FSJP experiments."""
    # Extract configuration parameters
    num_seeds = CONFIG['experiment_parameters']['num_seeds']
    num_jobs = CONFIG['difficulty_parameters']['num_jobs']
    ops_range = CONFIG['fixed_parameters']['operations_per_job']
    flex_range = CONFIG['fixed_parameters']['flexibility']
    machine_exp = CONFIG['fixed_parameters']['machine_scaling_exponent']
    random_seed_base = CONFIG['experiment_parameters']['random_seed_base']
    test_name = CONFIG['experiment_parameters'].get('test_name', 'default_test')
    
    print(f"Starting FSJP experiments with {num_seeds} seeds")
    print(f"Test name: {test_name}")
    print(f"Number of jobs: {num_jobs}")
    print(f"Operations per job: {ops_range}, Flexibility: {flex_range}")
    print(f"Machine scaling exponent: {machine_exp}")
    
    # Get enabled algorithms
    enabled_algorithms = [alg for alg, enabled in CONFIG['algorithms'].items() if enabled]
    print("Enabled algorithms:", enabled_algorithms)
    print("-" * 50)
    
    results = {}
    instances = []  # Store all instances for validation
    
    # Initialize results manager
    results_manager = ResultsManager(test_name)
    
    for seed_idx in range(num_seeds):
        seed = random_seed_base + seed_idx
        print(f"\nRunning seed {seed_idx+1}/{num_seeds} (seed value: {seed})")
        
        # Generate problem instance
        instance = FSJPInstance(seed=seed)
        instances.append(instance)  # Store for validation
        print(instance)
        
        # Run enabled algorithms
        for alg_name in enabled_algorithms:
            print(f"  Running {alg_name}...", end="", flush=True)
            result = run_algorithm(alg_name, instance)
            
            # Add seed to result
            result['seed'] = seed
            
            print(f" Done. Makespan: {result['makespan']:.2f}, Time: {result['execution_time']:.4f}s")
            
            # Store result
            if alg_name not in results:
                results[alg_name] = []
            results[alg_name].append(result)
    
    # Print summary
    print("\n" + "=" * 50)
    print("RESULTS SUMMARY")
    print("=" * 50)
    
    # Calculate statistics
    stats = {}
    
    for alg_name, alg_results in results.items():
        makespans = [r['makespan'] for r in alg_results]
        times = [r['execution_time'] for r in alg_results]
        
        stats[alg_name] = {
            'avg_makespan': sum(makespans) / len(makespans),
            'min_makespan': min(makespans),
            'max_makespan': max(makespans),
            'avg_time': sum(times) / len(times)
        }
        
        print(f"{alg_name}:")
        print(f"  Average makespan: {stats[alg_name]['avg_makespan']:.2f}")
        print(f"  Best makespan: {stats[alg_name]['min_makespan']:.2f}")
        print(f"  Average time: {stats[alg_name]['avg_time']:.4f}s")
        print()
    
    # Save results using the structured manager
    config_info = {
        'test_name': test_name,
        'num_jobs': num_jobs,
        'operations_per_job': ops_range,
        'flexibility': flex_range,
        'machine_scaling_exponent': machine_exp,
        'random_seed_base': random_seed_base,
        'num_seeds': num_seeds,
        'algorithms': enabled_algorithms
    }
    
    saved_files = results_manager.save_all_results(config_info, instances, results)
    
    print(f"\nResults saved to:")
    print(f"  - {saved_files['results_summary']} (configuration and results summary)")
    print(f"  - {saved_files['instances']} (problem instances)")
    for alg_name in enabled_algorithms:
        print(f"  - {saved_files[f'{alg_name}_solutions']} (solutions)")
        print(f"  - {saved_files[f'{alg_name}_validations']} (validations)")
    
    # Generate visualization charts
    print("\nGenerating visualization charts...")
    
    # Load the saved results.json file
    results_file = saved_files['results_summary']
    with open(results_file, 'r') as f:
        results_data = json.load(f)
    
    # Create output directory for charts
    charts_dir = os.path.join("results", test_name, "charts")
    os.makedirs(charts_dir, exist_ok=True)
    
    # Generate charts
    generate_runtime_chart(results_data, charts_dir)
    generate_makespan_chart(results_data, charts_dir)
    
    print(f"Visualization charts saved to {charts_dir}")


if __name__ == "__main__":
    main() 