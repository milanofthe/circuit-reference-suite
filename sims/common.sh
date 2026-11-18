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
#   lib/            on LD_LIBRARY_PATH, where an install has one
#   version         one line: the version as the simulator reports it, and its source
#   runtime-apt     apt packages the binaries need at run time, one per line
#
# sims/env.sh puts every current install on PATH and installs the union of their
# runtime-apt. Nothing outside $SIMS/<name>/ is written that a later job relies on.

set -euo pipefail

REPO=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
SIMS=${SIMS:-/cache/circsims}
JOBS=${FALLLOW_CORES:-$(nproc)}
SRC=${SRC:-/scratch/src}
mkdir -p "$SIMS" "$SRC"
# out of the shipped workspace: its .git may point to a path that only exists where it was shipped from
cd "$SRC"

log() { printf '[%s] %s\n' "$(date +%H:%M:%S)" "$*" >&2; }

# retry(cmd...): up to 5 attempts, for flaky upstream servers
retry() {
    local i
    for i in 1 2 3 4 5; do
        "$@" && return 0
        log "attempt $i failed: $*"
        sleep $((i * 10))
    done
    return 1
}

# quiet(cmd...): run a build step, stream only its progress lines (make directories,
# cmake targets, errors), the last 80 lines of its output if it fails
quiet() {
    local f pid rc=0
    f=$(mktemp)
    log "$*"
    "$@" > "$f" 2>&1 &
    pid=$!
    tail -n +1 -f --pid=$pid "$f" | grep --line-buffered -E 'Entering directory|^\[ *[0-9]+%\] Built target|error:|Error ' || true
    wait $pid || rc=$?
    if [ $rc -ne 0 ]; then
        tail -n 80 "$f"
        log "failed with $rc: $*"
    fi
    rm -f "$f"
    return $rc
}

# smoke($dir, cmd...): run cmd in a scratch copy of $dir (a directory, or a case name
# under cases/), print the tail of its output, its exit code (124: timeout after 300 s)
# and the files it wrote. Never fails the build.
smoke() {
    local src=$1 d rc=0
    shift
    [ -d "$src" ] || src=$REPO/cases/$src
    d=$(mktemp -d "${TMPDIR:-/tmp}/smoke.XXXXXX")
    cp -r "$src/." "$d"
    sleep 1
    touch "$d/.stamp"
    log "smoke: $src: $*"
    (cd "$d" && timeout 300 "$@") < /dev/null > "$d/.out" 2>&1 || rc=$?
    tail -n 30 "$d/.out"
    log "smoke exit code: $rc; files written: $(cd "$d" && find . -newer .stamp -type f ! -name .out | sort | tr '\n' ' ')"
}

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
