from os import environ
from hpccm import config, Stage
from hpccm.building_blocks import gnu, openmpi, generic_build, mkl, python
from hpccm.building_blocks.packages import packages
from hpccm.primitives import label, baseimage, workdir, shell, environment, runscript, comment
from fire import Fire
from hpccm_containers.utils import from_prefix
# ==================== generating arch files ====================
# arch files can be found in the /opt/cp2k-toolchain/install/arch subdirectory
# Wrote /opt/cp2k-toolchain/install/arch/local.ssmp
# Wrote /opt/cp2k-toolchain/install/arch/local.sdbg
# Wrote /opt/cp2k-toolchain/install/arch/local.psmp
# Wrote /opt/cp2k-toolchain/install/arch/local.pdbg
# Wrote /opt/cp2k-toolchain/install/arch/local_warn.psmp
# Wrote /opt/cp2k-toolchain/install/arch/local_coverage.pdbg
# ========================== usage =========================
# Done!
# Now copy:
#   cp /opt/cp2k-toolchain/install/arch/* to the cp2k/arch/ directory
# To use the installed tools and libraries and cp2k version
# compiled with it you will first need to execute at the prompt:
#   source /opt/cp2k-toolchain/install/setup
# To build CP2K you should change directory:
#   cd cp2k/
#   make -j 1 ARCH=local VERSION="ssmp sdbg psmp pdbg"

# arch files for GPU enabled CUDA versions are named "local_cuda.*"
# arch files for valgrind versions are named "local_valgrind.*"
# arch files for coverage versions are named "local_coverage.*"

# Note that these pre-built arch files are for the GNU compiler, users have to adapt them for other compilers.
# It is possible to use the provided CP2K arch files as guidance.

def build(container_format='singularity', os='ubuntu20.04', cuda_version='11.0', gpu_version='V100', mkl_version='2020.0-088', version='psmp', tag='8.1.0'):
    image = f'nvcr.io/nvidia/cuda:{cuda_version}-devel-{os}'
    config.set_container_format(container_format)
    stage0 = Stage(name='stage0')
    stage0 += baseimage(image=image, _bootstrap='docker')
    stage0 += label(metadata={'maintainer': 'Luhan Cheng', 'email': 'luhan.cheng@monash.edu'})
    stage0 += comment('Toolchain installation translated from https://github.com/cp2k/cp2k/blob/master/tools/toolchain/Dockerfile.cuda_mkl')

    stage0 += packages(apt=['git', 'gfortran', 'mpich', 'libmpich-dev', 'software-properties-common', 'python-dev'])
    stage0 += python()
    stage0 += shell(commands=[
        f'git clone --depth 1 --branch v{tag} https://github.com/cp2k/cp2k.git /cp2k',
        'cd /cp2k',
        'git submodule update --init --recursive'
    ])
    stage0 += shell(commands=['/cp2k/tools/toolchain/install_requirements_ubuntu.sh'])
    stage0 += environment(variables={
        'CUDA_PATH': '/usr/local/cuda',
        'LD_LIBRARY_PATH': '/usr/local/cuda/:${LD_LIBRARY_PATH}',
        'MKLROOT': '/opt/intel/compilers_and_libraries/linux/mkl',
        **from_prefix('/usr/local/cuda')
    })
    stage0 += mkl(
        eula=True,
        version=mkl_version
    )
    stage0 += workdir(directory='/opt/cp2k-toolchain')
    stage0 += shell(commands=[
        'cd /opt/cp2k-toolchain',
        'mkdir scripts && cp -r /cp2k/tools/toolchain/scripts/* ./scripts/',
        'cp /cp2k/tools/toolchain/install_cp2k_toolchain.sh .',
    ])
    stage0 += shell(commands=[
        'cd /opt/cp2k-toolchain',
        f'./install_cp2k_toolchain.sh --mpi-mode=openmpi --math-mode=mkl --with-reflapack=no --with-scalapack=no --with-elpa=no --gpu-ver={gpu_version}',
        'rm -rf ./build'
    ])
    stage0 += shell(commands=[
        'cp /opt/cp2k-toolchain/install/arch/* /cp2k/arch/',
        'cd /cp2k',
        "sed  's/source /. /g' /opt/cp2k-toolchain/install/setup > /opt/cp2k-toolchain/install/setup ",
        '. /opt/cp2k-toolchain/install/setup',
        f'make ARCH=local VERSION="{version}" | tee /var/tmp/log.txt'
    ])
    stage0 += environment(variables={
        'PATH': '/cp2k/exe/local:$PATH'
    })
    stage0 += shell(commands=[
        'ln -s /usr/lib/x86_64-linux-gnu/libncursesw.so.6 /usr/lib/x86_64-linux-gnu/libncursesw.so.5',
        'ln -s /usr/lib/x86_64-linux-gnu/libtinfo.so.6 /usr/lib/x86_64-linux-gnu/libtinfo.so.5'
    ])
    stage0 += environment(variables={'LD_LIBRARY_PATH': '/usr/lib/x86_64-linux-gnu/:$LD_LIBRARY_PATH'})
    return stage0


if __name__ == '__main__':
    Fire(build)
