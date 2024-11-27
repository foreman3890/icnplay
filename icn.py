import subprocess
import csv
import time
import os
import signal

# File containing addresses and private keys
csv_file = '1.csv'

# Messages to detect in the output
success_message = 'msg="Next automatic check should be in about'
error_message = "ERROR: Executing sla-oracle-node"
host_error_message = "(6) Could not resolve host: console.icn.global"

# Function to kill any process using port 9000
def kill_process_on_port(port):
    try:
        result = subprocess.check_output(f"lsof -t -i:{port}", shell=True).strip()
        if result:
            pid = int(result)
            os.kill(pid, signal.SIGTERM)
            print(f"Terminated process {pid} using port {port}.")
    except subprocess.CalledProcessError:
        print(f"No process using port {port}.")

# Read private keys from CSV
with open(csv_file, mode='r') as file:
    csv_reader = csv.DictReader(file)
    for row in csv_reader:
        private_key = row['private_key']
        
        # Retry loop for each private key
        while True:
            # Ensure port 9000 is free before starting the process
            kill_process_on_port(9000)
            
            # Construct the command with the private key
            command = f"curl -o- https://console.icn.global/downloads/install/start.sh | bash -s -- -p {private_key[2:]}"
            
            # Run the command as a subprocess
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            
            try:
                error_occurred = False
                while True:
                    output = process.stdout.readline()
                    if output:
                        print(output.strip())  # Print output to console
                        if success_message in output:
                            print(f"Detected success message for private key: {private_key}. Moving to the next key.")
                            process.terminate()
                            process.wait()  # Ensure the process has completely stopped
                            break
                        elif error_message in output or host_error_message in output:
                            print(f"Error detected for private key: {private_key}. Retrying.")
                            error_occurred = True
                            process.terminate()
                            process.wait()
                            time.sleep(3)  # Short delay before retrying
                            break
                    else:
                        time.sleep(1)  # Wait briefly if no output is detected

                # Exit the retry loop if success, otherwise retry on error
                if not error_occurred:
                    break
            
            except KeyboardInterrupt:
                print("Process interrupted. Moving to the next key.")
                process.terminate()
                process.wait()
                break

print("All private keys have been processed.")
