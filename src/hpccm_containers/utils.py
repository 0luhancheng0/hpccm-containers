from hpccm.primitives import environment
import hpccm
from hpccm.primitives import baseimage, label
import re
from hpccm.primitives import shell


class shell_with_log(shell):
    def __init__(self, **kwargs):
        rep = {" ": "_", "/": "_", "|": "_", '\\': "_", "&": "_"}
        rep = dict((re.escape(k), v) for k, v in rep.items())
        pattern = re.compile("|".join(rep.keys()))
        commands = kwargs.get('commands', [])
        self.logfiles = ['/var/tmp/' + pattern.sub(lambda m: rep[re.escape(m.group(0))], command) + '.log' for command in commands]
        for i in range(len(commands)):
            commands[i] = f"{commands[i]} 2>&1 | tee -a {self.logfiles[i]}"
        if len(commands) != 0:
            commands.append('rm ' + ' '.join(self.logfiles))
        kwargs['commands'] = commands
        super().__init__(**kwargs)


def add_flags(flags=[], variables=['CPPFLAGS', 'CFLAGS', 'CXXFLAGS']):
    flags = ' '.join(flags)
    return {variable: f'"{flags} ${variable}"' for variable in variables}


def add_include_path(include_path):

    return {
        **prepend_path(include_path, 'C_INCLUDE_PATH'),
        **prepend_path(include_path, 'CXX_INCLUDE_PATH'),
    }


def add_library_path(library_path):
    return {
        **prepend_path(library_path, 'LIBRARY_PATH'),
        **prepend_path(library_path, 'LD_LIBRARY_PATH'),
    }


def from_prefix(prefix):
    return {
        **add_binary(f'{prefix}/bin'),
        **add_include_path(f'{prefix}/include'),
        **add_include_path(f'{prefix}/lib'),
        **add_library_path(f'{prefix}/lib64')
    }


def prepend_path(path, variable):
    return {variable: f'{path}:${variable}'}


def add_binary(binpath):
    return prepend_path(binpath, 'PATH')


def CVL_ubuntu_stage(gpu=False, stage_name='stage0'):
    image = "Characterisation-Virtual-Laboratory/CharacterisationVL-Software:2004" if not gpu else 'Characterisation-Virtual-Laboratory/CharacterisationVL-Software:2004-cuda11.0'
    stage0 = hpccm.Stage(name=stage_name)
    hpccm.config.set_container_format("singularity")
    stage0 += baseimage(image=image, _bootstrap='shub', _distro='ubuntu20')
    stage0 += label(metadata={'maintainer': 'Luhan Cheng', 'email': 'luhan.cheng@monash.edu'})
    return stage0


if __name__ == '__main__':
    print(from_prefix('/usr/local'))
