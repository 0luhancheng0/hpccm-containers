from hpccm.Stage import Stage
from hpccm.primitives.baseimage import baseimage
from hpccm import config
from hpccm.building_blocks import packages, generic_build, conda
from hpccm.primitives import environment, workdir, runscript, shell
from fire import Fire
from hpccm.primitives.comment import comment
from hpccm_containers.utils import from_prefix

def build(python_version='3.6', freesurfer_version='6.0.1'):
    stage0 = Stage()
    config.set_container_format('singularity')
    stage0 += baseimage(image='nvidia/cuda:10.0-cudnn7-runtime-ubuntu16.04', _bootstrap='docker')
    stage0 += shell(commands=['rm /bin/sh', 'ln -s /bin/bash /bin/sh', '/bin/bash'])
    stage0 += packages(
        apt=['build-essential', 'cmake', 'git', 'vim', 'wget', 'ca-certificates', 'bzip2', 'libx11-6', 'libjpeg-dev', 'libpng-dev', 'bc', 'tar', 'zip', 'gawk', 'tcsh', 'time', 'libgomp1', 'libglu1-mesa', 'libglu1-mesa-dev', 'perl-modules']
    )
    stage0 += comment("https://github.com/Deep-MI/FastSurfer/blob/master/Docker/Dockerfile")
    stage0 += shell(commands=[
        f"wget -qO- https://surfer.nmr.mgh.harvard.edu/pub/dist/freesurfer/{freesurfer_version}/freesurfer-Linux-centos6_x86_64-stable-pub-v{freesurfer_version}.tar.gz | tar zxv --no-same-owner -C /opt \
        --exclude='freesurfer/trctrain' \
        --exclude='freesurfer/subjects/fsaverage_sym' \
        --exclude='freesurfer/subjects/fsaverage3' \
        --exclude='freesurfer/subjects/fsaverage4' \
        --exclude='freesurfer/subjects/fsaverage5' \
        --exclude='freesurfer/subjects/fsaverage6' \
        --exclude='freesurfer/subjects/cvs_avg35' \
        --exclude='freesurfer/subjects/cvs_avg35_inMNI152' \
        --exclude='freesurfer/subjects/bert' \
        --exclude='freesurfer/subjects/V1_average' \
        --exclude='freesurfer/average/mult-comp-cor' \
        --exclude='freesurfer/lib/cuda' \
        --exclude='freesurfer/lib/qt'",

    ])
    stage0 += conda(
        channels=['pytorch', 'conda-forge'],
        packages=[f'python={python_version}', 'scipy', 'numpy', 'matplotlib', 'h5py', 'scikit-image', 'pytorch', 'cudatoolkit=10.0',
                  'pytorch=1.2.0=py3.6_cuda10.0.130_cudnn7.6.2_0', 'torchvision=0.4.0', 'scikit-sparse', 'nibabel=2.5.1', 'pillow=7.1.1'],
        eula=True,
    )
    stage0 += generic_build(
        repository='https://github.com/Deep-MI/FastSurfer.git',
        # branch='c5894bd',
        build=['git checkout c5894bd'],
        install=['mkdir /fastsurfer && mv * /fastsurfer/']
    )
    stage0 += environment(variables={
        'OS': 'Linux',
        'FS_OVERRIDE': 0,
        'FIX_VERTEX_AREA': '',
        'SUBJECTS_DIR': '/opt/freesurfer/subjects',
        'FSF_OUTPUT_FORMAT': 'nii.gz',
        'MNI_DIR': '/opt/freesurfer/mni',
        'LOCAL_DIR': '/opt/freesurfer/local',
        'FREESURFER_HOME': '/opt/freesurfer',
        'FSFAST_HOME': '/opt/freesurfer/fsfast',
        'PERL5LIB': '/opt/freesurfer/mni/lib/perl5/5.8.5',
        'MNI_PERL4LIB': '/opt/freesurfer/mni/lib/perl5/5.8.5',
        'PYTHONNUMBUFFERED': 0,
        'PATH': '/fastsurfer/recon_surf:/fastsurfer:/usr/local/anaconda/bin:/opt/freesurfer/bin:/opt/freesurfer/fsfast/bin:/opt/freesurfer/tktools:/opt/freesurfer/mni/bin:$PATH',
        **from_prefix('/usr/local/cuda')
    })
    stage0 += runscript(commands=[
        'cd /fastsurfer',
        'source /usr/local/anaconda/etc/profile.d/conda.sh',
        'source $FREESURFER_HOME/SetUpFreeSurfer.sh',
        "$*"
    ])
    return stage0

if __name__ == '__main__':
    Fire(build)
