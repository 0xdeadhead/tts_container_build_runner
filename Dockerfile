FROM ubuntu:22.04 AS base

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app
COPY . /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gfortran libopenblas-dev liblapack-dev \
    python3 python3-dev python3-distutils curl \
    && rm -rf /var/lib/apt/lists/*

RUN curl -sS https://bootstrap.pypa.io/get-pip.py -o /tmp/get-pip.py \
    && python3 /tmp/get-pip.py \
    && python3 -m pip install --no-cache-dir --upgrade pip setuptools wheel

# Ensure numpy wheel is available
RUN python3 -m pip install --no-cache-dir numpy==2.0.2

# Build wheels for everything into /wheels; ignore failures so we can build pkuseg wheel separately if needed
RUN python3 -m pip wheel --wheel-dir=/wheels -r requirements.txt || true

# If pkuseg wheel didn't get built above, build pkuseg wheel explicitly with no build isolation
RUN PIP_NO_BUILD_ISOLATION=1 python3 -m pip wheel --wheel-dir=/wheels pkuseg==0.0.25 || true

# Install from wheelhouse only
RUN python3 -m pip install --no-index --find-links=/wheels --no-cache-dir -r requirements.txt

FROM base AS serverless
CMD ["python3", "-u", "main.py"]

FROM base AS pod
CMD ["/bin/bash"]
