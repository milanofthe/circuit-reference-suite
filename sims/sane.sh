# SANE from a local sane-dev checkout: the job ships that checkout, not this repository,
# so this script is passed as the command (sane-dev is private; nothing to clone).
#
#   cd ../sane-dev && falllow run --machine milan-box-01 --cache circsims --cpu 12 --memory 16G \
#       -e REV=$(git rev-parse --short HEAD) \
#       -- bash -c "$(cat ../circuit-reference-suite/sims/common.sh ../circuit-reference-suite/sims/sane.sh)"
#
# common.sh changes into $SRC; the shipped checkout is /workspace.
# Installs the Python module into $SIMS/sane/<rev>/python; sims/sane/run.py in this
# repository runs a deck on it.

: "${REV:?the sane-dev revision, from git rev-parse --short HEAD}"
log "sane $REV: build"
pip install -q maturin numpy
maturin build --release -m /workspace/crates/py/Cargo.toml -o "$SRC/wheels" 2>&1 | grep -vE "^\s+(Compiling|Downloaded|Downloading)" || true
prefix=$(prefix_for sane "$REV")
pip install -q --no-deps --target "$prefix/python" "$SRC"/wheels/*.whl
echo "sane-dev $REV" > "$prefix/version"
PYTHONPATH="$prefix/python" python3 -c "import sane; m = sane.Model.from_netlist('V1 a 0 1\nR1 a b 1k\nR2 b 0 1k\n'); print('smoke: v(b) =', m.at().operating_point()['b'])"
finish sane "$REV" "$prefix"
