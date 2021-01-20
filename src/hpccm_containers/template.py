from hpccm import config, Stage
from hpccm.building_blocks import gnu, openmpi, packages
from hpccm.primitives import label, baseimage
from fire import Fire
from hpccm.primitives.runscript import runscript
from hpccm.primitives.shell import shell


def build(container_format='singularity', os='ubuntu20.04', cuda_version='11.0', openmpi_version='4.0.3', gnu_version='10'):
    image = f'nvcr.io/nvidia/cuda:{cuda_version}-devel-{os}'
    config.set_container_format(container_format)
    stage0 = Stage(name='stage0')
    stage0 += baseimage(image=image, _bootstrap='docker')
    stage0 += label(metadata={'maintainer': 'Luhan Cheng', 'email': 'luhan.cheng@monash.edu'})
    stage0 += shell(commands=['rm /usr/bin/sh', 'ln -s /usr/bin/bash /usr/bin/sh', '/usr/bin/bash'])
    stage0 += packages(apt=['wget', 'git', 'software-properties-common', 'build-essential'])
    compilers = gnu(
        version=gnu_version,
        source=True,
        openacc=True,
    )
    mpi_compilers += openmpi(
        cuda=True,
        infiniband=False,
        version=openmpi_version,
        toolchain=compilers.toolchain
    )
    stage0 += compilers
    stage0 += mpi_compilers
    stage0 += runscript(commands=['/usr/bin/bash'])
    return stage0


if __name__ == '__main__':
    Fire(build)
