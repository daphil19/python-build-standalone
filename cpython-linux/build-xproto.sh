#!/usr/bin/env bash
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

set -ex

cd /build

pkg-config --version

export PATH=/tools/${TOOLCHAIN}/bin:/tools/host/bin:$PATH
export PKG_CONFIG_PATH=/tools/deps/share/pkgconfig

tar -xf xproto-${XPROTO_VERSION}.tar.gz
pushd xproto-${XPROTO_VERSION}

CFLAGS="-fPIC" ./configure \
    --prefix=/tools/deps

make -j `nproc`
make -j `nproc` install DESTDIR=/build/out
