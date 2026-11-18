# ngspice: newest release tarball from SourceForge, batch build with OSDI, XSPICE, CIDER
# and KLU. VERSION=47 builds that release instead of the newest.
. "$(dirname "$0")/common.sh"

VERSION=${VERSION:-$(git ls-remote --tags https://git.code.sf.net/p/ngspice/ngspice \
    | grep -o 'ngspice-[0-9.]*$' | sed 's/^ngspice-//' | sort -V | tail -1)}
log "ngspice $VERSION"

apt_install make pkg-config libfftw3-dev
cd "$SRC"
retry curl -fsSL -o ngspice.tar.gz \
    "https://downloads.sourceforge.net/project/ngspice/ng-spice-rework/$VERSION/ngspice-$VERSION.tar.gz"
rm -rf "ngspice-$VERSION"
tar xzf ngspice.tar.gz
cd "ngspice-$VERSION"

PREFIX=$(prefix_for ngspice "$VERSION")
mkdir -p build && cd build
quiet ../configure --prefix="$PREFIX" --with-x=no --with-readline=no --disable-debug \
    --enable-osdi --enable-xspice --enable-cider --enable-klu --enable-openmp
quiet make -j"$JOBS"
quiet make install
test -x "$PREFIX/bin/ngspice"

out=$("$PREFIX/bin/ngspice" -v 2>&1 || true)
echo "$out"
{ grep -m1 -o 'ngspice-[^ ]*.*' <<< "$out"
  echo "source: https://downloads.sourceforge.net/project/ngspice/ng-spice-rework/$VERSION"; } > "$PREFIX/version"
finish ngspice "$VERSION" "$PREFIX" libfftw3-double3 libgomp1

export PATH="$PREFIX/bin:$PATH"
smoke ngspice_examples_cider_diode ngspice -b diode.cir
smoke ngspice_examples_xspice_pwm_osc ngspice -b -r out.raw pwm-sin.cir
smoke vacask_rc/ngspice ngspice -b runme.sim
d=$(mktemp -d)
printf 'broken netlist\nv1 1 0 1\nr1 1 0 undefined_model_xyz\nq1 1 0 0 nomodel\n.op\n.end\n' > "$d/bad.cir"
smoke "$d" ngspice -b bad.cir
printf 'nonconvergent\nv1 1 0 1\nr1 1 2 1k\n.tran 1n 1u\n.control\nrun\nprint v(3)\n.endc\n.end\n' > "$d/bad.cir"
smoke "$d" ngspice -b bad.cir
