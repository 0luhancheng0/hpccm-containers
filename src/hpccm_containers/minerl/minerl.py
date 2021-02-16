
import os
from hpccm import config, Stage
from hpccm.building_blocks import gnu, openmpi, packages, nvhpc, pip, conda

from hpccm.primitives import label, baseimage, comment, runscript, shell, environment
from fire import Fire
from hpccm_containers.utils import add_include_path, add_library_path, from_prefix


def build(container_format='singularity', os_release='ubuntu', os_version='20.04', cuda_version='11.0'):
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

    stage0 += packages(apt=['wget', 'git', 'software-properties-common', 'build-essential', 'locales'])
    stage0 += shell(commands=['locale-gen en_AU.UTF-8'])

    stage0 += comment('Installing vglrun and TurboVNC')
    stage0 += packages(apt=['ubuntu-desktop', 'vim', 'mesa-utils', 'python3-pip', 'python3-pyqt5', 'pyqt5-dev', 'python3-tk'])
    stage0 += shell(commands=[
        'wget https://swift.rc.nectar.org.au/v1/AUTH_810/CVL-Singularity-External-Files/turbovnc_2.2.5_amd64.deb && dpkg -i turbovnc_2.2.5_amd64.deb && rm turbovnc_2.2.5_amd64.deb',
        'wget https://swift.rc.nectar.org.au/v1/AUTH_810/CVL-Singularity-External-Files/virtualgl_2.6.4_amd64.deb && dpkg -i virtualgl_2.6.4_amd64.deb && rm virtualgl_2.6.4_amd64.deb',
        'apt update',
        'apt -y upgrade'
    ])

    stage0 += conda(
        eula=True,
        packages=['python=3.8.5', 'openjdk', 'pip'],
    )
    stage0 += environment(variables=from_prefix('/usr/local/anaconda'))
    stage0 += shell(commands=['pip install --upgrade minerl'])
    stage0 += shell(commands=[
        'wget https://launcher.mojang.com/download/Minecraft.deb && dpkg -i Minecraft.deb && rm Minecraft.deb',
    ])

    stage0 += runscript(commands=['source /usr/local/anaconda/etc/profile.d/conda.sh', '/usr/local/anaconda/bin/python3 $*'])



    return stage0


if __name__ == '__main__':
    Fire(build)
