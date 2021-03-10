
import os
from typing import ValuesView
from hpccm import config, Stage
from hpccm.building_blocks import gnu, openmpi, packages, nvhpc, generic_build
from hpccm.building_blocks.generic_autotools import generic_autotools
from hpccm.primitives import label, baseimage, comment, runscript, shell, environment
from fire import Fire
from hpccm.toolchain import toolchain
from hpccm_containers.utils import add_include_path, add_library_path, from_prefix, add_binary


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

    stage0 += packages(apt=['wget', 'git', 'software-properties-common', 'build-essential', 'locales', 'zlib1g-dev', 'perl', 'ncbi-blast+', 'libx11-dev'])
    stage0 += shell(commands=['locale-gen en_AU.UTF-8'])

    stage0 += gnu(version='10')

    stage0 += generic_build(
        url='http://search.cpan.org/CPAN/authors/id/Y/YA/YANICK/Parallel-ForkManager-1.19.tar.gz',
        prefix='/usr/local/parallel-forkmanager',
        build=['perl Makefile.PL', 'make install'],
        install=['mv * /usr/local/parallel-forkmanager/']
    )
    stage0 += environment(variables=add_binary('/usr/local/parallel-forkmanager'))

    stage0 += generic_build(
        url='ftp://ftp.ebi.ac.uk/pub/software/clustalw2/2.1/clustalw-2.1-linux-x86_64-libcppstatic.tar.gz',
        prefix='/usr/local/clustalw',
        install=['mv clustalw2 /usr/local/clustalw/clustalw']
    )
    stage0 += environment(variables=add_binary('/usr/local/clustalw'))

    stage0 += generic_autotools(
        url='ftp://emboss.open-bio.org/pub/EMBOSS/EMBOSS-6.6.0.tar.gz',
        prefix='/usr/local/emboss',
    )
    stage0 += environment(variables=from_prefix('/usr/local/emboss'))

    stage0 += generic_autotools(
        url='https://www.tbi.univie.ac.at/RNA/download/sourcecode/2_4_x/ViennaRNA-2.4.17.tar.gz',
        prefix='/usr/local/viennarna'
    )
    stage0 += environment(variables=from_prefix('/usr/local/viennarna'))

    stage0 += generic_build(
        url='https://github.com/weizhongli/cdhit/archive/V4.8.1.tar.gz',
        prefix='/usr/local/cdhit',
        directory='cdhit-4.8.1',
        build=['make'],
        install=['mv * /usr/local/cdhit/']
    )
    stage0 += environment(variables=add_binary('/usr/local/cdhit'))

    stage0 += generic_build(
        repository='https://github.com/ambarishbiswas/CRISPRDetect_2.2.git',
        commit='0f8249f',
        prefix='/usr/local/crisprdetect',
        install=['mv * /usr/local/crisprdetect/']
    )
    stage0 += environment(variables=add_binary('/usr/local/crisprdetect'))
    return stage0


if __name__ == '__main__':
    Fire(build)
