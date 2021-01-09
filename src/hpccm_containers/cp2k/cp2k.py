from hpccm import config, Stage
from hpccm.building_blocks import gnu, openmpi, generic_build, mkl
from hpccm.building_blocks.packages import packages
from hpccm.primitives import label, baseimage, workdir, shell, environment, runscript
from fire import Fire


def build(container_format='singularity', os='ubuntu20.04', cuda_version='11.0', gpu_version='P100', mkl_version='2020.0-088'):
    image = f'nvcr.io/nvidia/cuda:{cuda_version}-devel-{os}'
    config.set_container_format(container_format)
    stage0 = Stage(name='stage0')
    stage0 += baseimage(image=image, _bootstrap='docker')
    stage0 += label(metadata={'maintainer': 'Luhan Cheng', 'email': 'luhan.cheng@monash.edu'})
    stage0 += packages(apt=['git', 'gfortran', 'mpich', 'libmpich-dev'])
    stage0 += shell(commands=['git clone --depth 1 --branch v8.1.0 https://github.com/cp2k/cp2k.git /cp2k'])
    stage0 += shell(commands=['/cp2k/tools/toolchain/install_requirements_ubuntu.sh'])
    stage0 += environment(variables={
        'CUDA_PATH': '/usr/local/cuda',
        'LD_LIBRARY_PATH': '/usr/local/cuda/:${LD_LIBRARY_PATH}',
        'MKLROOT': '/opt/intel/compilers_and_libraries/linux/mkl'
    })
    stage0 += mkl(
        eula=True,
        version=mkl_version
    )
    stage0 += workdir(directory='/opt/cp2k-toolchain')
    stage0 += shell(commands=[
        'cd /opt/cp2k-toolchain',
        'mkdir scripts && mv /cp2k/tools/toolchain/scripts/* ./scripts/',
        'mv /cp2k/tools/toolchain/install_cp2k_toolchain.sh .',
        'rm -rf /cp2k'
    ])
    stage0 += shell(commands=[
        'cd /opt/cp2k-toolchain',
        f'./install_cp2k_toolchain.sh --mpi-mode=mpich --math-mode=mkl --with-reflapack=no --with-scalapack=no --with-elpa=no --gpu-ver={gpu_version}',
        'rm -rf ./build'
    ])
    stage0 += runscript(commands=[
        'cd /opt/cp2k-toolchain',
        '/bin/bash "$@"'
    ])


    return stage0


if __name__ == '__main__':
    Fire(build)
