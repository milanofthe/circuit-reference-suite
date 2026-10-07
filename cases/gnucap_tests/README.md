# gnucap tests

test | gnucap | status: **complete**

## Source

- Authors: Albert Davis, Felix Salfelder, gnucap contributors
- URL: https://git.savannah.gnu.org/cgit/gnucap.git (commit `a24393f48094cb475b62738d13efe21ef9805767`)
- Path: `tests`
- License: GPL-3.0-or-later

## Netlists

| file | dialect | analyses | devices | size | linear | portability | libraries |
|---|---|---|---|---|---|---|---|
| [`1lin.ckt`](1lin.ckt) | gnucap | op, dc | 5 | tiny | no | core | - |
| [`basic.ckt`](basic.ckt) | gnucap | op, op | 7 | tiny | yes | core | - |
| [`bm_complex.1.ckt`](bm_complex.1.ckt) | gnucap | ac, ac | 3 | tiny | yes | core | - |
| [`bm_complex.1a.ckt`](bm_complex.1a.ckt) | gnucap | op, ac, ac | 3 | tiny | yes | core | - |
| [`bm_complex.2.ckt`](bm_complex.2.ckt) | gnucap | ac, ac | 3 | tiny | yes | core | - |
| [`bm_complex.3.ckt`](bm_complex.3.ckt) | gnucap | ac, ac | 3 | tiny | yes | core | - |
| [`bm_complex.4.ckt`](bm_complex.4.ckt) | gnucap | ac, ac | 3 | tiny | yes | core | - |
| [`bm_cond.1.ckt`](bm_cond.1.ckt) | gnucap | dc, ac, dc | 3 | tiny | yes | core | - |
| [`bm_cond.2.ckt`](bm_cond.2.ckt) | gnucap | tran, ac | 5 | tiny | yes | core | - |
| [`bm_cond.3.ckt`](bm_cond.3.ckt) | gnucap | tran, ac | 5 | tiny | yes | core | - |
| [`bm_exp.1.ckt`](bm_exp.1.ckt) | gnucap | tran | 1 | tiny | yes | core | - |
| [`bm_exp.1p.ckt`](bm_exp.1p.ckt) | gnucap | tran | 1 | tiny | yes | core | - |
| [`bm_exp.2.ckt`](bm_exp.2.ckt) | gnucap | tran | 1 | tiny | yes | core | - |
| [`bm_exp.3.ckt`](bm_exp.3.ckt) | gnucap | tran | 1 | tiny | yes | core | - |
| [`bm_exp.3p.ckt`](bm_exp.3p.ckt) | gnucap | tran | 1 | tiny | yes | core | - |
| [`bm_exp.4p.ckt`](bm_exp.4p.ckt) | gnucap | tran, tran | 1 | tiny | yes | core | - |
| [`bm_exp.5p.ckt`](bm_exp.5p.ckt) | gnucap | tran, tran | 1 | tiny | yes | core | - |
| [`bm_fit.0.1.ckt`](bm_fit.0.1.ckt) | gnucap | op, dc, dc, dc | 7 | tiny | yes | core | - |
| [`bm_fit.1.1.ckt`](bm_fit.1.1.ckt) | gnucap | op, dc, dc, dc | 7 | tiny | yes | core | - |
| [`bm_fit.2.1.ckt`](bm_fit.2.1.ckt) | gnucap | op, dc | 7 | tiny | yes | core | - |
| [`bm_fit.2.2.ckt`](bm_fit.2.2.ckt) | gnucap | op, dc | 7 | tiny | yes | core | - |
| [`bm_fit.2.3.ckt`](bm_fit.2.3.ckt) | gnucap | op, dc | 7 | tiny | yes | core | - |
| [`bm_fit.2.4.ckt`](bm_fit.2.4.ckt) | gnucap | op, dc | 7 | tiny | yes | core | - |
| [`bm_fit.3.1.ckt`](bm_fit.3.1.ckt) | gnucap | op, dc, dc, dc | 5 | tiny | yes | core | - |
| [`bm_fit.3.2.ckt`](bm_fit.3.2.ckt) | gnucap | op, dc, dc, dc | 5 | tiny | yes | core | - |
| [`bm_fit.3.3.ckt`](bm_fit.3.3.ckt) | gnucap | tran | 1 | tiny | yes | core | - |
| [`bm_poly.1.ckt`](bm_poly.1.ckt) | gnucap | op, dc, dc, dc | 15 | small | no | core | - |
| [`bm_poly.2.ckt`](bm_poly.2.ckt) | gnucap | op, dc, dc, dc | 15 | small | no | core | - |
| [`bm_posy.1.ckt`](bm_posy.1.ckt) | gnucap | dc | 2 | tiny | yes | core | - |
| [`bm_pulse.1.ckt`](bm_pulse.1.ckt) | gnucap | tran | 5 | tiny | no | core | - |
| [`bm_pulse.1a.ckt`](bm_pulse.1a.ckt) | gnucap | tran | 5 | tiny | no | core | - |
| [`bm_pulse.2.ckt`](bm_pulse.2.ckt) | gnucap | tran | 5 | tiny | no | core | - |
| [`bm_pulse.2a.ckt`](bm_pulse.2a.ckt) | gnucap | tran | 5 | tiny | no | core | - |
| [`bm_pulse.3.ckt`](bm_pulse.3.ckt) | gnucap | tran | 5 | tiny | no | core | - |
| [`bm_pulse.3a.ckt`](bm_pulse.3a.ckt) | gnucap | tran | 5 | tiny | no | core | - |
| [`bm_pulse.4.ckt`](bm_pulse.4.ckt) | gnucap | tran | 1 | tiny | yes | core | - |
| [`bm_pulse.4a.ckt`](bm_pulse.4a.ckt) | gnucap | tran | 1 | tiny | yes | core | - |
| [`bm_pulse.4b.ckt`](bm_pulse.4b.ckt) | gnucap | tran | 2 | tiny | yes | core | - |
| [`bm_pwl.1.ckt`](bm_pwl.1.ckt) | gnucap | op, dc, dc, dc | 7 | tiny | yes | core | - |
| [`bm_pwl.2.ckt`](bm_pwl.2.ckt) | gnucap | op, dc, dc, dc | 5 | tiny | yes | core | - |
| [`bm_pwl.3.ckt`](bm_pwl.3.ckt) | gnucap | op, dc, tran | 3 | tiny | yes | core | - |
| [`bm_pwl.4.ckt`](bm_pwl.4.ckt) | gnucap | dc | 4 | tiny | yes | core | - |
| [`bm_pwl.5.ckt`](bm_pwl.5.ckt) | gnucap | tran | 1 | tiny | yes | core | - |
| [`bm_sffm.1.ckt`](bm_sffm.1.ckt) | gnucap | tran | 4 | tiny | yes | core | - |
| [`bm_sffm.2.ckt`](bm_sffm.2.ckt) | gnucap | tran | 3 | tiny | yes | core | - |
| [`bm_sffm.3.ckt`](bm_sffm.3.ckt) | gnucap | tran | 4 | tiny | yes | core | - |
| [`bm_sffm.4.ckt`](bm_sffm.4.ckt) | gnucap | tran | 4 | tiny | yes | core | - |
| [`bm_sffm.5.ckt`](bm_sffm.5.ckt) | gnucap | tran | 4 | tiny | yes | core | - |
| [`bm_sin.1.ckt`](bm_sin.1.ckt) | gnucap | tran | 2 | tiny | yes | core | - |
| [`bm_sin.2.ckt`](bm_sin.2.ckt) | gnucap | tran | 1 | tiny | yes | core | - |
| [`bm_sin.3.ckt`](bm_sin.3.ckt) | gnucap | tran | 1 | tiny | yes | core | - |
| [`bm_sin.4.ckt`](bm_sin.4.ckt) | gnucap | tran | 1 | tiny | yes | core | - |
| [`bm_sin.5.ckt`](bm_sin.5.ckt) | gnucap | tran | 1 | tiny | yes | core | - |
| [`bm_sin.6.ckt`](bm_sin.6.ckt) | gnucap | tran | 1 | tiny | yes | core | - |
| [`bm_sin.7.ckt`](bm_sin.7.ckt) | gnucap | tran | 1 | tiny | yes | core | - |
| [`bm_sin.8.ckt`](bm_sin.8.ckt) | gnucap | tran | 1 | tiny | yes | core | - |
| [`bm_sin.9.ckt`](bm_sin.9.ckt) | gnucap | tran | 1 | tiny | yes | core | - |
| [`bm_table.1.1.ckt`](bm_table.1.1.ckt) | gnucap | op, dc, dc, dc | 7 | tiny | yes | core | - |
| [`bm_table.2.1.ckt`](bm_table.2.1.ckt) | gnucap | op, dc | 7 | tiny | yes | core | - |
| [`bm_table.2.2.ckt`](bm_table.2.2.ckt) | gnucap | op, dc | 7 | tiny | yes | core | - |
| [`bm_table.2.3.ckt`](bm_table.2.3.ckt) | gnucap | op, dc | 7 | tiny | yes | core | - |
| [`bm_table.2.4.ckt`](bm_table.2.4.ckt) | gnucap | op, dc | 7 | tiny | yes | core | - |
| [`bm_table.3.1.ckt`](bm_table.3.1.ckt) | gnucap | op, dc, dc, dc | 5 | tiny | yes | core | - |
| [`bm_table.3.2.ckt`](bm_table.3.2.ckt) | gnucap | op, dc, dc, dc | 5 | tiny | yes | core | - |
| [`bm_table.3.3.ckt`](bm_table.3.3.ckt) | gnucap | tran | 1 | tiny | yes | core | - |
| [`bm_table.error1.ckt`](bm_table.error1.ckt) | gnucap | op | 1 | tiny | no | core | - |
| [`bm_tanh.1.ckt`](bm_tanh.1.ckt) | gnucap | dc, ac, dc, ac, dc, ac, dc, ac | 4 | tiny | yes | core | - |
| [`bm_tanh.2.ckt`](bm_tanh.2.ckt) | gnucap | dc, dc, dc, dc, dc, dc, dc, dc, dc, dc, dc, dc, dc, dc, dc, dc | 2 | tiny | yes | core | - |
| [`bmm_cap.1.ckt`](bmm_cap.1.ckt) | gnucap | op, tran, ac, ac | 3 | tiny | yes | core | - |
| [`bmm_cap.2.ckt`](bmm_cap.2.ckt) | gnucap | op, tran, ac, ac | 3 | tiny | yes | core | - |
| [`bmm_cap.3.ckt`](bmm_cap.3.ckt) | gnucap | op, tran, ac, ac | 3 | tiny | yes | core | - |
| [`bmm_cap.4.ckt`](bmm_cap.4.ckt) | gnucap | op, tran, ac, ac | 3 | tiny | yes | core | - |
| [`bmm_cap.5.ckt`](bmm_cap.5.ckt) | gnucap | op, tran, ac, ac | 3 | tiny | yes | core | - |
| [`bmm_res.1.ckt`](bmm_res.1.ckt) | gnucap | op, ac | 3 | tiny | yes | core | - |
| [`bmm_res.1p.ckt`](bmm_res.1p.ckt) | gnucap | op, ac | 3 | tiny | yes | core | - |
| [`bmm_res.2.ckt`](bmm_res.2.ckt) | gnucap | op, ac | 3 | tiny | yes | core | - |
| [`bmm_res.2p.ckt`](bmm_res.2p.ckt) | gnucap | op, ac | 3 | tiny | yes | core | - |
| [`bmm_res.3.ckt`](bmm_res.3.ckt) | gnucap | op, ac | 3 | tiny | yes | core | - |
| [`bmm_res.3p.ckt`](bmm_res.3p.ckt) | gnucap | op, ac | 3 | tiny | yes | core | - |
| [`bmm_res.4.ckt`](bmm_res.4.ckt) | gnucap | op, ac | 3 | tiny | yes | core | - |
| [`bmm_res.4p.ckt`](bmm_res.4p.ckt) | gnucap | op, ac | 3 | tiny | yes | core | - |
| [`bmm_res.5.ckt`](bmm_res.5.ckt) | gnucap | op, ac | 3 | tiny | yes | core | - |
| [`bmm_res.5p.ckt`](bmm_res.5p.ckt) | gnucap | op, ac | 3 | tiny | yes | core | - |
| [`c.ckt`](c.ckt) | gnucap | op | 14 | small | no | core | - |
| [`c_delete.2.ckt`](c_delete.2.ckt) | gnucap | op, op, op, op, op, op, op, op, op | 14 | small | no | core | - |
| [`c_delete.3.ckt`](c_delete.3.ckt) | gnucap | op, op, op | 14 | small | no | core | - |
| [`c_delete.4.ckt`](c_delete.4.ckt) | gnucap | op | 5 | tiny | yes | core | - |
| [`c_delete.5.ckt`](c_delete.5.ckt) | gnucap | op | 5 | tiny | yes | core | - |
| [`c_delete.6.ckt`](c_delete.6.ckt) | gnucap | op, op, op, op | 5 | tiny | yes | core | - |
| [`c_delete.7.ckt`](c_delete.7.ckt) | gnucap | op, op, op, op | 5 | tiny | yes | core | - |
| [`c_delete.ckt`](c_delete.ckt) | gnucap | op, op, op, op, op, op, op | 9 | tiny | yes | core | - |
| [`c_genrat.1.ckt`](c_genrat.1.ckt) | gnucap | op, tran, tran | 2 | tiny | yes | core | - |
| [`c_global.0.ckt`](c_global.0.ckt) | gnucap | op | 3 | tiny | yes | core | - |
| [`c_global.1.ckt`](c_global.1.ckt) | gnucap | op | 3 | tiny | yes | core | - |
| [`c_lib.1.ckt`](c_lib.1.ckt) | gnucap | op | 15 | small | yes | core | - |
| [`c_measure.1.ckt`](c_measure.1.ckt) | gnucap | tran | 5 | tiny | no | core | - |
| [`c_measure.1s.ckt`](c_measure.1s.ckt) | gnucap | tran | 5 | tiny | no | core | - |
| [`c_measure.2.ckt`](c_measure.2.ckt) | gnucap | tran | 1 | tiny | yes | core | - |
| [`c_measure.2s.ckt`](c_measure.2s.ckt) | gnucap | tran | 1 | tiny | yes | core | - |
| [`c_modify.ckt`](c_modify.ckt) | gnucap | op, op, op, op, op, op, op | 3 | tiny | yes | core | - |
| [`cc.ckt`](cc.ckt) | gnucap | op | 14 | small | no | core | - |
| [`charge-cons.ckt`](charge-cons.ckt) | gnucap | op, tran | 5 | tiny | no | core | - |
| [`charge-cons2.ckt`](charge-cons2.ckt) | gnucap | op, tran | 6 | tiny | no | core | - |
| [`charge-cons3.ckt`](charge-cons3.ckt) | gnucap | op, tran | 6 | tiny | no | core | - |
| [`current.ckt`](current.ckt) | gnucap | op, ac | 2 | tiny | yes | core | - |
| [`d_bjt-diffpair-ccs.ckt`](d_bjt-diffpair-ccs.ckt) | gnucap | op, tran, ac, op, ac | 12 | small | no | core | - |
| [`d_bjt-diffpair-cjc.ckt`](d_bjt-diffpair-cjc.ckt) | gnucap | op, tran, ac, op, ac | 12 | small | no | core | - |
| [`d_bjt-diffpair-dc.ckt`](d_bjt-diffpair-dc.ckt) | gnucap | op | 12 | small | no | core | - |
| [`d_bjt-diffpair-nocap.ckt`](d_bjt-diffpair-nocap.ckt) | gnucap | op, tran, op, ac | 12 | small | no | core | - |
| [`d_bjt-diffpair-tf.ckt`](d_bjt-diffpair-tf.ckt) | gnucap | dc, tran, op, ac | 13 | small | no | core | - |
| [`d_bjt-diffpair-tr.ckt`](d_bjt-diffpair-tr.ckt) | gnucap | op, tran, ac | 12 | small | no | core | - |
| [`d_bjt-diffpair-tran.ckt`](d_bjt-diffpair-tran.ckt) | gnucap | op, tran | 12 | small | no | core | - |
| [`d_bjt-pnp.ckt`](d_bjt-pnp.ckt) | gnucap | op, op, op, op, op, op, op, op | 6 | tiny | no | core | - |
| [`d_bjt-rca3040.ckt`](d_bjt-rca3040.ckt) | gnucap | op, ac, dc, tran | 26 | small | no | core | - |
| [`d_bjt-rtlinv.ckt`](d_bjt-rtlinv.ckt) | gnucap | op, dc, tran | 8 | tiny | no | core | - |
| [`d_bjt-schmitt-bypass.ckt`](d_bjt-schmitt-bypass.ckt) | gnucap | op, tran | 15 | small | no | core | - |
| [`d_bjt-schmitt-nobypass.ckt`](d_bjt-schmitt-nobypass.ckt) | gnucap | op, tran | 15 | small | no | core | - |
| [`d_bjt-schmitt-stat.ckt`](d_bjt-schmitt-stat.ckt) | gnucap | op | 15 | small | no | core | - |
| [`d_bjt.2.ckt`](d_bjt.2.ckt) | gnucap | op, op, op, op, op, op, op, op | 6 | tiny | no | core | - |
| [`d_bjt.ckt`](d_bjt.ckt) | gnucap | op, op, op, op, op, op, op, op | 6 | tiny | no | core | - |
| [`d_bjt.error1.ckt`](d_bjt.error1.ckt) | gnucap | op | 1 | tiny | no | core | - |
| [`d_cap.1.ckt`](d_cap.1.ckt) | gnucap | tran | 3 | tiny | yes | core | - |
| [`d_cap.2.ckt`](d_cap.2.ckt) | gnucap | tran | 3 | tiny | yes | core | - |
| [`d_cap.3.ckt`](d_cap.3.ckt) | gnucap | tran, tran | 3 | tiny | yes | core | - |
| [`d_cap.3a.ckt`](d_cap.3a.ckt) | gnucap | tran, tran | 3 | tiny | yes | core | - |
| [`d_cap.4.ckt`](d_cap.4.ckt) | gnucap | tran, tran, tran, tran, tran | 3 | tiny | yes | core | - |
| [`d_cap.5.ckt`](d_cap.5.ckt) | gnucap | tran, tran, tran, tran | 3 | tiny | yes | core | - |
| [`d_cap.6.ckt`](d_cap.6.ckt) | gnucap | tran, tran, tran, tran | 3 | tiny | yes | core | - |
| [`d_cap.ic1.ckt`](d_cap.ic1.ckt) | gnucap | tran | 2 | tiny | yes | core | - |
| [`d_cap.ic2.ckt`](d_cap.ic2.ckt) | gnucap | tran | 2 | tiny | yes | core | - |
| [`d_cap.ic4.ckt`](d_cap.ic4.ckt) | gnucap | tran, tran | 11 | small | yes | core | - |
| [`d_cccs.1.ckt`](d_cccs.1.ckt) | gnucap | op, tran, ac | 13 | small | yes | core | - |
| [`d_cccs.2.ckt`](d_cccs.2.ckt) | gnucap | op, tran, ac | 38 | small | no | core | - |
| [`d_cccs.3.ckt`](d_cccs.3.ckt) | gnucap | op, tran, ac | 13 | small | yes | core | - |
| [`d_cccs.4.ckt`](d_cccs.4.ckt) | gnucap | op, tran, ac | 13 | small | yes | core | - |
| [`d_cccs.5.ckt`](d_cccs.5.ckt) | gnucap | op, tran, ac | 40 | small | no | core | - |
| [`d_cccs.6.ckt`](d_cccs.6.ckt) | gnucap | op, tran, ac, op, tran, ac | 14 | small | yes | core | - |
| [`d_ccvs.1.ckt`](d_ccvs.1.ckt) | gnucap | op, tran, ac, op, tran, ac | 17 | small | yes | core | - |
| [`d_ccvs.2.ckt`](d_ccvs.2.ckt) | gnucap | op, tran, ac | 38 | small | no | core | - |
| [`d_ccvs.3.ckt`](d_ccvs.3.ckt) | gnucap | op, tran, ac | 45 | small | no | core | - |
| [`d_coil.1.ckt`](d_coil.1.ckt) | gnucap | ac, tran | 19 | small | yes | core | - |
| [`d_coil.1a.ckt`](d_coil.1a.ckt) | gnucap | ac, tran | 19 | small | yes | core | - |
| [`d_coil.1b.ckt`](d_coil.1b.ckt) | gnucap | ac, tran | 19 | small | yes | core | - |
| [`d_coil.1c.ckt`](d_coil.1c.ckt) | gnucap | ac, tran | 20 | small | yes | core | - |
| [`d_coil.1d.ckt`](d_coil.1d.ckt) | gnucap | ac, tran | 31 | small | yes | core | - |
| [`d_coil.1e.ckt`](d_coil.1e.ckt) | gnucap | ac, ac, tran | 29 | small | yes | core | - |
| [`d_coil.2.ckt`](d_coil.2.ckt) | gnucap | ac, ac, tran | 26 | small | yes | core | - |
| [`d_coil.3.ckt`](d_coil.3.ckt) | gnucap | ac, ac, tran | 19 | small | yes | core | - |
| [`d_coil.4.ckt`](d_coil.4.ckt) | gnucap | dc, ac | 5 | tiny | yes | core | - |
| [`d_coil.5.ckt`](d_coil.5.ckt) | gnucap | op, ac, tran | 9 | tiny | yes | core | - |
| [`d_coil.5.spice`](d_coil.5.spice) | gnucap | op, ac, tran | 9 | tiny | yes | core | - |
| [`d_coil.error1.ckt`](d_coil.error1.ckt) | gnucap | ac | 3 | tiny | yes | core | - |
| [`d_coil.error2.ckt`](d_coil.error2.ckt) | gnucap | ac | 3 | tiny | yes | core | - |
| [`d_coil.error3.ckt`](d_coil.error3.ckt) | gnucap | ac | 3 | tiny | yes | core | - |
| [`d_coil.error4.ckt`](d_coil.error4.ckt) | gnucap | ac | 3 | tiny | yes | core | - |
| [`d_coil.error5.ckt`](d_coil.error5.ckt) | gnucap | ac | 3 | tiny | yes | core | - |
| [`d_coil.m3.ckt`](d_coil.m3.ckt) | gnucap | ac, ac, tran | 58 | small | yes | core | - |
| [`d_coil.m3a.ckt`](d_coil.m3a.ckt) | gnucap | ac, ac, tran | 23 | small | yes | core | - |
| [`d_coil.m3r.ckt`](d_coil.m3r.ckt) | gnucap | ac, ac, tran | 58 | small | yes | core | - |
| [`d_coil.ports0.ckt`](d_coil.ports0.ckt) | gnucap | ac, ac, tran | 10 | small | yes | core | - |
| [`d_coil.ports0g.ckt`](d_coil.ports0g.ckt) | gnucap | ac, ac, tran | 11 | small | yes | core | - |
| [`d_coil.ports1.ckt`](d_coil.ports1.ckt) | gnucap | ac, ac, tran | 48 | small | yes | core | - |
| [`d_diode.1.ckt`](d_diode.1.ckt) | gnucap | op, dc | 3 | tiny | no | core | - |
| [`d_diode.10.ckt`](d_diode.10.ckt) | gnucap | op, op | 3 | tiny | no | core | - |
| [`d_diode.10a.ckt`](d_diode.10a.ckt) | gnucap | op, op | 3 | tiny | no | core | - |
| [`d_diode.11.ckt`](d_diode.11.ckt) | gnucap | op | 5 | tiny | no | core | - |
| [`d_diode.11a.ckt`](d_diode.11a.ckt) | gnucap | op | 5 | tiny | no | core | - |
| [`d_diode.11b.ckt`](d_diode.11b.ckt) | gnucap | op | 5 | tiny | no | core | - |
| [`d_diode.11c.ckt`](d_diode.11c.ckt) | gnucap | op | 5 | tiny | no | core | - |
| [`d_diode.11d.ckt`](d_diode.11d.ckt) | gnucap | op | 5 | tiny | no | core | - |
| [`d_diode.12.ckt`](d_diode.12.ckt) | gnucap | ac, dc, ac, tran, ac, tran, ac, tran, ac, tran, ac | 3 | tiny | no | core | - |
| [`d_diode.2.ckt`](d_diode.2.ckt) | gnucap | op | 3 | tiny | no | core | - |
| [`d_diode.3.ckt`](d_diode.3.ckt) | gnucap | op, dc, dc, op | 3 | tiny | no | core | - |
| [`d_diode.4.ckt`](d_diode.4.ckt) | gnucap | op, dc, dc, op | 3 | tiny | no | core | - |
| [`d_diode.5.ckt`](d_diode.5.ckt) | gnucap | op, dc, dc, op | 3 | tiny | no | core | - |
| [`d_diode.6.ckt`](d_diode.6.ckt) | gnucap | op, dc, dc, op | 3 | tiny | no | core | - |
| [`d_diode.7.ckt`](d_diode.7.ckt) | gnucap | op, dc, dc, op | 3 | tiny | no | core | - |
| [`d_diode.8.ckt`](d_diode.8.ckt) | gnucap | op, dc, dc, op | 3 | tiny | no | core | - |
| [`d_diode.9.ckt`](d_diode.9.ckt) | gnucap | op, dc, dc, op | 3 | tiny | no | core | - |
| [`d_diode.9m.ckt`](d_diode.9m.ckt) | gnucap | op | 3 | tiny | no | core | - |
| [`d_diode.error1.ckt`](d_diode.error1.ckt) | gnucap | op | 1 | tiny | no | core | - |
| [`d_logic.1.ckt`](d_logic.1.ckt) | gnucap | op | 8 | tiny | no | core | - |
| [`d_logic.2.ckt`](d_logic.2.ckt) | gnucap | op | 8 | tiny | no | core | - |
| [`d_logic.3.ckt`](d_logic.3.ckt) | gnucap | op | 8 | tiny | no | core | - |
| [`d_logic.4.ckt`](d_logic.4.ckt) | gnucap | op | 8 | tiny | no | core | - |
| [`d_logic.5.ckt`](d_logic.5.ckt) | gnucap | op | 8 | tiny | no | core | - |
| [`d_logic.6.ckt`](d_logic.6.ckt) | gnucap | op | 8 | tiny | no | core | - |
| [`d_logic.7.ckt`](d_logic.7.ckt) | gnucap | op | 8 | tiny | no | core | - |
| [`d_logic.error1.ckt`](d_logic.error1.ckt) | gnucap | op | 1 | tiny | no | core | - |
| [`d_logic_nand-dc.ckt`](d_logic_nand-dc.ckt) | gnucap | dc | 5 | tiny | no | core | - |
| [`d_logic_tr_ab1.ckt`](d_logic_tr_ab1.ckt) | gnucap | op, tran | 3 | tiny | no | core | - |
| [`d_logic_tr_ab2.ckt`](d_logic_tr_ab2.ckt) | gnucap | op, tran | 4 | tiny | no | core | - |
| [`d_logic_tr_an1.ckt`](d_logic_tr_an1.ckt) | gnucap | op, tran | 3 | tiny | no | core | - |
| [`d_logic_tr_an2.ckt`](d_logic_tr_an2.ckt) | gnucap | op, tran | 4 | tiny | no | core | - |
| [`d_logic_tr_db1.ckt`](d_logic_tr_db1.ckt) | gnucap | op, tran | 3 | tiny | no | core | - |
| [`d_logic_tr_db2.ckt`](d_logic_tr_db2.ckt) | gnucap | op, tran | 4 | tiny | no | core | - |
| [`d_logic_tr_dn1.ckt`](d_logic_tr_dn1.ckt) | gnucap | op, tran | 3 | tiny | no | core | - |
| [`d_logic_tr_dn2.ckt`](d_logic_tr_dn2.ckt) | gnucap | op, tran | 4 | tiny | no | core | - |
| [`d_logic_tr_mb1a.ckt`](d_logic_tr_mb1a.ckt) | gnucap | op, tran | 3 | tiny | no | core | - |
| [`d_logic_tr_mb1b.ckt`](d_logic_tr_mb1b.ckt) | gnucap | op, tran | 3 | tiny | no | core | - |
| [`d_logic_tr_mb2a.ckt`](d_logic_tr_mb2a.ckt) | gnucap | op, tran | 4 | tiny | no | core | - |
| [`d_logic_tr_mb2b.ckt`](d_logic_tr_mb2b.ckt) | gnucap | op, tran | 4 | tiny | no | core | - |
| [`d_logic_tr_mn1a.ckt`](d_logic_tr_mn1a.ckt) | gnucap | op, tran | 3 | tiny | no | core | - |
| [`d_logic_tr_mn1b.ckt`](d_logic_tr_mn1b.ckt) | gnucap | op, tran | 3 | tiny | no | core | - |
| [`d_logic_tr_mn2a.ckt`](d_logic_tr_mn2a.ckt) | gnucap | op, tran | 4 | tiny | no | core | - |
| [`d_logic_tr_mn2b.ckt`](d_logic_tr_mn2b.ckt) | gnucap | op, tran | 4 | tiny | no | core | - |
| [`d_macro.1.ckt`](d_macro.1.ckt) | gnucap | op, op | 13 | small | yes | core | - |
| [`d_mos.error1.ckt`](d_mos.error1.ckt) | gnucap | op | 1 | tiny | no | core | - |
| [`d_mos.error2.ckt`](d_mos.error2.ckt) | gnucap | op | 1 | tiny | no | core | - |
| [`d_mos.error3.ckt`](d_mos.error3.ckt) | gnucap | op | 1 | tiny | no | core | - |
| [`d_mos.error4.ckt`](d_mos.error4.ckt) | gnucap | op | 1 | tiny | no | core | - |
| [`d_mos.swp0.ckt`](d_mos.swp0.ckt) | gnucap | dc, dc, dc, dc | 2 | tiny | no | core | - |
| [`d_mos.swp1.ckt`](d_mos.swp1.ckt) | gnucap | dc, dc, dc, dc | 2 | tiny | no | core | - |
| [`d_mos1.bin1.ckt`](d_mos1.bin1.ckt) | gnucap | op, dc, tran | 14 | small | no | core | - |
| [`d_mos1.bin2.ckt`](d_mos1.bin2.ckt) | gnucap | op, dc, tran | 14 | small | no | core | - |
| [`d_mos1.bin3.ckt`](d_mos1.bin3.ckt) | gnucap | op, dc, tran | 14 | small | no | core | - |
| [`d_mos1.inv.bug.ckt`](d_mos1.inv.bug.ckt) | gnucap | dc | 7 | tiny | no | core | - |
| [`d_mos1.inv1.ckt`](d_mos1.inv1.ckt) | gnucap | op, dc, tran | 14 | small | no | core | - |
| [`d_mos1.inv2.ckt`](d_mos1.inv2.ckt) | gnucap | op, dc, tran | 14 | small | no | core | - |
| [`d_mos1.inv3.ckt`](d_mos1.inv3.ckt) | gnucap | op, dc, tran | 14 | small | no | core | - |
| [`d_mos1.lin1.ckt`](d_mos1.lin1.ckt) | gnucap | op, op, op, op, op, op, op, op, op, op, dc | 5 | tiny | no | core | - |
| [`d_mos1.lin1.late.ckt`](d_mos1.lin1.late.ckt) | gnucap | op, op, op, op, op, op, op, op, op, op, dc | 5 | tiny | no | core | - |
| [`d_mos1.lin1.none.ckt`](d_mos1.lin1.none.ckt) | gnucap | op, op, op, op, op, op, op, op, op, op, dc | 5 | tiny | no | core | - |
| [`d_mos1.lin1.spice`](d_mos1.lin1.spice) | gnucap | op, dc | 5 | tiny | no | core | - |
| [`d_mos1.lin2.ckt`](d_mos1.lin2.ckt) | gnucap | op, op, op, op, op, op, op, op, op, op, dc | 5 | tiny | no | core | - |
| [`d_mos1.lin3.ckt`](d_mos1.lin3.ckt) | gnucap | op, op, op, op, op, op, op, op, op, op, dc | 5 | tiny | no | core | - |
| [`d_mos1.lin4.ckt`](d_mos1.lin4.ckt) | gnucap | op, op, op, op, op, op, op, op, op, op, dc | 5 | tiny | no | core | - |
| [`d_mos1.lin5.ckt`](d_mos1.lin5.ckt) | gnucap | op, op, op, op, op, op, op, op, op, op, dc | 4 | tiny | no | core | - |
| [`d_mos1.n+1.ckt`](d_mos1.n+1.ckt) | gnucap | op | 3 | tiny | no | core | - |
| [`d_mos1.n-1.ckt`](d_mos1.n-1.ckt) | gnucap | op | 3 | tiny | no | core | - |
| [`d_mos1.n0.ckt`](d_mos1.n0.ckt) | gnucap | op | 3 | tiny | no | core | - |
| [`d_mos1.nand1.ckt`](d_mos1.nand1.ckt) | gnucap | op, op, op, op, op, tran | 7 | tiny | no | core | - |
| [`d_mos1.nand2.ckt`](d_mos1.nand2.ckt) | gnucap | op, op, op, op, op, tran | 7 | tiny | no | core | - |
| [`d_mos1.nand3.ckt`](d_mos1.nand3.ckt) | gnucap | op, op, op, op, op, tran | 7 | tiny | no | core | - |
| [`d_mos1.p+1.ckt`](d_mos1.p+1.ckt) | gnucap | op | 3 | tiny | no | core | - |
| [`d_mos1.p-1.ckt`](d_mos1.p-1.ckt) | gnucap | op | 3 | tiny | no | core | - |
| [`d_mos1.p0.ckt`](d_mos1.p0.ckt) | gnucap | op | 3 | tiny | no | core | - |
| [`d_mos1.plin.ckt`](d_mos1.plin.ckt) | gnucap | op, op, op, op, op, op, op, op, op, op | 5 | tiny | no | core | - |
| [`d_mos1.psat1.ckt`](d_mos1.psat1.ckt) | gnucap | op, op, op, op, op, op, op, op, op, op, op, op | 4 | tiny | no | core | - |
| [`d_mos1.psat2.ckt`](d_mos1.psat2.ckt) | gnucap | op, op, op, op, op, op, op, op, op, op, op, op | 4 | tiny | no | core | - |
| [`d_mos1.psat3.ckt`](d_mos1.psat3.ckt) | gnucap | op, op, op, op, op, op, op, op, op, op, op, op | 4 | tiny | no | core | - |
| [`d_mos1.sat1.ckt`](d_mos1.sat1.ckt) | gnucap | op | 4 | tiny | no | core | - |
| [`d_mos1.sat2.ckt`](d_mos1.sat2.ckt) | gnucap | op, op, op, op, op, op, op, op, op, op, op, op | 4 | tiny | no | core | - |
| [`d_mos1.sat2.spice`](d_mos1.sat2.spice) | gnucap | op | 4 | tiny | no | core | - |
| [`d_mos1.sat3.ckt`](d_mos1.sat3.ckt) | gnucap | op, op, op, op, op, op, op, op, op, op, op, op | 4 | tiny | no | core | - |
| [`d_mos1.sat4.ckt`](d_mos1.sat4.ckt) | gnucap | op, op, op, op, op, op, op, op, op, op, op, op | 4 | tiny | no | core | - |
| [`d_mos1.sat5.ckt`](d_mos1.sat5.ckt) | gnucap | op, op, op, op, op, op, op, op, op, op, op, op | 3 | tiny | no | core | - |
| [`d_mos1.sat6.ckt`](d_mos1.sat6.ckt) | gnucap | op, op, op, op, op, op, op, op, op, op, op, op | 4 | tiny | no | core | - |
| [`d_mos1.sat7.ckt`](d_mos1.sat7.ckt) | gnucap | op, op, op, op, op, op, op, op, op, op | 3 | tiny | no | core | - |
| [`d_mos1.sts.ckt`](d_mos1.sts.ckt) | gnucap | op, op, op, op, op, op, op, op, op, op | 5 | tiny | no | core | - |
| [`d_mos1.temp0.ckt`](d_mos1.temp0.ckt) | gnucap | dc, dc, op | 3 | tiny | no | core | - |
| [`d_mos1.temp1.ckt`](d_mos1.temp1.ckt) | gnucap | dc, dc, op | 3 | tiny | no | core | - |
| [`d_mos1.temp2.ckt`](d_mos1.temp2.ckt) | gnucap | dc, dc, dc | 3 | tiny | no | core | - |
| [`d_mos1.zero.ckt`](d_mos1.zero.ckt) | gnucap | op, ac, tran | 6 | tiny | no | core | - |
| [`d_mos2.inv1.ckt`](d_mos2.inv1.ckt) | gnucap | op, dc, tran | 14 | small | no | core | - |
| [`d_mos2.lin1.ckt`](d_mos2.lin1.ckt) | gnucap | op, op, op, op, op, op, op, op, op, op, dc | 5 | tiny | no | core | - |
| [`d_mos2.lin1.late.ckt`](d_mos2.lin1.late.ckt) | gnucap | op, op, op, op, op, op, op, op, op, op, dc | 5 | tiny | no | core | - |
| [`d_mos2.lin1r.ckt`](d_mos2.lin1r.ckt) | gnucap | op, op, op, op, op, op, op, op, op, op, dc | 5 | tiny | no | core | - |
| [`d_mos2.lin1z.ckt`](d_mos2.lin1z.ckt) | gnucap | op, op, op, op, op, op, op, op, op, op, dc | 5 | tiny | no | core | - |
| [`d_mos2.lin2.ckt`](d_mos2.lin2.ckt) | gnucap | op, op, op, op, op, op, op, op, op, op, dc | 5 | tiny | no | core | - |
| [`d_mos2.lin3.ckt`](d_mos2.lin3.ckt) | gnucap | op, op, op, op, op, op, op, op, op, op, dc | 5 | tiny | no | core | - |
| [`d_mos2.lin4.ckt`](d_mos2.lin4.ckt) | gnucap | op, op, op, op, op, op, op, op, op, op, dc | 5 | tiny | no | core | - |
| [`d_mos2.lin5.ckt`](d_mos2.lin5.ckt) | gnucap | op, op, op, op, op, op, op, op, op, op, dc | 4 | tiny | no | core | - |
| [`d_mos2.n+1.ckt`](d_mos2.n+1.ckt) | gnucap | op | 3 | tiny | no | core | - |
| [`d_mos2.n-1.ckt`](d_mos2.n-1.ckt) | gnucap | op | 3 | tiny | no | core | - |
| [`d_mos2.n0.ckt`](d_mos2.n0.ckt) | gnucap | op | 3 | tiny | no | core | - |
| [`d_mos2.nand1.ckt`](d_mos2.nand1.ckt) | gnucap | op, op, op, op, op, tran | 8 | tiny | no | core | - |
| [`d_mos2.p+1.ckt`](d_mos2.p+1.ckt) | gnucap | op | 3 | tiny | no | core | - |
| [`d_mos2.p-1.ckt`](d_mos2.p-1.ckt) | gnucap | op | 3 | tiny | no | core | - |
| [`d_mos2.p0.ckt`](d_mos2.p0.ckt) | gnucap | op | 3 | tiny | no | core | - |
| [`d_mos2.plin.ckt`](d_mos2.plin.ckt) | gnucap | op, op, op, op, op, op, op, op, op, op | 5 | tiny | no | core | - |
| [`d_mos2.psat1.ckt`](d_mos2.psat1.ckt) | gnucap | op | 4 | tiny | no | core | - |
| [`d_mos2.psat2.ckt`](d_mos2.psat2.ckt) | gnucap | op | 4 | tiny | no | core | - |
| [`d_mos2.psat3.ckt`](d_mos2.psat3.ckt) | gnucap | op | 4 | tiny | no | core | - |
| [`d_mos2.sat1.ckt`](d_mos2.sat1.ckt) | gnucap | op, op, op, op, op, op, op, op, op, op, op, op | 4 | tiny | no | core | - |
| [`d_mos2.sat2.ckt`](d_mos2.sat2.ckt) | gnucap | op, op, op, op, op, op, op, op, op, op, op, op | 4 | tiny | no | core | - |
| [`d_mos2.sat3.ckt`](d_mos2.sat3.ckt) | gnucap | op, op, op, op, op, op, op, op, op, op, op, op | 4 | tiny | no | core | - |
| [`d_mos2.sat4.ckt`](d_mos2.sat4.ckt) | gnucap | op, op, op, op, op, op, op, op, op, op, op, op | 4 | tiny | no | core | - |
| [`d_mos2.sat5.ckt`](d_mos2.sat5.ckt) | gnucap | op, op, op, op, op, op, op, op, op, op, op, op | 3 | tiny | no | core | - |
| [`d_mos2.sat6.ckt`](d_mos2.sat6.ckt) | gnucap | op, op, op, op, op, op, op, op, op, op, op, op | 4 | tiny | no | core | - |
| [`d_mos2.sat7.ckt`](d_mos2.sat7.ckt) | gnucap | op, op, op, op, op, op, op, op, op, op | 3 | tiny | no | core | - |
| [`d_mos2.sts.ckt`](d_mos2.sts.ckt) | gnucap | op, op, op, op, op, op, op, op, op, op | 5 | tiny | no | core | - |
| [`d_mos2.zero.ckt`](d_mos2.zero.ckt) | gnucap | op, ac | 6 | tiny | no | core | - |
| [`d_mos3.inv1.ckt`](d_mos3.inv1.ckt) | gnucap | op, dc, tran | 14 | small | no | core | - |
| [`d_mos3.lin1.ckt`](d_mos3.lin1.ckt) | gnucap | op, dc | 5 | tiny | no | core | - |
| [`d_mos3.lin1r.ckt`](d_mos3.lin1r.ckt) | gnucap | op, op, op, op, op, op, op, op, op, op, dc | 5 | tiny | no | core | - |
| [`d_mos3.lin1z.ckt`](d_mos3.lin1z.ckt) | gnucap | op, op, op, op, op, op, op, op, op, op, dc | 5 | tiny | no | core | - |
| [`d_mos3.lin2.ckt`](d_mos3.lin2.ckt) | gnucap | op, op, op, op, op, op, op, op, op, op, dc | 5 | tiny | no | core | - |
| [`d_mos3.lin3.ckt`](d_mos3.lin3.ckt) | gnucap | op, op, op, op, op, op, op, op, op, op, dc | 5 | tiny | no | core | - |
| [`d_mos3.lin4.ckt`](d_mos3.lin4.ckt) | gnucap | op, op, op, op, op, op, op, op, op, op, dc | 5 | tiny | no | core | - |
| [`d_mos3.lin5.ckt`](d_mos3.lin5.ckt) | gnucap | op, op, op, op, op, op, op, op, op, op, dc | 4 | tiny | no | core | - |
| [`d_mos3.n+1.ckt`](d_mos3.n+1.ckt) | gnucap | op | 3 | tiny | no | core | - |
| [`d_mos3.n-1.ckt`](d_mos3.n-1.ckt) | gnucap | op | 3 | tiny | no | core | - |
| [`d_mos3.n0.ckt`](d_mos3.n0.ckt) | gnucap | op | 3 | tiny | no | core | - |
| [`d_mos3.nand1.ckt`](d_mos3.nand1.ckt) | gnucap | op, op, op, op, op, tran | 8 | tiny | no | core | - |
| [`d_mos3.p+1.ckt`](d_mos3.p+1.ckt) | gnucap | op | 3 | tiny | no | core | - |
| [`d_mos3.p-1.ckt`](d_mos3.p-1.ckt) | gnucap | op | 3 | tiny | no | core | - |
| [`d_mos3.p0.ckt`](d_mos3.p0.ckt) | gnucap | op | 3 | tiny | no | core | - |
| [`d_mos3.plin.ckt`](d_mos3.plin.ckt) | gnucap | op, op, op, op, op, op, op, op, op, op | 5 | tiny | no | core | - |
| [`d_mos3.psat1.ckt`](d_mos3.psat1.ckt) | gnucap | op | 4 | tiny | no | core | - |
| [`d_mos3.psat2.ckt`](d_mos3.psat2.ckt) | gnucap | op | 4 | tiny | no | core | - |
| [`d_mos3.psat3.ckt`](d_mos3.psat3.ckt) | gnucap | op | 4 | tiny | no | core | - |
| [`d_mos3.sat000.ckt`](d_mos3.sat000.ckt) | gnucap | op | 4 | tiny | no | core | - |
| [`d_mos3.sat007.ckt`](d_mos3.sat007.ckt) | gnucap | op | 3 | tiny | no | core | - |
| [`d_mos3.sat1.ckt`](d_mos3.sat1.ckt) | gnucap | op, op, op, op, op, op, op, op, op, op | 4 | tiny | no | core | - |
| [`d_mos3.sat2.ckt`](d_mos3.sat2.ckt) | gnucap | op, op, op, op, op, op, op, op, op, op, op, op | 4 | tiny | no | core | - |
| [`d_mos3.sat3.ckt`](d_mos3.sat3.ckt) | gnucap | op, op, op, op, op, op, op, op, op, op, op, op | 4 | tiny | no | core | - |
| [`d_mos3.sat4.ckt`](d_mos3.sat4.ckt) | gnucap | op, op, op, op, op, op, op, op, op, op, op, op | 4 | tiny | no | core | - |
| [`d_mos3.sat5.ckt`](d_mos3.sat5.ckt) | gnucap | op, op, op, op, op, op, op, op, op, op, op, op | 3 | tiny | no | core | - |
| [`d_mos3.sat6.ckt`](d_mos3.sat6.ckt) | gnucap | op, op, op, op, op, op, op, op, op, op, op, op | 4 | tiny | no | core | - |
| [`d_mos3.sat7.ckt`](d_mos3.sat7.ckt) | gnucap | op, op, op, op, op, op, op, op, op, op | 3 | tiny | no | core | - |
| [`d_mos3.sts.ckt`](d_mos3.sts.ckt) | gnucap | op, op, op, op, op, op, op, op, op, op | 5 | tiny | no | core | - |
| [`d_mos3.sts000.ckt`](d_mos3.sts000.ckt) | gnucap | op | 5 | tiny | no | core | - |
| [`d_mos3.zero.ckt`](d_mos3.zero.ckt) | gnucap | op, ac | 6 | tiny | no | core | - |
| [`d_mos4.1.ckt`](d_mos4.1.ckt) | gnucap | dc | 17 | small | no | core | - |
| [`d_mos4.2.ckt`](d_mos4.2.ckt) | gnucap | dc | 17 | small | no | core | - |
| [`d_mos4.3.ckt`](d_mos4.3.ckt) | gnucap | dc | 17 | small | no | core | - |
| [`d_mos49.nand1.ckt`](d_mos49.nand1.ckt) | gnucap | op, op, op, op, tran | 8 | tiny | no | core | - |
| [`d_mos5.1.ckt`](d_mos5.1.ckt) | gnucap | dc | 17 | small | no | core | - |
| [`d_mos6.inv1.ckt`](d_mos6.inv1.ckt) | gnucap | op, dc, tran | 14 | small | no | core | - |
| [`d_mos6.lin1.ckt`](d_mos6.lin1.ckt) | gnucap | op, op, op, op, op, op, op, op, op, op, op, dc | 5 | tiny | no | core | - |
| [`d_mos6.lin1.spice`](d_mos6.lin1.spice) | gnucap | op, dc | 5 | tiny | no | core | - |
| [`d_mos6.lin1r.ckt`](d_mos6.lin1r.ckt) | gnucap | op, op, op, op, op, op, op, op, op, op, op, dc | 5 | tiny | no | core | - |
| [`d_mos6.lin1r.spice`](d_mos6.lin1r.spice) | gnucap | op, dc | 5 | tiny | no | core | - |
| [`d_mos6.lin1z.ckt`](d_mos6.lin1z.ckt) | gnucap | op, op, op, op, op, op, op, op, op, op, op, dc | 5 | tiny | no | core | - |
| [`d_mos6.lin1z.spice`](d_mos6.lin1z.spice) | gnucap | op, dc | 5 | tiny | no | core | - |
| [`d_mos6.lin2.ckt`](d_mos6.lin2.ckt) | gnucap | op, op, op, op, op, op, op, op, op, op, op, dc | 4 | tiny | no | core | - |
| [`d_mos6.lin2.spice`](d_mos6.lin2.spice) | gnucap | op, dc | 4 | tiny | no | core | - |
| [`d_mos6.lin2r.ckt`](d_mos6.lin2r.ckt) | gnucap | op, op, op, op, op, op, op, op, op, op, op, dc | 4 | tiny | no | core | - |
| [`d_mos6.lin2r.spice`](d_mos6.lin2r.spice) | gnucap | op, dc | 4 | tiny | no | core | - |
| [`d_mos6.lin2z.ckt`](d_mos6.lin2z.ckt) | gnucap | op, op, op, op, op, op, op, op, op, op, op, dc | 4 | tiny | no | core | - |
| [`d_mos6.lin2z.spice`](d_mos6.lin2z.spice) | gnucap | op, dc | 4 | tiny | no | core | - |
| [`d_mos6.n+1.ckt`](d_mos6.n+1.ckt) | gnucap | op | 3 | tiny | no | core | - |
| [`d_mos6.n-1.ckt`](d_mos6.n-1.ckt) | gnucap | op | 3 | tiny | no | core | - |
| [`d_mos6.n0.ckt`](d_mos6.n0.ckt) | gnucap | op | 3 | tiny | no | core | - |
| [`d_mos6.nand1.ckt`](d_mos6.nand1.ckt) | gnucap | op, op, op, op, op, tran | 7 | tiny | no | core | - |
| [`d_mos6.p+1.ckt`](d_mos6.p+1.ckt) | gnucap | op | 3 | tiny | no | core | - |
| [`d_mos6.p-1.ckt`](d_mos6.p-1.ckt) | gnucap | op | 3 | tiny | no | core | - |
| [`d_mos6.p0.ckt`](d_mos6.p0.ckt) | gnucap | op | 3 | tiny | no | core | - |
| [`d_mos6.plin.ckt`](d_mos6.plin.ckt) | gnucap | op, op, op, op, op, op, op, op, op, op | 5 | tiny | no | core | - |
| [`d_mos6.psat1.ckt`](d_mos6.psat1.ckt) | gnucap | op | 4 | tiny | no | core | - |
| [`d_mos6.psat2.ckt`](d_mos6.psat2.ckt) | gnucap | op | 4 | tiny | no | core | - |
| [`d_mos6.psat3.ckt`](d_mos6.psat3.ckt) | gnucap | op | 4 | tiny | no | core | - |
| [`d_mos6.sat1.ckt`](d_mos6.sat1.ckt) | gnucap | op, op, op, op, op, op, op, op, op, op, op | 4 | tiny | no | core | - |
| [`d_mos6.sat1.spice`](d_mos6.sat1.spice) | gnucap | op | 4 | tiny | no | core | - |
| [`d_mos6.sat1r.ckt`](d_mos6.sat1r.ckt) | gnucap | op, op, op, op, op, op, op, op, op, op, op | 4 | tiny | no | core | - |
| [`d_mos6.sat1r.spice`](d_mos6.sat1r.spice) | gnucap | op | 4 | tiny | no | core | - |
| [`d_mos6.sat1s.ckt`](d_mos6.sat1s.ckt) | gnucap | op, op, op, op, op, op, op, op, op, op, op | 4 | tiny | no | core | - |
| [`d_mos6.sat1s.spice`](d_mos6.sat1s.spice) | gnucap | op | 4 | tiny | no | core | - |
| [`d_mos6.sat1v.ckt`](d_mos6.sat1v.ckt) | gnucap | op, op, op, op, op, op, op, op, op, op, op | 4 | tiny | no | core | - |
| [`d_mos6.sat1v.spice`](d_mos6.sat1v.spice) | gnucap | op | 4 | tiny | no | core | - |
| [`d_mos6.sat2.ckt`](d_mos6.sat2.ckt) | gnucap | op, op, op, op, op, op, op, op, op, op, op | 3 | tiny | no | core | - |
| [`d_mos6.sat2.spice`](d_mos6.sat2.spice) | gnucap | op | 3 | tiny | no | core | - |
| [`d_mos6.sat2r.ckt`](d_mos6.sat2r.ckt) | gnucap | op, op, op, op, op, op, op, op, op, op, op | 3 | tiny | no | core | - |
| [`d_mos6.sat2r.spice`](d_mos6.sat2r.spice) | gnucap | op | 3 | tiny | no | core | - |
| [`d_mos6.sat3.ckt`](d_mos6.sat3.ckt) | gnucap | op, op, op, op, op, op, op, op, op, op, op | 3 | tiny | no | core | - |
| [`d_mos6.sat3.spice`](d_mos6.sat3.spice) | gnucap | op, dc | 3 | tiny | no | core | - |
| [`d_mos6.sat3r.ckt`](d_mos6.sat3r.ckt) | gnucap | op, op, op, op, op, op, op, op, op, op, op | 3 | tiny | no | core | - |
| [`d_mos6.sat3r.spice`](d_mos6.sat3r.spice) | gnucap | op | 3 | tiny | no | core | - |
| [`d_mos6.sts.ckt`](d_mos6.sts.ckt) | gnucap | op, op, op, op, op, op, op, op, op, op | 5 | tiny | no | core | - |
| [`d_mos6.sts000.ckt`](d_mos6.sts000.ckt) | gnucap | op | 5 | tiny | no | core | - |
| [`d_mos6.zero.ckt`](d_mos6.zero.ckt) | gnucap | op, ac | 6 | tiny | no | core | - |
| [`d_mos7.alpha.ckt`](d_mos7.alpha.ckt) | gnucap | op, op, op, op, op, op, op, op, op, op, dc | 5 | tiny | no | core | - |
| [`d_mos7.inv1.ckt`](d_mos7.inv1.ckt) | gnucap | op, dc, tran | 14 | small | no | core | - |
| [`d_mos7.lin1.ckt`](d_mos7.lin1.ckt) | gnucap | op, op, op, op, op, op, op, op, op, op, dc | 5 | tiny | no | core | - |
| [`d_mos7.lin2.ckt`](d_mos7.lin2.ckt) | gnucap | op, op, op, op, op, op, op, op, op, op, dc | 4 | tiny | no | core | - |
| [`d_mos7.nand1.ckt`](d_mos7.nand1.ckt) | gnucap | op, op, op, op, tran | 8 | tiny | no | core | - |
| [`d_mos7.nand1.nobypass.ckt`](d_mos7.nand1.nobypass.ckt) | gnucap | op, op, op, op, tran | 8 | tiny | no | core | - |
| [`d_mos7.plin.ckt`](d_mos7.plin.ckt) | gnucap | op, op, op, op, op, op, op, op, op, op | 5 | tiny | no | core | - |
| [`d_mos7.psat.ckt`](d_mos7.psat.ckt) | gnucap | op, op, op, op, op, op, op, op, op, op | 4 | tiny | no | core | - |
| [`d_mos7.sat1.ckt`](d_mos7.sat1.ckt) | gnucap | op, op, op, op, op, op, op, op, op, op | 4 | tiny | no | core | - |
| [`d_mos7.sat2.ckt`](d_mos7.sat2.ckt) | gnucap | op, op, op, op, op, op, op, op, op, op | 4 | tiny | no | core | - |
| [`d_mos7.sat3.ckt`](d_mos7.sat3.ckt) | gnucap | op, op, op, op, op, op, op, op, op, op | 4 | tiny | no | core | - |
| [`d_mos7.sts.ckt`](d_mos7.sts.ckt) | gnucap | op, op, op, op, op, op, op, op, op, op | 5 | tiny | no | core | - |
| [`d_mos7.zero.ckt`](d_mos7.zero.ckt) | gnucap | op, op, op, op, op, op, op, op, op, op | 5 | tiny | no | core | - |
| [`d_mos8.nand1.ckt`](d_mos8.nand1.ckt) | gnucap | op, op, op, op, tran | 8 | tiny | no | core | - |
| [`d_mos8.sat2.ckt`](d_mos8.sat2.ckt) | gnucap | op | 4 | tiny | no | core | - |
| [`d_mos8.sat3.ckt`](d_mos8.sat3.ckt) | gnucap | op | 4 | tiny | no | core | - |
| [`d_mos8.sat4.ckt`](d_mos8.sat4.ckt) | gnucap | op | 4 | tiny | no | core | - |
| [`d_mos8c2.nand1.ckt`](d_mos8c2.nand1.ckt) | gnucap | op, op, op, op, tran | 8 | tiny | no | core | - |
| [`d_mos8c2.nand1.nobypass.ckt`](d_mos8c2.nand1.nobypass.ckt) | gnucap | op, op, op, op, tran | 8 | tiny | no | core | - |
| [`d_res.bug.2.ckt`](d_res.bug.2.ckt) | gnucap | dc | 2 | tiny | yes | core | - |
| [`d_res.bug.2fit.ckt`](d_res.bug.2fit.ckt) | gnucap | dc | 2 | tiny | yes | core | - |
| [`d_res.neg.0.ckt`](d_res.neg.0.ckt) | gnucap | dc | 2 | tiny | yes | core | - |
| [`d_subckt.1.ckt`](d_subckt.1.ckt) | gnucap | op, op | 13 | small | yes | core | - |
| [`d_subckt.2.ckt`](d_subckt.2.ckt) | gnucap | op, ac | 11 | small | yes | core | - |
| [`d_subckt.3.ckt`](d_subckt.3.ckt) | gnucap | op, ac | 11 | small | yes | core | - |
| [`d_subckt.4.ckt`](d_subckt.4.ckt) | gnucap | op | 5 | tiny | yes | core | - |
| [`d_subckt.5.ckt`](d_subckt.5.ckt) | gnucap | op | 5 | tiny | yes | core | - |
| [`d_subckt.6.ckt`](d_subckt.6.ckt) | gnucap | op | 8 | tiny | yes | core | - |
| [`d_subckt.7.ckt`](d_subckt.7.ckt) | gnucap | op | 18 | small | no | core | - |
| [`d_subckt.8.ckt`](d_subckt.8.ckt) | gnucap | op, op, op | 18 | small | no | core | - |
| [`d_subckt.bin.0.ckt`](d_subckt.bin.0.ckt) | gnucap | op | 2 | tiny | no | core | - |
| [`d_subckt.error3.ckt`](d_subckt.error3.ckt) | gnucap | op | 2 | tiny | yes | core | - |
| [`d_switch.c0.ckt`](d_switch.c0.ckt) | gnucap | tran | 5 | tiny | no | core | - |
| [`d_switch.c1.ckt`](d_switch.c1.ckt) | gnucap | dc, ac, tran, ac | 12 | small | no | core | - |
| [`d_switch.c1.inc.ckt`](d_switch.c1.inc.ckt) | gnucap | dc, ac, tran, ac | 12 | small | no | core | - |
| [`d_switch.c1.noinc.ckt`](d_switch.c1.noinc.ckt) | gnucap | dc, ac, tran, ac | 12 | small | no | core | - |
| [`d_switch.c1a.ckt`](d_switch.c1a.ckt) | gnucap | dc, ac, tran, ac | 12 | small | no | core | - |
| [`d_switch.c1r.ckt`](d_switch.c1r.ckt) | gnucap | dc, ac, tran, tran, tran, ac | 12 | small | no | core | - |
| [`d_switch.c2.ckt`](d_switch.c2.ckt) | gnucap | dc, ac, tran, ac | 12 | small | no | core | - |
| [`d_switch.c2a.ckt`](d_switch.c2a.ckt) | gnucap | dc, ac, tran, ac | 12 | small | no | core | - |
| [`d_switch.c2r.ckt`](d_switch.c2r.ckt) | gnucap | dc, ac, tran, tran, tran, ac | 12 | small | no | core | - |
| [`d_switch.c3.ckt`](d_switch.c3.ckt) | gnucap | dc, ac, tran, ac | 9 | tiny | no | core | - |
| [`d_switch.error1.ckt`](d_switch.error1.ckt) | gnucap | op | 1 | tiny | no | core | - |
| [`d_switch.error2.ckt`](d_switch.error2.ckt) | gnucap | op | 2 | tiny | no | core | - |
| [`d_switch.error3.ckt`](d_switch.error3.ckt) | gnucap | tran | 5 | tiny | no | core | - |
| [`d_switch.nro.1.ckt`](d_switch.nro.1.ckt) | gnucap | tran | 3 | tiny | no | core | - |
| [`d_switch.nro.1e.ckt`](d_switch.nro.1e.ckt) | gnucap | tran | 3 | tiny | no | core | - |
| [`d_switch.nro.1g.ckt`](d_switch.nro.1g.ckt) | gnucap | tran | 3 | tiny | no | core | - |
| [`d_switch.nro.1gr.ckt`](d_switch.nro.1gr.ckt) | gnucap | tran | 3 | tiny | no | core | - |
| [`d_switch.nro.2.auto.ckt`](d_switch.nro.2.auto.ckt) | gnucap | tran | 3 | tiny | no | core | - |
| [`d_switch.nro.2.ckt`](d_switch.nro.2.ckt) | gnucap | tran | 3 | tiny | no | core | - |
| [`d_switch.nro.3.ckt`](d_switch.nro.3.ckt) | gnucap | tran | 3 | tiny | no | core | - |
| [`d_switch.nro.3h.ckt`](d_switch.nro.3h.ckt) | gnucap | tran | 3 | tiny | no | core | - |
| [`d_switch.nro.4.ckt`](d_switch.nro.4.ckt) | gnucap | tran | 3 | tiny | no | core | - |
| [`d_switch.v.ckt`](d_switch.v.ckt) | gnucap | dc, ac, tran, ac | 4 | tiny | no | core | - |
| [`d_switch.vr.ckt`](d_switch.vr.ckt) | gnucap | dc, ac, tran, tran, tran, ac | 4 | tiny | no | core | - |
| [`d_tcap.1.ckt`](d_tcap.1.ckt) | gnucap | tran, tran | 5 | tiny | yes | core | - |
| [`d_tcap.2.ckt`](d_tcap.2.ckt) | gnucap | tran, tran | 5 | tiny | yes | core | - |
| [`d_tcap.3.ckt`](d_tcap.3.ckt) | gnucap | tran, tran | 5 | tiny | yes | core | - |
| [`d_tcap.4.ckt`](d_tcap.4.ckt) | gnucap | tran, tran | 5 | tiny | yes | core | - |
| [`d_tcap.5.ckt`](d_tcap.5.ckt) | gnucap | tran, tran | 5 | tiny | yes | core | - |
| [`d_trln.ac.ckt`](d_trln.ac.ckt) | gnucap | ac, ac, ac, ac | 16 | small | yes | core | - |
| [`d_trln.acp.ckt`](d_trln.acp.ckt) | gnucap | ac, ac, ac, ac | 16 | small | yes | core | - |
| [`d_trln.tr.100.im.ckt`](d_trln.tr.100.im.ckt) | gnucap | tran | 16 | small | yes | core | - |
| [`d_trln.tr.100.nim.ckt`](d_trln.tr.100.nim.ckt) | gnucap | tran | 16 | small | yes | core | - |
| [`d_trln.tr.300.im.ckt`](d_trln.tr.300.im.ckt) | gnucap | tran | 16 | small | yes | core | - |
| [`d_trln.tr.300.nim.ckt`](d_trln.tr.300.nim.ckt) | gnucap | tran | 16 | small | yes | core | - |
| [`d_trln.tr.im.ckt`](d_trln.tr.im.ckt) | gnucap | tran | 16 | small | yes | core | - |
| [`d_trln.tr.nim.ckt`](d_trln.tr.nim.ckt) | gnucap | tran | 16 | small | yes | core | - |
| [`d_vccap.1.ckt`](d_vccap.1.ckt) | gnucap | tran | 7 | tiny | yes | core | - |
| [`d_vccap.2.ckt`](d_vccap.2.ckt) | gnucap | tran | 7 | tiny | yes | core | - |
| [`d_vcg.1.ckt`](d_vcg.1.ckt) | gnucap | op, tran | 8 | tiny | no | core | - |
| [`d_vcg.4.ckt`](d_vcg.4.ckt) | gnucap | op, ac, ac, tran | 8 | tiny | no | core | - |
| [`d_vcr.1.ckt`](d_vcr.1.ckt) | gnucap | op, tran | 8 | tiny | yes | core | - |
| [`d_vcr.2.ckt`](d_vcr.2.ckt) | gnucap | op, tran | 10 | small | yes | core | - |
| [`d_vcr.4.ckt`](d_vcr.4.ckt) | gnucap | op, ac, ac, tran | 8 | tiny | yes | core | - |
| [`d_vcvs.1.ckt`](d_vcvs.1.ckt) | gnucap | op, op, op, ac, ac, ac | 7 | tiny | yes | core | - |
| [`d_vcvs.2.ckt`](d_vcvs.2.ckt) | gnucap | op, op, op, ac, ac, ac | 7 | tiny | yes | core | - |
| [`dcsweep.ckt`](dcsweep.ckt) | gnucap | dc, dc, dc | 6 | tiny | yes | core | - |
| [`e_ccsrc.1.ckt`](e_ccsrc.1.ckt) | gnucap | op, dc, dc, dc | 7 | tiny | yes | core | - |
| [`e_ccsrc.2.ckt`](e_ccsrc.2.ckt) | gnucap | op, dc, dc, dc | 7 | tiny | yes | core | - |
| [`e_node_change0.ckt`](e_node_change0.ckt) | gnucap | dc, dc, dc, dc, dc | 2 | tiny | no | core | - |
| [`e_node_probes.ckt`](e_node_probes.ckt) | gnucap | op, op, op, op, op, op, op | 3 | tiny | yes | core | - |
| [`e_storag.1.ckt`](e_storag.1.ckt) | gnucap | tran | 2 | tiny | yes | core | - |
| [`eq3-1153.ckt`](eq3-1153.ckt) | gnucap | dc, ac | 2561 | large | yes | core | - |
| [`eq3-1153.fg.ckt`](eq3-1153.fg.ckt) | gnucap | dc, ac | 2561 | large | yes | core | - |
| [`eq3-1153.fg2.ckt`](eq3-1153.fg2.ckt) | gnucap | dc, ac | 2562 | large | yes | core | - |
| [`eq3-1153.forward.ckt`](eq3-1153.forward.ckt) | gnucap | dc, ac | 2561 | large | yes | core | - |
| [`eq3-1153.reverse.ckt`](eq3-1153.reverse.ckt) | gnucap | dc, ac | 2561 | large | yes | core | - |
| [`eq3-1153.tr-b.ckt`](eq3-1153.tr-b.ckt) | gnucap | dc, ac, tran | 2561 | large | yes | core | - |
| [`eq3-1153.tr-nb.ckt`](eq3-1153.tr-nb.ckt) | gnucap | dc, ac, tran | 2561 | large | yes | core | - |
| [`eq3-1153.tr-ni.ckt`](eq3-1153.tr-ni.ckt) | gnucap | dc, ac, tran | 2561 | large | yes | core | - |
| [`eq3-1153.trace.ckt`](eq3-1153.trace.ckt) | gnucap | dc, ac | 2561 | large | yes | core | - |
| [`eqb1.ckt`](eqb1.ckt) | gnucap | ac | 81 | small | yes | core | - |
| [`eqboost.ckt`](eqboost.ckt) | gnucap | ac | 81 | small | yes | core | - |
| [`eqflat.ckt`](eqflat.ckt) | gnucap | ac | 81 | small | yes | core | - |
| [`eqmodify.ckt`](eqmodify.ckt) | gnucap | ac, ac | 81 | small | yes | core | - |
| [`grid.0.ckt`](grid.0.ckt) | gnucap | ac | 21 | small | yes | specific (.control script) | - |
| [`grid.1.ckt`](grid.1.ckt) | gnucap | ac | 821 | medium | yes | specific (.control script) | - |
| [`grid.2.ckt`](grid.2.ckt) | gnucap | ac | 7861 | large | yes | specific (.control script) | - |
| [`l.ckt`](l.ckt) | gnucap | tran, ac | 5 | tiny | yes | core | - |
| [`l2.ckt`](l2.ckt) | gnucap | tran, ac | 5 | tiny | yes | core | - |
| [`ll.ckt`](ll.ckt) | gnucap | tran, ac | 5 | tiny | yes | core | - |
| [`ll1.ckt`](ll1.ckt) | gnucap | tran, ac | 5 | tiny | yes | core | - |
| [`lll.ckt`](lll.ckt) | gnucap | tran, ac | 5 | tiny | yes | core | - |
| [`llll.ckt`](llll.ckt) | gnucap | tran, ac | 5 | tiny | yes | core | - |
| [`named_nodes.ckt`](named_nodes.ckt) | gnucap | op | 3 | tiny | yes | core | - |
| [`nmos100.1.ckt`](nmos100.1.ckt) | gnucap | op | 202 | medium | no | core | - |
| [`nmos100.ckt`](nmos100.ckt) | gnucap | op | 202 | medium | no | core | - |
| [`nmos15.ckt`](nmos15.ckt) | gnucap | op, op | 32 | small | no | core | - |
| [`nmos15a.ckt`](nmos15a.ckt) | gnucap | op, op | 32 | small | no | core | - |
| [`nmos1i.ckt`](nmos1i.ckt) | gnucap | op, op, op | 4 | tiny | no | core | - |
| [`nmp100.ckt`](nmp100.ckt) | gnucap | op | 301 | medium | no | core | - |
| [`opamp-ol-disto.2.ckt`](opamp-ol-disto.2.ckt) | gnucap | op, ac, dc, tran | 16 | small | no | core | - |
| [`opamp-ol-disto.ckt`](opamp-ol-disto.ckt) | gnucap | op, ac, dc, tran | 16 | small | no | core | - |
| [`opamp-ol.ckt`](opamp-ol.ckt) | gnucap | op, ac, dc, ac, dc | 15 | small | no | core | - |
| [`opamp-vf.1.ckt`](opamp-vf.1.ckt) | gnucap | op, ac, dc, tran | 14 | small | no | core | - |
| [`opamp-vf.1d.ckt`](opamp-vf.1d.ckt) | gnucap | op, ac, dc, tran | 14 | small | no | core | - |
| [`opamp-vf.2.ckt`](opamp-vf.2.ckt) | gnucap | op, ac, dc, tran | 14 | small | no | core | - |
| [`opamp-vf.3.ckt`](opamp-vf.3.ckt) | gnucap | op, ac, dc, tran | 14 | small | no | core | - |
| [`opamp-vf.ckt`](opamp-vf.ckt) | gnucap | op, ac, dc, tran | 14 | small | no | core | - |
| [`oscillator.1.ckt`](oscillator.1.ckt) | gnucap | tran | 3 | tiny | yes | core | - |
| [`oscillator.2.ckt`](oscillator.2.ckt) | gnucap | tran, tran, tran, tran, tran | 4 | tiny | yes | core | - |
| [`oscillator.3.ckt`](oscillator.3.ckt) | gnucap | tran | 3 | tiny | yes | core | - |
| [`oscillator.4.ckt`](oscillator.4.ckt) | gnucap | tran | 3 | tiny | yes | core | - |
| [`oscillator.5.ckt`](oscillator.5.ckt) | gnucap | tran | 3 | tiny | yes | core | - |
| [`oscillator.6.ckt`](oscillator.6.ckt) | gnucap | tran | 3 | tiny | yes | core | - |
| [`oscillator.7.ckt`](oscillator.7.ckt) | gnucap | tran, tran | 4 | tiny | yes | core | - |
| [`param.0.ckt`](param.0.ckt) | gnucap | op | 1 | tiny | yes | core | - |
| [`param.0a.ckt`](param.0a.ckt) | gnucap | dc | 1 | tiny | yes | core | - |
| [`param.1.ckt`](param.1.ckt) | gnucap | op | 3 | tiny | yes | core | - |
| [`param.11.ckt`](param.11.ckt) | gnucap | op | 7 | tiny | yes | core | - |
| [`param.12.ckt`](param.12.ckt) | gnucap | op | 1 | tiny | yes | core | - |
| [`param.2.ckt`](param.2.ckt) | gnucap | op | 3 | tiny | yes | core | - |
| [`param.2a.ckt`](param.2a.ckt) | gnucap | op | 3 | tiny | yes | core | - |
| [`param.2b.ckt`](param.2b.ckt) | gnucap | op | 3 | tiny | yes | core | - |
| [`param.3.ckt`](param.3.ckt) | gnucap | op | 2 | tiny | yes | core | - |
| [`param.4.ckt`](param.4.ckt) | gnucap | op | 2 | tiny | yes | core | - |
| [`param.5.ckt`](param.5.ckt) | gnucap | op | 3 | tiny | yes | core | - |
| [`param.6.ckt`](param.6.ckt) | gnucap | op | 2 | tiny | yes | core | - |
| [`param.7.ckt`](param.7.ckt) | gnucap | op | 4 | tiny | yes | core | - |
| [`param.8.ckt`](param.8.ckt) | gnucap | op | 4 | tiny | yes | core | - |
| [`param.9.ckt`](param.9.ckt) | gnucap | op | 1 | tiny | yes | core | - |
| [`pwl.spice`](pwl.spice) | gnucap | op, dc, dc, tran, tran, ac, ac | 32 | small | yes | core | - |
| [`s_dc.bin1.ckt`](s_dc.bin1.ckt) | gnucap | dc, dc, dc | 1 | tiny | no | core | - |
| [`s_tr.1.ckt`](s_tr.1.ckt) | gnucap | tran, tran, tran, tran, tran | 3 | tiny | yes | core | - |
| [`sl.ckt`](sl.ckt) | gnucap | op | 5 | tiny | no | core | - |
| [`trcurve.ckt`](trcurve.ckt) | gnucap | dc, dc | 8 | tiny | no | core | - |
| [`trcurve2.ckt`](trcurve2.ckt) | gnucap | op, dc, dc | 8 | tiny | no | core | - |
| [`trcurves.ckt`](trcurves.ckt) | gnucap | dc, dc | 8 | tiny | no | core | - |
| [`trunc-euler.ckt`](trunc-euler.ckt) | gnucap | tran | 5 | tiny | yes | core | - |
| [`trunc-gear.ckt`](trunc-gear.ckt) | gnucap | tran | 5 | tiny | yes | core | - |
| [`trunc-trap.ckt`](trunc-trap.ckt) | gnucap | tran | 5 | tiny | yes | core | - |
| [`vs.spice`](vs.spice) | gnucap | op, dc, ac, tran | 5 | tiny | yes | core | - |

Devices: instances once the subcircuits defined in this case are expanded; a device from a library or a compiled model counts once. Size, linear and portability: see the top README.

## Notes

Left out:
- `d_subckt.delete.0.ckt`: uses subcircuit x1, defined nowhere
- `d_subckt.error1.ckt`: uses subcircuit foo, defined nowhere
- `d_subckt.error2.ckt`: uses subcircuit foo, defined nowhere
- `d_subckt.error4.ckt`: uses subcircuit x1, defined nowhere

Generated by `python -m circref build`. Do not edit by hand.
