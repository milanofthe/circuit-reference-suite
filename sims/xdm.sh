# XDM, Xyce's netlist translator (HSPICE, PSpice, T-Spice, Spectre into Xyce):
#
#   falllow run --machine milan-box-01 --cache circsims --cpu 4 --memory 6G -- bash sims/xdm.sh
#
# Built without PyInstaller: the install holds the Python bundle (xdm_bdl.py and its Boost.Python
# modules) and bin/xdm_bdl runs it with the system /usr/bin/python3, the one Boost.Python is
# built for (the job image puts another python3 first on PATH).
#
#   xdm_bdl -s hspice -d <outdir> --auto netlist.sp    ->  <outdir>/netlist.sp (Xyce syntax)
#
# --auto translates the included and library files as well. The smoke test runs the
# translation through Xyce when sims/xyce.sh has installed it.

source "$(dirname "$0")/common.sh"
ROOT=$(cd "$(dirname "$0")/.." && pwd)

TAG=${RELEASE_TAG:-$(github_latest Xyce/XDM)}
VERSION=${TAG#Release-}

apt_install cmake make python3-dev libboost-python-dev

log "fetch Xyce/XDM $TAG"
mkdir -p "$SRC/xdm"
curl -fsSL "https://github.com/Xyce/XDM/archive/refs/tags/$TAG.tar.gz" | tar xz -C "$SRC/xdm" --strip-components=1

PREFIX=$(prefix_for xdm "$VERSION")
# the expression parser misses <sstream> and the global isnan of <math.h>, which newer
# libstdc++ headers no longer pull in: force-included instead of patching the source
cmake -S "$SRC/xdm" -B "$SRC/xdm-build" -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX="$PREFIX" \
    -DPython3_EXECUTABLE=/usr/bin/python3 -DCMAKE_CXX_FLAGS="-include sstream -include math.h"
cmake --build "$SRC/xdm-build" -j "$JOBS"
cmake --install "$SRC/xdm-build"

cat > "$PREFIX/bin/xdm_bdl" <<'EOF'
#!/bin/sh
exec /usr/bin/python3 "$(dirname "$(readlink -f "$0")")/../xdm_bundle/xdm_bdl.py" "$@"
EOF
chmod +x "$PREFIX/bin/xdm_bdl"

# smoke test on a copy: translate an HSPICE netlist with its library, run it in Xyce
log "smoke test"
REPORTED=$("$PREFIX/bin/xdm_bdl" -h | grep -o 'xdm [0-9][0-9.]*' | sed -n 1p)
log "reports: $REPORTED"
SMOKE=$SRC/xdm-smoke
mkdir -p "$SMOKE"
cp "$ROOT"/cases/xyce_xdm_hspice_diode_clipper/{diodeClipper.cir.hspice,nom.lib} "$SMOKE/"
cd "$SMOKE"
rc=0; "$PREFIX/bin/xdm_bdl" -s hspice -d out --auto diodeClipper.cir.hspice > xdm.log 2>&1 || rc=$?
tail -n 5 xdm.log; log "xdm_bdl diodeClipper.cir.hspice: exit $rc"; [ "$rc" = 0 ]
ls -l out
XYCE=$SIMS/xyce/current/bin/Xyce
if [ -x "$XYCE" ]; then
    rc=0; (cd out && "$XYCE" diodeClipper.cir.hspice > xyce.log 2>&1) || rc=$?
    tail -n 5 out/xyce.log; log "Xyce on the translation: exit $rc"; [ "$rc" = 0 ]
else
    log "no Xyce at $XYCE, translation not run"
fi

printf '%s (github Xyce/XDM %s)\n' "$REPORTED" "$TAG" > "$PREFIX/version"
# the packages of the shared libraries the modules were linked against (Boost.Python,
# libpython, libstdc++)
PKGS=$(ldd "$PREFIX"/xdm_bundle/*.so | awk '$2 == "=>" && $3 ~ /^\// { print $3 }' | sort -u |
    xargs readlink -f | xargs dpkg -S | cut -d: -f1 | sort -u)
finish xdm "$VERSION" "$PREFIX" python3 $PKGS
