# OpenVAF-reloaded: the newest release's Linux binary, Verilog-A to OSDI for ngspice and
# VACASK. Installed as openvaf-r (the name VACASK looks for) and openvaf.
# RELEASE_TAG=v24.0.2mob installs that release instead of the newest.
. "$(dirname "$0")/common.sh"

REPO_GH=OpenVAF/OpenVAF-Reloaded
TAG=${RELEASE_TAG:-$(github_latest $REPO_GH)}
VERSION=${TAG#v}
log "openvaf-r $TAG"

d=$(mktemp -d)
retry curl -fsSL -o "$d/openvaf.tar.gz" \
    "https://github.com/$REPO_GH/releases/download/$TAG/openvaf-r-$TAG-linux-x86_64.tar.gz"
tar xzf "$d/openvaf.tar.gz" -C "$d"
bin=$(find "$d" -type f -name 'openvaf-r' | head -n 1)
test -n "$bin"

PREFIX=$(prefix_for openvaf "$VERSION")
install -m 755 "$bin" "$PREFIX/bin/openvaf-r"
ln -s openvaf-r "$PREFIX/bin/openvaf"
# the binary links LLVM dynamically
apt_install libllvm18
ldd "$PREFIX/bin/openvaf-r"

# --version reports "unknown" in the release build, so the tag is the version
"$PREFIX/bin/openvaf-r" --version
{ echo "OpenVAF-reloaded $TAG"; echo "source: https://github.com/$REPO_GH/releases/tag/$TAG"; } > "$PREFIX/version"
finish openvaf "$VERSION" "$PREFIX" libllvm18

export PATH="$PREFIX/bin:$PATH"
smoke "$REPO/libraries/vacask_spice_va" openvaf-r resistor.va -o resistor.osdi
d=$(mktemp -d)
printf '`include "disciplines.vams"\nmodule broken(a, b);\ninout a, b;\nelectrical a, b;\nanalog begin\nI(a,b) <+ V(a,b) / undefined_r\nend\nendmodule\n' > "$d/broken.va"
smoke "$d" openvaf-r broken.va -o broken.osdi

# OSDI round trip in ngspice, if ngspice is installed
if [ -x "$SIMS/ngspice/current/bin/ngspice" ]; then
    # shellcheck disable=SC2046
    apt_install $(cat "$SIMS/ngspice/current/runtime-apt")
    d=$(mktemp -d)
    cp "$REPO/libraries/vacask_spice_va/resistor.va" "$d"
    (cd "$d" && openvaf-r resistor.va -o resistor.osdi)
    printf 'osdi resistor\nv1 1 0 1\nnr1 1 0 res r=2k\n.model res sp_resistor\n.control\npre_osdi resistor.osdi\nop\nprint -v1#branch\n.endc\n.end\n' > "$d/osdi.cir"
    smoke "$d" "$SIMS/ngspice/current/bin/ngspice" -b osdi.cir
fi
