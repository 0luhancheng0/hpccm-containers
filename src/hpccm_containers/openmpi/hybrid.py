
import os
from hpccm import config, Stage
from hpccm.building_blocks import packages, openmpi, gnu, ucx, gdrcopy, knem

from hpccm.primitives import label, baseimage, comment, runscript, shell, environment
from fire import Fire
from hpccm_containers.utils import from_prefix, add_binary


import yaml

# https://people.sc.fsu.edu/~jburkardt/c_src/hello_mpi/hello_mpi.c

TESTCASES = [
    'https://people.sc.fsu.edu/~jburkardt/c_src/hello_mpi/hello_mpi.c',
    'https://people.sc.fsu.edu/~jburkardt/c_src/communicator_mpi/communicator_mpi.c',
    'https://gist.githubusercontent.com/huzhifeng/d1cda3f0474261eda72b36ca83f24e21/raw/f2074c30030e01cd8e87ddffe0433df18161c61d/hybrid.c'
]

# TESTCASE_DIR = '/usr/local/testcases'
APPS = "/usr/local/app"

def build(container_format='singularity', os_release='ubuntu', os_version='20.04', openmpi_version='3.1.6', gnu_version='10', ucx_version="1.12.1", cuda_version='11.0', gdrcopy_version="1.3", knem_version="1.1.3"):
    config.set_container_format(container_format)

    image = f'nvcr.io/nvidia/cuda:{cuda_version}-devel-{os_release}{os_version}'

    stage0 = Stage(name='stage0')
    stage0 += baseimage(image=image, _bootstrap='docker')
    stage0 += environment(variables={
        'LC_ALL': 'en_AU.UTF-8',
        'LANGUAGE': 'en_AU.UTF-8',
    })
    stage0 += label(metadata={'maintainer': 'Luhan Cheng', 'email': 'luhan.cheng@monash.edu'})
    stage0 += shell(commands=['rm /usr/bin/sh', 'ln -s /usr/bin/bash /usr/bin/sh', '/usr/bin/bash'])
    stage0 += environment(variables=from_prefix('/usr/local/cuda'))
    stage0 += packages(apt=['wget', 'git', 'software-properties-common', 'build-essential', 'locales', 'zlib1g-dev'])
    stage0 += shell(commands=['locale-gen en_AU.UTF-8'])
    stage0 += gnu(version=gnu_version)

    stage0 += gdrcopy(version=gdrcopy_version, ldconfig=True)
    stage0 += knem(version=knem_version, ldconfig=True)
    stage0 += ucx(knem='/usr/local/knem', version=ucx_version, ldconfig=True)
    stage0 += openmpi(cuda=True, infiniband=False, version=openmpi_version, ucx="/usr/local/ucx", ldconfig=True)

    stage0 += shell(commands=[
        f'mkdir -p {APPS} && cd {APPS}',
        f"mkdir -p {APPS}/src {APPS}/bin",
        f'cd {APPS}/src', *[f'wget {i}' for i in TESTCASES],
        f"cd {APPS}", *[f"mpicc -fopenmp src/{i.split('/')[-1]} -o bin/{i.split('/')[-1].split('.')[0]}" for i in TESTCASES]])
    stage0 += environment(variables=add_binary(f"{APPS}/bin/"))


    return stage0


if __name__ == '__main__':
    Fire(build)
