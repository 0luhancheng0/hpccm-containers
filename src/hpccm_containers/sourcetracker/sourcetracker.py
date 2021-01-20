import wget
import hpccm
from hpccm.building_blocks import packages, generic_build
from hpccm.primitives import environment
from hpccm_containers.utils import CVL_ubuntu_stage
from fire import Fire


def build(version='1.0.1'):
    stage0 = CVL_ubuntu_stage()
    stage0 += packages(apt=['r-base'])
    stage0 += generic_build(
        repository='https://github.com/danknights/sourcetracker.git',
        branch=f'v{version}',
        install=['mkdir -p /usr/local/sourcetracker/bin && mv src/SourceTracker.r /usr/local/sourcetracker/bin']
    )
    stage0 += environment(
        variables={'SOURCETRACKER_PATH': '/usr/local/sourcetracker/bin', 'PATH': '/usr/local/sourcetracker/bin:$PATH'}
    )
    return stage0

if __name__ == '__main__':
    Fire(build)
