from distutils.core import setup, Extension

setup(name = "apm_lowlevel",
      version = "0.1",
      maintainer = "Tilo Riemer",
      ext_modules = [Extension('apm_lowlevel', sources=['apm_lowlevel.c', 'apm_lowlevel_funcs.c'])]
      )
