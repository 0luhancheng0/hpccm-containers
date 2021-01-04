import hpccm
from pathlib import Path
from hpccm import building_blocks, primitives
from fire import Fire
def build(format='singularity', baseimage='ubuntu:18.04', qiime2_version='2020.11', python_version='py36'):
    hpccm.config.set_container_format(format)
    stage0 = hpccm.Stage(name='stage0')
    stage0 += primitives.baseimage(image=baseimage)
    environment_file = f"qiime2-{qiime2_version}-{python_version}-linux-conda.yml"
    url = f"https://data.qiime2.org/distro/core/{environment_file}"
    if not Path(environment_file).exists():
        wget.download(url)
    stage0 += building_blocks.conda(environment=environment_file, eula=True, packages=['mmvec'], channels=['conda-forge'])
    stage0 += primitives.shell(commands=[f"echo '#!/bin/bash\\nsource /usr/local/anaconda/bin/activate base\\n$@' > /usr/local/bin/entrypoint.sh", 'chmod a+x /usr/local/bin/entrypoint.sh'])
    stage0 += primitives.runscript(commands=['/usr/local/bin/entrypoint.sh'])

    return stage0
if __name__ == '__main__':
    Fire(build)

