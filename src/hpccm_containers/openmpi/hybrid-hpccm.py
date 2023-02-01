
TESTCASES = [
    'https://people.sc.fsu.edu/~jburkardt/c_src/hello_mpi/hello_mpi.c',
    'https://people.sc.fsu.edu/~jburkardt/c_src/communicator_mpi/communicator_mpi.c',
    'https://gist.githubusercontent.com/huzhifeng/d1cda3f0474261eda72b36ca83f24e21/raw/f2074c30030e01cd8e87ddffe0433df18161c61d/hybrid.c'
]
APPS = "/usr/local/app"


os_release = USERARG.get('os_release', 'ubuntu')
os_version = USERARG.get('os_version', '20.04')
cuda_version = USERARG.get('cuda_version', '11.0')
gnu_version = USERARG.get('gnu_version', '10')
gdrcopy_version = USERARG.get("gdrcopy_version", '1.3')
knem_version = USERARG.get('knem_version', '1.1.3')
ucx_version = USERARG.get('ucx_version', '1.12.1')
openmpi_version = USERARG.get('openmpi_version', '3.1.6')

image = f'nvcr.io/nvidia/cuda:{cuda_version}-devel-{os_release}{os_version}'
runtime_image = f"nvcr.io/nvidia/cuda:{cuda_version}-runtime-{os_release}{os_version}"

Stage0 += baseimage(image=image, _bootstrap='docker', _as="devel")


Stage0 += packages(apt=['wget', 'git', 'software-properties-common', 'build-essential', 'zlib1g-dev'])
Stage0 += python(python2=False, python3=True)
Stage0 += environment(variables={
    "PATH": "/usr/local/cuda/bin/:$PATH",
    "LD_LIBRARY_PATH": "/usr/local/cuda/lib64/:$LD_LIBRARY_PATH",
    "LIBRARY_PATH": "/usr/local/cuda/lib64/:$LIBRARY_PATH",
    "C_INCLUDE_PATH": "/usr/local/cuda/include:$C_INCLUDE_PATH",
    "CXX_INCLUDE_PATH": "/usr/local/cuda/include:$C_INCLUDE_PATH"
})
compiler = gnu(version=gnu_version)
Stage0 += compiler

Stage0 += gdrcopy(version=gdrcopy_version, ldconfig=True, toolchain=compiler.toolchain)
Stage0 += knem(version=knem_version, ldconfig=True)
Stage0 += ucx(gdcopy=True, knem=True, version=ucx_version, ldconfig=True, cuda=True, toolchain=compiler.toolchain)
Stage0 += openmpi(cuda=True, infiniband=False, version=openmpi_version, ucx=True, ldconfig=True, toolchain=compiler.toolchain)

Stage0 += shell(commands=[
    f'mkdir -p {APPS} && cd {APPS}',
    f"mkdir -p {APPS}/src {APPS}/bin",
    f'cd {APPS}/src', *[f'wget {i}' for i in TESTCASES],
    f"cd {APPS}", *[f"mpicc -fopenmp src/{i.split('/')[-1]} -o bin/{i.split('/')[-1].split('.')[0]}" for i in TESTCASES]])

Stage1 += baseimage(image=runtime_image)
Stage1 += Stage0.runtime(_from="devel")
Stage1 += environment(variables={
    'LC_ALL': 'en_AU.UTF-8',
    'LANGUAGE': 'en_AU.UTF-8',
})

Stage1 += shell(commands=[
    'rm -f /bin/sh && ln -s /bin/bash /bin/sh',
    'rm -f /usr/bin/sh && ln -s /usr/bin/bash /usr/bin/sh',
    '/bin/bash',
])
Stage1 += packages(apt=['wget', 'git', 'software-properties-common', 'build-essential', 'locales', 'zlib1g-dev',
                        'ubuntu-desktop', 'vim', 'mesa-utils'])
Stage1 += shell(commands=['locale-gen en_AU.UTF-8'])
Stage1 += shell(commands=[
    'wget https://swift.rc.nectar.org.au/v1/AUTH_810/CVL-Singularity-External-Files/turbovnc_2.2.5_amd64.deb && dpkg -i turbovnc_2.2.5_amd64.deb && rm turbovnc_2.2.5_amd64.deb',
    'wget https://swift.rc.nectar.org.au/v1/AUTH_810/CVL-Singularity-External-Files/virtualgl_2.6.4_amd64.deb && dpkg -i virtualgl_2.6.4_amd64.deb && rm virtualgl_2.6.4_amd64.deb',
    'apt update',
    'apt -y upgrade'
])
Stage1 += copy(_from='devel', src=f'{APPS}/bin', dest=f"{APPS}/bin")
Stage1 += environment(variables={
    "PATH": "/usr/local/cuda/bin/:$PATH",
    "LD_LIBRARY_PATH": "/usr/local/cuda/lib64/:$LD_LIBRARY_PATH"
})

Stage1 += label(metadata={'maintainer': 'Luhan Cheng', 'email': 'luhan.cheng@monash.edu'})




