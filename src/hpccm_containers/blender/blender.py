
import os
from hpccm import config, Stage
from hpccm.building_blocks import gnu, openmpi, packages, nvhpc, generic_build, python
from hpccm.primitives import label, baseimage, comment, runscript, shell, environment
from fire import Fire
from hpccm_containers.utils import add_include_path, add_library_path, from_prefix


def build(container_format='singularity', os_release='ubuntu', os_version='18.04', blender_version='2.92.0'):
    config.set_container_format(container_format)

    image = f'{os_release}:{os_version}'

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
        '/bin/bash'
    ])
    stage0 += packages(apt=['wget', 'git', 'software-properties-common', 'build-essential', 'locales', 'zlib1g-dev'])
    stage0 += python(python3=True, devel=True)
    stage0 += shell(commands=['locale-gen en_AU.UTF-8'])

    stage0 += comment('Installing vglrun and TurboVNC')
    stage0 += packages(apt=['ubuntu-desktop', 'vim', 'mesa-utils', 'python3-pip', 'python3-pyqt5', 'pyqt5-dev', 'python3-tk'])
    stage0 += shell(commands=[
        'wget https://swift.rc.nectar.org.au/v1/AUTH_810/CVL-Singularity-External-Files/turbovnc_2.2.5_amd64.deb && dpkg -i turbovnc_2.2.5_amd64.deb && rm turbovnc_2.2.5_amd64.deb',
        'wget https://swift.rc.nectar.org.au/v1/AUTH_810/CVL-Singularity-External-Files/virtualgl_2.6.4_amd64.deb && dpkg -i virtualgl_2.6.4_amd64.deb && rm virtualgl_2.6.4_amd64.deb',
        'apt update',
        'apt -y upgrade'
    ])
    stage0 += gnu(version='10')
    main_version = blender_version.rsplit('.', 1)[0]
    blender_source = f"https://ftp.nluug.nl/pub/graphics/blender/release/Blender{main_version}/blender-{blender_version}-linux64.tar.xz"
    prefix = '/usr/local/blender'
    stage0 += generic_build(
        url=blender_source,
        prefix=prefix,
        install=[f'mv * {prefix}']
    )
    python_dir = f"{prefix}/{main_version}/python"
    stage0 += environment(variables={
        'PATH': f'{prefix}:{python_dir}/bin:$PATH',
        'LD_LIBRARY_PATH': f"{prefix}/lib:$LD_LIBRARY_PATH",
    })

    stage0 += packages(apt=['libopenexr-dev'])
    stage0 += shell(commands=[
        f'cd {python_dir}/bin',
        './python3.7m -m ensurepip',
        './python3.7m -m pip install -U pip setuptools wheel numpy',
        './python3.7m -m pip install -U opencv-python openexr bpycv'
    ])

    blenderGIS_source = "https://github.com/domlysz/BlenderGIS/archive/refs/tags/v2.2.4-10/2020.zip"
    stage0 += shell(commands=[
        f"wget {blenderGIS_source} /var/tmp/",
        f"{prefix}/blender -y -b --python-expr 'import bpy;bpy.ops.wm.addon_install(filepath=/var/tmp/2020.zip)'"
    ])


    return stage0


if __name__ == '__main__':
    Fire(build)
