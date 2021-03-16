
import os
from hpccm import config, Stage
from hpccm.building_blocks import gnu, openmpi, packages, nvhpc, generic_build, generic_autotools
from hpccm.primitives import label, baseimage, comment, runscript, shell, environment
from fire import Fire
from hpccm_containers.utils import add_binary, add_include_path, add_library_path, from_prefix


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
    stage0 += shell(commands=['rm /usr/bin/sh', 'ln -s /usr/bin/bash /usr/bin/sh', '/usr/bin/bash'])

    stage0 += packages(apt=['wget', 'git', 'software-properties-common', 'build-essential', 'locales', 'zlib1g-dev',
                            'perl', 'openssh-server', 'libssl-dev', 'gnuplot', 'globus-gridftp-server-progs', 'rsync', 'acl-dev'])
    stage0 += gnu(version='10')
    stage0 += shell(commands=[
        'yes | cpan Data::MessagePack',
        'yes | cpan IO::Socket::SSL'
    ])

    stage0 += generic_build(
        repository='https://github.com/eeertekin/bbcp.git',
        commit='64af832',
        prefix='/usr/local/bbcp/',
        build=['make -C src'],
        install=['mv bin/amd64_linux/bbcp /usr/local/bbcp/']
    )
    stage0 += environment(variables=add_binary('/usr/local/bbcp'))

    stage0 += generic_build(
        repository='https://github.com/pkolano/shift.git',
        commit='ffb7f5f',
        prefix='/usr/local/shift',
        directory='shift/c',
        build=['make nolustre'],
        install=['mdkir /usr/local/shift/bin && mv c/shift-bin /usr/local/shift/bin']
    )
    return stage0


if __name__ == '__main__':
    Fire(build)
