
import os
from hpccm import config, Stage
from hpccm.building_blocks import gnu, openmpi, packages
from hpccm.primitives import label, baseimage, comment, runscript, shell, environment
from fire import Fire
from hpccm_containers.utils import add_include_path, add_library_path, from_prefix, shell_with_log


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

    stage0 += packages(apt=['perl', 'libmodule-install-perl', 'libxml-parser-perl', 'cpanminus'])
    stage0 += shell(commands=[
        'cpanm inc::latest',
        'cpanm BioPerl Bio::SeqIO Getopt::Euclid List::Util Math::Random::MT version'
    ])
    stage0 += shell(commands=[
        'wget https://sourceforge.net/projects/biogrinder/files/biogrinder/Grinder-0.5.4/Grinder-0.5.4.tar.gz && tar -xf Grinder-0.5.4.tar.gz && rm Grinder-0.5.4.tar.gz',
        'cd Grinder-0.5.4',
        'perl Makefile.PL',
        'make',
        'make install'
    ])


    return stage0


if __name__ == '__main__':
    Fire(build)
