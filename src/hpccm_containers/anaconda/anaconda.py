
import os
from hpccm import config, Stage
from hpccm.building_blocks import gnu, openmpi, packages, conda
from hpccm.primitives import label, baseimage
from fire import Fire
from hpccm.primitives.comment import comment
from hpccm.primitives.environment import environment
from hpccm.primitives.runscript import runscript
from hpccm.primitives.shell import shell
from hpccm_containers.utils import add_include_path, add_library_path, from_prefix


def build(container_format='singularity', os_release='ubuntu', os_version='20.04', conda_packages=['conda', 'numpy', 'scipy', 'pandas'],
          python_version='3.9.1', channels=['anaconda', 'defaults', 'conda-forge'], anaconda_version='4.9.2'):
    config.set_container_format(container_format)

    image = f'{os_release}:{os_version}'

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
    stage0 += conda(
        eula=True,
        packages=[f'python={python_version}'] + conda_packages,
        channels=channels,
        version=anaconda_version
    )
    stage0 += environment(variables=from_prefix('/usr/local/anaconda'))

    stage0 += runscript(commands=['source /usr/local/anaconda/etc/profile.d/conda.sh', '/usr/local/anaconda/bin/python3 $*'])

    return stage0


if __name__ == '__main__':
    Fire(build)
