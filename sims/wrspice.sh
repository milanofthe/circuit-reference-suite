# WRspice: newest xt-* tag of github wrcad/xictools, only WRspice and what it depends on
# (xt_base, KLU, vl, adms for the Verilog-A device modules), no graphics.
# TAG=xt-4.3.24 builds that tag instead of the newest.
. "$(dirname "$0")/common.sh"

URL=https://github.com/wrcad/xictools.git
TAG=${TAG:-$(retry git ls-remote --tags $URL | grep -o 'xt-[0-9.]*$' | sort -V | tail -n 1)}
VERSION=${TAG#xt-}
log "WRspice from xictools $TAG"

apt_install make autoconf automake flex bison gpp libgsl-dev libtiff-dev libjpeg-dev \
    libncurses-dev file
cd "$SRC"
rm -rf xictools
retry git -c advice.detachedHead=false clone -q --depth 1 --branch "$TAG" $URL xictools
cd xictools

PREFIX=$(prefix_for wrspice "$VERSION")
cp Makefile.sample Makefile
# BTF/LIB only resolves on case-insensitive file systems
sed -i 's|^BTF/Lib/libbtf.a: BTF/LIB$|BTF/Lib/libbtf.a: BTF/Lib|' KLU/Makefile.in
# the stubs for a build without graphics toolkit lack savefonts
grep -q 'com_savefonts(wordlist\*) { }' wrspice/src/cp/commands.cc ||
    sed -i 's|^CommandTab::com_setfont(wordlist\*) { }$|&\n\nvoid\nCommandTab::com_savefonts(wordlist*) { }|' wrspice/src/cp/commands.cc
SUBDIRS=(xt_base adms KLU vl wrspice)
# the Makefiles use bash tests
MK=(SHELL=/bin/bash)
quiet make "${MK[@]}" PREFIX=--prefix="$PREFIX" ITOPOK=--enable-itopok=yes "SUBDIRS=${SUBDIRS[*]}" config
# per directory: the top-level Makefile ignores the errors of its subdirectories
# parallel where the Makefiles allow it (adms races), serial to finish what a parallel run
# left; serial install (parallel mkdirs collide); -j1 explicit against an inherited MAKEFLAGS
for s in "${SUBDIRS[@]}"; do quiet make "${MK[@]}" -C "$s" -j"$JOBS" || quiet make "${MK[@]}" -C "$s" -j1; done
for s in "${SUBDIRS[@]}"; do [ ! -d "$s/packages" ] || quiet make "${MK[@]}" -C "$s" -j1 install; done
ls "$PREFIX" "$PREFIX"/xictools "$PREFIX"/xictools/*
wr=$(find "$PREFIX" -name wrspice -type f -perm -u+x -print -quit)
test -n "$wr"
ln -sfn "../${wr#"$PREFIX"/}" "$PREFIX/bin/wrspice"
find "$PREFIX" -name "*.so" | sed -n 1,40p
ldd "$wr" || true

out=$("$PREFIX/bin/wrspice" -v 2>&1 < /dev/null || true)
echo "$out"
{ head -n 2 <<< "$out" | tr '\n' ' '; echo; echo "source: $URL tag $TAG"; } > "$PREFIX/version"
finish wrspice "$VERSION" "$PREFIX" libgsl27 libncurses6 libtiff6 libjpeg8

export PATH="$PREFIX/bin:$PATH"
smoke wrspice_examples_jjexamples wrspice -b jjdc.cir
smoke wrspice_devlib_adms_examples_cap_tests wrspice -b test.sp
d=$(mktemp -d)
printf 'broken netlist\nv1 1 0 1\nr1 1 0 undefined_param_xyz\nq1 1 0 0 nomodel\n.op\n.end\n' > "$d/bad.cir"
smoke "$d" wrspice -b bad.cir
