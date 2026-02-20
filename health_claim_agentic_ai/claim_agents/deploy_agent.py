import os
import subprocess

def run(cmd):
    print(f" {cmd}")
    subprocess.run(cmd, shell=True, check=True)

if __name__ == "__main__":

    print("Training ML model...")
    run("python ml/train_model.py")

    print("Building Docker image...")
    run("docker build -t insurance-ai:latest .")

    print("Running container...")
    run("docker run -d -p 5000:5000 --name insurance_ai insurance-ai:latest")

    print(" Deployment complete")
