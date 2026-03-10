import os
import subprocess

def run(cmd):
    print(f"> {cmd}")
    subprocess.run(cmd, shell=True, check=True)

if __name__ == "__main__":

    print("🔹 Training ML model...")
    run("python ml/train_model.py")

    print("🔹 Stopping old container (if exists)...")
    run("docker stop insurance_ai || true")

    print("🔹 Removing old container (if exists)...")
    run("docker rm insurance_ai || true")

    print("🔹 Building Docker image...")
    run("docker build -t insurance-ai:latest .")

    print("🔹 Running new container...")
    run("docker run -d -p 5000:5000 --name insurance_ai insurance-ai:latest")

    print("🚀 Deployment complete!")
