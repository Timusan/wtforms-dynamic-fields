import sys
import re
from setuptools import setup
from setuptools.command.test import test as TestCommand

# Pytest class not used for now ... testing is
# initiated via Tox.
class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ['--strict', '--verbose']
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)

class Tox(TestCommand):
    #user_options = [('tox-args=', 'a', "Arguments to pass to tox")]
    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.tox_args = None
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True
    def run_tests(self):
        import tox
        import shlex
        errno = tox.cmdline(args=shlex.split(self.tox_args))
        sys.exit(errno)

long_description = open('README.txt').read()

with open('wtforms_dynamic_fields/__init__.py') as f:
    m = re.findall(r'__version__\s*=\s*\'(.*)\'', f.read())
    version = m[0]

setup(
    name='WTForms-Dynamic-Fields',
    version=version,
    url='https://github.com/timusan/wtforms-dynamic-fields',
    license='BSD',
    author='Tim van der Linden',
    tests_require=['tox'],
    install_requires=['WTForms>=2.0.1'],
    cmdclass={'test': Tox},
    author_email='tim@shisaa.jp',
    description='Simple wrapper to add "dynamic" (sets of) fields to an already instantiated WTForms form.',
    long_description=long_description,
    packages=['wtforms_dynamic_fields', 'tests'],
    include_package_data=True,
    platforms='any',
    test_suite='wtforms_dynamic_fields.tests',
    classifiers = [
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Development Status :: 3 - Alpha',
        'Natural Language :: English',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        ]
)
