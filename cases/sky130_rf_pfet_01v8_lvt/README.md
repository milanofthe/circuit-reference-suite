# SKY130 rf_pfet_01v8_lvt model checks

device | ngspice | status: **complete**

## Source

- Authors: SkyWater Technology Foundry, Google
- URL: https://github.com/fossi-foundation/skywater-pdk-libs-sky130_fd_pr (commit `16f93a795d87ea2b393fe5c74d32674e111e44a2`)
- Path: `cells/rf_pfet_01v8_lvt/tests`
- License: Apache-2.0

## Netlists

| file | dialect | analyses | devices | size | linear | portability | libraries |
|---|---|---|---|---|---|---|---|
| [`sky130_fd_pr__rf_pfet_01v8_lvt_aM02W3p00L0p35__pfet_vth.spice`](sky130_fd_pr__rf_pfet_01v8_lvt_aM02W3p00L0p35__pfet_vth.spice) | ngspice | dc, dc | 6 | tiny | no | specific (.control script) | [sky130_fd_pr](../../libraries/sky130_fd_pr) |
| [`sky130_fd_pr__rf_pfet_01v8_lvt_aM02W3p00L0p50__pfet_vth.spice`](sky130_fd_pr__rf_pfet_01v8_lvt_aM02W3p00L0p50__pfet_vth.spice) | ngspice | dc, dc | 6 | tiny | no | specific (.control script) | [sky130_fd_pr](../../libraries/sky130_fd_pr) |
| [`sky130_fd_pr__rf_pfet_01v8_lvt_aM02W5p00L0p35__pfet_vth.spice`](sky130_fd_pr__rf_pfet_01v8_lvt_aM02W5p00L0p35__pfet_vth.spice) | ngspice | dc, dc | 6 | tiny | no | specific (.control script) | [sky130_fd_pr](../../libraries/sky130_fd_pr) |
| [`sky130_fd_pr__rf_pfet_01v8_lvt_aM02W5p00L0p50__pfet_vth.spice`](sky130_fd_pr__rf_pfet_01v8_lvt_aM02W5p00L0p50__pfet_vth.spice) | ngspice | dc, dc | 6 | tiny | no | specific (.control script) | [sky130_fd_pr](../../libraries/sky130_fd_pr) |
| [`sky130_fd_pr__rf_pfet_01v8_lvt_aM04W3p00L0p35__pfet_vth.spice`](sky130_fd_pr__rf_pfet_01v8_lvt_aM04W3p00L0p35__pfet_vth.spice) | ngspice | dc, dc | 6 | tiny | no | specific (.control script) | [sky130_fd_pr](../../libraries/sky130_fd_pr) |
| [`sky130_fd_pr__rf_pfet_01v8_lvt_aM04W3p00L0p50__pfet_vth.spice`](sky130_fd_pr__rf_pfet_01v8_lvt_aM04W3p00L0p50__pfet_vth.spice) | ngspice | dc, dc | 6 | tiny | no | specific (.control script) | [sky130_fd_pr](../../libraries/sky130_fd_pr) |
| [`sky130_fd_pr__rf_pfet_01v8_lvt_aM04W5p00L0p35__pfet_vth.spice`](sky130_fd_pr__rf_pfet_01v8_lvt_aM04W5p00L0p35__pfet_vth.spice) | ngspice | dc, dc | 6 | tiny | no | specific (.control script) | [sky130_fd_pr](../../libraries/sky130_fd_pr) |
| [`sky130_fd_pr__rf_pfet_01v8_lvt_aM04W5p00L0p50__pfet_vth.spice`](sky130_fd_pr__rf_pfet_01v8_lvt_aM04W5p00L0p50__pfet_vth.spice) | ngspice | dc, dc | 6 | tiny | no | specific (.control script) | [sky130_fd_pr](../../libraries/sky130_fd_pr) |

Devices: instances once the subcircuits defined in this case are expanded; a device from a library or a compiled model counts once. Size, linear and portability: see the top README.

## External references

| as written | resolves to | netlists |
|---|---|---|
| `../../../models/sky130.lib.spice` | [libraries/sky130_fd_pr/models/sky130.lib.spice](../../libraries/sky130_fd_pr/models/sky130.lib.spice) | 8 |
| `../sky130_fd_pr__rf_pfet_01v8_lvt_aM02W3p00L0p35.spice` | [libraries/sky130_fd_pr/cells/rf_pfet_01v8_lvt/sky130_fd_pr__rf_pfet_01v8_lvt_aM02W3p00L0p35.spice](../../libraries/sky130_fd_pr/cells/rf_pfet_01v8_lvt/sky130_fd_pr__rf_pfet_01v8_lvt_aM02W3p00L0p35.spice) | 1 |
| `../sky130_fd_pr__rf_pfet_01v8_lvt_aM02W3p00L0p50.spice` | [libraries/sky130_fd_pr/cells/rf_pfet_01v8_lvt/sky130_fd_pr__rf_pfet_01v8_lvt_aM02W3p00L0p50.spice](../../libraries/sky130_fd_pr/cells/rf_pfet_01v8_lvt/sky130_fd_pr__rf_pfet_01v8_lvt_aM02W3p00L0p50.spice) | 1 |
| `../sky130_fd_pr__rf_pfet_01v8_lvt_aM02W5p00L0p35.spice` | [libraries/sky130_fd_pr/cells/rf_pfet_01v8_lvt/sky130_fd_pr__rf_pfet_01v8_lvt_aM02W5p00L0p35.spice](../../libraries/sky130_fd_pr/cells/rf_pfet_01v8_lvt/sky130_fd_pr__rf_pfet_01v8_lvt_aM02W5p00L0p35.spice) | 1 |
| `../sky130_fd_pr__rf_pfet_01v8_lvt_aM02W5p00L0p50.spice` | [libraries/sky130_fd_pr/cells/rf_pfet_01v8_lvt/sky130_fd_pr__rf_pfet_01v8_lvt_aM02W5p00L0p50.spice](../../libraries/sky130_fd_pr/cells/rf_pfet_01v8_lvt/sky130_fd_pr__rf_pfet_01v8_lvt_aM02W5p00L0p50.spice) | 1 |
| `../sky130_fd_pr__rf_pfet_01v8_lvt_aM04W3p00L0p35.spice` | [libraries/sky130_fd_pr/cells/rf_pfet_01v8_lvt/sky130_fd_pr__rf_pfet_01v8_lvt_aM04W3p00L0p35.spice](../../libraries/sky130_fd_pr/cells/rf_pfet_01v8_lvt/sky130_fd_pr__rf_pfet_01v8_lvt_aM04W3p00L0p35.spice) | 1 |
| `../sky130_fd_pr__rf_pfet_01v8_lvt_aM04W3p00L0p50.spice` | [libraries/sky130_fd_pr/cells/rf_pfet_01v8_lvt/sky130_fd_pr__rf_pfet_01v8_lvt_aM04W3p00L0p50.spice](../../libraries/sky130_fd_pr/cells/rf_pfet_01v8_lvt/sky130_fd_pr__rf_pfet_01v8_lvt_aM04W3p00L0p50.spice) | 1 |
| `../sky130_fd_pr__rf_pfet_01v8_lvt_aM04W5p00L0p35.spice` | [libraries/sky130_fd_pr/cells/rf_pfet_01v8_lvt/sky130_fd_pr__rf_pfet_01v8_lvt_aM04W5p00L0p35.spice](../../libraries/sky130_fd_pr/cells/rf_pfet_01v8_lvt/sky130_fd_pr__rf_pfet_01v8_lvt_aM04W5p00L0p35.spice) | 1 |
| `../sky130_fd_pr__rf_pfet_01v8_lvt_aM04W5p00L0p50.spice` | [libraries/sky130_fd_pr/cells/rf_pfet_01v8_lvt/sky130_fd_pr__rf_pfet_01v8_lvt_aM04W5p00L0p50.spice](../../libraries/sky130_fd_pr/cells/rf_pfet_01v8_lvt/sky130_fd_pr__rf_pfet_01v8_lvt_aM04W5p00L0p50.spice) | 1 |

Generated by `python -m circref build`. Do not edit by hand.
