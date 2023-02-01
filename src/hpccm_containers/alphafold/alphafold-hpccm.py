




os_release = USERARG.get('os_release', 'ubuntu')
os_version = USERARG.get('os_version', '20.04')
cuda_version = USERARG.get('cuda_version', '11.0')
python_version = USERARG.get('python_version', '3.8')
alphafold_path = USERARG.get('alphafold_path', '/opt/alphafold')
version = USERARG.get('version', '2.1.2')
image = f'nvcr.io/nvidia/cuda:{cuda_version}-devel-{os_release}{os_version}'
runtime_image = f"nvcr.io/nvidia/cuda:{cuda_version}-runtime-{os_release}{os_version}"

Stage0 += baseimage(image=image, _bootstrap='docker', _as="devel")


Stage0 += packages(apt=['wget', 'git', 'software-properties-common', 'build-essential', 'zlib1g-dev'])

Stage0 += environment(variables={
    "PATH": "/usr/local/cuda/bin/:$PATH",
    "LD_LIBRARY_PATH": "/usr/local/cuda/lib64/:$LD_LIBRARY_PATH",
    "LIBRARY_PATH": "/usr/local/cuda/lib64/:$LIBRARY_PATH",
    "C_INCLUDE_PATH": "/usr/local/cuda/include:$C_INCLUDE_PATH",
    "CXX_INCLUDE_PATH": "/usr/local/cuda/include:$C_INCLUDE_PATH"
})

Stage0 += conda(
    eula=True,
    packages=[f'python={python_version}', "openmm==7.5.1", "cudnn==8.2.1.32", "cudatoolkit==11.0.3", "pdbfixer==1.7", "hmmer==3.3.2", "hhsuite==3.3.0", "kalign2==2.04"],
    channels=['conda-forge', 'bioconda'],
)
Stage0 += shell(commands=['/usr/local/anaconda/bin/conda activate base'])

Stage0 += shell(commands=[f"mkdir -p {alphafold_path}", f'git clone -b v{version} https://github.com/deepmind/alphafold.git {alphafold_path}'])
Stage0 += environment(variables={"ALPHAFOLD_PATH": f"{alphafold_path}"})

Stage0 += shell(commands=[f'wget -q -P {alphafold_path}/alphafold/common/ https://git.scicore.unibas.ch/schwede/openstructure/-/raw/7102c63615b64735c4941278d92b554ec94415f8/modules/mol/alg/src/stereo_chemical_props.txt'])
Stage0 += pip(packages=["absl-py==0.13.0", "biopython==1.79", "chex==0.0.7", "dm-haiku==0.0.4", "dm-tree==0.1.6", "immutabledict==2.0.0", "ml-collections==0.1.0", "numpy==1.19.5", "scipy==1.7.0", "tensorflow==2.5.0", "pandas==1.3.4", "tensorflow-cpu==2.5.0"], pip='/usr/loca/anaconda/bin/pip3')
Stage0 += pip(packages=["jax", "jaxlib==0.1.69+cuda111 -f https://storage.googleapis.com/jax-releases/jax_releases.html"], upgrade=True, pip='/usr/loca/anaconda/bin/pip3')
Stage0 += pip(packages=[f'-r {alphafold_path}/requirements.txt'], pip='/usr/loca/anaconda/bin/pip3')
Stage0 += shell(commands=[f'cd /usr/local/anaconda/lib/python{python_version}/site-packages/ && patch -p0 < {alphafold_path}/docker/openmm.patch'])
Stage0 += shell(commands=[f'cd {alphafold_path}', 'wget https://raw.githubusercontent.com/0luhancheng0/hpccm-containers/main/src/hpccm_containers/alphafold/run_alphafold.sh && chmod a+x run_alphafold.sh'])

Stage1 += baseimage(image=runtime_image)
Stage1 += environment(variables={
    'LC_ALL': 'en_AU.UTF-8',
    'LANGUAGE': 'en_AU.UTF-8',
})
Stage1 += shell(commands=[
    'rm -f /bin/sh && ln -s /bin/bash /bin/sh',
    'rm -f /usr/bin/sh && ln -s /usr/bin/bash /usr/bin/sh',
    '/bin/bash',
])
Stage1 += Stage0.runtime(_from="devel")
Stage1 += packages(apt=['wget', 'git', 'software-properties-common', 'build-essential', 'locales', 'zlib1g-dev',
                        'ubuntu-desktop', 'vim', 'mesa-utils'])
Stage1 += shell(commands=['locale-gen en_AU.UTF-8'])
Stage1 += shell(commands=[
    'wget https://swift.rc.nectar.org.au/v1/AUTH_810/CVL-Singularity-External-Files/turbovnc_2.2.5_amd64.deb && dpkg -i turbovnc_2.2.5_amd64.deb && rm turbovnc_2.2.5_amd64.deb',
    'wget https://swift.rc.nectar.org.au/v1/AUTH_810/CVL-Singularity-External-Files/virtualgl_2.6.4_amd64.deb && dpkg -i virtualgl_2.6.4_amd64.deb && rm virtualgl_2.6.4_amd64.deb',
    'apt update',
    'apt -y upgrade'
])
Stage1 += environment(variables={
    "PATH": "/usr/local/cuda/bin/:$PATH",
    "LD_LIBRARY_PATH": "/usr/local/cuda/lib64/:$LD_LIBRARY_PATH"
})
Stage1 += environment(variables={"ALPHAFOLD_PATH": f"{alphafold_path}"})
Stage1 += copy(_from="devel", src=alphafold_path, dest=alphafold_path)
Stage1 += runscript(commands=['source /usr/local/anaconda/etc/profile.d/conda.sh', f"cd {alphafold_path}", f'{alphafold_path}/run_alphafold.sh $@'])

Stage1 += label(metadata={'maintainer': 'Luhan Cheng', 'email': 'luhan.cheng@monash.edu'})
