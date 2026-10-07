# IHP SG13G2 moshv model tests

device | ngspice | status: **complete**

## Source

- Authors: IHP GmbH
- URL: https://github.com/IHP-GmbH/IHP-Open-PDK (commit `5e6d592e4002946a4616f798c357f0f3c06cf3b6`)
- Path: `ihp-sg13g2/libs.tech/gnucap/tests/ngspice/moshv`
- License: Apache-2.0

## Netlists

| file | dialect | analyses | devices | size | linear | portability | libraries |
|---|---|---|---|---|---|---|---|
| [`tb_moshv_inv_ff.sp`](tb_moshv_inv_ff.sp) | ngspice | dc | 4 | tiny | no | specific (.control script, Verilog-A model) | [ihp_sg13g2](../../libraries/ihp_sg13g2) |
| [`tb_moshv_inv_ff_rf.sp`](tb_moshv_inv_ff_rf.sp) | ngspice | dc | 4 | tiny | no | specific (.control script, Verilog-A model) | [ihp_sg13g2](../../libraries/ihp_sg13g2) |
| [`tb_moshv_inv_fs.sp`](tb_moshv_inv_fs.sp) | ngspice | dc | 4 | tiny | no | specific (.control script, Verilog-A model) | [ihp_sg13g2](../../libraries/ihp_sg13g2) |
| [`tb_moshv_inv_fs_rf.sp`](tb_moshv_inv_fs_rf.sp) | ngspice | dc | 4 | tiny | no | specific (.control script, Verilog-A model) | [ihp_sg13g2](../../libraries/ihp_sg13g2) |
| [`tb_moshv_inv_sf.sp`](tb_moshv_inv_sf.sp) | ngspice | dc | 4 | tiny | no | specific (.control script, Verilog-A model) | [ihp_sg13g2](../../libraries/ihp_sg13g2) |
| [`tb_moshv_inv_sf_rf.sp`](tb_moshv_inv_sf_rf.sp) | ngspice | dc | 4 | tiny | no | specific (.control script, Verilog-A model) | [ihp_sg13g2](../../libraries/ihp_sg13g2) |
| [`tb_moshv_inv_ss.sp`](tb_moshv_inv_ss.sp) | ngspice | dc | 4 | tiny | no | specific (.control script, Verilog-A model) | [ihp_sg13g2](../../libraries/ihp_sg13g2) |
| [`tb_moshv_inv_ss_rf.sp`](tb_moshv_inv_ss_rf.sp) | ngspice | dc | 4 | tiny | no | specific (.control script, Verilog-A model) | [ihp_sg13g2](../../libraries/ihp_sg13g2) |
| [`tb_moshv_inv_tt.sp`](tb_moshv_inv_tt.sp) | ngspice | dc | 4 | tiny | no | specific (.control script, Verilog-A model) | [ihp_sg13g2](../../libraries/ihp_sg13g2) |
| [`tb_moshv_inv_tt_rf.sp`](tb_moshv_inv_tt_rf.sp) | ngspice | dc | 4 | tiny | no | specific (.control script, Verilog-A model) | [ihp_sg13g2](../../libraries/ihp_sg13g2) |
| [`tb_moshv_nmos_id_vd_ng1.sp`](tb_moshv_nmos_id_vd_ng1.sp) | ngspice | dc | 3 | tiny | no | specific (.control script, Verilog-A model) | [ihp_sg13g2](../../libraries/ihp_sg13g2) |
| [`tb_moshv_nmos_id_vd_ng1_rf.sp`](tb_moshv_nmos_id_vd_ng1_rf.sp) | ngspice | dc | 3 | tiny | no | specific (.control script, Verilog-A model) | [ihp_sg13g2](../../libraries/ihp_sg13g2) |
| [`tb_moshv_nmos_id_vd_ng2.sp`](tb_moshv_nmos_id_vd_ng2.sp) | ngspice | dc | 3 | tiny | no | specific (.control script, Verilog-A model) | [ihp_sg13g2](../../libraries/ihp_sg13g2) |
| [`tb_moshv_nmos_id_vd_ng2_rf.sp`](tb_moshv_nmos_id_vd_ng2_rf.sp) | ngspice | dc | 3 | tiny | no | specific (.control script, Verilog-A model) | [ihp_sg13g2](../../libraries/ihp_sg13g2) |
| [`tb_moshv_nmos_id_vd_ng3.sp`](tb_moshv_nmos_id_vd_ng3.sp) | ngspice | dc | 3 | tiny | no | specific (.control script, Verilog-A model) | [ihp_sg13g2](../../libraries/ihp_sg13g2) |
| [`tb_moshv_nmos_id_vd_ng3_rf.sp`](tb_moshv_nmos_id_vd_ng3_rf.sp) | ngspice | dc | 3 | tiny | no | specific (.control script, Verilog-A model) | [ihp_sg13g2](../../libraries/ihp_sg13g2) |
| [`tb_moshv_nmos_id_vd_ng4.sp`](tb_moshv_nmos_id_vd_ng4.sp) | ngspice | dc | 3 | tiny | no | specific (.control script, Verilog-A model) | [ihp_sg13g2](../../libraries/ihp_sg13g2) |
| [`tb_moshv_nmos_id_vd_ng4_rf.sp`](tb_moshv_nmos_id_vd_ng4_rf.sp) | ngspice | dc | 3 | tiny | no | specific (.control script, Verilog-A model) | [ihp_sg13g2](../../libraries/ihp_sg13g2) |
| [`tb_moshv_pmos_id_vd_ng1.sp`](tb_moshv_pmos_id_vd_ng1.sp) | ngspice | dc | 3 | tiny | no | specific (.control script, Verilog-A model) | [ihp_sg13g2](../../libraries/ihp_sg13g2) |
| [`tb_moshv_pmos_id_vd_ng1_rf.sp`](tb_moshv_pmos_id_vd_ng1_rf.sp) | ngspice | dc | 3 | tiny | no | specific (.control script, Verilog-A model) | [ihp_sg13g2](../../libraries/ihp_sg13g2) |
| [`tb_moshv_pmos_id_vd_ng2.sp`](tb_moshv_pmos_id_vd_ng2.sp) | ngspice | dc | 3 | tiny | no | specific (.control script, Verilog-A model) | [ihp_sg13g2](../../libraries/ihp_sg13g2) |
| [`tb_moshv_pmos_id_vd_ng2_rf.sp`](tb_moshv_pmos_id_vd_ng2_rf.sp) | ngspice | dc | 3 | tiny | no | specific (.control script, Verilog-A model) | [ihp_sg13g2](../../libraries/ihp_sg13g2) |
| [`tb_moshv_pmos_id_vd_ng3.sp`](tb_moshv_pmos_id_vd_ng3.sp) | ngspice | dc | 3 | tiny | no | specific (.control script, Verilog-A model) | [ihp_sg13g2](../../libraries/ihp_sg13g2) |
| [`tb_moshv_pmos_id_vd_ng3_rf.sp`](tb_moshv_pmos_id_vd_ng3_rf.sp) | ngspice | dc | 3 | tiny | no | specific (.control script, Verilog-A model) | [ihp_sg13g2](../../libraries/ihp_sg13g2) |
| [`tb_moshv_pmos_id_vd_ng4.sp`](tb_moshv_pmos_id_vd_ng4.sp) | ngspice | dc | 3 | tiny | no | specific (.control script, Verilog-A model) | [ihp_sg13g2](../../libraries/ihp_sg13g2) |
| [`tb_moshv_pmos_id_vd_ng4_rf.sp`](tb_moshv_pmos_id_vd_ng4_rf.sp) | ngspice | dc | 3 | tiny | no | specific (.control script, Verilog-A model) | [ihp_sg13g2](../../libraries/ihp_sg13g2) |

Devices: instances once the subcircuits defined in this case are expanded; a device from a library or a compiled model counts once. Size, linear and portability: see the top README.

## External references

| as written | resolves to | netlists |
|---|---|---|
| `cornerMOShv.lib` | [libraries/ihp_sg13g2/ihp-sg13g2/libs.tech/ngspice/models/cornerMOShv.lib](../../libraries/ihp_sg13g2/ihp-sg13g2/libs.tech/ngspice/models/cornerMOShv.lib) | 26 |
| `mosvar` | [libraries/ihp_sg13g2/ihp-sg13g2/libs.tech/verilog-a/mosvar/mosvar.va](../../libraries/ihp_sg13g2/ihp-sg13g2/libs.tech/verilog-a/mosvar/mosvar.va) | 26 |
| `psp103va` | [libraries/ihp_sg13g2/ihp-sg13g2/libs.tech/verilog-a/psp103/psp103.va](../../libraries/ihp_sg13g2/ihp-sg13g2/libs.tech/verilog-a/psp103/psp103.va) | 26 |
| `pspnqs103va` | [libraries/ihp_sg13g2/ihp-sg13g2/libs.tech/verilog-a/psp103/psp103_nqs.va](../../libraries/ihp_sg13g2/ihp-sg13g2/libs.tech/verilog-a/psp103/psp103_nqs.va) | 26 |

## Notes

IHP's ngspice model tests (`libs.tech/gnucap/tests/ngspice`). Upstream runs them with a
`.spiceinit` that puts `libs.tech/ngspice/models` on ngspice's `sourcepath` and loads the
PSP103, R3_CMC, MOSVAR and MOM capacitor models as OSDI; `resolve` does the same here.
Monte Carlo decks use fixed seeds.

Left out:
- `tb_moshv_mc_mm_ff.sp`: uses subcircuit sg13_hv_nmos, defined nowhere
- `tb_moshv_mc_mm_ff_rf.sp`: uses subcircuit sg13_hv_nmos, defined nowhere
- `tb_moshv_mc_mm_fs.sp`: uses subcircuit sg13_hv_nmos, defined nowhere
- `tb_moshv_mc_mm_fs_rf.sp`: uses subcircuit sg13_hv_nmos, defined nowhere
- `tb_moshv_mc_mm_sf.sp`: uses subcircuit sg13_hv_nmos, defined nowhere
- `tb_moshv_mc_mm_sf_rf.sp`: uses subcircuit sg13_hv_nmos, defined nowhere
- `tb_moshv_mc_mm_ss.sp`: uses subcircuit sg13_hv_nmos, defined nowhere
- `tb_moshv_mc_mm_ss_rf.sp`: uses subcircuit sg13_hv_nmos, defined nowhere
- `tb_moshv_mc_mm_tt.sp`: uses subcircuit sg13_hv_nmos, defined nowhere
- `tb_moshv_mc_mm_tt_rf.sp`: uses subcircuit sg13_hv_nmos, defined nowhere
- `tb_moshv_mc_stat.sp`: uses subcircuit sg13_hv_nmos, defined nowhere
- `tb_moshv_mc_stat_rf.sp`: uses subcircuit sg13_hv_nmos, defined nowhere

Generated by `python -m circref build`. Do not edit by hand.
