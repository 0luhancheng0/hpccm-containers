from os import environ
from hpccm import config, Stage
from hpccm.building_blocks import gnu, openmpi, packages, boost, python, generic_build
from hpccm.building_blocks.generic_autotools import generic_autotools
from hpccm.building_blocks.generic_cmake import generic_cmake
from hpccm.primitives import label, baseimage, comment
from fire import Fire
from hpccm.primitives.environment import environment
from hpccm.primitives.shell import shell
from hpccm.toolchain import toolchain
from hpccm_containers.utils import from_library, from_prefix, shell_with_log, add_flags, add_library_path, add_include_path


def build(container_format='singularity', openmpi_version='2.0.4', gnu_version='10', cfdem_prefix='/usr/local/cfdem',
          cfdem_version='3.8.0', liggghts_prefix='/usr/local/ligghts', lpp_prefix='/usr/local/lpp', image='ubuntu:20.04',
          mlton_version='on-20210117-release', gmp_version='6.2.1'):

    config.set_container_format(container_format)
    stage0 = Stage(name='stage0')
    stage0 += baseimage(image=image, _bootstrap='docker')
    stage0 += label(metadata={'maintainer': 'Luhan Cheng', 'email': 'luhan.cheng@monash.edu'})
    stage0 += shell(commands=['rm /usr/bin/sh', 'ln -s /usr/bin/bash /usr/bin/sh', '/usr/bin/bash'])
    stage0 += packages(apt=['locales', 'wget', 'software-properties-common', 'git', 'build-essential', 'flex',
                            'bison', 'cmake', 'zlib1g-dev', 'gnuplot', 'libreadline-dev', 'libncurses-dev',
                            'libxt-dev', 'libscotch-dev', 'libptscotch-dev', 'libvtk6-dev', 'python-numpy',
                            'python-dev', 'qt5-default', 'git-core', 'libboost-system-dev', 'libboost-thread-dev',
                            'libqt5x11extras5-dev', 'qttools5-dev', 'curl', 'libgl1-mesa-dev', 'libosmesa6-dev', 'libssh2-1',
                            'libtool'])
    compilers = gnu(version=gnu_version)
    stage0 += compilers
    openmpi_building_block = openmpi(version=openmpi_version, toolchain=compilers.toolchain, cuda=False)
    stage0 += openmpi_building_block

    stage0 += generic_autotools(
        url=f'https://gmplib.org/download/gmp/gmp-{gmp_version}.tar.xz',
        prefix='/usr/local/gmp',
        directory=f'gmp-{gmp_version}/',
    )
    stage0 += environment(variables=from_library('/usr/local/gmp'))


    stage0 += generic_build(
        repository='https://github.com/MLton/mlton.git',
        branch=mlton_version,
        build=['make -j'],
        install=['make PREFIX=/usr/local/mlton']
    )


    if cfdem_version == '3.8.0':
        OF_release = '5.x'
        OF_commitHashtag = '538044ac05c4672b37c7df607dca1116fa88df88'
    else:
        raise Exception('Check https://github.com/CFDEMproject/CFDEMcoupling-PUBLIC/blob/master/src/lagrangian/cfdemParticle/cfdTools/versionInfo.H')
    stage0 += comment('Obtain CFDEM source')
    stage0 += shell(commands=[
        f'mkdir -p {cfdem_prefix} {liggghts_prefix} {lpp_prefix}',
        f'git clone --branch {cfdem_version} https://github.com/CFDEMproject/CFDEMcoupling-PUBLIC.git {cfdem_prefix}',
        f'git clone --branch {cfdem_version} https://github.com/CFDEMproject/LIGGGHTS-PUBLIC.git {liggghts_prefix}',
        f'git clone https://github.com/CFDEMproject/LPP.git {lpp_prefix}'
    ])

    stage0 += comment('Install OpenFoam')
    openfoam_prefix = f'/usr/local/OpenFOAM-{OF_release}'
    thirdparty_prefix = f'/usr/local/ThirdParty-{OF_release}'
    stage0 += shell(commands=[
        f'mkdir -p {openfoam_prefix} {thirdparty_prefix}',
        f'git clone https://github.com/OpenFOAM/OpenFOAM-{OF_release}.git {openfoam_prefix} && cd {openfoam_prefix} && git checkout {OF_commitHashtag}',
        f'git clone https://github.com/OpenFOAM/ThirdParty-{OF_release}.git {thirdparty_prefix}',
    ])
    stage0 += shell(commands=[
        f'echo "source {openfoam_prefix}/etc/bashrc" >> ~/.bashrc',
    ])
    # DLIB_PATH = '/usr/lib/x86_64-linux-gnu'
    # INCLUDE_PATH = '/usr/include'

    stage0 += shell_with_log(commands=[
        f'{thirdparty_prefix}/Allwmake -j',  # this breaks with openmpi >= 3,  error: static assertion failed: "MPI_Type_extent was removed in MPI-3.0.  Use MPI_Type_get_extent instead."
        # f'{thirdparty_prefix}/makeParaView -mpi -mesa -mesa-lib {DLIB_PATH}/libOSMesa.so -mesa-include {INCLUDE_PATH}/GL -verbose',
        f'{thirdparty_prefix}/makeParaView -mpi'
        'wmRefresh'
    ])
    stage0 += shell(commands=[
        f'{openfoam_prefix}/Allwmake -j',
    ])


# /usr/bin/g++ -fPIC    -O3 -DNDEBUG  -Wl,--no-undefined -lc    -shared -Wl,-soname,libvtkCommonSystem-pv5.4.so.1 -o ../../../lib/libvtkCommonSystem-pv5.4.so.1 CMakeFiles/vtkCommonSystem.dir/vtkClientSocket.cxx.o CMakeFiles/vtkCommonSystem.dir/vtkDirectory.cxx.o CMakeFiles/vtkCommonSystem.dir/vtkServerSocket.cxx.o CMakeFiles/vtkCommonSystem.dir/vtkSocket.cxx.o CMakeFiles/vtkCommonSystem.dir/vtkSocketCollection.cxx.o CMakeFiles/vtkCommonSystem.dir/vtkThreadMessager.cxx.o CMakeFiles/vtkCommonSystem.dir/vtkTimerLog.cxx.o  -Wl,-rpath,/usr/local/ThirdParty-5.x/build/linux64Gcc/ParaView-5.4.0/lib: ../../../lib/libvtkCommonCore-pv5.4.so.1 ../../../lib/libvtksys-pv5.4.so.1 -lpthread -ldl

    return stage0


if __name__ == '__main__':
    Fire(build)
