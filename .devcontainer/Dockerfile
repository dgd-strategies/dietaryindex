# Base image with Python preinstalled and VS Code settings
FROM mcr.microsoft.com/vscode/devcontainers/python:3.11

# Install Git LFS which may be needed for large files
RUN apt-get update && \
    apt-get install -y git-lfs && \
    git lfs install && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

WORKDIR /workspace/dietaryindex

CMD ["bash"]
