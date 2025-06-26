FROM python:3.11-slim

WORKDIR /workspace/dietaryindex
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt && pip install --no-cache-dir -e .
CMD ["bash"]
