# SKY130 esd_rf_diode_pw2nd_11v0 model checks

device | ngspice | status: **complete**

## Source

- Authors: SkyWater Technology Foundry, Google
- URL: https://github.com/fossi-foundation/skywater-pdk-libs-sky130_fd_pr (commit `16f93a795d87ea2b393fe5c74d32674e111e44a2`)
- Path: `cells/esd_rf_diode_pw2nd_11v0/tests`
- License: Apache-2.0

## Netlists

| file | dialect | analyses | devices | libraries |
|---|---|---|---|---|
| [`sky130_fd_pr__esd_rf_diode_pw2nd_11v0_100__diode_vth.spice`](sky130_fd_pr__esd_rf_diode_pw2nd_11v0_100__diode_vth.spice) | ngspice | dc | 4 | [sky130_fd_pr](../../libraries/sky130_fd_pr) |
| [`sky130_fd_pr__esd_rf_diode_pw2nd_11v0_100__parasitic__diode_pw2dn__diode_vth.spice`](sky130_fd_pr__esd_rf_diode_pw2nd_11v0_100__parasitic__diode_pw2dn__diode_vth.spice) | ngspice | dc | 4 | [sky130_fd_pr](../../libraries/sky130_fd_pr) |
| [`sky130_fd_pr__esd_rf_diode_pw2nd_11v0_200__diode_vth.spice`](sky130_fd_pr__esd_rf_diode_pw2nd_11v0_200__diode_vth.spice) | ngspice | dc | 4 | [sky130_fd_pr](../../libraries/sky130_fd_pr) |
| [`sky130_fd_pr__esd_rf_diode_pw2nd_11v0_200__parasitic__diode_pw2dn__diode_vth.spice`](sky130_fd_pr__esd_rf_diode_pw2nd_11v0_200__parasitic__diode_pw2dn__diode_vth.spice) | ngspice | dc | 4 | [sky130_fd_pr](../../libraries/sky130_fd_pr) |
| [`sky130_fd_pr__esd_rf_diode_pw2nd_11v0_300__diode_vth.spice`](sky130_fd_pr__esd_rf_diode_pw2nd_11v0_300__diode_vth.spice) | ngspice | dc | 4 | [sky130_fd_pr](../../libraries/sky130_fd_pr) |
| [`sky130_fd_pr__esd_rf_diode_pw2nd_11v0_300__parasitic__diode_pw2dn__diode_vth.spice`](sky130_fd_pr__esd_rf_diode_pw2nd_11v0_300__parasitic__diode_pw2dn__diode_vth.spice) | ngspice | dc | 4 | [sky130_fd_pr](../../libraries/sky130_fd_pr) |

Devices: instances once the subcircuits defined in this case are expanded; a device from a library or a compiled model counts once.

## External references

| in | as written | resolves to |
|---|---|---|
| `sky130_fd_pr__esd_rf_diode_pw2nd_11v0_100__diode_vth.spice` | `../../../models/sky130.lib.spice` | [libraries/sky130_fd_pr/models/sky130.lib.spice](../../libraries/sky130_fd_pr/models/sky130.lib.spice) |
| `sky130_fd_pr__esd_rf_diode_pw2nd_11v0_100__diode_vth.spice` | `../../../models/sky130_fd_pr__model__diode_pw2nd_11v0.model.spice` | [libraries/sky130_fd_pr/models/sky130_fd_pr__model__diode_pw2nd_11v0.model.spice](../../libraries/sky130_fd_pr/models/sky130_fd_pr__model__diode_pw2nd_11v0.model.spice) |
| `sky130_fd_pr__esd_rf_diode_pw2nd_11v0_100__parasitic__diode_pw2dn__diode_vth.spice` | `../../../models/parasitics/sky130_fd_pr__model__parasitic__diodes_pw2dn.model.spice` | [libraries/sky130_fd_pr/models/parasitics/sky130_fd_pr__model__parasitic__diodes_pw2dn.model.spice](../../libraries/sky130_fd_pr/models/parasitics/sky130_fd_pr__model__parasitic__diodes_pw2dn.model.spice) |
| `sky130_fd_pr__esd_rf_diode_pw2nd_11v0_100__parasitic__diode_pw2dn__diode_vth.spice` | `../../../models/sky130.lib.spice` | [libraries/sky130_fd_pr/models/sky130.lib.spice](../../libraries/sky130_fd_pr/models/sky130.lib.spice) |
| `sky130_fd_pr__esd_rf_diode_pw2nd_11v0_200__diode_vth.spice` | `../../../models/sky130.lib.spice` | [libraries/sky130_fd_pr/models/sky130.lib.spice](../../libraries/sky130_fd_pr/models/sky130.lib.spice) |
| `sky130_fd_pr__esd_rf_diode_pw2nd_11v0_200__diode_vth.spice` | `../../../models/sky130_fd_pr__model__diode_pw2nd_11v0.model.spice` | [libraries/sky130_fd_pr/models/sky130_fd_pr__model__diode_pw2nd_11v0.model.spice](../../libraries/sky130_fd_pr/models/sky130_fd_pr__model__diode_pw2nd_11v0.model.spice) |
| `sky130_fd_pr__esd_rf_diode_pw2nd_11v0_200__parasitic__diode_pw2dn__diode_vth.spice` | `../../../models/parasitics/sky130_fd_pr__model__parasitic__diodes_pw2dn.model.spice` | [libraries/sky130_fd_pr/models/parasitics/sky130_fd_pr__model__parasitic__diodes_pw2dn.model.spice](../../libraries/sky130_fd_pr/models/parasitics/sky130_fd_pr__model__parasitic__diodes_pw2dn.model.spice) |
| `sky130_fd_pr__esd_rf_diode_pw2nd_11v0_200__parasitic__diode_pw2dn__diode_vth.spice` | `../../../models/sky130.lib.spice` | [libraries/sky130_fd_pr/models/sky130.lib.spice](../../libraries/sky130_fd_pr/models/sky130.lib.spice) |
| `sky130_fd_pr__esd_rf_diode_pw2nd_11v0_300__diode_vth.spice` | `../../../models/sky130.lib.spice` | [libraries/sky130_fd_pr/models/sky130.lib.spice](../../libraries/sky130_fd_pr/models/sky130.lib.spice) |
| `sky130_fd_pr__esd_rf_diode_pw2nd_11v0_300__diode_vth.spice` | `../../../models/sky130_fd_pr__model__diode_pw2nd_11v0.model.spice` | [libraries/sky130_fd_pr/models/sky130_fd_pr__model__diode_pw2nd_11v0.model.spice](../../libraries/sky130_fd_pr/models/sky130_fd_pr__model__diode_pw2nd_11v0.model.spice) |
| `sky130_fd_pr__esd_rf_diode_pw2nd_11v0_300__parasitic__diode_pw2dn__diode_vth.spice` | `../../../models/parasitics/sky130_fd_pr__model__parasitic__diodes_pw2dn.model.spice` | [libraries/sky130_fd_pr/models/parasitics/sky130_fd_pr__model__parasitic__diodes_pw2dn.model.spice](../../libraries/sky130_fd_pr/models/parasitics/sky130_fd_pr__model__parasitic__diodes_pw2dn.model.spice) |
| `sky130_fd_pr__esd_rf_diode_pw2nd_11v0_300__parasitic__diode_pw2dn__diode_vth.spice` | `../../../models/sky130.lib.spice` | [libraries/sky130_fd_pr/models/sky130.lib.spice](../../libraries/sky130_fd_pr/models/sky130.lib.spice) |

Generated by `python -m circref build`. Do not edit by hand.
