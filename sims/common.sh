# Sourced by every sims/<name>.sh. One build script per simulator, run as a pool job on the
# machine that runs the suite, with the named cache that holds the simulators:
#
#   falllow run --machine milan-box-01 --cache circsims --cpu 8 --memory 16G -- bash sims/ngspice.sh
#
# A script resolves the newest upstream release itself (or takes VERSION from the
# environment), builds it and installs into $SIMS/<name>/<version>/, then points
# $SIMS/<name>/current at it. The install holds:
#
#   bin/            everything the run puts on PATH
#   lib/, python/   on LD_LIBRARY_PATH and PYTHONPATH, where an install has them
#   version         one line: the version as the simulator reports it, and its source
#   runtime-apt     apt packages the binaries need at run time, one per line
#
# sims/env.sh puts every current install on PATH and installs the union of their
# runtime-apt. Nothing outside $SIMS/<name>/ is written that a later job relies on.

set -euo pipefail

SIMS=${SIMS:-/cache/circsims}
JOBS=${FALLLOW_CORES:-$(nproc)}
SRC=${SRC:-/scratch/src}
mkdir -p "$SIMS" "$SRC"

log() { printf '[%s] %s\n' "$(date +%H:%M:%S)" "$*"; }

apt_install() {
    log "apt: $*"
    export DEBIAN_FRONTEND=noninteractive
    if [ -z "${_APT_UPDATED:-}" ]; then apt-get update -qq; _APT_UPDATED=1; fi
    apt-get install -y -qq --no-install-recommends "$@" >/dev/null
}

# newest release tag of a GitHub repository; RELEASE_TAG overrides
github_latest() {
    curl -fsSL "https://api.github.com/repos/$1/releases/latest" | python3 -c 'import json,sys; print(json.load(sys.stdin)["tag_name"])'
}

# install($name, $version): the prefix to install into, emptied first
prefix_for() {
    local p="$SIMS/$1/$2"
    rm -rf "$p"
    mkdir -p "$p/bin"
    printf '%s\n' "$p"
}

# finish($name, $version, $prefix, runtime apt packages...): record and switch current
finish() {
    local name=$1 version=$2 prefix=$3
    shift 3
    printf '%s\n' "$@" > "$prefix/runtime-apt"
    ln -sfn "$version" "$SIMS/$name/current"
    log "installed $name $version at $prefix"
    du -sh "$prefix"
}
