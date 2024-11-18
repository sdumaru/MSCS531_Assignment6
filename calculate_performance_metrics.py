import os
import sys

# Path to the m5out folder and stats.txt file
STATS_FILE_PATH = 'm5out/stats.txt'

def parse_stats(file_path, num_cpus):
    """Parse the stats.txt file and extract relevant performance metrics for each CPU."""
    metrics = {}
    cpu_metrics = {f"CPU{i}": {} for i in range(num_cpus)}
    try:
        with open(file_path, 'r') as f:
            for line in f:
                # Skip comments or empty lines
                if line.startswith("#") or line.strip() == "":
                    continue
                
                if "simSeconds" in line:
                    metrics['execution_time'] = float(line.split()[1])

                # Extract metrics based on their key for each CPU
                for i in range(num_cpus):
                    prefix = f"system.cpu{i}."
                    if f'{prefix}cpi' in line:
                        cpu_metrics[f"CPU{i}"]['CPI'] = float(line.split()[1])
                    elif f'{prefix}commitStats0.numInsts ' in line:
                        cpu_metrics[f"CPU{i}"]['commit_insts'] = int(line.split()[1])
                    elif f'{prefix}numCycles' in line:
                        cpu_metrics[f"CPU{i}"]['num_cycles'] = int(line.split()[1])
                    elif f'{prefix}ipc' in line:
                        cpu_metrics[f"CPU{i}"]['IPC'] = float(line.split()[1])
                    elif f'{prefix}commitStats0.committedInstType::SimdFloatAdd' in line:
                        cpu_metrics[f"CPU{i}"]['SIMD_float_add'] = int(line.split()[1])
                    elif f'{prefix}commitStats0.committedInstType::SimdFloatCvt' in line:
                        cpu_metrics[f"CPU{i}"]['SIMD_float_convert'] = int(line.split()[1])
                    elif f'{prefix}commitStats0.committedInstType::SimdFloatMult ' in line:
                        cpu_metrics[f"CPU{i}"]['SIMD_float_multiply'] = int(line.split()[1])

    except FileNotFoundError:
        print(f"Error: {file_path} not found.")
        return None
    
    return (metrics, cpu_metrics)

def main():
    # Check for proper command-line arguments
    if len(sys.argv) != 2:
        print("Usage: python script.py <number_of_cpus>")
        return
    
    try:
        num_cpus = int(sys.argv[1])
        if num_cpus < 1:
            raise ValueError("Number of CPUs must be at least 1.")
    except ValueError as e:
        print(f"Error: {e}")
        return

    # Parse stats.txt and extract metrics for each CPU
    (stats, cpu_stats) = parse_stats(STATS_FILE_PATH, num_cpus)
    
    if stats is None:
        print("Error: Unable to parse stats.txt")
        return

    execution_time = stats.get('execution_time', 0)
    print(f"Total execution time: {execution_time:.5f}")

    # Display the metrics for each CPU
    for cpu, data in cpu_stats.items():
        num_cycles = data.get('num_cycles', 0)
        commit_insts = data.get('commit_insts', 0)
        ipc = data.get('IPC', 0)
        cpi = data.get('CPI', 0)
        simd_float_add = data.get('SIMD_float_add', 0)
        simd_float_cvt = data.get('SIMD_float_convert', 0)
        simd_float_mult = data.get('SIMD_float_multiply', 0)

        print(f"\nMetrics for {cpu}:")
        print(f"  Total Cycles: {num_cycles} per thread")
        print(f"  Total Committed Instructions: {commit_insts} per thread")
        print(f"  Instruction Throughput (IPC): {ipc:.5f} Instructions/Cycle")
        print(f"  Average Instruction Latency (CPI): {cpi:.2f} Cycles/Instruction")
        print(f"  SIMD Float Add: {simd_float_add} Counts")
        print(f"  SIMD Float Convert: {simd_float_cvt} Counts")
        print(f"  SIMD Float Multiply: {simd_float_mult} Counts")    

if __name__ == "__main__":
    main()
