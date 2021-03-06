from hpccm import config, Stage
from hpccm.building_blocks import gnu, openmpi, packages, nvhpc, generic_build
from hpccm.primitives import label, baseimage
from fire import Fire
from hpccm.primitives.comment import comment
from hpccm.primitives.environment import environment
from hpccm.primitives.runscript import runscript
from hpccm.primitives.shell import shell


def build(container_format='singularity', os='ubuntu:18.04'):
    image = os
    config.set_container_format(container_format)
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

    stage0 += shell(commands=[
        'cd /etc/apt/sources.list.d/',
        'wget http://downloads.perfsonar.net/debian/perfsonar-release.list',
        'wget -qO - http://downloads.perfsonar.net/debian/perfsonar-official.gpg.key | apt-key add -',
        'add-apt-repository -y universe',
        'apt-get update'
    ])
    stage0 += packages(apt=['perfsonar-tools', 'perfsonar-testpoint', 'perfsonar-core', 'perfsonar-centralmanagement', 'perfsonar-toolkit'])
    stage0 += shell(commands=['/usr/lib/perfsonar/scripts/install-optional-packages.py'])

    return stage0


if __name__ == '__main__':
    Fire(build)
