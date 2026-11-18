# gnucap: newest release or snapshot tag, from the official read-only GitHub mirror of
# savannah (git.savannah.gnu.org answers 5xx for minutes at a time), with its default plugins (spice,
# spectre and verilog languages, the device models). The test plugins the gnucap test
# decks load (.load ./c_debug.so, ./cbs.so) go to lib/gnucap-tests/.
# VERSION=20260729-dev builds that tag instead of the newest.
. "$(dirname "$0")/common.sh"

URL=https://github.com/gnucap/gnucap.git
VERSION=${VERSION:-$(retry git ls-remote --tags $URL | grep -v '\^{}' \
    | grep -oE 'refs/tags/(dev-)?[0-9]{8}(-dev)?$' | sed 's|refs/tags/||' \
    | awk '{d=$0; gsub(/[^0-9]/, "", d); print d, $0}' | sort -n | tail -n 1 | cut -d' ' -f2)}
log "gnucap $VERSION"

apt_install make libreadline-dev
cd "$SRC"
rm -rf gnucap
retry git -c advice.detachedHead=false clone -q --depth 1 --branch "$VERSION" $URL gnucap
cd gnucap

PREFIX=$(prefix_for gnucap "$VERSION")
mkdir -p build && cd build
quiet ../configure --prefix="$PREFIX"
quiet make -j"$JOBS"
quiet make install
test -x "$PREFIX/bin/gnucap"
export PATH="$PREFIX/bin:$PATH" LD_LIBRARY_PATH="$PREFIX/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"

mkdir -p "$PREFIX/lib/gnucap-tests"
for p in c_debug cbs; do
    # shellcheck disable=SC2046
    g++ -shared -fPIC $(gnucap-conf --cppflags) $(gnucap-conf --cxxflags) \
        -o "$PREFIX/lib/gnucap-tests/$p.so" "../tests/$p.cc"
done
ls "$PREFIX/lib" "$PREFIX/lib/gnucap-tests"

out=$(gnucap --acs -b /dev/null 2>&1 || true)
echo "$out"
{ grep 'version: ' <<< "$out" | tr '\n' ' '; echo; echo "source: $URL tag $VERSION"; } > "$PREFIX/version"
finish gnucap "$VERSION" "$PREFIX" libreadline8t64

smoke gnucap_tests gnucap --acs -b basic.ckt
smoke vacask_rc/gnucap gnucap --acs -b runme.sim
d=$(mktemp -d)
cp "$REPO/cases/gnucap_tests/d_coil.1a.ckt" "$PREFIX/lib/gnucap-tests/c_debug.so" "$d"
smoke "$d" gnucap --acs -b d_coil.1a.ckt
printf 'broken netlist\nv1 1 0 1\nr1 1 0 undefined_param_xyz\nq1 1 0 0 nomodel\n.op\n.end\n' > "$d/bad.ckt"
smoke "$d" gnucap --acs -b bad.ckt
