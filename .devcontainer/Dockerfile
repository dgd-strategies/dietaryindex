FROM python:3.11-slim

WORKDIR /workspace/dietaryindex/python
COPY python/requirements.txt ./requirements.txt
RUN apt-get update \
    && apt-get install -y --no-install-recommends r-base \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir -e .
CMD ["bash"]
