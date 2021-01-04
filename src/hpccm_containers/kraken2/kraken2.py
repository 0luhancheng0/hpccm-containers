import wget
import hpccm
from hpccm.building_blocks import packages, generic_autotools, generic_build
from hpccm.primitives import shell, environment
from hpccm_containers.utils import from_prefix, stage_template, add_binary
from fire import Fire


def build(image="Characterisation-Virtual-Laboratory/CharacterisationVL-Software:2004", version='2.1.1'):
    stage0 = stage_template(cpu=True)
    stage0 += generic_build(
        repository='https://github.com/DerrickWood/kraken2.git',
        branch=f'v{version}',
        install=['./install_kraken2.sh /usr/local/kraken2'],
    )
    stage0 += environment(variables=add_binary('/usr/local/kraken2/bin'))
    return stage0

if __name__ == '__main__':
    Fire(build)
