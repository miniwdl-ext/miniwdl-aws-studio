#!/bin/bash
# Bootstrap miniwdl-aws in fresh SageMaker Studio "System Terminal"
# (Following successful deploy of CDK stack)
# Warning: overwrites ~/.config/miniwdl.cfg if any

set -euo pipefail

if ! [ -f '/opt/ml/metadata/resource-metadata.json' ]; then
    >&2 echo 'This script is meant to run within a SageMaker Studio System Terminal.'
    exit 1
fi

pip3 install --upgrade miniwdl miniwdl-aws
curl -Ls https://github.com/miniwdl-ext/miniwdl-aws-studio/raw/main/miniwdl_aws_studio.cfg > ~/.config/miniwdl.cfg
miniwdl run_self_test --dir ~/miniwdl/self_test
