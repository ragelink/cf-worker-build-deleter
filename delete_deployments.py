#!/usr/bin/env python3
import os
import sys
import argparse

def main_wrapper():
    # Add the deleter directory to the Python path
    deleter_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'deleter')
    src_dir = os.path.join(deleter_dir, 'src')
    sys.path.insert(0, deleter_dir)
    sys.path.insert(0, src_dir)
    
    # First check if there's an envfile in the current directory or parent
    # and copy any arguments related to envfile location
    root_envfile = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'envfile')
    deleter_envfile = os.path.join(deleter_dir, 'envfile')
    
    # If we have args relating to env-file, adjust paths before passing to real script
    new_args = []
    i = 0
    while i < len(sys.argv):
        if sys.argv[i] == '--env-file' and i + 1 < len(sys.argv):
            # Convert relative paths to absolute
            env_file_path = sys.argv[i + 1]
            if not os.path.isabs(env_file_path):
                env_file_path = os.path.abspath(env_file_path)
            new_args.extend(['--env-file', env_file_path])
            i += 2
        else:
            new_args.append(sys.argv[i])
            i += 1
    
    # Replace sys.argv with our potentially modified arguments
    sys.argv = new_args
    
    # Import and run the main function from the implementation
    try:
        # Try from deleter.src module (preferred path)
        from deleter.src.delete_deployments import main
        main()
    except ImportError as e:
        try:
            # Try with direct src import
            sys.path.insert(0, src_dir)
            from delete_deployments import main as src_main
            src_main()
        except ImportError:
            try:
                # Legacy path for backward compatibility
                from deleter.delete_deployments import main
                main()
            except ImportError:
                print(f"Error: Could not import the delete_deployments module: {e}")
                print("Make sure you're running this script from the project root directory.")
                sys.exit(1)

if __name__ == "__main__":
    main_wrapper() 