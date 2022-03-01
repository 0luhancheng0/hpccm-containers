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

    stage0 += packages(apt=['wget', 'git', 'software-properties-common', 'build-essential', 'locales', 'zlib1g-dev'])
    stage0 += shell(commands=['locale-gen en_AU.UTF-8'])

    stage0 += comment('Installing vglrun and TurboVNC')
    stage0 += packages(apt=['ubuntu-desktop', 'vim', 'mesa-utils', 'python3-pip', 'python3-pyqt5', 'pyqt5-dev',
                            'python3-tk', 'cmake', 'libgtk2.0-dev', 'libasound2-dev', 'libavformat-dev', 'libjack-jackd2-dev', 'uuid-dev'])
    stage0 += shell(commands=[
        'wget https://swift.rc.nectar.org.au/v1/AUTH_810/CVL-Singularity-External-Files/turbovnc_2.2.5_amd64.deb && dpkg -i turbovnc_2.2.5_amd64.deb && rm turbovnc_2.2.5_amd64.deb',
        'wget https://swift.rc.nectar.org.au/v1/AUTH_810/CVL-Singularity-External-Files/virtualgl_2.6.4_amd64.deb && dpkg -i virtualgl_2.6.4_amd64.deb && rm virtualgl_2.6.4_amd64.deb',
        'apt update',
        'apt -y upgrade'
    ])
    stage0 += shell(commands=[
        'pip install conan'
    ])
    stage0 += generic_cmake(
        repository='https://github.com/audacity/audacity/',
        branch='Audacity-3.0.5'
    )

    return stage0


if __name__ == '__main__':
    Fire(build)
