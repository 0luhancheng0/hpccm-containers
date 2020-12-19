from hpccm_containers.qiime2 import qiime2
import hpccm
from hpccm import building_blocks, primitives
from fire import Fire
def build(version='1v.0.6'):
    stage1 = hpccm.Stage()
    stage1 += qiime2.build()
    stage1 += building_blocks.pip(packages=['numpy'])
    stage1 += building_blocks.generic_build(
        repository='https://github.com/biocore/mmvec.git',
        branch=version,
        build=['python setup.py install']
    )
    return stage1

if __name__ == '__main__':
    Fire(build)

