from __future__ import generator_stop
from os import environ
from hpccm import config, Stage
from hpccm.building_blocks import gnu, conda, python, pip, generic_autotools
from hpccm.building_blocks.generic_build import generic_build
from hpccm.building_blocks.packages import packages
from hpccm.primitives import label, baseimage, copy, shell
from fire import Fire
from hpccm.primitives.environment import environment
from hpccm_containers.utils import from_prefix


def build(container_format='singularity', os='ubuntu20.04', cuda_version='11.0', tensorflow_version='2.2.0', pytorch_version='1.7.1', pycuda_version='v2020.1'):
    image = f'nvcr.io/nvidia/cuda:{cuda_version}-devel-{os}'
    config.set_container_format(container_format)
    stage0 = Stage(name='stage0')
    stage0 += baseimage(image=image, _bootstrap='docker')
    stage0 += label(metadata={'maintainer': 'Luhan Cheng', 'email': 'luhan.cheng@monash.edu'})
    stage0 += packages(apt=['libxml2-dev', 'libxslt-dev', 'python3-pip', 'git'])
    stage0 += conda(
        eula=True,
        packages=['python=3.7', f'tensorflow-gpu={tensorflow_version}', f'pytorch={pytorch_version}', 'torchvision', 'torchaudio'],
        channels=['pytorch', 'anaconda', 'conda-forge']
    )
    stage0 += generic_build(
        repository='https://github.com/inducer/pycuda.git',
        branch=pycuda_version,
        build=[f'./configure.py --cuda-root=/usr/local/cuda-{cuda_version}'],
    )
    stage0 += environment(variables=from_prefix('/usr/local/pycuda'))
    version = "7.2.1.6"
    os = "Ubuntu-18.04"
    arch = 'x86_64'
    cuda = "cuda-11.0"
    cudnn = "cudnn8.0"
    filename = f'TensorRT-{version}.{os}.{arch}-gnu.{cuda}.{cudnn}.tar.gz'
    TENSORRT_ROOT='/usr/local/tensorrt'
    stage0 += copy(src=f'{filename}', dest=f'/{filename}')
    stage0 += shell(commands=[
        f'mkdir -p {TENSORRT_ROOT}',
        f'tar -xf /TensorRT-7.2.1.6.Ubuntu-18.04.x86_64-gnu.cuda-11.0.cudnn8.0.tar.gz --strip-components 1 -C {TENSORRT_ROOT}',
        'rm -rf /TensorRT-7.2.1.6.Ubuntu-18.04.x86_64-gnu.cuda-11.0.cudnn8.0.tar.gz'
    ])
    stage0 += environment(variables={
        'LD_LIBRARY_PATH': f'$LD_LIBRARY_PATH:{TENSORRT_ROOT}/lib/',
        'PATH': f'$PATH:{TENSORRT_ROOT}/bin/',
        'C_INCLUDE_PATH': f'$C_INCLUDE_PATH:{TENSORRT_ROOT}/include/',
        **from_prefix('/usr/local/cuda'),
        **from_prefix('/usr/local/anaconda')
    })
    stage0 += pip(packages=[
        f'{TENSORRT_ROOT}/python/tensorrt-7.2.1.6-cp37-none-linux_x86_64.whl', f'{TENSORRT_ROOT}/uff/uff-0.6.9-py2.py3-none-any.whl',
        f'{TENSORRT_ROOT}/graphsurgeon/graphsurgeon-0.4.5-py2.py3-none-any.whl', f'{TENSORRT_ROOT}/onnx_graphsurgeon/onnx_graphsurgeon-0.2.6-py2.py3-none-any.whl'
    ], pip='pip3')
    cudnn_src = 'cudnn-11.0-linux-x64-v8.0.5.39.tgz'
    stage0 += copy(src=cudnn_src, dest=f'/{cudnn_src}')
    stage0 += shell(commands=[
        'mkdir -p /cudnn',
        f'tar -xf /{cudnn_src} -C /cudnn --strip-components 1',
        'cp /cudnn/include/cudnn*.h /usr/local/cuda/include',
        'cp /cudnn/lib64/libcudnn* /usr/local/cuda/lib64',
        'chmod a+r /usr/local/cuda/include/cudnn*.h /usr/local/cuda/lib64/libcudnn*',
        'rm -rf /cudnn /cudnn-11.0-linux-x64-v8.0.5.39.tgz'
    ])

    return stage0


if __name__ == '__main__':
    Fire(build)
