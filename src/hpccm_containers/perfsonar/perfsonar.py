from hpccm import config, Stage
from hpccm.building_blocks import gnu, openmpi, packages, nvhpc, generic_build
from hpccm.primitives import label, baseimage
from fire import Fire
from hpccm.primitives.comment import comment
from hpccm.primitives.environment import environment
from hpccm.primitives.runscript import runscript
from hpccm.primitives.shell import shell


def build(container_format='singularity', os='ubuntu:20.04'):
    # image = f'nvcr.io/nvidia/cuda:{cuda_version}-devel-{os}'
    image=os
    config.set_container_format(container_format)
    stage0 = Stage(name='stage0')
    stage0 += baseimage(image=image, _bootstrap='docker')
    stage0 += environment(variables={
        'LC_ALL': 'en_AU.UTF-8',
        'LANGUAGE': 'en_AU.UTF-8',
    })
    stage0 += label(metadata={'maintainer': 'Luhan Cheng', 'email': 'luhan.cheng@monash.edu'})
    stage0 += shell(commands=['rm /usr/bin/sh', 'ln -s /usr/bin/bash /usr/bin/sh', '/usr/bin/bash'])
    stage0 += packages(apt=['wget', 'git', 'software-properties-common', 'build-essential', 'locales'])
    stage0 += shell(commands=['locale-gen en_AU.UTF-8'])
    stage0 += generic_build(
        repository='https://github.com/perfsonar/toolkit.git',
        branch='4.4.0',
        build=['make install']
    )

    return stage0


if __name__ == '__main__':
    Fire(build)
