import os
import subprocess
from datetime import datetime

# Product configuration
PRODUCT_NAME = "Chevrolet Silverado 1500"
COMPETITOR1 = "Ford F-150"
COMPETITOR2 = "Dodge Ram 1500"

def ensure_directories():
    """Create necessary directories if they don't exist."""
    directories = ['temp_files', 'logs', 'output']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Ensured directory exists: {directory}/")

def run_script(script_name, section_name):
    """Run a Python script and handle any errors."""
    print("\n" + "=" * 80, flush=True)
    print(f"Running {section_name}...", flush=True)
    print("=" * 80, flush=True)
    
    try:
        process = subprocess.Popen(['python', f'scripts/{script_name}'],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True,
                                bufsize=1,
                                universal_newlines=True)
        
        # Stream stdout in real-time
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip(), flush=True)
                
        # Get the return code
        return_code = process.poll()
        
        if return_code != 0:
            print("Error running", section_name + ":", flush=True)
            error_output = process.stderr.read()
            if error_output:
                print("Error output:", error_output, flush=True)
            print("\nError: Failed to complete", section_name + ". Stopping process.", flush=True)
            exit(1)
            
    except Exception as e:
        print(f"Error executing {script_name}: {str(e)}", flush=True)
        exit(1)

def main():
    print(f"Starting battlecard generation at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Ensure all necessary directories exist
    ensure_directories()
    
    # Get the current timestamp for the run
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    print(f"\nRun timestamp: {timestamp}")
    
    # Create a run-specific log directory
    run_log_dir = os.path.join('logs', f'run_{timestamp}')
    os.makedirs(run_log_dir, exist_ok=True)
    print(f"Created run log directory: {run_log_dir}/")
       
    # Define the sequence of scripts to run
    scripts = [
        ('search-benefits.py', 'Product Benefits Search'),
        ('rag-valueprop.py', 'Value Proposition RAG'),
        ('rag-qualifying.py', 'Qualifying Questions RAG'),
        ('rag-usecases.py', 'Use Cases RAG'),
        ('search-competitor1.py', 'Competitor 1 Search'),
        ('search-competitor2.py', 'Competitor 2 Search'),
        ('rag-competitive.py', 'Competitive Analysis RAG'),
        ('rag-objection.py', 'Objection Handling RAG'),
        ('rag-actionplan.py', 'Action Plan RAG'),
        ('rag-strategicoverview.py', 'Strategic Overview RAG'),
        ('combine_json.py', 'JSON Combination'),
        ('json_to_markdown.py', 'Markdown Conversion')
    ]
    
    # Run each script in sequence
    for script_name, section_name in scripts:
        run_script(script_name, section_name)
    
    print("\nBattlecard generation complete!")

if __name__ == "__main__":
    main()
