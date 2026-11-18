# Xyce, serial, release build, with Verilog-A plugin support (Xyce/ADMS):
#
#   falllow run --machine milan-box-01 --cache circsims --cpu 12 --memory 16G --timeout 3h -- bash sims/xyce.sh
#
# The dependencies are built at the versions the Xyce release is tested with in its own CI
# (gitlab-ci/ci.yml of the release: SuiteSparse for AMD, Trilinos, ADMS) and kept in
# $SIMS/xyce/deps/<project>-<tag>: a failed or repeated Xyce build reuses them, and
# buildxyceplugin.sh compiles plugins against the Trilinos headers there. Trilinos is
# shared, as plugin support requires a shared Xyce; libxyce.so finds it through its RPATH.
# Build trees live in $SIMS/xyce/build so a killed job resumes, and are removed on success.
#
# Plugins, from the installed bin/ (the .va path must be absolute):
#   buildxyceplugin.sh -o <name> /abs/model.va <outdir>   ->  <outdir>/lib<name>.so
#   Xyce -plugin <outdir>/lib<name>.so netlist.cir

source "$(dirname "$0")/common.sh"
ROOT=$(cd "$(dirname "$0")/.." && pwd)

TAG=${RELEASE_TAG:-$(github_latest Xyce/Xyce)}
VERSION=${TAG#Release-}
DEPS=$SIMS/xyce/deps
BUILD=$SIMS/xyce/build
LOGS=$BUILD/logs
mkdir -p "$DEPS" "$LOGS"

# g++ on Trilinos and Xyce sources stays below this per compile job; caps the parallelism
# to the memory the job got
MIB_PER_JOB=${MIB_PER_JOB:-1536}
MEM_JOBS=$(( ${FALLLOW_MEMORY_MIB:-$((JOBS * MIB_PER_JOB))} / MIB_PER_JOB ))
JOBS=$(( MEM_JOBS < JOBS ? MEM_JOBS : JOBS ))
JOBS=$(( JOBS < 1 ? 1 : JOBS ))
log "xyce $TAG, $JOBS build jobs"

apt_install cmake ninja-build make gfortran bison flex bc perl libxml-libxml-perl \
    libblas-dev liblapack-dev libfftw3-dev

# fetch(repo, tag): the source tree of a GitHub tag, unpacked once into $BUILD/src
fetch() {
    local dir=$BUILD/src/${1#*/}-$2
    if [ ! -d "$dir" ]; then
        log "fetch $1 $2" >&2
        rm -rf "$dir.part"
        mkdir -p "$dir.part"
        curl -fsSL "https://github.com/$1/archive/refs/tags/$2.tar.gz" | tar xz -C "$dir.part" --strip-components=1
        mv "$dir.part" "$dir"
    fi
    printf '%s\n' "$dir"
}

# step(name, command...): full output to $LOGS/<name>.log; streams every 100th build step
# and every error line, and the end of the log if the command fails
step() {
    local name=$1 t0=$SECONDS
    shift
    log "$name: start"
    if ! "$@" 2>&1 | tee "$LOGS/$name.log" | awk '
            /^\[[0-9]+\/[0-9]+\]/ { split(substr($1, 2), a, "/"); if (a[1] % 100 == 0 || a[1] == a[2] + 0) { print; fflush() } next }
            /[Ee]rror|FAILED/ { print; fflush() }'; then
        log "$name: FAILED, end of $LOGS/$name.log:"
        tail -n 80 "$LOGS/$name.log"
        exit 1
    fi
    log "$name: done in $(( SECONDS - t0 )) s"
}

XYCE_SRC=$(fetch Xyce/Xyce "$TAG")
ci_version() { awk -v k="$1" '$1 == k":" { print $2 }' "$XYCE_SRC/gitlab-ci/ci.yml"; }
SS_TAG=$(ci_version SuiteSparseVersion)
TRI_TAG=$(ci_version TrilinosVersion)
ADMS_TAG=$(ci_version ADMSVersion)
[ -n "$SS_TAG" ] && [ -n "$TRI_TAG" ] && [ -n "$ADMS_TAG" ] || { log "dependency versions not found in gitlab-ci/ci.yml"; exit 1; }
log "dependencies from Xyce CI: SuiteSparse $SS_TAG, Trilinos $TRI_TAG, ADMS $ADMS_TAG"
SS=$DEPS/suitesparse-$SS_TAG
TRI=$DEPS/trilinos-$TRI_TAG
ADMS=$DEPS/adms-$ADMS_TAG

# cmake_dep(name, prefix, repo, tag, cmake args...): fetch, configure, build and install
# once; a .done marker in the prefix records a complete install
cmake_dep() {
    local name=$1 prefix=$2 repo=$3 tag=$4 src
    shift 4
    if [ -f "$prefix/.done" ]; then log "$name: cached at $prefix"; return; fi
    rm -rf "$prefix"
    src=$(fetch "$repo" "$tag")
    step "$name-configure" cmake -G Ninja -S "$src" -B "$BUILD/$name" -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_INSTALL_PREFIX="$prefix" "$@"
    step "$name-build" cmake --build "$BUILD/$name" -j "$JOBS" --target install
    touch "$prefix/.done"
}

# AMD only, static and position independent: linked into the shared Trilinos libraries
cmake_dep suitesparse "$SS" DrTimothyAldenDavis/SuiteSparse "$SS_TAG" \
    -DSUITESPARSE_ENABLE_PROJECTS="suitesparse_config;amd" \
    -DBUILD_SHARED_LIBS=OFF -DBUILD_STATIC_LIBS=ON -DCMAKE_POSITION_INDEPENDENT_CODE=ON \
    -DSUITESPARSE_USE_OPENMP=OFF -DSUITESPARSE_USE_FORTRAN=OFF -DSUITESPARSE_USE_CUDA=OFF

cmake_dep trilinos "$TRI" trilinos/Trilinos "$TRI_TAG" \
    -C "$XYCE_SRC/cmake/trilinos/trilinos-new-base.cmake" \
    -DBUILD_SHARED_LIBS=ON -DCMAKE_INSTALL_RPATH="$TRI/lib" \
    -DAMD_INCLUDE_DIRS="$SS/include/suitesparse" -DAMD_LIBRARY_DIRS="$SS/lib" \
    -DAMD_LIBRARY_NAMES="amd;suitesparseconfig"

cmake_dep adms "$ADMS" Qucs/ADMS "$ADMS_TAG"

PREFIX=$(prefix_for xyce "$VERSION")
step xyce-configure env PATH="$ADMS/bin:$PATH" cmake -G Ninja -S "$XYCE_SRC" -B "$BUILD/xyce" \
    -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX="$PREFIX" -DTrilinos_ROOT="$TRI" \
    -DXyce_PLUGIN_SUPPORT=ON -DBUILD_SHARED_LIBS=ON -DXyce_USE_FFT=ON -DXyce_TEST_BINARIES=OFF
grep -q "Plugin compatibility enabled" "$LOGS/xyce-configure.log" || { log "plugin support not enabled"; exit 1; }
step xyce-build cmake --build "$BUILD/xyce" -j "$JOBS" --target install

# smoke test on a copy: one netlist, and one Verilog-A plugin built and loaded
log "smoke test"
"$PREFIX/bin/Xyce" -v
SMOKE=$SRC/xyce-smoke
mkdir -p "$SMOKE/plugin"
cp "$ROOT/cases/xyce_4049osc/4049osc.cir" "$ROOT/cases/xyce_verilogplugin/rlc_series.cir" "$SMOKE/"
cp "$ROOT/cases/xyce_verilogplugin/toys/rlc2.va" "$SMOKE/plugin/"
cd "$SMOKE"
rc=0; "$PREFIX/bin/Xyce" 4049osc.cir > 4049osc.log 2>&1 || rc=$?
tail -n 5 4049osc.log; log "4049osc.cir: exit $rc"; [ "$rc" = 0 ]
(cd plugin && "$PREFIX/bin/buildxyceplugin.sh" -o rlc2 "$SMOKE/plugin/rlc2.va" "$SMOKE/plugin") \
    || { log "buildxyceplugin failed:"; tail -n 60 plugin/buildxyceplugin.log plugin/CMakeFiles/CMakeOutput.log 2>/dev/null; exit 1; }
rc=0; "$PREFIX/bin/Xyce" -plugin "$SMOKE/plugin/librlc2.so" rlc_series.cir > rlc_series.log 2>&1 || rc=$?
tail -n 5 rlc_series.log; log "rlc_series.cir with plugin librlc2.so: exit $rc"; [ "$rc" = 0 ]
ls -l "$SMOKE"

printf '%s (github Xyce/Xyce %s; Trilinos %s, SuiteSparse %s, ADMS %s)\n' \
    "$("$PREFIX/bin/Xyce" -v 2>&1 | sed -n 1p)" "$TAG" "$TRI_TAG" "$SS_TAG" "$ADMS_TAG" > "$PREFIX/version"
rm -rf "$BUILD"
# run time: BLAS, LAPACK, FFTW, gfortran runtime of Trilinos; cmake, make, g++, bc for
# buildxyceplugin.sh
finish xyce "$VERSION" "$PREFIX" libblas3 liblapack3 libfftw3-double3 libgfortran5 \
    cmake make g++ bc
