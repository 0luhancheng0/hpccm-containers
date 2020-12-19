
from hpccm.building_blocks import packages, boost, generic_autotools, generic_build
from hpccm.primitives import baseimage, shell, label, environment
from hpccm_containers.utils import from_prefix
import hpccm
from fire import Fire

def build(image="Characterisation-Virtual-Laboratory/CharacterisationVL-Software:2004", _bootstrap='shub', mash_version='v2.2.2', capnp_version='0.8.0', quicktree_version='v2.5'):
    stage0 = hpccm.Stage()
    hpccm.config.set_container_format("singularity")
    stage0 += baseimage(image=image, _bootstrap=_bootstrap, _distro='ubuntu20')
    stage0 += label(metadata={'maintainer': 'Luhan Cheng', 'email': 'luhan.cheng@monash.edu'})
    stage0 += packages(ospackages=['cpanminus', 'libexpat1-dev', 'sqlite3', 'libsqlite3-dev', 'autoconf'])
    stage0 += generic_build(
        repository='https://github.com/khowe/quicktree',
        branch=quicktree_version,
        build=['make'],
        install=[
            'mv quicktree /usr/local/bin',
            'mv include/* /usr/local/include/'
        ],
    )
    stage0 += boost()
    stage0 += generic_autotools(
        url=f'https://capnproto.org/capnproto-c++-{capnp_version}.tar.gz'
    )
    stage0 += shell(commands=['cpanm -l /usr/local/perl5 --notest BioPerl Bio::Sketch::Mash DBD::SQLite DBI'])
    stage0 += generic_autotools(
        repository=f'https://github.com/marbl/Mash',
        preconfigure=['./bootstrap.sh'],
        branch=mash_version,
        with_capnp='/usr/local/',
        with_boost='/usr/local/boost/',
    )
    stage0 += environment(variables={'PERL5LIB': '$PERL5LIB:/usr/local', **from_prefix('/usr/local/mashtree')})
    stage0 += shell(commands=['cpanm -f -l /usr/local/mashtree Mashtree'])
    return stage0
if __name__ == "__main__":
    Fire(build)
