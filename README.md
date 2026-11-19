# Circuit Reference Suite

Circuit netlists with every device model they need, for benchmarking circuit
simulators against each other under the same conditions. A circuit
(`circuits/<name>.toml`) states what is computed, independent of any simulator;
adapters write it in each simulator's dialect. Upstream files are committed byte
for byte and hash-checked. License per case and library.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="plots/accuracy-dark.png">
  <img alt="Analyses within an error of the reference, per simulator and precision level" src="plots/accuracy.png">
</picture>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="plots/time-dark.png">
  <img alt="Analyses within a wall time of the fastest simulator" src="plots/time.png">
</picture>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="plots/work-dark.png">
  <img alt="Error against wall time of every run, per simulator" src="plots/work.png">
</picture>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="plots/references-dark.png">
  <img alt="Analyses per type and reference status" src="plots/references.png">
</picture>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="plots/status-dark.png">
  <img alt="Runs per simulator and status" src="plots/status.png">
</picture>

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
