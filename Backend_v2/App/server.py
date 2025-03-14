import subprocess
import os

# full paths
app_path = r"/home/capstoneheroes/EFDS-AI/EFDS-master/Frontend/app.py"
urt_data_path = r"/home/capstoneheroes/EFDS-AI/Backend_v2/App/urt_data.py"

# Run both apps
subprocess.Popen(["python", app_path])
subprocess.Popen(["python", urt_data_path])
