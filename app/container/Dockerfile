FROM nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu22.04

WORKDIR /app

RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Bind python3.10 to python (for library code compatibility and ease of use)
RUN ln -s /usr/bin/python3.10 /usr/bin/python

# Install remaining dependencies
COPY app/container/requirements_container.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy code
COPY app/ .

ENV PYTHONPATH=/app

# Pre-download models load with CPU to avoid CUDA versions errors during build
# Create safe globals to avoid pickle errors
RUN python - <<EOF
import whisperx
import torch
import collections
import omegaconf
import typing
import pyannote.audio.core
torch.serialization.add_safe_globals([omegaconf.base.ContainerMetadata])
torch.serialization.add_safe_globals([omegaconf.listconfig.ListConfig])
torch.serialization.add_safe_globals([typing.Any])
torch.serialization.add_safe_globals([list])
torch.serialization.add_safe_globals([collections.defaultdict])
torch.serialization.add_safe_globals([dict])
torch.serialization.add_safe_globals([int])
torch.serialization.add_safe_globals([omegaconf.nodes.AnyNode])
torch.serialization.add_safe_globals([omegaconf.base.Metadata])
torch.serialization.add_safe_globals([torch.torch_version.TorchVersion])
torch.serialization.add_safe_globals([pyannote.audio.core.model.Introspection])
torch.serialization.add_safe_globals([pyannote.audio.core.task.Specifications])
torch.serialization.add_safe_globals([pyannote.audio.core.task.Problem])
torch.serialization.add_safe_globals([pyannote.audio.core.task.Resolution])
whisperx.load_model("medium", device="cpu", compute_type="float32")
whisperx.load_align_model(
    language_code="ja",
    device="cpu",
    model_name="vumichien/wav2vec2-xls-r-300m-japanese-large-ver2"
)
EOF

CMD ["python", "-m", "container.TranscriptionInstance"]
