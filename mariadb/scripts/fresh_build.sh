#!/bin/bash
# Fresh debug build dir (used when an incremental build fails after a branch switch)
BLD=/home/user/mdb_build_dbg
rm -rf $BLD && mkdir -p $BLD && cd $BLD && cmake -G Ninja /home/user/mdb_src -DCMAKE_BUILD_TYPE=Debug -DMYSQL_MAINTAINER_MODE=OFF \
 -DCMAKE_C_COMPILER_LAUNCHER=ccache -DCMAKE_CXX_COMPILER_LAUNCHER=ccache -DWITH_WSREP=OFF -DPLUGIN_COLUMNSTORE=NO -DPLUGIN_ROCKSDB=NO \
 -DPLUGIN_MROONGA=NO -DPLUGIN_SPIDER=NO -DPLUGIN_TOKUDB=NO -DPLUGIN_CONNECT=NO -DPLUGIN_S3=NO -DPLUGIN_DUCKDB=NO -DWITH_SSL=system \
 -DWITH_UNIT_TESTS=OFF -DWITH_EMBEDDED_SERVER=OFF > cmake.log 2>&1
