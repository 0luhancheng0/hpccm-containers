from os import environ
from hpccm import config, Stage
from hpccm.building_blocks import packages, conda, pip
from hpccm.primitives import label, baseimage, shell, environment, runscript
from fire import Fire
from hpccm_containers.utils import from_prefix


def build(
    container_format='singularity', flavour="devel", os_release='ubuntu', os_version='20.04',
    cuda_version='11.3.0', python_version='3.8', anaconda_version='4.9.2', alphafold_path="/opt/alphafold", version='2.1.2'):

    config.set_container_format(container_format)
    image = f'nvcr.io/nvidia/cuda:{cuda_version}-{flavour}-{os_release}{os_version}'

    stage0 = Stage(name='stage0')
    stage0 += baseimage(image=image, _bootstrap='docker')
    stage0 += environment(variables={
        'LC_ALL': 'en_AU.UTF-8',
        'LANGUAGE': 'en_AU.UTF-8',
    })
    stage0 += label(metadata={'maintainer': 'Luhan Cheng', 'email': 'luhan.cheng@monash.edu'})
    stage0 += shell(commands=[
        'rm -f /bin/sh && ln -s /bin/bash /bin/sh',
        'rm -f /usr/bin/sh && ln -s /usr/bin/bash /usr/bin/sh',
        '/bin/bash',
    ])

    stage0 += environment(variables=from_prefix('/usr/local/cuda'))
    stage0 += packages(apt=['wget', 'git', 'software-properties-common', 'build-essential', 'locales', 'zlib1g-dev', 'vim'])
    stage0 += shell(commands=['locale-gen en_AU.UTF-8'])

    stage0 += conda(
        eula=True,
        packages=[f'python={python_version}', "openmm==7.5.1", "cudnn==8.2.1.32", "cudatoolkit==11.0.3", "pdbfixer==1.7", "hmmer==3.3.2", "hhsuite==3.3.0", "kalign2==2.04"],
        channels=['conda-forge', 'bioconda'],
        version=anaconda_version
    )
    stage0 += environment(variables=from_prefix('/usr/local/anaconda'))
    stage0 += shell(commands=['conda activate base'])


    stage0 += shell(commands=[f"mkdir -p {alphafold_path}", f'git clone -b v{version} https://github.com/deepmind/alphafold.git {alphafold_path}'])
    stage0 += environment(variables={"ALPHAFOLD_PATH": f"{alphafold_path}"})

    stage0 += shell(commands=[f'wget -q -P {alphafold_path}/alphafold/common/ https://git.scicore.unibas.ch/schwede/openstructure/-/raw/7102c63615b64735c4941278d92b554ec94415f8/modules/mol/alg/src/stereo_chemical_props.txt'])
    stage0 += pip(packages=["absl-py==0.13.0", "biopython==1.79", "chex==0.0.7", "dm-haiku==0.0.4", "dm-tree==0.1.6", "immutabledict==2.0.0", "ml-collections==0.1.0", "numpy==1.19.5", "scipy==1.7.0", "tensorflow==2.5.0", "pandas==1.3.4", "tensorflow-cpu==2.5.0"], pip='pip3')
    stage0 += pip(packages=["jax", "jaxlib==0.1.69+cuda111 -f https://storage.googleapis.com/jax-releases/jax_releases.html"], upgrade=True, pip='pip3')
    stage0 += pip(packages=[f'-r {alphafold_path}/requirements.txt'], pip='pip3')
    stage0 += shell(commands=[f'cd /usr/local/anaconda/lib/python{python_version}/site-packages/ && patch -p0 < {alphafold_path}/docker/openmm.patch'])
    stage0 += shell(commands=[f'cd {alphafold_path}', 'wget https://raw.githubusercontent.com/0luhancheng0/hpccm-containers/main/src/hpccm_containers/alphafold/run_alphafold.sh && chmod a+x run_alphafold.sh'])
    stage0 += runscript(commands=['source /usr/local/anaconda/etc/profile.d/conda.sh', f"cd {alphafold_path}", f'{alphafold_path}/run_alphafold.sh $@'])

    return stage0


if __name__ == '__main__':
    Fire(build)
