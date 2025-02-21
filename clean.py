#!/usr/bin/env python3

import os
import glob

def clean_directory(directory: str, pattern: str = "*") -> None:
    """Remove files matching pattern in the specified directory."""
    if not os.path.exists(directory):
        print(f"Directory {directory} does not exist. Skipping...")
        return
    
    files = glob.glob(os.path.join(directory, pattern))
    if not files:
        print(f"No files found in {directory} matching pattern {pattern}")
        return
    
    for file_path in files:
        try:
            os.remove(file_path)
            print(f"Removed: {file_path}")
        except Exception as e:
            print(f"Error removing {file_path}: {e}")

def main():
    # Get the root directory (where this script is located)
    root_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Clean temp_files directory (JSON files only)
    temp_dir = os.path.join(root_dir, "temp_files")
    print("\nCleaning temporary JSON files...")
    clean_directory(temp_dir, "*.json")
    
    # Clean output directory (all files)
    output_dir = os.path.join(root_dir, "output")
    print("\nCleaning output files...")
    clean_directory(output_dir)
    
    # Clean logs directory (all files)
    logs_dir = os.path.join(root_dir, "logs")
    print("\nCleaning logs files...")
    clean_directory(logs_dir)
    
    print("\nCleanup complete!")

if __name__ == "__main__":
    main()
