# FSJP Solver

A streamlined solver for the Flexible Shop Job Problem (FSJP) - a generalization of the classic job shop scheduling problem that allows operations to be processed on multiple eligible machines.

## Overview

The FSJP is characterized by:
- Jobs consisting of sequences of operations
- Operations that can be processed on one or more eligible machines
- The objective of minimizing the overall makespan (completion time)

**Note:** In this implementation, machines are homogeneous. While the FSJP traditionally allows for machine-dependent processing times, our implementation uses the same processing time for an operation across all eligible machines. This means processing times depend only on the operation itself, not on which machine processes it.

## Components

- **Core Engine**: `main.py` - Generates instances and runs algorithms
- **Algorithms**: 
  - `shortest_processing_time.py` - Prioritizes operations with shortest processing times  
- **Configuration**: `config.json` - Controls all parameters
- **Results Management**: `results_manager.py` - Structured saving of experiment results
- **Visualization**: `visualize_results.py` - Generates performance charts from results

### Algorithm Behavior with Homogeneous Machines

Since machines are homogeneous in this implementation:

- **Shortest Processing Time** first selects the operation with the absolute shortest processing time, then assigns it to the machine where it can start earliest (typically the first available machine).

## Quick Start

1. Ensure Python 3.6+ is installed
2. Set up a virtual environment:
   ```bash
   # Create a virtual environment
   python3 -m venv venv
   
   # Activate the virtual environment
   # On Linux/macOS:
   source venv/bin/activate
   # On Windows:
   # venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure parameters in `config.json`
5. Run the solver:
   ```bash
   python main.py
   ```
   This will:
   - Run the algorithms on generated problem instances
   - Save results in the `results/[test_name]/` directory
   - Automatically generate visualization charts in `results/[test_name]/charts/`

6. If you want to regenerate charts for existing results:
   ```bash
   # Automatically uses most recent test results
   python visualize_results.py
   
   # Or specify a test name
   python visualize_results.py --test-name basic_test
   ```
7. When finished, deactivate the virtual environment:
   ```bash
   deactivate
   ```

## Development Setup

### Virtual Environment

This project uses a virtual environment to manage dependencies. The virtual environment is not committed to the repository (it's in the `.gitignore` file).

To create or recreate the virtual environment from scratch:
```bash
# Create a new virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # On Linux/macOS
# venv\Scripts\activate   # On Windows

# Install dependencies
pip install -r requirements.txt
```

### Git and .gitignore

The project includes a `.gitignore` file that excludes:
- Virtual environment folders (`venv/`)
- Python cache files (`__pycache__/`, `.pyc`, etc.)
- Results and instances directories (`results/`, `instances/`)
- IDE-specific files

When adding new generated files or directories that should not be committed, consider updating the `.gitignore` file.

## Configuration

The `config.json` file contains all parameters:

```json
{
  "difficulty_parameters": {
    "num_jobs": 10
  },
  "fixed_parameters": {
    "operations_per_job": [7, 10],
    "flexibility": [1, 5],
    "machine_scaling_exponent": 0.5,
    "operation_duration": [1, 10]
  },
  "experiment_parameters": {
    "test_name": "basic_test",
    "num_seeds": 50,
    "random_seed_base": 42000
  },
  "algorithms": {
    "shortest_processing_time": true
  }
}
```

### Key Parameters

- **num_jobs**: Number of jobs to generate
- **operations_per_job**: Range for random number of operations per job
- **flexibility**: Range for random number of eligible machines per operation
- **machine_scaling_exponent**: Controls how machines scale with job count
- **operation_duration**: Range for operation processing times
- **num_seeds**: Number of random problem instances to generate and solve
- **algorithms**: Enable/disable specific solving algorithms

## Results Structure

Results are saved in a structured format:

```
results/
    [test_name]/
        results.json                # Combined configuration and results summary
        instances.json              # All problem instances used in the test
        [algorithm_name]/
            solutions.json          # Complete schedules for each problem instance
            validations.csv         # Makespan and validity verification for each seed
        charts/
            runtime_comparison.png  # Bar chart of algorithm runtimes
            makespan_comparison.png # Bar chart of algorithm makespans
```

The `results.json` file contains both the configuration used for the experiment and the performance summary of each algorithm, including average makespans and runtimes with their standard deviations.

The `instances.json` file contains all problem instances that were used in the test, allowing for reproducibility and further analysis.

The `solutions.json` file contains the actual schedules produced by the algorithm, including the assignment of operations to machines and their timing.

The `validations.csv` file contains the makespan (completion time) and validity status for each seed. Validity is verified by checking that:
1. Operations of each job are scheduled in the correct order
2. No machine processes multiple operations simultaneously
3. All operations are accounted for in the schedule

The visualization charts in the `charts/` directory provide a graphical representation of algorithm performance, with error bars showing the standard deviation across all test seeds.

## Extending

To add a new algorithm:

1. Create a file in `algorithms/` (e.g., `my_algorithm.py`)
2. Implement the function with the same name as the file
3. Enable it in `config.json`

Example algorithm signature:

```python
def my_algorithm(instance):
    # Implement your algorithm here
    return {
        'makespan': float,  # Objective value (lower is better)
        'schedule': list    # List of scheduled operations
    }
```

## License

MIT 