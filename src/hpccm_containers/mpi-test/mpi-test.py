from hpccm.building_blocks import pgi, nvhpc
from hpccm.primitives import baseimage, copy, shell
from hpccm import Stage, config
from fire import Fire

import hpccm
from hpccm.primitives.runscript import runscript


def build():
    stage0 = Stage()
    config.set_container_format('singularity')
    stage0 += baseimage(image='ubuntu:18.04')
    stage0 += nvhpc(
        eula=True,
        mpi=True,
    )

    stage0 += copy(src='heat_mpi.f90', dest='/var/tmp/heat_mpi.f90')
    stage0 += shell(commands=['mpif90 /var/tmp/heat_mpi.f90 -o /usr/local/bin/heat_mpi'])
    return stage0

if __name__ == '__main__':
    Fire(build)
