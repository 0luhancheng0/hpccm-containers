from distutils import version
from hpccm import config, Stage
from hpccm.building_blocks import gnu, openmpi, packages, conda, generic_build, pip
from hpccm.primitives import label, baseimage, shell
from fire import Fire
from hpccm.primitives.environment import environment
from hpccm.toolchain import toolchain


def build(container_format='singularity', gnu_version='9', fermi_lite_version='0.1', macs_version='3.0.0a5'):
    image = 'ubuntu:20.04'
    config.set_container_format(container_format)
    stage0 = Stage(name='stage0')
    stage0 += baseimage(image=image, _bootstrap='docker')
    stage0 += label(metadata={'maintainer': 'Luhan Cheng', 'email': 'luhan.cheng@monash.edu'})
    stage0 += packages(apt=['wget', 'software-properties-common', 'build-essential', 'git', 'python-dev', 'zlib1g-dev'])
    compilers = gnu(version=gnu_version)
    stage0 += compilers
    stage0 += generic_build(
        repository='https://github.com/lh3/fermi-lite',
        branch=f'v{fermi_lite_version}',
        build=['make'],
        install=['mkdir -p /usr/local/fermi_lite/', 'mv * /usr/local/fermi_lite/'],
        toolchain=compilers.toolchain
    )
    stage0 += environment(variables={
        'PATH': '/usr/local/fermi_lite/:/usr/local/anaconda/bin:$PATH',
        'LIBRARY_PATH': '/usr/local/fermi_lite/:$LIBRARY_PATH',
        'C_INCLUDE_PATH': '/usr/local/fermi_lite/:$C_INCLUDE_PATH'
    })
    stage0 += conda(
        packages=['python=3.8', 'numpy', 'cython', 'cykhash'],
        channels=['anaconda', 'conda-forge'],
        eula=True
    )
    stage0 += generic_build(
        repository='https://github.com/macs3-project/MACS.git',
        recursive=True,
        branch=f'v{macs_version}',
        build=['python3 setup.py install'],
    )

    return stage0


if __name__ == '__main__':
    Fire(build)
