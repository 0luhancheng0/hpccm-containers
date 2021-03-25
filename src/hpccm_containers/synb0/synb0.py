
import os
from hpccm import config, Stage
from hpccm.building_blocks import gnu, openmpi, packages, nvhpc, generic_build, generic_cmake
from hpccm.primitives import label, baseimage, comment, runscript, shell, environment
from fire import Fire
from hpccm.toolchain import toolchain
from hpccm_containers.utils import add_include_path, add_library_path, from_prefix


def build(container_format='singularity', os_release='ubuntu', os_version='20.04', synb0_commit='4b35200', ants_version='2.3.5'):
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
    stage0 += packages(apt=['wget', 'git', 'software-properties-common', 'build-essential', 'locales', 'zlib1g-dev', 'cmake'])
    stage0 += shell(commands=['locale-gen en_AU.UTF-8'])

    stage0 += shell(commands=['mkdir /OUTPUTS /INPUTS'])
    compiler = gnu(version='10')
    stage0 += compiler
    stage0 += packages(apt=['libgomp1', 'bc', 'dc', 'gzip', 'perl', 'tcsh', 'python3.6'])
    stage0 += generic_cmake(
        repository='https://github.com/ANTsX/ANTs.git',
        branch=f'v{ants_version}',
        prefix='/usr/local/ants',
        toolchain=compiler.toolchain
    )
    stage0 += environment(variables={
        'PATH': "/usr/local/ants/bin:$PATH",
        "ANTSPATH": "/usr/local/ants/bin"
    })
    stage0 += shell(commands=[
        'mkdir /usr/local/synb0',
        'git clone https://github.com/MASILab/Synb0-DISCO.git /usr/local/synb0',
        'cd /usr/local/synb0',
        f'git checkout {synb0_commit}',
    ])
    stage0 += runscript(commands=[
        '/usr/local/synb0/extra/pipeline.sh'
    ])




    return stage0


if __name__ == '__main__':
    Fire(build)
