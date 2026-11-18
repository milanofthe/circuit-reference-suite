# VACASK: the newest release's Linux binary from codeberg (binary, its module and include
# directories with the precompiled .osdi devices). .va files are compiled with the
# OpenVAF-reloaded install (sims/openvaf.sh, run that first): VACASK looks for
# openvaf-r next to its own binary first, so bin/openvaf-r links to that install.
# RELEASE_TAG=_0.3.4 installs that release instead of the newest.
. "$(dirname "$0")/common.sh"

API=https://codeberg.org/api/v1/repos/arpadbuermen/VACASK
TAG=${RELEASE_TAG:-$(curl -fsSL "$API/releases?limit=20" | python3 -c '
import json, sys
print(next(r["tag_name"] for r in json.load(sys.stdin)
           if not r["prerelease"] and any(a["name"].endswith("_linux-x86_64.tar.gz") for a in r["assets"])))')}
VERSION=${TAG#_}
log "VACASK $TAG"
OPENVAF=$SIMS/openvaf/current/bin/openvaf-r
test -x "$OPENVAF" || { log "no OpenVAF-reloaded at $OPENVAF, run sims/openvaf.sh first"; exit 1; }

d=$(mktemp -d)
retry curl -fsSL -o "$d/vacask.tar.gz" \
    "https://codeberg.org/arpadbuermen/VACASK/releases/download/$TAG/vacask_${VERSION}_linux-x86_64.tar.gz"
tar xzf "$d/vacask.tar.gz" -C "$d" --strip-components=1
log "bundled OpenVAF: $("$d/bin/openvaf-r" --version 2>&1 | head -n 1 || true)"

PREFIX=$(prefix_for vacask "$VERSION")
install -m 755 "$d/bin/vacask" "$PREFIX/bin/vacask"
ln -s "$(readlink -f "$OPENVAF")" "$PREFIX/bin/openvaf-r"
mkdir -p "$PREFIX/lib"
cp -r "$d/lib/vacask" "$PREFIX/lib/"
RUNTIME=(libklu2 libopenblas0 libgomp1)
apt_install "${RUNTIME[@]}" "$(cat "$SIMS/openvaf/current/runtime-apt")"
ldd "$PREFIX/bin/vacask"
! ldd "$PREFIX/bin/vacask" | grep 'not found'

out=$("$PREFIX/bin/vacask" -dp 2>&1 || true)
echo "$out"
{ grep -m1 -i 'vacask' <<< "$out" || echo "VACASK $VERSION"
  echo "source: https://codeberg.org/arpadbuermen/VACASK/releases/tag/$TAG"; } > "$PREFIX/version"
finish vacask "$VERSION" "$PREFIX" "${RUNTIME[@]}"

export PATH="$PREFIX/bin:$PATH"
smoke vacask_rc/vacask vacask -sp runme.sim
# the same circuit with its devices compiled from Verilog-A by OpenVAF
d=$(mktemp -d)
cp "$REPO/libraries/vacask_va/resistor.va" "$REPO/libraries/vacask_va/capacitor.va" "$d"
sed -e 's|"spice/resistor.osdi"|"resistor.va"|; s|"spice/capacitor.osdi"|"capacitor.va"|' \
    -e 's|model r sp_resistor|model r resistor|; s|model c sp_capacitor|model c capacitor|' \
    -e 's|stop=1 |stop=10m |' "$REPO/cases/vacask_rc/vacask/runme.sim" > "$d/runme.sim"
grep -n 'load\|model' "$d/runme.sim"
smoke "$d" vacask -sp runme.sim
printf 'broken\nload "nonexistent.osdi"\nr1 (1 0) nomodel r=1k\ncontrol\n  analysis op1 op\nendc\n' > "$d/bad.sim"
smoke "$d" vacask -sp bad.sim
