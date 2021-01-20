import wget
import hpccm
from hpccm.building_blocks import packages, boost, generic_autotools, generic_build, pip, conda
from hpccm.primitives import baseimage, shell, label, environment
from hpccm_containers.utils import from_prefix, CVL_ubuntu_stage
from fire import Fire


def build(version='1.14.6-0'):
    stage0 = CVL_ubuntu_stage()
    stage0 += conda(
        channels=['bioconda', 'conda-forge', 'defaults'],
        packages=[f'prokka={version}'],
        eula=True
    )
    return stage0

if __name__ == '__main__':
    Fire(build)
