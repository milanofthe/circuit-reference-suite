# WRspice: newest xt-* tag of github wrcad/xictools, only WRspice and what it depends on
# (xt_base, KLU, vl), no graphics, and ADMS for the Verilog-A device modules. The device
# modules WRspice ships as sources, the ADMS examples (devlib/adms/examples and
# examples.old) and the retired devices (devlib/obsolete), are built into
# modules/<set>/<module>.so, set adms, adms.old or obsolete, which WRspice loads with -m.
# TAG=xt-4.3.24 builds that tag instead of the newest.
. "$(dirname "$0")/common.sh"

URL=https://github.com/wrcad/xictools.git
TAG=${TAG:-$(retry git ls-remote --tags $URL | grep -o 'xt-[0-9.]*$' | sort -V | tail -n 1)}
VERSION=${TAG#xt-}
log "WRspice from xictools $TAG"

apt_install make autoconf automake libtool flex bison gpp libgsl-dev libtiff-dev libjpeg-dev \
    libncurses-dev file perl libxml-libxml-perl unzip
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
SUBDIRS=(xt_base KLU vl wrspice)
# the Makefiles use bash tests
MK=(SHELL=/bin/bash)
quiet make "${MK[@]}" PREFIX=--prefix="$PREFIX" ITOPOK=--enable-itopok=yes "SUBDIRS=${SUBDIRS[*]}" config
# per directory: the top-level Makefile ignores the errors of its subdirectories
# parallel where the Makefiles allow it, serial to finish what a parallel run left;
# serial install (parallel mkdirs collide); -j1 explicit against an inherited MAKEFLAGS
for s in "${SUBDIRS[@]}"; do quiet make "${MK[@]}" -C "$s" -j"$JOBS" || quiet make "${MK[@]}" -C "$s" -j1; done
for s in "${SUBDIRS[@]}"; do [ ! -d "$s/packages" ] || quiet make "${MK[@]}" -C "$s" -j1 install; done
ls "$PREFIX" "$PREFIX"/xictools "$PREFIX"/xictools/*
wr=$(find "$PREFIX" -name wrspice -type f -perm -u+x -print -quit)
test -n "$wr"
ln -sfn "../${wr#"$PREFIX"/}" "$PREFIX/bin/wrspice"
ldd "$wr" || true

# ADMS from the release tarball xictools ships in adms/, with its own build. The admsXml
# xictools builds from its pre-generated sources (adms/adms_wr) expands no `define macro
# here: a module of three lines that defines and uses one fails to lex with it and passes
# with this build, and every example that uses a macro fails with it.
mkdir -p "$SRC/adms"
tar xzf adms/ADMS-release-*.tar.gz -C "$SRC/adms" --strip-components=1 2>/dev/null
(cd "$SRC/adms" && quiet ./bootstrap.sh && quiet ./configure --prefix="$PREFIX/adms" &&
    quiet make -j"$JOBS" && quiet make install)
"$PREFIX/adms/bin/admsXml" --version 2>&1 | sed -n 1,2p

# Device modules. A module that does not build is logged with the first error and skipped.
MODULES=$PREFIX/modules
mkdir -p "$MODULES"/{adms,adms.old,obsolete}
export PATH="$PREFIX/adms/bin:$PREFIX/bin:$PATH"
DEVLIB=$PWD/wrspice/devlib
built=() failed=()
for set in adms adms.old; do
    dir=$DEVLIB/adms/${set/adms/examples}
    for ex in "$dir"/*/; do
        ex=${ex%/}
        [ -x "$ex/mkmk" ] || continue
        # the examples.old directories lack the download recipe of the template; their
        # sources are local, and the shipped empty recipe says so
        [ -f "$ex/link.mk" ] || cp "$DEVLIB/adms/examples/cap/link.mk" "$ex/"
        (cd "$ex" && ./mkmk && make -j1 SHELL=/bin/bash PREFIX="$PREFIX" > build.log 2>&1) || true
        name=$(sed -n 's/^MODULE = //p' "$ex/Makefile")
        if [ -f "$ex/$name.so" ]; then
            install -m 644 "$ex/$name.so" "$MODULES/$set/$name.so"
            built+=("$set/$name")
        else
            failed+=("$set/$name")
            log "module $set/$name ($(sed -n 's/^MODELNAME = //p; s/^LEVEL = //p' "$ex/Makefile" | tr '\n' ' ')): $(grep -m1 -i 'fatal\|error\|no rule' "$ex/build.log" | cut -c1-200)"
        fi
    done
done
for ex in "$DEVLIB"/obsolete/*/; do
    rel=wrspice/devlib/obsolete/$(basename "$ex")
    [ -f "$ex/Makefile.in" ] || continue
    # the retired devices are not configured; their Makefiles come from the same
    # config.status as the others, their headers sit one directory further up
    (cd xt_base && ./config.status --file="../$rel/Makefile:../$rel/Makefile.in") > /dev/null
    (cd "$ex" && make -j"$JOBS" SHELL=/bin/bash MKMOD=1 INCLUDE=-I../../include > build.log 2>&1) || true
    name=$(sed -n 's/^MODULE = //p' "$ex/Makefile")
    if [ -f "$ex/$name.so" ]; then
        install -m 644 "$ex/$name.so" "$MODULES/obsolete/$name.so"
        built+=("obsolete/$name")
    else
        failed+=("obsolete/$name")
        log "module obsolete/$name: $(grep -m1 -i ' error\|Error ' "$ex/build.log" | cut -c1-200)"
    fi
done
log "device modules built: ${built[*]}"
log "device modules failed: ${failed[*]}"

out=$("$PREFIX/bin/wrspice" -v 2>&1 < /dev/null || true)
echo "$out"
{ grep -m1 -o "WRspice.*release [^,]*" <<< "$out" || echo "WRspice $VERSION"; echo "source: $URL tag $TAG"; } > "$PREFIX/version"
finish wrspice "$VERSION" "$PREFIX" libgsl27 libncurses6 libtiff6 libjpeg8

export PATH="$PREFIX/bin:$PATH"
smoke wrspice_examples_jjexamples wrspice -b jjdc.cir
d=$(mktemp -d)
cp "$REPO/cases/wrspice_devlib_adms_examples_cap_tests/test.sp" "$d"
smoke "$d" wrspice -m "$MODULES/adms/cap.so" -b test.sp
d=$(mktemp -d)
printf 'broken netlist\nv1 1 0 1\nr1 1 0 undefined_param_xyz\nq1 1 0 0 nomodel\n.op\n.end\n' > "$d/bad.cir"
smoke "$d" wrspice -b bad.cir
