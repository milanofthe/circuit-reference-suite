# Xyce_Regression LEAD_CURRENTS

test | xyce | status: **complete**

## Source

- Authors: Sandia National Laboratories
- URL: https://github.com/Xyce/Xyce_Regression (commit `7bb7e98f0ed3a81a7d1cf1d10b68592107ed40b2`)
- Path: `Netlists/LEAD_CURRENTS`
- License: GPL-3.0-or-later

## Netlists

| file | dialect | analyses | devices | size | linear | portability | libraries |
|---|---|---|---|---|---|---|---|
| [`lead_bjt_gear.cir`](lead_bjt_gear.cir) | xyce | tran | 4 | tiny | no | core | - |
| [`lead_bjt_trap.cir`](lead_bjt_trap.cir) | xyce | tran | 4 | tiny | no | core | - |
| [`lead_bsim3_gear.cir`](lead_bsim3_gear.cir) | xyce | tran | 30 | small | no | core | - |
| [`lead_bsim3_trap.cir`](lead_bsim3_trap.cir) | xyce | tran | 30 | small | no | core | - |
| [`lead_bsim4_gear.cir`](lead_bsim4_gear.cir) | xyce | tran | 30 | small | no | core | - |
| [`lead_bsim4_trap.cir`](lead_bsim4_trap.cir) | xyce | tran | 30 | small | no | core | - |
| [`lead_bsrc_ac.cir`](lead_bsrc_ac.cir) | xyce | op, ac | 10 | small | no | core | - |
| [`lead_bsrc_gear.cir`](lead_bsrc_gear.cir) | xyce | tran | 4 | tiny | no | core | - |
| [`lead_bsrc_trap.cir`](lead_bsrc_trap.cir) | xyce | tran | 4 | tiny | no | core | - |
| [`lead_dio1_gear.cir`](lead_dio1_gear.cir) | xyce | tran | 4 | tiny | no | core | - |
| [`lead_dio1_m2_gear.cir`](lead_dio1_m2_gear.cir) | xyce | tran | 4 | tiny | no | core | - |
| [`lead_dio1_m2_trap.cir`](lead_dio1_m2_trap.cir) | xyce | tran | 4 | tiny | no | core | - |
| [`lead_dio1_trap.cir`](lead_dio1_trap.cir) | xyce | tran | 4 | tiny | no | core | - |
| [`lead_ind_gear.cir`](lead_ind_gear.cir) | xyce | tran | 3 | tiny | yes | core | - |
| [`lead_ind_noise.cir`](lead_ind_noise.cir) | xyce | op, noise | 7 | tiny | yes | specific (analysis noise) | - |
| [`lead_ind_trap.cir`](lead_ind_trap.cir) | xyce | tran | 3 | tiny | yes | core | - |
| [`lead_mil_gear.cir`](lead_mil_gear.cir) | xyce | tran | 16 | small | yes | core | - |
| [`lead_mil_trap.cir`](lead_mil_trap.cir) | xyce | tran | 16 | small | yes | core | - |
| [`lead_min2_gear.cir`](lead_min2_gear.cir) | xyce | tran | 11 | small | yes | core | - |
| [`lead_min2_trap.cir`](lead_min2_trap.cir) | xyce | tran | 11 | small | yes | core | - |
| [`lead_min_ac.cir`](lead_min_ac.cir) | xyce | op, ac | 8 | tiny | yes | core | - |
| [`lead_min_gear.cir`](lead_min_gear.cir) | xyce | tran | 11 | small | yes | core | - |
| [`lead_min_trap.cir`](lead_min_trap.cir) | xyce | tran | 11 | small | yes | core | - |
| [`lead_njfet_gear.cir`](lead_njfet_gear.cir) | xyce | tran | 6 | tiny | no | core | - |
| [`lead_njfet_trap.cir`](lead_njfet_trap.cir) | xyce | tran | 6 | tiny | no | core | - |
| [`lead_nmes_gear.cir`](lead_nmes_gear.cir) | xyce | tran | 4 | tiny | no | core | - |
| [`lead_nmes_trap.cir`](lead_nmes_trap.cir) | xyce | tran | 4 | tiny | no | core | - |
| [`lead_nmos1_gear.cir`](lead_nmos1_gear.cir) | xyce | tran | 7 | tiny | no | core | - |
| [`lead_nmos1_trap.cir`](lead_nmos1_trap.cir) | xyce | tran | 7 | tiny | no | core | - |
| [`lead_nmos3_gear.cir`](lead_nmos3_gear.cir) | xyce | tran | 7 | tiny | no | core | - |
| [`lead_nmos3_trap.cir`](lead_nmos3_trap.cir) | xyce | tran | 7 | tiny | no | core | - |
| [`lead_nsoi_gear.cir`](lead_nsoi_gear.cir) | xyce | tran | 14 | small | no | core | - |
| [`lead_nsoi_trap.cir`](lead_nsoi_trap.cir) | xyce | tran | 14 | small | no | core | - |
| [`lead_pde_2d.cir`](lead_pde_2d.cir) | xyce | dc | 8 | tiny | no | specific (Xyce device (Y or digital U)) | - |
| [`lead_pde_2d2.cir`](lead_pde_2d2.cir) | xyce | dc | 10 | small | no | specific (Xyce device (Y or digital U)) | - |
| [`lead_pde_dio.cir`](lead_pde_dio.cir) | xyce | dc | 3 | tiny | no | specific (Xyce device (Y or digital U)) | - |
| [`lead_pjfet_tran_gear.cir`](lead_pjfet_tran_gear.cir) | xyce | tran | 10 | small | no | core | - |
| [`lead_pjfet_tran_trap.cir`](lead_pjfet_tran_trap.cir) | xyce | tran | 10 | small | no | core | - |
| [`lead_pmos1.cir`](lead_pmos1.cir) | xyce | dc | 9 | tiny | no | core | - |
| [`lead_psoi_gear.cir`](lead_psoi_gear.cir) | xyce | tran | 16 | small | no | core | - |
| [`lead_psoi_trap.cir`](lead_psoi_trap.cir) | xyce | tran | 16 | small | no | core | - |
| [`lead_r_c_gear.cir`](lead_r_c_gear.cir) | xyce | tran | 6 | tiny | yes | core | - |
| [`lead_r_c_trap.cir`](lead_r_c_trap.cir) | xyce | tran | 6 | tiny | yes | core | - |
| [`lead_sw_gear.cir`](lead_sw_gear.cir) | xyce | tran | 5 | tiny | no | core | - |
| [`lead_sw_trap.cir`](lead_sw_trap.cir) | xyce | tran | 5 | tiny | no | core | - |
| [`lead_tra_gear.cir`](lead_tra_gear.cir) | xyce | tran | 11 | small | yes | core | - |
| [`lead_tra_trap.cir`](lead_tra_trap.cir) | xyce | tran | 11 | small | yes | core | - |
| [`lead_vdmos_gear.cir`](lead_vdmos_gear.cir) | xyce | tran | 10 | small | no | core | - |
| [`lead_vdmos_trap.cir`](lead_vdmos_trap.cir) | xyce | tran | 10 | small | no | core | - |

Devices: instances once every subcircuit is expanded, those of libraries too; a compiled model counts once. Size, linear and portability: see the top README.

Generated by `python -m circref build`. Do not edit by hand.
