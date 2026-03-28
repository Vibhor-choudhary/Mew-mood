import subprocess
import sys
import os

def run(cmd):
    subprocess.run(cmd, shell=True, check=True)

print("Setting up MeowMood...")

# Step 1 - Install Git LFS
print("Installing Git LFS...")
try:
    run("git lfs install")
    print("Git LFS ready.")
except:
    print("Git LFS not found. Installing...")
    if sys.platform == "darwin":
        run("brew install git-lfs && git lfs install")
    elif sys.platform == "win32":
        print("Please install Git LFS from https://git-lfs.com then run setup.py again")
        sys.exit(1)
    else:
        run("sudo apt-get install git-lfs -y && git lfs install")

# Step 2 - Pull LFS files (downloads model.pth)
print("Downloading ML models...")
try:
    run("git lfs pull")
    print("Models downloaded successfully.")
except:
    print("Could not download models via LFS.")

# Step 3 - Install Python dependencies
print("Installing Python dependencies...")
run(f"{sys.executable} -m pip install -r requirements.txt")

# Step 4 - Create uploads folder if missing
os.makedirs("uploads", exist_ok=True)
print("Uploads folder ready.")

print("\nSetup complete! Run: python app.py")
