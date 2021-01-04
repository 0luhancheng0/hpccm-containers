import wget
import hpccm
from hpccm.building_blocks import packages, boost, generic_autotools, generic_build, pip
from hpccm.primitives import baseimage, shell, label, environment
from hpccm_containers.utils import from_prefix, stage_template
from fire import Fire


def build(image="Characterisation-Virtual-Laboratory/CharacterisationVL-Software:2004", version='1.0.1'):
    stage0 = stage_template(cpu=True)
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
