from hpccm.primitives import environment
import hpccm
from hpccm.primitives import baseimage, label
def from_prefix(prefix):

    return {
        "PATH": f"{prefix}/bin:$PATH",
        'LIBRARY_PATH': f"{prefix}/lib:$LIBRARY_PATH",
        'C_INCLUDE_PATH': f"{prefix}/include:$C_INCLUDE_PATH",
        "CXX_INCLUDE_PATH": f"{prefix}/include:$CXX_INCLUDE_PATH",
        'LD_LIBRARY_PATH': f"{prefix}/lib:$LD_LIBRARY_PATH",
    }
def stage_template(cpu=True):
    image = "Characterisation-Virtual-Laboratory/CharacterisationVL-Software:2004" if cpu else 'Characterisation-Virtual-Laboratory/CharacterisationVL-Software:2004-cuda11.0'
    stage0 = hpccm.Stage()
    hpccm.config.set_container_format("singularity")
    stage0 += baseimage(image=image, _bootstrap='shub', _distro='ubuntu20')
    stage0 += label(metadata={'maintainer': 'Luhan Cheng', 'email': 'luhan.cheng@monash.edu'})
    return stage0
if __name__ == '__main__':
    print(from_prefix('/usr/local'))
