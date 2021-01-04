import wget
import hpccm
from hpccm.building_blocks import packages, generic_autotools, generic_build
from hpccm.primitives import shell, environment
from hpccm_containers.utils import from_prefix, stage_template
from fire import Fire


def build(image="Characterisation-Virtual-Laboratory/CharacterisationVL-Software:2004", version='0.5'):
    stage0 = stage_template(cpu=True)
    return stage0

if __name__ == '__main__':
    Fire(build)
