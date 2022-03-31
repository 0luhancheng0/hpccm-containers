from hpccm import config, Stage
from hpccm.building_blocks import packages
from hpccm.primitives import label, baseimage, comment, shell, environment
from fire import Fire
from hpccm_containers.utils import from_prefix


def build(container_format='singularity', os_release='ubuntu', os_version='20.04', gpu=True, cuda_version='11.0', desktop=True):
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

    stage0 += packages(apt=['wget', 'git', 'software-properties-common', 'build-essential', 'locales', 'zlib1g-dev', 'dirmngr', 'gpg-agent'])
    stage0 += shell(commands=['locale-gen en_AU.UTF-8'])
    stage0 += shell(commands=[
        "wget -O- http://neuro.debian.net/lists/bionic.us-ca.full | tee /etc/apt/sources.list.d/neurodebian.sources.list",
        "apt-key adv --recv-keys --keyserver hkps://keyserver.ubuntu.com 0xA5D32F012649A5A9 2>&1",
    ])
    stage0 += packages(apt=["fsl-complete"])



    return stage0


if __name__ == '__main__':
    Fire(build)
