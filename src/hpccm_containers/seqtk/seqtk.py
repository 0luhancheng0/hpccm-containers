import hpccm
import wget
from fire import Fire
from hpccm.building_blocks import boost, generic_autotools, generic_build
from hpccm.primitives import environment, label, shell
from hpccm_containers.utils import add_binary, from_prefix, stage_template


def build(version='1.3'):
    stage0 = stage_template()
    stage0 += generic_build(
        repository='https://github.com/lh3/seqtk.git',
        branch=f'v{version}',
        build=['make'],
        install=['mkdir -p /usr/local/seqtk/bin && cp seqtk /usr/local/seqtk/bin/']
    )
    stage0 += environment(variables=add_binary('/usr/local/seqtk/bin'))

    return stage0

if __name__ == '__main__':
    Fire(build)
