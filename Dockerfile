FROM ubuntu:22.04 AS base

# Avoid interactive prompts during package install
ENV DEBIAN_FRONTEND=noninteractive

# Set default working directory
WORKDIR /app
COPY . /app

# Update and install build-essential
RUN apt-get update && apt-get install -y build-essential python3 curl python3-dev
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && python3 get-pip.py
RUN pip install -U pip setuptools wheel
RUN pip install "numpy>=1.24,<1.26" 
RUN pip install --no-build-isolation "pkuseg==0.0.25"
# pip install chatterbox-tts
RUN pip install --no-cache-dir -r requirements.txt
# RUN pip install --no-cache-dir chatterbox-tts runpod


FROM base AS serverless
CMD ["python3", "-u", "main.py"]

FROM base AS pod
CMD ["/bin/bash"]