from posixpath import commonpath
from hpccm.building_blocks import packages, boost, generic_autotools, generic_build, pip
import wget
from hpccm.primitives import baseimage, shell, label, environment
from hpccm_containers.utils import from_prefix, stage_template
import hpccm
from fire import Fire
import os


def build(image="Characterisation-Virtual-Laboratory/CharacterisationVL-Software:2004", version='0.5', fsl_version='6.0.4', bru2nii_version='v1.0.20180303'):

    stage0 = stage_template(cpu=True)
    stage0 += packages(apt=['snapd'])
    stage0 += shell(commands=['snapd install blender'])
    stage0 += pip(packages=['argh', 'joblib', 'matplotlib>=2.0.2', 'numpy>=1.13.3', 'pandas', 'seaborn', 'statsmodels', 'nibabel', 'nipy>=0.4.1', 'nipype>=1.0.0', 'pybids<=0.6.5', 'scikit-image', 'scipy', 'nilearn'], pip='pip3')
    fslinstaller_url = 'https://fsl.fmrib.ox.ac.uk/fsldownloads/fslinstaller.py'
    if not os.path.exists('./fslinstaller.py'):
        wget.download(fslinstaller_url)
    stage0 += shell(commands=[f'python fslinstaller.py  -d /usr/local/fsl/{fsl_version} -V {fsl_version}'])
    stage0 += generic_build(
        url=f'https://github.com/neurolabusc/Bru2Nii/releases/download/{bru2nii_version}/Bru2_Linux.zip',
        install=['mv Bru2 Bru2Nii /usr/local/bin']
    )
    stage0 += shell(commands=[
        'cd /usr/local/',
        'wget http://chymera.eu/distfiles/mouse-brain-atlases-0.5.3.tar.xz && tar -xf mouse-brain-atlases-0.5.3.tar.xz && rm mouse-brain-atlases-0.5.3.tar.xz',
        'wget http://chymera.eu/distfiles/mouse-brain-atlasesHD-0.5.3.tar.xz && tar -xf mouse-brain-atlasesHD-0.5.3.tar.xz && rm mouse-brain-atlasesHD-0.5.3.tar.xz',
    ])
    # stage0 += generic_build(
    #     repository='https://github.com/IBT-FMI/mouse-brain-atlases_generator.git',
    #     branch='0.5',
    #     build=['./make_archives.sh -v 0.5 -m'],
    # )
    # stage0 += generic_build(
    #     repository='https://github.com/IBT-FMI/SAMRI.git',
    #     branch=version,
    #     build=['cd .gentoo && ./install.sh'],
    # )
    return stage0
if __name__ == '__main__':
    Fire(build)
