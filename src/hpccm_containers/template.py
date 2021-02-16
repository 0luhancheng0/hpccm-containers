
import os
from hpccm import config, Stage
from hpccm.building_blocks import gnu, openmpi, packages, nvhpc
from hpccm.primitives import label, baseimage, comment, runscript, shell, environment
from fire import Fire
from hpccm_containers.utils import add_include_path, add_library_path, from_prefix


def build(container_format='singularity', os_release='ubuntu', os_version='20.04', gpu=True, cuda_version='11.0', desktop=True):
    config.set_container_format(container_format)
    if gpu:
        image = f'nvcr.io/nvidia/cuda:{cuda_version}-devel-{os_release}{os_version}'
    else:
        image = f'{os_release}:{os_version}'

    stage0 = Stage(name='stage0')
    stage0 += baseimage(image=image, _bootstrap='docker')
    stage0 += environment(variables={
        'LC_ALL': 'en_AU.UTF-8',
        'LANGUAGE': 'en_AU.UTF-8',
    })
    stage0 += label(metadata={'maintainer': 'Luhan Cheng', 'email': 'luhan.cheng@monash.edu'})
    stage0 += shell(commands=['rm /usr/bin/sh', 'ln -s /usr/bin/bash /usr/bin/sh', '/usr/bin/bash'])
    if gpu:
        stage0 += environment(variables=from_prefix('/usr/local/cuda'))
    stage0 += packages(apt=['wget', 'git', 'software-properties-common', 'build-essential', 'locales'])
    stage0 += shell(commands=['locale-gen en_AU.UTF-8'])
    if desktop:
        stage0 += comment('Installing vglrun and TurboVNC')
        stage0 += packages(apt=['ubuntu-desktop', 'vim', 'mesa-utils', 'python3-pip', 'python3-pyqt5', 'pyqt5-dev', 'python3-tk'])
        stage0 += shell(commands=[
            'wget https://swift.rc.nectar.org.au/v1/AUTH_810/CVL-Singularity-External-Files/turbovnc_2.2.5_amd64.deb && dpkg -i turbovnc_2.2.5_amd64.deb && rm turbovnc_2.2.5_amd64.deb',
            'wget https://swift.rc.nectar.org.au/v1/AUTH_810/CVL-Singularity-External-Files/virtualgl_2.6.4_amd64.deb && dpkg -i virtualgl_2.6.4_amd64.deb && rm virtualgl_2.6.4_amd64.deb',
            'apt update',
            'apt -y upgrade'
        ])
    if gpu:
        stage0 += nvhpc(
            eula=True,
            cuda=True
        )
    return stage0


if __name__ == '__main__':
    Fire(build)
