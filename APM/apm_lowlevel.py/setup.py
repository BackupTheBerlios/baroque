from distutils.core import setup, Extension
import sys

if sys.platform == "darwin":

    setup(name = "apm_lowlevel",
          version = "0.2",
          maintainer = "Tilo Riemer",
          ext_modules = [Extension('apm_lowlevel', sources=['apm_lowlevel.c', 'apm_lowlevel_funcs.c'], extra_link_args = ['-framework', 'Carbon', '-framework', 'IOKit'])]
    )

else:

    setup(name = "apm_lowlevel",
          version = "0.2",
          maintainer = "Tilo Riemer",
          ext_modules = [Extension('apm_lowlevel', sources=['apm_lowlevel.c', 'apm_lowlevel_funcs.c'])]
    )
