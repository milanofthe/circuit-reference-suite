# Sourced by the job that runs the suite: every current simulator install on PATH, its
# runtime packages installed. Layout in sims/common.sh.

SIMS=${SIMS:-/cache/circsims}
_pkgs=$(cat "$SIMS"/*/current/runtime-apt 2>/dev/null | sort -u | grep -v '^$' || true)
if [ -n "$_pkgs" ]; then
    export DEBIAN_FRONTEND=noninteractive
    apt-get update -qq && apt-get install -y -qq --no-install-recommends $_pkgs >/dev/null
fi
for _d in "$SIMS"/*/current; do
    [ -d "$_d/bin" ] && PATH="$_d/bin:$PATH"
    [ -d "$_d/lib" ] && LD_LIBRARY_PATH="$_d/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
    [ -d "$_d/python" ] && PYTHONPATH="$_d/python${PYTHONPATH:+:$PYTHONPATH}"
done
export PATH LD_LIBRARY_PATH PYTHONPATH SIMS
unset _d _pkgs
