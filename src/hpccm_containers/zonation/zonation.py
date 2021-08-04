from hpccm import config, Stage
from hpccm.building_blocks import packages, generic_cmake
from hpccm.primitives import label, baseimage, comment, shell, environment
from fire import Fire
from hpccm_containers.utils import from_prefix


def build(container_format='singularity', os_release='ubuntu', os_version='18.04'):
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

    stage0 += packages(apt=['wget', 'git', 'software-properties-common', 'build-essential', 'locales', 'zlib1g-dev',
                            'cmake', 'unzip', 'libqt4-dev', 'libfftw3-dev', 'libqwt-dev', 'libboost-all-dev', 'libgdal-dev'])
    stage0 += shell(commands=['locale-gen en_AU.UTF-8'])
    stage0 += generic_cmake(
        repository='https://github.com/cbig/zonation-core.git',
        branch='4.0.0',
        prefix='/usr/local/zonation'
    )
    stage0 += environment(variables=from_prefix('/usr/local/zonation'))


    return stage0


if __name__ == '__main__':
    Fire(build)
