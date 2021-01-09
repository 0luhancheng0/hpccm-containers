

import hpccm
from hpccm.building_blocks import packages, openmpi, gnu, intel_psxe

from hpccm.primitives import label
from fire import Fire
from hpccm import config, primitives, Stage
from fire import Fire
from hpccm.toolchain import toolchain
import wget
from pathlib import Path

# https://gitlab.com/nvidia/container-images/cuda/blob/master/doc/supported-tags.md


def build(container_format='singularity', os='ubuntu20.04', cuda_version='11.0', openmpi_version='4.0.3', gnu_version='9.1.0'):
    baseimage = f'nvcr.io/nvidia/cuda:{cuda_version}-devel-{os}'
    config.set_container_format(container_format)
    stage0 = Stage(name='stage0')
    stage0 += primitives.baseimage(image=baseimage, _bootstrap='docker')
    stage0 += label(metadata={'maintainer': 'Luhan Cheng', 'email': 'luhan.cheng@monash.edu'})
    compilers = gnu(
        version=gnu_version,
        source=True,
        openacc=True,
    )
    stage0 += openmpi(
        cuda=True,
        infiniband=False,
        version=openmpi_version,
        toolchain=compilers.toolchain
    )
    return stage0

if __name__ == '__main__':
    Fire(build)
