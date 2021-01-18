from hpccm import config, Stage
from hpccm.building_blocks import gnu, openmpi, packages
from hpccm.primitives import label, baseimage
from fire import Fire


def build(container_format='singularity', os='ubuntu20.04', cuda_version='11.0', openmpi_version='4.0.3', gnu_version='8.1.0'):
    image = f'nvcr.io/nvidia/cuda:{cuda_version}-devel-{os}'
    config.set_container_format(container_format)
    stage0 = Stage(name='stage0')
    stage0 += baseimage(image=image, _bootstrap='docker')
    stage0 += label(metadata={'maintainer': 'Luhan Cheng', 'email': 'luhan.cheng@monash.edu'})
    stage0 += packages(apt=['wget', 'git', 'software-properties-common', 'build-essential'])
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
