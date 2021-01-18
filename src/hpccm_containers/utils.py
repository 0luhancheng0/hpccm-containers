from hpccm.primitives import environment
import hpccm
from hpccm.primitives import baseimage, label


def from_prefix(prefix):

    return {
        **add_binary(f'{prefix}/bin/'),
        **prepend_path(f'{prefix}/include', 'C_INCLUDE_PATH'),
        **prepend_path(f'{prefix}/include', 'CXX_INCLUDE_PATH'),
        **prepend_path(f'{prefix}/lib', 'LIBRARY_PATH'),
        **prepend_path(f'{prefix}/lib', 'LD_LIBRARY_PATH'),
        **prepend_path(f'{prefix}/lib64', 'LIBRARY_PATH'),
        **prepend_path(f'{prefix}/lib64', 'LD_LIBRARY_PATH'),
    }


def prepend_path(path, variable):
    return {variable: f'{path}:${variable}'}


def add_binary(binpath):
    return prepend_path(binpath, 'PATH')


def stage_template(gpu=False, stage_name='stage0'):
    image = "Characterisation-Virtual-Laboratory/CharacterisationVL-Software:2004" if not gpu else 'Characterisation-Virtual-Laboratory/CharacterisationVL-Software:2004-cuda11.0'
    stage0 = hpccm.Stage(name=stage_name)
    hpccm.config.set_container_format("singularity")
    stage0 += baseimage(image=image, _bootstrap='shub', _distro='ubuntu20')
    stage0 += label(metadata={'maintainer': 'Luhan Cheng', 'email': 'luhan.cheng@monash.edu'})
    return stage0


if __name__ == '__main__':
    print(from_prefix('/usr/local'))
