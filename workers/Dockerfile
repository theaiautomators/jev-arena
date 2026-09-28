# Existing Blackwell-compatible CUDA/PyTorch base; setup records its image digest.
FROM vllm/vllm-openai:nightly@sha256:ce3c3c81a19e6a4beddf398a6c93e0bf84c067c4f5ddef7f9a22f0ac2a74e457
USER root
RUN python3 -m pip install --no-cache-dir 'transformers==5.17.0' 'accelerate>=1.12' 'peft>=0.18' 'einops' 'safetensors' 'fastapi' 'numpy' 'laya==0.3.20' 'decider-ai==1.3.0'
COPY .arena/sources/jevk5 /opt/jevk5
RUN python3 -m pip install --no-deps /opt/jevk5
COPY .arena/sources/semif /opt/semif
RUN python3 -m pip install --no-deps /opt/semif
COPY .arena/sources/laya /opt/laya
RUN python3 -m pip install --no-deps /opt/laya
COPY .arena/sources/nimble/nimble /opt/arena/nimble
COPY workers/runner.py /opt/arena/runner.py
COPY arena/wire.py /opt/arena/wire.py
ENTRYPOINT ["python3", "-u", "/opt/arena/runner.py"]
