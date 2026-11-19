# Circuit Reference Suite

Circuit netlists with every device model they need, for benchmarking circuit
simulators against each other under the same conditions. A circuit
(`circuits/<name>.toml`) states what is computed, independent of any simulator;
adapters write it in each simulator's dialect. Upstream files are committed byte
for byte and hash-checked. License per case and library.

![Analyses within an error of the reference, per simulator and precision level](plots/accuracy.png)

![Analyses within a wall time of the fastest simulator](plots/time.png)

![Error against wall time of every run, per simulator](plots/work.png)

![Analyses per type and reference status](plots/references.png)

![Runs per simulator and status](plots/status.png)

## Layout

```
circuits/<name>.toml         a circuit: body netlist, analyses, signals, options
cases/<id>/case.toml         source, files with sha256, netlists and dialects, resolve table
libraries/<id>/library.toml  model libraries shared by cases (PDK models, Verilog-A)
sims/<simulator>.sh          builds a simulator, newest release (sims/common.sh)
bench.toml                   precision levels, comparison bounds, plot style
```

## Usage

```
pip install -e .
python -m circref check                  # schema, hashes, references, generated READMEs
python -m circref run --out OUT [circuit globs] [--sim S] [--level L]
python -m circref compare OUT            # OUT/compare.json, OUT/plots/
```
