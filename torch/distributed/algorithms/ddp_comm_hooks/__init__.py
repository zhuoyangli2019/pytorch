from enum import Enum
from functools import partial

import torch.distributed.algorithms.compression.default_hooks as default
import torch.distributed.algorithms.compression.quantization_hooks as quantization
from torch.nn.parallel import DistributedDataParallel


def ddp_comm_hook_wrapper(comm_hook, model, state):
    model._register_comm_hook(state, comm_hook)


class DDPCommHookType(Enum):
    ALLREDUCE = partial(ddp_comm_hook_wrapper, comm_hook=default.allreduce_hook)
    FP16_COMPRESS = partial(ddp_comm_hook_wrapper, comm_hook=default.allreduce_hook)
    QUANTIZE_PER_TENSOR = partial(
        ddp_comm_hook_wrapper, comm_hook=quantization.quantization_pertensor_hook
    )
    QUANTIZE_PER_CHANNEL = partial(
        ddp_comm_hook_wrapper, comm_hook=quantization.quantization_perchannel_hook
    )


def register_ddp_comm_hook(
    comm_hook_type: DDPCommHookType, model: DistributedDataParallel, state=None
):
    """
        Registers the hooks of ``torch.distributed.algorithms.ddp_comm_hooks``
        to the DDP model. User can specify the type of hook as an enum
        ``DDPCommHookType`` type using ``comm_hook_type`` input. State input will
        be passed to the model.

        Example::
            >>> register_ddp_comm_hook(DDPCommHookType.FP16_COMPRESS, model, state)
    """
    DDPCommHookType.value(model=model, state=state)


def register_ddp_comm_hook_string_wrapper(comm_hook_name, model, state=None):
    """
    Registers the hooks of ``torch.distributed.algorithms.ddp_comm_hooks`` by
    taking ``comm_hook_name`` input as a ``str```. Also, checks whether hook
    is in ``DDPCommHookType``.
    """
    assert comm_hook_name in DDPCommHookType.__members__.keys(), (
        "%s is not in the supported DDP communication hook types: %s."
        % (comm_hook_name, list(DDPCommHookType.__members__.keys())),
    )
    register_ddp_comm_hook(getattr(DDPCommHookType, comm_hook_name), model, state)
