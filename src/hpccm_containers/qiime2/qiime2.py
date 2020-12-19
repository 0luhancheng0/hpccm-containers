from hpccm import config, primitives, Stage
from fire import Fire
from hpccm.building_blocks import conda
from hpccm.building_blocks.packages import packages
import wget
from pathlib import Path
def build(format='singularity', baseimage='ubuntu:18.04', qiime2_version='2020.11', python_version='py36'):
    config.set_container_format(format)
    stage0 = Stage(name='stage0')
    stage0 += primitives.baseimage(image=baseimage)
    environment_file = f"qiime2-{qiime2_version}-{python_version}-linux-conda.yml"
    url = f"https://data.qiime2.org/distro/core/{environment_file}"
    if not Path(environment_file).exists():
        wget.download(url)
    stage0 += conda(environment=environment_file, eula=True)
    stage0 += primitives.shell(commands=[f"echo '#!/bin/bash\\nsource /usr/local/anaconda/bin/activate base\\n$@' > /usr/local/bin/entrypoint.sh", 'chmod a+x /usr/local/bin/entrypoint.sh'])
    stage0 += primitives.runscript(commands=['/usr/local/bin/entrypoint.sh'])
    return stage0
if __name__ == "__main__":
    Fire(build)
