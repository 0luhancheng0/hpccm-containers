import os
from hpccm import config, Stage
from hpccm.building_blocks import gnu, openmpi, packages, nvhpc, conda, gnu, generic_cmake
from hpccm.primitives import label, baseimage, workdir, copy, runscript
from fire import Fire
from hpccm.primitives.comment import comment
from hpccm.primitives.environment import environment
from hpccm.primitives.runscript import runscript
from hpccm.primitives.shell import shell
from hpccm_containers.utils import add_include_path, add_library_path, from_prefix

import wget
def build(container_format='singularity', os_release='ubuntu', os_version='20.04', fmriprep_version='20.2.1', fsl_version='5.0.9', python_version='3.8.6', gnu_version='10', ants_version='2.3.6'):
    config.set_container_format(container_format)

    image = f'{os_release}:{os_version}'

    stage0 = Stage(name='stage0')
    stage0 += baseimage(image=image, _bootstrap='docker')
    stage0 += environment(variables={
        'LC_ALL': 'en_AU.UTF-8',
        'LANGUAGE': 'en_AU.UTF-8',
    })
    stage0 += label(metadata={'maintainer': 'Luhan Cheng', 'email': 'luhan.cheng@monash.edu', 'SourceDockerfile': 'https://github.com/nipreps/fmriprep/blob/master/Dockerfile'})

    stage0 += shell(commands=['rm /bin/sh', 'ln -s /bin/bash /bin/sh', '/bin/bash'])

    stage0 += packages(apt=['wget', 'git', 'software-properties-common', 'build-essential', 'locales', 'cmake', 'python2.7'])
    stage0 += gnu(version=gnu_version)
    stage0 += shell(commands=['locale-gen en_AU.UTF-8'])
    stage0 += conda(
        eula=True,
        pacakges=[f'python={python_version}']
    )
    stage0 += environment(variables=from_prefix('/usr/local/anaconda'))

    stage0 += shell(commands=[
        'wget https://fsl.fmrib.ox.ac.uk/fsldownloads/fslinstaller.py',
        'mkdir -p /usr/local/fsl',
        f'python2.7 fslinstaller.py -d /usr/local/fsl/ -V {fsl_version} -q',
        'rm fslinstaller.py'
    ])

    stage0 += generic_cmake(
        repository='https://github.com/ANTsX/ANTs.git',
        branch=f'v{ants_version}',
        prefix='/usr/local/ants'
    )



    return stage0


if __name__ == '__main__':
    Fire(build)
