#!/usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import argparse
import datetime
import os
import pathlib
import subprocess
import sys
import venv


ROOT = pathlib.Path(os.path.abspath(__file__)).parent
BUILD = ROOT / 'build'
DIST = ROOT / 'dist'
VENV = BUILD / 'venv'
PIP = VENV / 'bin' / 'pip'
PYTHON = VENV / 'bin' / 'python'
REQUIREMENTS = ROOT / 'requirements.txt'
MAKE_DIR = ROOT / 'cpython-linux'


def bootstrap():
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--libressl', action='store_true')
    parser.add_argument('--musl', action='store_true')
    parser.add_argument('--optimized', action='store_true')
    parser.add_argument('--python',
                        default='cpython-3.7',
                        help='name of Python to build')

    args = parser.parse_args()

    BUILD.mkdir(exist_ok=True)
    DIST.mkdir(exist_ok=True)

    venv.create(VENV, with_pip=True)

    subprocess.run([str(PIP), 'install', '-r', str(REQUIREMENTS)],
                   check=True)

    os.environ['PYBUILD_BOOTSTRAPPED'] = '1'
    os.environ['PATH'] = '%s:%s' % (str(VENV / 'bin'), os.environ['PATH'])
    os.environ['PYTHONPATH'] = str(ROOT)

    if args.debug:
        os.environ['PYBUILD_DEBUG'] = '1'
    if args.libressl:
        os.environ['PYBUILD_LIBRESSL'] = '1'
    if args.musl:
        os.environ['PYBUILD_MUSL'] = '1'
    if args.optimized:
        os.environ['PYBUILD_OPTIMIZED'] = '1'
    os.environ['PYBUILD_PYTHON'] = args.python

    subprocess.run([str(PYTHON), __file__], check=True)


def run():
    from pythonbuild.downloads import DOWNLOADS
    from pythonbuild.utils import compress_python_archive

    now = datetime.datetime.utcnow()

    env = dict(os.environ)
    env['PYTHONUNBUFFERED'] = '1'

    entry = DOWNLOADS[os.environ['PYBUILD_PYTHON']]
    env['PYBUILD_PYTHON_VERSION'] = entry['version']

    subprocess.run(['make'],
                   cwd=str(MAKE_DIR), env=env, check=True)

    basename = 'cpython-%s-linux64' % entry['version']
    extra = ''

    if 'PYBUILD_MUSL' in os.environ:
        basename += '-musl'
        extra = '-musl'
    if 'PYBUILD_DEBUG' in os.environ:
        basename += '-debug'
        extra += '-debug'
    if 'PYBUILD_OPTIMIZED' in os.environ:
        basename += '-pgo'
        extra = '-pgo'

    basename += '.tar'

    source_path = BUILD / basename
    compress_python_archive(source_path, DIST, 'cpython-%s-linux64%s-%s' % (
        entry['version'], extra,
        now.strftime('%Y%m%dT%H%M')))


if __name__ == '__main__':
    try:
        if 'PYBUILD_BOOTSTRAPPED' not in os.environ:
            bootstrap()
        else:
            run()
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)
