FROM ubuntu:22.04 

# Avoid interactive prompts during package install
ENV DEBIAN_FRONTEND=noninteractive

# Update and install build-essential
RUN apt-get update && apt-get install -y build-essential python3 curl python3-dev
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && python3 get-pip.py
RUN pip install numpy
RUN pip install chatterbox-tts

# Set default working directory
WORKDIR /app

# Default command
CMD ["/bin/bash"]

