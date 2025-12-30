import torch
import collections
import omegaconf
import typing
import pyannote.audio.core

def add_globals():
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