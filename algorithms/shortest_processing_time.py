"""
Shortest Processing Time (SPT) algorithm for the FSJP.
"""

def shortest_processing_time(instance):
    """
    A greedy algorithm for FSJP using the Shortest Processing Time heuristic.
    At each step, schedules the operation with the shortest processing time
    on its best eligible machine.
    
    Args:
        instance: FSJPInstance to schedule
        
    Returns:
        dict: Dictionary containing the makespan and schedule
    """
    # Machine availability times
    machine_available = [0] * instance.num_machines
    
    # Job completion tracking
    job_operation_idx = [0] * instance.num_jobs
    job_completion = [0] * instance.num_jobs
    
    # Schedule operations until all jobs are complete
    schedule = []
    
    while not all(job_operation_idx[j] >= len(instance.jobs[j]['operations']) 
                 for j in range(instance.num_jobs)):
        
        # Find next operation to schedule using SPT
        best_processing_time = float('inf')
        best_job = -1
        best_machine = -1
        best_start_time = float('inf')
        
        for job_id in range(instance.num_jobs):
            # Skip if job is complete
            if job_operation_idx[job_id] >= len(instance.jobs[job_id]['operations']):
                continue
            
            # Get the next operation for this job
            operation = instance.jobs[job_id]['operations'][job_operation_idx[job_id]]
            
            # Find the machine with the shortest processing time for this operation
            for machine in operation['eligible_machines']:
                processing_time = operation['processing_times'][machine]
                start_time = max(machine_available[machine], job_completion[job_id])
                
                # Prioritize by processing time, then by start time
                if (processing_time < best_processing_time or 
                    (processing_time == best_processing_time and start_time < best_start_time)):
                    best_processing_time = processing_time
                    best_start_time = start_time
                    best_job = job_id
                    best_machine = machine
                    best_completion_time = start_time + processing_time
        
        # Schedule the best operation
        if best_job != -1:
            operation = instance.jobs[best_job]['operations'][job_operation_idx[best_job]]
            
            schedule.append({
                'job_id': best_job,
                'operation_id': operation['operation_id'],
                'machine': best_machine,
                'start_time': best_start_time,
                'completion_time': best_completion_time
            })
            
            # Update state
            machine_available[best_machine] = best_completion_time
            job_completion[best_job] = best_completion_time
            job_operation_idx[best_job] += 1
    
    # Calculate makespan (maximum completion time)
    makespan = max(job_completion)
    
    return {
        'makespan': makespan,
        'schedule': schedule,
        'algorithm_type': 'shortest_processing_time'
    } 