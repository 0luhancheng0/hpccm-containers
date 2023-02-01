import hpccm
from hpccm.building_blocks.base import bb_base
from hpccm.building_blocks.packages import packages
from hpccm.building_blocks import generic_cmake
from hpccm.common import linux_distro
from hpccm.primitives.comment import comment
from hpccm.primitives.copy import copy
from hpccm.primitives.environment import environment
from hpccm.primitives.shell import shell
from hpccm.toolchain import toolchain
from copy import copy as _copy
from hpccm.templates import CMakeBuild, downloader, git, wget


class turbovnc(bb_base, hpccm.templates.wget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__url = kwargs.get("url", "https://swift.rc.nectar.org.au/v1/AUTH_810/CVL-Singularity-External-Files/turbovnc_2.2.5_amd64.deb")
        self.__outfile = kwargs.get("outfile", "turbovnc.deb")
        self += self.download_step(url=self.__url, outfile="turbovnc.deb")
        self.__instruction()
    def __instruction(self):
        self += f'dpkg -i {self.__outfile}'
        self += f"rm {self.__outfile}"



# class turbovnc(bb_base, hpccm.templates.ConfigureMake, hpccm.templates.envvars, hpccm.templates.CMakeBuild, hpccm.templates.git):
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         self.__repository = kwargs.get("repository", "https://github.com/TurboVNC/turbovnc.git")
#         self.__ospackages = kwargs.get('ospackages', ['cmake', 'git', 'openjdk-8-jdk'])
#         self.__prefix = kwargs.get('prefix', '/usr/local/turbovnc')
#         self.__version = kwargs.pop('version', '2.2.7')
#         self.__ospackages = kwargs.pop('ospackages', ['cmake'])
#         self.__check = kwargs.pop('check', False)
#         self.__configure_opts = kwargs.pop('configure_opts', [])
#         self.__toolchain = _copy(kwargs.pop('toolchain', toolchain()))

#         self.__bb = generic_cmake(
#             annotations={'version': self.__version},
#             repository=self.__repository,
#             branch=self.__version,
#             base_annotation=self.__class__.__name__,
#             check=self.__check,
#             configure_opts=self.__configure_opts,
#             comment=False,
#             # devel_environment=self.environment_variables,
#             prefix=self.__prefix,
#             # runtime_environment=self.environment_variables,
#             toolchain=self.__toolchain,
#         )
#         self += self.__bb
#     def __setup():
#         return "wget http://downloads.sourceforge.net/project/libjpeg-turbo/2.1.3/libjpeg-turbo-2.1.3.tar.gz"

