FROM ubuntu:22.04 AS base

# Avoid interactive prompts during package install
ENV DEBIAN_FRONTEND=noninteractive

# Set default working directory
WORKDIR /app
COPY . /app

# Update and install build-essential
RUN apt-get update && apt-get install -y build-essential python3.11 curl python3.11-dev git 
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && python3.11 get-pip.py
# pip install chatterbox-tts
#RUN python3.11 -m pip install --upgrade pip "numpy>=1.24.0,<1.26.0" 
RUN python3.11 -m pip install "git+https://github.com/0xdeadhead/chatterbox-tts.git@eng_only#egg=chatterbox-tts"
RUN python3.11 -m pip install --no-cache-dir -r requirements.txt
# RUN python3.11 -m pip install --upgrade numpy==2.3.4
# RUN pip install --no-cache-dir chatterbox-tts runpod


FROM base AS serverless
CMD ["python3.11", "-u", "main.py"]

FROM base AS pod
CMD ["/bin/bash"]