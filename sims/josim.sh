# JoSIM: the newest release's Linux binary (built on glibc 2.12, runs anywhere).
# RELEASE_TAG=v3.1.0 installs that release instead of the newest.
. "$(dirname "$0")/common.sh"

REPO_GH=JoeyDelp/JoSIM
TAG=${RELEASE_TAG:-$(github_latest $REPO_GH)}
VERSION=${TAG#v}
log "JoSIM $TAG"

d=$(mktemp -d)
retry curl -fsSL -o "$d/josim.tar.gz" \
    "https://github.com/$REPO_GH/releases/download/$TAG/JoSIM-$TAG-linux-x64-rhel6.tar.gz"
tar xzf "$d/josim.tar.gz" -C "$d"

PREFIX=$(prefix_for josim "$VERSION")
install -m 755 "$d/bin/josim-cli" "$PREFIX/bin/josim-cli"
ln -sfn josim-cli "$PREFIX/bin/josim"
ldd "$PREFIX/bin/josim-cli" || true

out=$("$PREFIX/bin/josim-cli" -v 2>&1 || true)
echo "$out"
{ echo "JoSIM $(grep -m1 '^v[0-9]' <<< "$out")"
  echo "source: https://github.com/$REPO_GH/releases/tag/$TAG"; } > "$PREFIX/version"
finish josim "$VERSION" "$PREFIX"

export PATH="$PREFIX/bin:$PATH"
smoke josim_test josim-cli -o out.csv ex_jtl_basic.cir
smoke josim_test_comp josim-cli -o out.csv jj.cir
d=$(mktemp -d)
printf '* broken\nB01 1 0 nomodel area=1\nL01 1 2 undefined_value\nXQ 2 0 nosubckt\n.tran 0.25p 100p\n.print DEVV L01\n.end\n' > "$d/bad.cir"
smoke "$d" josim-cli -o out.csv bad.cir
