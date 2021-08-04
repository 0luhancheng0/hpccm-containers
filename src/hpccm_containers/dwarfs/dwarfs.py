
import os
from hpccm import config, Stage
from hpccm.building_blocks import gnu, openmpi, packages, cmake, generic_cmake
from hpccm.primitives import label, baseimage, comment, runscript, shell, environment
from fire import Fire
from hpccm_containers.utils import add_include_path, add_library_path, from_prefix


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

    stage0 += packages(apt=['g++', 'clang', 'cmake', 'make', 'bison', 'flex', 'ronn', 'fuse3', 'pkg-config', 'binutils-dev', 'libarchive-dev', 'libboost-context-dev', 'libboost-filesystem-dev', 'libboost-program-options-dev', 'libboost-python-dev', 'libboost-regex-dev', 'libboost-system-dev', 'libboost-thread-dev', 'libevent-dev', 'libjemalloc-dev', 'libdouble-conversion-dev', 'libiberty-dev', 'liblz4-dev', 'liblzma-dev', 'libssl-dev', 'libunwind-dev', 'libdwarf-dev', 'libelf-dev', 'libfmt-dev', 'libfuse3-dev', 'libgoogle-glog-dev'])

    stage0 += generic_cmake(
        prefix='/usr/local/dwarfs',
        repository='https://github.com/mhx/dwarfs.git',
        branch='v0.5.5',
        recursive=True,
        cmake_opts=["-D WITH_TESTS=1"],
    )
    stage0 += environment(variables=from_prefix('/usr/local/dwarfs'))

    return stage0


if __name__ == '__main__':
    Fire(build)
