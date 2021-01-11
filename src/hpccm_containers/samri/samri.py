from posixpath import commonpath
from hpccm.building_blocks import packages, boost, generic_autotools, generic_build, pip, gnu, cmake, generic_cmake
from hpccm.toolchain import toolchain
import wget
from hpccm.primitives import baseimage, shell, label, environment, comment
from hpccm_containers.utils import from_prefix, stage_template
from hpccm import Stage, config
from fire import Fire
import os

def build(container_format='singularity', version='0.5', fsl_version='6.0.4', bru2nii_version='v1.0.20180303', gnu_version='9.1.0', ants_version='v2.3.5'):
    config.set_container_format(container_format)
    stage0 = Stage(name='stage0')
    stage0 += baseimage(image='Characterisation-Virtual-Laboratory/CharacterisationVL-Software:2004', _bootstrap='shub',  _distro='ubuntu20')
    stage0 += label(metadata={'maintainer': 'Luhan Cheng', 'email': 'luhan.cheng@monash.edu'})

    stage0 += packages(apt=['snapd'])
    compilers = gnu(
        version=gnu_version
    )
    stage0 += compilers
    stage0 += shell(commands=['snapd install blender'])

    stage0 += comment('https://github.com/IBT-FMI/SAMRI')
    stage0 += pip(packages=['argh', 'joblib', 'matplotlib>=2.0.2', 'numpy>=1.13.3', 'pandas', 'seaborn', 'statsmodels', 'nibabel', 'nipy>=0.4.1', 'nipype>=1.0.0', 'pybids<=0.6.5', 'scikit-image', 'scipy', 'nilearn', 'pytest'], pip='pip3')
    fslinstaller_url = 'https://fsl.fmrib.ox.ac.uk/fsldownloads/fslinstaller.py'
    if not os.path.exists('./fslinstaller.py'):
        wget.download(fslinstaller_url)
    stage0 += shell(commands=[f'python fslinstaller.py -d /usr/local/fsl/{fsl_version} -V {fsl_version}'])
    stage0 += generic_build(
        url=f'https://github.com/neurolabusc/Bru2Nii/releases/download/{bru2nii_version}/Bru2_Linux.zip',
        install=['mv Bru2 Bru2Nii /usr/local/bin/']
    )
    stage0 += shell(commands=[
        'cd /usr/local/',
        'wget http://chymera.eu/distfiles/mouse-brain-atlases-0.5.3.tar.xz && tar -xf mouse-brain-atlases-0.5.3.tar.xz && rm mouse-brain-atlases-0.5.3.tar.xz',
        'wget http://chymera.eu/distfiles/mouse-brain-atlasesHD-0.5.3.tar.xz && tar -xf mouse-brain-atlasesHD-0.5.3.tar.xz && rm mouse-brain-atlasesHD-0.5.3.tar.xz',
    ])
    stage0 += generic_cmake(
        toolchain=compilers.toolchain,
        repository='https://github.com/ANTsX/ANTs.git',
        branch=ants_version,
        prefix='/usr/local/ants'
    )
    stage0 += shell(commands=[
        'mkdir -p /usr/local/afni/',
        'wget https://afni.nimh.nih.gov/pub/dist/tgz/linux_ubuntu_16_64.tgz',
        'tar -xf linux_ubuntu_16_64.tgz -C /usr/local/afni/',
        'rm linux_ubuntu_16_64.tgz'
    ])

    stage0 += generic_build(
        repository='https://github.com/IBT-FMI/SAMRI.git',
        branch=version,
        build=[
            'echo "export PATH=\$HOME/.local/bin/:\$PATH" >> ~/.bashrc',
            'source ~/.bashrc',
            'python setup.py install'
        ]
    )
    stage0 += environment(variables={
        'PATH': '/usr/local/ants/bin:/usr/local/afni/linux_ubuntu_16_64:$PATH',
        'ANTSPATH': '/usr/local/ants/bin',
        'AFNI_ROOT': '/usr/local/afni/linux_ubuntu_16_64'
    })
    # stage0 += comment('https://afni.nimh.nih.gov/pub/dist/doc/htmldoc/background_install/install_instructs/steps_linux_ubuntu20.html#what-to-do')
    # stage0 += packages(apt=['tcsh', 'xfonts-base', 'libssl-dev', 'python-is-python3', 'python3-matplotlib',
    #                         'gsl-bin', 'netpbm', 'gnome-tweak-tool', 'libjpeg62', 'xvfb', 'xterm', 'vim',
    #                         'curl', 'gedit', 'evince', 'eog', 'libglu1-mesa-dev', 'libglw1-mesa', 'libxm4', 'build-essential',
    #                         'libcurl4-openssl-dev', 'libxml2-dev', 'libgfortran-8-dev', 'libgomp1', 'gnome-terminal', 'nautilus',
    #                         'gnome-icon-theme-symbolic', 'firefox', 'xfonts-100dpi', 'r-base-dev'], apt_repositories=['universe'])
    # stage0 += shell(commands=[
    #     'ln -s /usr/lib/x86_64-linux-gnu/libgsl.so.23 /usr/lib/x86_64-linux-gnu/libgsl.so.19',
    #     'curl -O https://afni.nimh.nih.gov/pub/dist/bin/misc/@update.afni.binaries',
    #     'tcsh @update.afni.binaries -package linux_ubuntu_16_64 -do_extras',
    #     'cp $HOME/abin/AFNI.afnirc $HOME/.afnirc',
    #     'suma -update_env',
    # ])

    return stage0
if __name__ == '__main__':
    Fire(build)
