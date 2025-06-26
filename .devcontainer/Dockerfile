FROM rocker/r-ver:4.3.2

RUN apt-get update && apt-get install -y python3 python3-pip && rm -rf /var/lib/apt/lists/*
RUN R -e "install.packages(c('dplyr','readr','haven'))"
RUN pip3 install pandas pytest
WORKDIR /workspace/dietaryindex
CMD ["bash"]
