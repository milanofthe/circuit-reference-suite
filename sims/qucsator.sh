# qucsator_rf: newest release of github ra3xdh/qucsator_rf, built with CMake.
# RELEASE_TAG=1.0.7 builds that release instead of the newest.
. "$(dirname "$0")/common.sh"

REPO_GH=ra3xdh/qucsator_rf
TAG=${RELEASE_TAG:-$(github_latest $REPO_GH)}
VERSION=${TAG#v}
log "qucsator_rf $TAG"

apt_install make cmake flex bison gperf dos2unix
cd "$SRC"
rm -rf qucsator && mkdir qucsator
retry curl -fsSL -o qucsator.tar.gz "https://github.com/$REPO_GH/archive/refs/tags/$TAG.tar.gz"
tar xzf qucsator.tar.gz -C qucsator --strip-components=1
cd qucsator

PREFIX=$(prefix_for qucsator "$VERSION")
quiet cmake -S . -B build -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX="$PREFIX"
quiet cmake --build build -j"$JOBS"
quiet cmake --install build
ls "$PREFIX/bin"
test -x "$PREFIX/bin/qucsator_rf"

out=$("$PREFIX/bin/qucsator_rf" -v 2>&1 || true)
echo "$out"
{ head -n 1 <<< "$out"; echo "source: https://github.com/$REPO_GH/releases/tag/$TAG"; } > "$PREFIX/version"
finish qucsator "$VERSION" "$PREFIX"

export PATH="$PREFIX/bin:$PATH"
smoke qucsator_tests_basic_components_capacitor qucsator_rf -i capacitor@dc.net -o capacitor@dc.dat
smoke qucsator_tests_basic_u_ri qucsator_rf -i u=ri@ac.net -o u=ri@ac.dat
d=$(mktemp -d)
printf 'Vdc:V1 _net0 gnd U="1 V"\n.DC:DC1 Temp="26.85"\nR:R1 _net0 _net1 R="1 Ohm" Undefined="3"\nXYZ:Q1 _net1 gnd\n' > "$d/bad.net"
smoke "$d" qucsator_rf -i bad.net -o bad.dat
printf 'Vdc:V1 _net0 gnd U="1 V"\n.DC:DC1 Temp="26.85"\nR:R1 _net0 gnd R="1 Ohm"\nEqn:Eqn1 assertV="assert(1 > 2)" Export="yes"\n' > "$d/bad.net"
smoke "$d" qucsator_rf -i bad.net -o bad.dat
