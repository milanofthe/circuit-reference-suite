# ahkab: github ahkab/ahkab master (the last release, 0.18, is from 2015; master from 2019)
# in a venv inside the prefix, on a Python and numpy/scipy/sympy of its time, with a
# uv-managed interpreter kept in the prefix too. bin/ahkab runs `python -m ahkab`.
# COMMIT=<sha> installs that commit instead of master.
. "$(dirname "$0")/common.sh"

GH=https://github.com/ahkab/ahkab
COMMIT=${COMMIT:-$(retry git ls-remote $GH refs/heads/master | cut -f1)}
UPSTREAM=$(curl -fsSL "https://raw.githubusercontent.com/ahkab/ahkab/$COMMIT/ahkab/__version__.py" \
    | grep -o "[0-9][0-9.]*")
VERSION=$UPSTREAM-g${COMMIT:0:7}
log "ahkab $VERSION"

# the newest of each package that still has the APIs ahkab uses (np.float, np.int, ...)
PYTHON=3.9
PINS=(numpy==1.21.6 scipy==1.7.3 sympy==1.9 tabulate==0.8.10 matplotlib==3.5.3)

PREFIX=$(prefix_for ahkab "$VERSION")
export UV_PYTHON_INSTALL_DIR=$PREFIX/python UV_CACHE_DIR=$SRC/uv-cache
uv venv --python "$PYTHON" "$PREFIX/venv"
uv pip install --python "$PREFIX/venv/bin/python" "${PINS[@]}" "ahkab @ git+$GH@$COMMIT"
cat > "$PREFIX/bin/ahkab" <<EOF
#!/bin/sh
# ahkab $VERSION; plots go to the non-interactive backend
MPLBACKEND=\${MPLBACKEND:-Agg} exec "$PREFIX/venv/bin/python" -m ahkab "\$@"
EOF
chmod +x "$PREFIX/bin/ahkab"

out=$("$PREFIX/bin/ahkab" --version 2>/dev/null || true)
echo "$out"
{ echo "ahkab $UPSTREAM ($(head -n 1 <<< "$out")) commit $COMMIT, Python $PYTHON, ${PINS[*]}"
  echo "source: $GH/commit/$COMMIT"; } > "$PREFIX/version"
finish ahkab "$VERSION" "$PREFIX"

export PATH="$PREFIX/bin:$PATH"
smoke ahkab_tests_ohms_law ahkab -o out ohms_law.ckt
smoke ahkab_tests_tran_trap ahkab -o out tran_trap.ckt
d=$(mktemp -d)
printf 'broken netlist\nv1 1 0 type=vdc vdc=1\nr1 1 0 undefined_value\nq1 1 0 0 nomodel\n.op\n.end\n' > "$d/bad.ckt"
smoke "$d" ahkab -o out bad.ckt
