
import os
from hpccm import config, Stage
from hpccm.building_blocks import gnu, openmpi, packages, nvhpc, hdf5, openmpi, fftw, cmake
from hpccm.primitives import label, baseimage, comment, runscript, shell, environment
from fire import Fire
from hpccm_containers.utils import add_include_path, add_library_path, from_prefix


def build(container_format='singularity', os_release='ubuntu', os_version='20.04', cuda_version='11.0.3', plugins=['scipion-em-motioncorr', 'scipion-pyworkflow', 'scipion-em', 'scipion-app'], xmipp_version='v3.22.01-Eris'):
    # config.set_cpu_architecture('x86_64')
    config.set_container_format(container_format)

    # image = f'{os_release}:{os_version}'
    image = f'nvcr.io/nvidia/cuda:{cuda_version}-devel-{os_release}{os_version}'

    stage0 = Stage(name='stage0')
    stage0 += baseimage(image=image, _bootstrap='docker')
    stage0 += environment(variables={
        'LC_ALL': 'en_AU.UTF-8',
        'LANGUAGE': 'en_AU.UTF-8',
    })
    stage0 += label(metadata={'maintainer': 'Luhan Cheng', 'email': 'luhan.cheng@monash.edu'})
    stage0 += shell(commands=[
        'rm -f /bin/sh && ln -s /bin/bash /bin/sh',
        'rm -f /usr/bin/sh && ln -s /usr/bin/bash /usr/bin/sh',
        '/bin/bash',
    ])

    stage0 += packages(apt=['wget', 'git', 'software-properties-common', 'build-essential', 'locales', 'zlib1g-dev'])
    stage0 += shell(commands=['locale-gen en_AU.UTF-8'])

    stage0 += packages(apt=['freeglut3-dev', 'build-essential', 'libx11-dev', 'libxmu-dev', 'libxi-dev', 'libglu1-mesa', 'libglu1-mesa-dev', 'mesa-utils', 'libgl1-mesa-glx'])
    stage0 += environment(variables=from_prefix('/usr/local/cuda'))

    stage0 += comment('Installing vglrun and TurboVNC')
    stage0 += packages(apt=['ubuntu-desktop', 'vim', 'mesa-utils', 'python3-pip', 'python3-pyqt5', 'pyqt5-dev', 'python3-tk'])
    stage0 += shell(commands=[
        'wget https://swift.rc.nectar.org.au/v1/AUTH_810/CVL-Singularity-External-Files/turbovnc_2.2.5_amd64.deb && dpkg -i turbovnc_2.2.5_amd64.deb && rm turbovnc_2.2.5_amd64.deb',
        'wget https://swift.rc.nectar.org.au/v1/AUTH_810/CVL-Singularity-External-Files/virtualgl_2.6.4_amd64.deb && dpkg -i virtualgl_2.6.4_amd64.deb && rm virtualgl_2.6.4_amd64.deb',
        'apt update',
        'apt -y upgrade'
    ])
    compiler = gnu(version='8')
    stage0 += compiler
    stage0 += hdf5()
    stage0 += openmpi(cuda=True, toolchain=compiler.toolchain, infiniband=False)
    stage0 += fftw(mpi=True, toolchain=compiler.toolchain)

    stage0 += packages(apt=['make', 'python3-tk', 'libtiff5-dev', 'libjpeg-dev', 'libsqlite3-dev', 'openjdk-8-jdk', 'default-jdk', 'cmake', 'python3-opencv'])

    stage0 += shell(commands=[
        'python3 -m pip install scons numpy',
        f'git clone -b {xmipp_version} https://github.com/I2PC/xmipp.git xmipp-bundle',
        'cd xmipp-bundle',
        './xmipp config noAsk',
        './xmipp',
    ])
    prefix='/usr/local/scipion'
    stage0 += shell(commands=[
        'python3 -m pip install --user scipion-installer',
        f'python3 -m scipioninstaller {prefix} -j 4',
        'scipion3 installp -p ' + ' -p '.join(plugins)
    ])
    stage0 += environment(variables=from_prefix(prefix))

    return stage0


if __name__ == '__main__':
    Fire(build)
