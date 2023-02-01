




os_release = USERARG.get('os_release', 'ubuntu')
os_version = USERARG.get('os_version', '20.04')
cuda_version = USERARG.get('cuda_version', '11.0')

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
Stage1 += environment(variables={
    "PATH": "/usr/local/cuda/bin/:$PATH",
    "LD_LIBRARY_PATH": "/usr/local/cuda/lib64/:$LD_LIBRARY_PATH"
})
Stage1 += label(metadata={'maintainer': 'Luhan Cheng', 'email': 'luhan.cheng@monash.edu'})
