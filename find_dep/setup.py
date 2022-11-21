from setuptools import setup, Extension

module1 = Extension('finddep',
                    include_dirs = ['/usr/local/include'],
                    library_dirs = ['/usr/local/lib'],
                    language = 'c++',
                    extra_compile_args = [ '-std=c++20' ],
                    sources = ['src/find_dep.cpp'])

setup(name = 'finddep',
      version = '1.0',
      description = 'Find dependencies between columns of numpy array',
      author = 'Frédéric Pennerath',
      author_email = 'frederic.pennerath@centralesupelec.fr',
      url = '',
      ext_modules = [module1])

