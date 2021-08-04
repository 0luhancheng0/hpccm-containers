from hpccm import config, Stage
from hpccm.building_blocks import packages, generic_cmake
from hpccm.primitives import label, baseimage, comment, shell, environment
from fire import Fire
from hpccm_containers.utils import from_prefix


def build(container_format='singularity', os_release='ubuntu', os_version='20.04'):
    config.set_container_format(container_format)

    image = f'{os_release}:{os_version}'

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

    stage0 += packages(apt=['wget', 'git', 'software-properties-common', 'build-essential', 'locales', 'zlib1g-dev', 'bc', 'cmake',
                            'bison', 'flex', 'libx11-dev', 'x11proto-core-dev', 'libxi6', 'libxi-dev', 'libxmu6', 'libxmu-dev',
                            'libxmu-headers', 'libgl1-mesa-dev', 'libglu1-mesa-dev', 'libjpeg-dev', 'libevent-dev', 'libncurses-dev',
                            'pkg-config', 'libopenblas-dev'])
    stage0 += shell(commands=['locale-gen en_AU.UTF-8'])

    stage0 += comment('Installing vglrun and TurboVNC')
    stage0 += packages(apt=['ubuntu-desktop', 'vim', 'mesa-utils', 'python3-pip', 'python3-pyqt5', 'pyqt5-dev', 'python3-tk'])
    stage0 += shell(commands=[
        'wget https://swift.rc.nectar.org.au/v1/AUTH_810/CVL-Singularity-External-Files/turbovnc_2.2.5_amd64.deb && dpkg -i turbovnc_2.2.5_amd64.deb && rm turbovnc_2.2.5_amd64.deb',
        'wget https://swift.rc.nectar.org.au/v1/AUTH_810/CVL-Singularity-External-Files/virtualgl_2.6.4_amd64.deb && dpkg -i virtualgl_2.6.4_amd64.deb && rm virtualgl_2.6.4_amd64.deb',
        'apt update',
        'apt -y upgrade'
    ])
    stage0 += generic_cmake(
        repository='https://github.com/BIC-MNI/minc-toolkit-v2.git',
        branch='release-1.9.18.1',
        recursive=True,
        prefix='/opt/minc/1.9.18',
        preconfigure=['sed -i -e \'s/http\:\/\/mirrors\.ibiblio\.org\/gnu\/ftp\/gnu\/gsl/http\:\/\/ftp\.\sun\.ac\.za\/ftp\/pub\/mirrors\/ftp\.gnu\.org\/gsl/g\' cmake-modules/BuildGSL.cmake', ],
        cmake_opts=['-DCMAKE_BUILD_TYPE:STRING=Release', '-DCMAKE_INSTALL_PREFIX:PATH=/opt/minc/1.9.18', '-DMT_BUILD_ABC:BOOL=ON',
                    '-DMT_BUILD_ANTS:BOOL=ON', '-DMT_BUILD_C3D:BOOL=ON', '-DMT_BUILD_ELASTIX:BOOL=ON', '-DMT_BUILD_IM:BOOL=OFF',
                    '-DMT_BUILD_ITK_TOOLS:BOOL=ON', '-DMT_BUILD_LITE:BOOL=OFF', '-DMT_BUILD_SHARED_LIBS:BOOL=ON', '-DMT_BUILD_VISUAL_TOOLS:BOOL=ON',
                    '-DMT_USE_OPENMP:BOOL=ON', '-DUSE_SYSTEM_FFTW3D:BOOL=OFF', '-DUSE_SYSTEM_FFTW3F:BOOL=OFF', '-DUSE_SYSTEM_GLUT:BOOL=OFF',
                    '-DUSE_SYSTEM_GSL:BOOL=OFF', '-DUSE_SYSTEM_HDF5:BOOL=OFF', '-DUSE_SYSTEM_ITK:BOOL=OFF', '-DUSE_SYSTEM_NETCDF:BOOL=OFF',
                    '-DUSE_SYSTEM_NIFTI:BOOL=OFF', '-DUSE_SYSTEM_PCRE:BOOL=OFF', '-DUSE_SYSTEM_ZLIB:BOOL=OFF']
    )
    stage0 += environment(variables=from_prefix('/opt/minc/1.9.18.1'))
    return stage0


if __name__ == '__main__':
    Fire(build)
