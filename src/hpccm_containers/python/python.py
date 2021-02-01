from __future__ import annotations
from os import close
from sys import path
from hpccm import config, Stage
from hpccm.building_blocks import gnu, generic_autotools, gnu, mkl, pip
from hpccm.building_blocks.packages import packages
from hpccm.primitives import label, baseimage, shell, runscript
from fire import Fire

from hpccm.primitives.environment import environment
from hpccm_containers.utils import from_prefix

from hpccm.templates import git

def build(container_format='singularity', image='ubuntu:20.04', version='3.8.7', gnu_version='10', mkl_version='2020.0-088', numpy_version='1.20.0rc2'):
    config.set_container_format(container_format)
    stage0 = Stage(name='stage0')
    stage0 += baseimage(image=image, _bootstrap='docker')
    stage0 += label(metadata={'maintainer': 'Luhan Cheng', 'email': 'luhan.cheng@monash.edu'})
    stage0 += shell(commands=['rm /bin/sh && ln -s /bin/bash /bin/sh', '/bin/bash'])

    filename = f'Python-{version}.tar.xz'
    url = f'https://www.python.org/ftp/python/{version}/{filename}'
    stage0 += packages(apt=['wget', 'xz-utils', 'build-essential', 'software-properties-common', 'libsqlite3-dev',
                            'libssl-dev', 'libbz2-dev', 'libgdbm-compat-dev', 'libssl-dev', 'liblzma-dev', 'tk-dev',
                            'uuid-dev', 'libreadline-dev', 'zlib1g-dev', 'python-dev', 'libncurses*-dev', 'libgdbm-dev',
                            'libsqlite3-dev', 'libffi-dev', 'git'])
    compiler = gnu(version=gnu_version)
    stage0 += compiler
    # stage0 += shell(commands=[
    #     'export LDFLAGS="-rpath /usr/local/python/bin $LDFLAGS"'
    # ])
    stage0 += generic_autotools(
        url=url,
        directory=f'Python-{version}',
        prefix='/usr/local/python',
        with_computed_goto=True,
        with_threads=True,
        enable_shared=True,
        enable_profiling=True,
        enable_optimizations=True,
        with_pydebug=True,
        enable_ipv6=True,
        toolchain=compiler.toolchain,
        # build_environment={
        #     'CPPFLAGS': '"-Wl,-rpath=/usr/local/python/lib $CPPFLAGS"'
        # }
    )
    stage0 += packages(apt=['patchelf'])
    stage0 += shell(commands=[
        # 'snap install patchelf --edge --classic',
        'patchelf --set-rpath /usr/local/python/lib /usr/local/python/bin/python3',
    ])
    stage0 += environment(variables=from_prefix('/usr/local/python'))
    stage0 += mkl(version=mkl_version, eula=True)
    stage0 += shell(commands=['. /opt/intel/mkl/bin/mklvars.sh intel64'])
    stage0 += pip(packages=['Cython>0.29.21', 'pytest>1.15', 'Hypothesis>5.3.0'], pip='pip3')
    stage0 += shell(commands=[
        git().clone_step(repository='https://github.com/numpy/numpy.git', branch=f'v{numpy_version}'),

    ])
    stage0 += runscript(commands=['/bin/bash', 'source /opt/intel/mkl/bin/mklvars.sh intel64', '/usr/local/python/bin/python3 $*'])

    return stage0


if __name__ == '__main__':
    Fire(build)
