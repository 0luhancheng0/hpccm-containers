from hpccm import config, Stage
from hpccm.building_blocks import gnu, openmpi, conda
from hpccm.building_blocks.pip import pip
from hpccm.primitives import label, baseimage
from fire import Fire
from hpccm_containers.utils import CVL_ubuntu_stage

def build(version='0.11.5'):
    stage0 = CVL_ubuntu_stage()
    stage0 += pip(
        packages=['numpy', 'h5py', 'ncempy', 'numba', 'scikit-image', 'scikit-learn', 'PyQt5', 'pyqtgraph', 'qtconsole', 'ipywidgets', 'tqdm', 'ipyparallel', 'dask', f'py4dstem=={version}'],
        pip='pip3'
    )
    return stage0


if __name__ == '__main__':
    Fire(build)
