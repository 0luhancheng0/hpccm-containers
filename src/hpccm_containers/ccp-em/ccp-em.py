from hpccm import config, Stage
from hpccm import primitives
from hpccm.building_blocks import packages
from hpccm.primitives import label, baseimage, comment, shell, environment
from fire import Fire
from hpccm_containers.utils import from_prefix, add_binary


def build(container_format='singularity', os_release='ubuntu', os_version='20.04', cuda_version='11.0'):
    config.set_container_format(container_format)
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

    stage0 += environment(variables=from_prefix('/usr/local/cuda'))
    stage0 += packages(apt=['wget', 'git', 'software-properties-common', 'build-essential', 'locales', 'zlib1g-dev'])
    stage0 += shell(commands=['locale-gen en_AU.UTF-8'])

    stage0 += comment('Installing vglrun and TurboVNC')
    stage0 += packages(apt=['ubuntu-desktop', 'vim', 'mesa-utils', 'python3-pip', 'python3-pyqt5', 'pyqt5-dev', 'python3-tk'])
    stage0 += shell(commands=[
        'wget https://swift.rc.nectar.org.au/v1/AUTH_810/CVL-Singularity-External-Files/turbovnc_2.2.5_amd64.deb && dpkg -i turbovnc_2.2.5_amd64.deb && rm turbovnc_2.2.5_amd64.deb',
        'wget https://swift.rc.nectar.org.au/v1/AUTH_810/CVL-Singularity-External-Files/virtualgl_2.6.4_amd64.deb && dpkg -i virtualgl_2.6.4_amd64.deb && rm virtualgl_2.6.4_amd64.deb',
        'apt update',
        'apt -y upgrade'
    ])

    stage0 += comment('Installing pre-requisites')
    stage0 += primitives.copy(src="./ccp4-7.1.014-shelx-arpwarp-linux64.tar.gz", dest="/opt/ccp4-7.1.014-shelx-arpwarp-linux64.tar.gz")
    stage0 += shell(commands=[
        'cd /opt && tar -xf ccp4-7.1.014-shelx-arpwarp-linux64.tar.gz && rm ccp4-7.1.014-shelx-arpwarp-linux64.tar.gz',
        'touch $HOME/.agree2ccp4v6',
        'cd ccp4-7.1',
        './BINARY.setup',
    ])
    stage0 += environment(variables=add_binary('/opt/ccp4-7.1/bin'))

    stage0 += comment('Installing CCP-EM')
    stage0 += primitives.copy(src="./ccpem-1.5.0-linux-x86_64.tar.gz", dest="/opt/ccpem-1.5.0-linux-x86_64.tar.gz")
    stage0 += primitives.copy(src="./input.txt", dest="/opt/input.txt")
    stage0 += shell(commands=[
        'touch $HOME/.agree2ccpemv1',
        'cd /opt && tar -xf ccpem-1.5.0-linux-x86_64.tar.gz && rm ccpem-1.5.0-linux-x86_64.tar.gz',
        'cd ccpem-1.5.0',
        './install_ccpem.sh',
        'cat /opt/input.txt | bash install_modeller.sh'
    ])




    return stage0


if __name__ == '__main__':
    Fire(build)
