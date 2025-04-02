import subprocess

# Define the command to run the PyShiny app
command = ["shiny", "run", "app.py" , "--reload", "--port", "3400", "--host", "0.0.0.0"]

# Start the subprocess
process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

print(f"Shiny app started on http://0.0.0.0:3400 (PID: {process.pid})")