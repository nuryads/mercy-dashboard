#!/bin/sh
set -eu
cd "$(dirname "$0")"
blender --background --python blender/build_blend.py -- "$PWD"
