#!/bin/bash
#
# Copyright (c) 2020 Institution of Parallel and Distributed System, Shanghai Jiao Tong University
# ServerlessBench is licensed under the Mulan PSL v1.
# You can use this software according to the terms and conditions of the Mulan PSL v1.
# You may obtain a copy of Mulan PSL v1 at:
#     http://license.coscl.org.cn/MulanPSL
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v1 for more details.
#

if [ -z "$GG_MODELPATH" ]; then
    echo "$0: ERROR: GG_MODELPATH environment variable not set"
    exit
else 
    echo GG_MODELPATH=$GG_MODELPATH
fi

if [ -z "$GG_STORAGE_URI" ]; then
    echo "$0: ERROR: GG_STORAGE_URI environment variable not set"
    exit
else 
    echo GG_STORAGE_URI=$GG_STORAGE_URI
fi

if [ -z "$AWS_ACCESS_KEY_ID" ]; then
    echo "$0: ERROR: AWS_ACCESS_KEY_ID environment variable not set"
    exit
fi

if [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
    echo "$0: ERROR: AWS_SECRET_ACCESS_KEY environment variable not set"
    exit
fi

if [ -z "$AWS_REGION" ]; then
    echo "$0: ERROR: AWS_REGION environment variable not set"
    exit
fi

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd $DIR/../

USAGE="$0 <JOBS-COUNT>"

JOBS_COUNT=${1?$USAGE}

if [ ! -d "llvm-project" ]; then
  printf "0. Clone LLVM from Github (it may take some time)\n"

  git clone https://github.com/llvm/llvm-project
fi

printf "1. Clear workspace\n"
$DIR/clear.sh

printf "2. Create build dir (llvm-build)\n"
mkdir llvm-build
cd llvm-build

printf "3. Initialize gg\n"
gg init

printf "4. Build llvm using patched cmake (see gg/src/models/wrappers/cmake)\n"
gg infer cmake ../llvm-project/llvm

printf "5. Create thunks for building llvm-tblgen\n"
gg infer make -j`nproc` llvm-tblgen

printf "6. Input trunk:\n"
cat bin/llvm-tblgen

printf "7. Build llvm-tblgen\n"
gg force --jobs=$JOBS_COUNT --engine=lambda bin/llvm-tblgen
