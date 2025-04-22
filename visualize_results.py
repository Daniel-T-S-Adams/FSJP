"""
Visualization script for FSJP experiment results.
Generates bar charts for algorithm runtime and makespan performance.
"""

import os
import json
import matplotlib.pyplot as plt
import numpy as np
import argparse
from matplotlib.ticker import MaxNLocator

def load_results(results_file):
    """
    Load results from a results.json file.
    
    Args:
        results_file: Path to the results.json file
        
    Returns:
        Dictionary containing the results data
    """
    with open(results_file, 'r') as f:
        return json.load(f)

def generate_runtime_chart(results_data, output_dir):
    """
    Generate a bar chart showing average runtimes for each algorithm.
    
    Args:
        results_data: Dictionary containing the experiment results
        output_dir: Directory to save the generated chart
    """
    # Extract algorithm names and their runtime stats
    algorithm_results = results_data.get('algorithm_results', {})
    algorithms = list(algorithm_results.keys())
    
    if not algorithms:
        print("No algorithm results found")
        return
    
    # Extract average runtime and standard deviation for each algorithm
    avg_times = [algorithm_results[alg]['avg_time'] for alg in algorithms]
    time_stds = [algorithm_results[alg].get('time_std', 0) for alg in algorithms]
    
    # Create the bar chart
    plt.figure(figsize=(10, 6))
    bars = plt.bar(algorithms, avg_times, yerr=time_stds, capsize=10)
    
    # Add data labels on top of the bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.001,
                f'{height:.4f}s',
                ha='center', va='bottom', rotation=0)
    
    # Add titles and labels
    plt.title('Runtime of Algorithms')
    plt.xlabel('Algorithm')
    plt.ylabel('Average Runtime (seconds)')
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    
    # Save the chart
    output_file = os.path.join(output_dir, 'runtime_comparison.png')
    plt.savefig(output_file, dpi=300)
    plt.close()
    
    print(f"Runtime chart saved to {output_file}")

def generate_makespan_chart(results_data, output_dir):
    """
    Generate a bar chart showing average makespan for each algorithm.
    
    Args:
        results_data: Dictionary containing the experiment results
        output_dir: Directory to save the generated chart
    """
    # Extract algorithm names and their makespan stats
    algorithm_results = results_data.get('algorithm_results', {})
    algorithms = list(algorithm_results.keys())
    
    if not algorithms:
        print("No algorithm results found")
        return
    
    # Extract average makespan and standard deviation for each algorithm
    avg_makespans = [algorithm_results[alg]['avg_makespan'] for alg in algorithms]
    makespan_stds = [algorithm_results[alg].get('makespan_std', 0) for alg in algorithms]
    
    # Create the bar chart
    plt.figure(figsize=(10, 6))
    bars = plt.bar(algorithms, avg_makespans, yerr=makespan_stds, capsize=10)
    
    # Add data labels on top of the bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.01 * max(avg_makespans),
                f'{height:.2f}',
                ha='center', va='bottom', rotation=0)
    
    # Add titles and labels
    plt.title('Average Makespan of Algorithms')
    plt.xlabel('Algorithm')
    plt.ylabel('Average Makespan')
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    
    # Save the chart
    output_file = os.path.join(output_dir, 'makespan_comparison.png')
    plt.savefig(output_file, dpi=300)
    plt.close()
    
    print(f"Makespan chart saved to {output_file}")

def main():
    """Main function to generate visualization charts."""
    parser = argparse.ArgumentParser(description='Generate visualization charts for FSJP experiment results')
    parser.add_argument('--test-name', type=str, default=None, help='Name of the test to visualize')
    parser.add_argument('--results-dir', type=str, default='results', help='Directory containing results')
    args = parser.parse_args()
    
    # If test name not provided, use the most recent test
    if args.test_name is None:
        test_dirs = [d for d in os.listdir(args.results_dir) 
                    if os.path.isdir(os.path.join(args.results_dir, d))]
        
        if not test_dirs:
            print(f"No test directories found in {args.results_dir}")
            return
        
        # Sort by modification time (most recent first)
        test_dirs.sort(key=lambda d: os.path.getmtime(os.path.join(args.results_dir, d)), reverse=True)
        test_name = test_dirs[0]
        print(f"Using most recent test: {test_name}")
    else:
        test_name = args.test_name
    
    # Construct path to results.json
    results_file = os.path.join(args.results_dir, test_name, 'results.json')
    
    if not os.path.exists(results_file):
        print(f"Results file not found: {results_file}")
        return
    
    # Load results data
    results_data = load_results(results_file)
    
    # Create output directory for charts
    output_dir = os.path.join(args.results_dir, test_name, 'charts')
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate charts
    generate_runtime_chart(results_data, output_dir)
    generate_makespan_chart(results_data, output_dir)
    
    print(f"Charts generated in {output_dir}")

if __name__ == "__main__":
    main() 