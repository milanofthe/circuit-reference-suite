# neospice tests/circuits

test | ngspice | status: **complete**

## Source

- Authors: neospice contributors
- URL: https://github.com/razorback16/neospice (commit `7f81041ea0f03533da18a59b95ff8e708e3206bd`)
- License: MIT

## Netlists

| file | dialect | analyses | devices | libraries |
|---|---|---|---|---|
| [`tests/circuits/am_offsets_phases.cir`](tests/circuits/am_offsets_phases.cir) | ngspice | tran | 4 | - |
| [`tests/circuits/am_source.cir`](tests/circuits/am_source.cir) | ngspice | tran | 2 | - |
| [`tests/circuits/asrc_ac_gain.cir`](tests/circuits/asrc_ac_gain.cir) | ngspice | ac | 3 | - |
| [`tests/circuits/asrc_ddt.cir`](tests/circuits/asrc_ddt.cir) | ngspice | tran | 4 | - |
| [`tests/circuits/asrc_hertz.cir`](tests/circuits/asrc_hertz.cir) | ngspice | op | 3 | - |
| [`tests/circuits/asrc_idt.cir`](tests/circuits/asrc_idt.cir) | ngspice | tran | 4 | - |
| [`tests/circuits/asrc_multi_var.cir`](tests/circuits/asrc_multi_var.cir) | ngspice | op | 4 | - |
| [`tests/circuits/asrc_pwl.cir`](tests/circuits/asrc_pwl.cir) | ngspice | op | 3 | - |
| [`tests/circuits/asrc_square.cir`](tests/circuits/asrc_square.cir) | ngspice | op | 3 | - |
| [`tests/circuits/asrc_tempco.cir`](tests/circuits/asrc_tempco.cir) | ngspice | op | 3 | - |
| [`tests/circuits/asrc_tempco_current.cir`](tests/circuits/asrc_tempco_current.cir) | ngspice | op | 3 | - |
| [`tests/circuits/asrc_temper.cir`](tests/circuits/asrc_temper.cir) | ngspice | op | 3 | - |
| [`tests/circuits/asrc_trig.cir`](tests/circuits/asrc_trig.cir) | ngspice | op | 3 | - |
| [`tests/circuits/asrc_vccs.cir`](tests/circuits/asrc_vccs.cir) | ngspice | op | 3 | - |
| [`tests/circuits/asrc_voltage_doubler.cir`](tests/circuits/asrc_voltage_doubler.cir) | ngspice | op | 3 | - |
| [`tests/circuits/bc547a_test.cir`](tests/circuits/bc547a_test.cir) | ngspice | op, ac | 11 | - |
| [`tests/circuits/bjt_ce_noise.cir`](tests/circuits/bjt_ce_noise.cir) | ngspice | noise | 5 | - |
| [`tests/circuits/bjt_off_bias.cir`](tests/circuits/bjt_off_bias.cir) | ngspice | op | 20 | - |
| [`tests/circuits/bsim3_cmos_inverter.cir`](tests/circuits/bsim3_cmos_inverter.cir) | ngspice | tran | 5 | - |
| [`tests/circuits/bsim3_nmos_ac.cir`](tests/circuits/bsim3_nmos_ac.cir) | ngspice | ac | 4 | - |
| [`tests/circuits/bsim3_nmos_dc.cir`](tests/circuits/bsim3_nmos_dc.cir) | ngspice | op | 3 | - |
| [`tests/circuits/bsim3_nmos_iv.cir`](tests/circuits/bsim3_nmos_iv.cir) | ngspice | dc | 3 | - |
| [`tests/circuits/bsim3_pmos_dc.cir`](tests/circuits/bsim3_pmos_dc.cir) | ngspice | op | 3 | - |
| [`tests/circuits/bsim3v32_nmos_ac.cir`](tests/circuits/bsim3v32_nmos_ac.cir) | ngspice | ac | 4 | - |
| [`tests/circuits/bsim3v32_nmos_dc_op.cir`](tests/circuits/bsim3v32_nmos_dc_op.cir) | ngspice | op | 3 | - |
| [`tests/circuits/bsimsoi_nmos_ac.cir`](tests/circuits/bsimsoi_nmos_ac.cir) | ngspice | ac | 4 | - |
| [`tests/circuits/bsimsoi_nmos_dc_op.cir`](tests/circuits/bsimsoi_nmos_dc_op.cir) | ngspice | op | 4 | - |
| [`tests/circuits/bsimsoi_pmos_dc_op.cir`](tests/circuits/bsimsoi_pmos_dc_op.cir) | ngspice | op | 4 | - |
| [`tests/circuits/cccs_poly.cir`](tests/circuits/cccs_poly.cir) | ngspice | op | 5 | - |
| [`tests/circuits/cccs_poly2.cir`](tests/circuits/cccs_poly2.cir) | ngspice | op | 8 | - |
| [`tests/circuits/ccvs_poly.cir`](tests/circuits/ccvs_poly.cir) | ngspice | op | 5 | - |
| [`tests/circuits/cmos_inverter.cir`](tests/circuits/cmos_inverter.cir) | ngspice | tran | 5 | - |
| [`tests/circuits/cmos_inverter_resistance.cir`](tests/circuits/cmos_inverter_resistance.cir) | ngspice | tran | 4 | - |
| [`tests/circuits/coupled_inductor_ac.cir`](tests/circuits/coupled_inductor_ac.cir) | ngspice | ac | 6 | - |
| [`tests/circuits/coupled_inductor_dc.cir`](tests/circuits/coupled_inductor_dc.cir) | ngspice | op | 5 | - |
| [`tests/circuits/coupled_inductor_transient.cir`](tests/circuits/coupled_inductor_transient.cir) | ngspice | tran | 6 | - |
| [`tests/circuits/dc_current_sweep.cir`](tests/circuits/dc_current_sweep.cir) | ngspice | dc | 2 | - |
| [`tests/circuits/dc_nested.cir`](tests/circuits/dc_nested.cir) | ngspice | dc | 5 | - |
| [`tests/circuits/diode_ac_response.cir`](tests/circuits/diode_ac_response.cir) | ngspice | ac | 3 | - |
| [`tests/circuits/diode_dc_sweep.cir`](tests/circuits/diode_dc_sweep.cir) | ngspice | dc | 3 | - |
| [`tests/circuits/diode_flicker_noise.cir`](tests/circuits/diode_flicker_noise.cir) | ngspice | noise | 3 | - |
| [`tests/circuits/diode_grading_ac.cir`](tests/circuits/diode_grading_ac.cir) | ngspice | ac | 20 | - |
| [`tests/circuits/diode_grading_transient.cir`](tests/circuits/diode_grading_transient.cir) | ngspice | tran | 3 | - |
| [`tests/circuits/diode_iv.cir`](tests/circuits/diode_iv.cir) | ngspice | op | 3 | - |
| [`tests/circuits/diode_noise.cir`](tests/circuits/diode_noise.cir) | ngspice | noise | 3 | - |
| [`tests/circuits/diode_rectifier.cir`](tests/circuits/diode_rectifier.cir) | ngspice | tran | 4 | - |
| [`tests/circuits/diode_temperature_noise_delta.cir`](tests/circuits/diode_temperature_noise_delta.cir) | ngspice | noise | 3 | - |
| [`tests/circuits/diode_temperature_noise_hot.cir`](tests/circuits/diode_temperature_noise_hot.cir) | ngspice | noise | 3 | - |
| [`tests/circuits/diode_temperature_noise_zero.cir`](tests/circuits/diode_temperature_noise_zero.cir) | ngspice | noise | 3 | - |
| [`tests/circuits/diode_transient.cir`](tests/circuits/diode_transient.cir) | ngspice | tran | 3 | - |
| [`tests/circuits/exp_source.cir`](tests/circuits/exp_source.cir) | ngspice | tran | 3 | - |
| [`tests/circuits/hfet1_nfet_ac.cir`](tests/circuits/hfet1_nfet_ac.cir) | ngspice | ac | 4 | - |
| [`tests/circuits/hfet1_nfet_dc_op.cir`](tests/circuits/hfet1_nfet_dc_op.cir) | ngspice | op | 3 | - |
| [`tests/circuits/hfet2_nfet_ac.cir`](tests/circuits/hfet2_nfet_ac.cir) | ngspice | ac | 4 | - |
| [`tests/circuits/hfet2_nfet_dc_op.cir`](tests/circuits/hfet2_nfet_dc_op.cir) | ngspice | op | 3 | - |
| [`tests/circuits/hfet2_nfet_iv_sweep.cir`](tests/circuits/hfet2_nfet_iv_sweep.cir) | ngspice | dc | 3 | - |
| [`tests/circuits/hfet2_nfet_transient.cir`](tests/circuits/hfet2_nfet_transient.cir) | ngspice | tran | 4 | - |
| [`tests/circuits/hisim2_nmos_ac.cir`](tests/circuits/hisim2_nmos_ac.cir) | ngspice | ac | 4 | - |
| [`tests/circuits/hisim2_nmos_dc_op.cir`](tests/circuits/hisim2_nmos_dc_op.cir) | ngspice | op | 4 | - |
| [`tests/circuits/hisim2_nmos_iv_sweep.cir`](tests/circuits/hisim2_nmos_iv_sweep.cir) | ngspice | dc | 3 | - |
| [`tests/circuits/hisim2_pmos_dc_op.cir`](tests/circuits/hisim2_pmos_dc_op.cir) | ngspice | op | 4 | - |
| [`tests/circuits/hisimhv_nmos_ac.cir`](tests/circuits/hisimhv_nmos_ac.cir) | ngspice | ac | 4 | - |
| [`tests/circuits/hisimhv_nmos_dc_op.cir`](tests/circuits/hisimhv_nmos_dc_op.cir) | ngspice | op | 4 | - |
| [`tests/circuits/hisimhv_nmos_noise.cir`](tests/circuits/hisimhv_nmos_noise.cir) | ngspice | noise | 4 | - |
| [`tests/circuits/hisimhv_pmos_dc_op.cir`](tests/circuits/hisimhv_pmos_dc_op.cir) | ngspice | op | 4 | - |
| [`tests/circuits/inductor_model.cir`](tests/circuits/inductor_model.cir) | ngspice | ac | 3 | - |
| [`tests/circuits/isrc_ac.cir`](tests/circuits/isrc_ac.cir) | ngspice | ac | 3 | - |
| [`tests/circuits/jfet2_njf_ac.cir`](tests/circuits/jfet2_njf_ac.cir) | ngspice | ac | 4 | - |
| [`tests/circuits/jfet2_njf_dc.cir`](tests/circuits/jfet2_njf_dc.cir) | ngspice | op | 4 | - |
| [`tests/circuits/jfet2_njf_tran.cir`](tests/circuits/jfet2_njf_tran.cir) | ngspice | tran | 4 | - |
| [`tests/circuits/jfet_noise.cir`](tests/circuits/jfet_noise.cir) | ngspice | noise | 5 | - |
| [`tests/circuits/ltra_ac_lc.cir`](tests/circuits/ltra_ac_lc.cir) | ngspice | ac | 4 | - |
| [`tests/circuits/ltra_ac_lc_floating.cir`](tests/circuits/ltra_ac_lc_floating.cir) | ngspice | ac | 6 | - |
| [`tests/circuits/ltra_ac_rc.cir`](tests/circuits/ltra_ac_rc.cir) | ngspice | ac | 4 | - |
| [`tests/circuits/ltra_ac_rg.cir`](tests/circuits/ltra_ac_rg.cir) | ngspice | ac | 4 | - |
| [`tests/circuits/ltra_ac_rg_options.cir`](tests/circuits/ltra_ac_rg_options.cir) | ngspice | ac | 4 | - |
| [`tests/circuits/ltra_ac_rlc.cir`](tests/circuits/ltra_ac_rlc.cir) | ngspice | ac | 4 | - |
| [`tests/circuits/ltra_dc_rc.cir`](tests/circuits/ltra_dc_rc.cir) | ngspice | op | 3 | - |
| [`tests/circuits/ltra_dc_rg.cir`](tests/circuits/ltra_dc_rg.cir) | ngspice | op | 3 | - |
| [`tests/circuits/ltra_tran_lc.cir`](tests/circuits/ltra_tran_lc.cir) | ngspice | tran | 3 | - |
| [`tests/circuits/ltra_tran_rc.cir`](tests/circuits/ltra_tran_rc.cir) | ngspice | tran | 3 | - |
| [`tests/circuits/ltra_tran_rlc.cir`](tests/circuits/ltra_tran_rlc.cir) | ngspice | tran | 3 | - |
| [`tests/circuits/mes_ac.cir`](tests/circuits/mes_ac.cir) | ngspice | ac | 3 | - |
| [`tests/circuits/mes_dc_op.cir`](tests/circuits/mes_dc_op.cir) | ngspice | op | 3 | - |
| [`tests/circuits/mes_noise_area.cir`](tests/circuits/mes_noise_area.cir) | ngspice | noise | 4 | - |
| [`tests/circuits/mes_noise_area_last.cir`](tests/circuits/mes_noise_area_last.cir) | ngspice | noise | 4 | - |
| [`tests/circuits/mes_noise_flicker.cir`](tests/circuits/mes_noise_flicker.cir) | ngspice | noise | 4 | - |
| [`tests/circuits/mes_noise_hot.cir`](tests/circuits/mes_noise_hot.cir) | ngspice | noise | 4 | - |
| [`tests/circuits/mes_noise_multiplier.cir`](tests/circuits/mes_noise_multiplier.cir) | ngspice | noise | 4 | - |
| [`tests/circuits/mes_noise_pmf.cir`](tests/circuits/mes_noise_pmf.cir) | ngspice | noise | 4 | - |
| [`tests/circuits/mes_noise_scaled_hot.cir`](tests/circuits/mes_noise_scaled_hot.cir) | ngspice | noise | 4 | - |
| [`tests/circuits/mes_noise_state_offset.cir`](tests/circuits/mes_noise_state_offset.cir) | ngspice | noise | 7 | - |
| [`tests/circuits/mes_noise_thermal.cir`](tests/circuits/mes_noise_thermal.cir) | ngspice | noise | 4 | - |
| [`tests/circuits/mes_parallel.cir`](tests/circuits/mes_parallel.cir) | ngspice | op, ac, tran | 7 | - |
| [`tests/circuits/model_expression_precedence_0.cir`](tests/circuits/model_expression_precedence_0.cir) | ngspice | op | 18 | - |
| [`tests/circuits/model_expression_precedence_27.cir`](tests/circuits/model_expression_precedence_27.cir) | ngspice | op | 18 | - |
| [`tests/circuits/model_expression_precedence_60.cir`](tests/circuits/model_expression_precedence_60.cir) | ngspice | op | 18 | - |
| [`tests/circuits/model_expression_precedence_direct_0.cir`](tests/circuits/model_expression_precedence_direct_0.cir) | ngspice | op | 18 | - |
| [`tests/circuits/model_expression_precedence_direct_27.cir`](tests/circuits/model_expression_precedence_direct_27.cir) | ngspice | op | 18 | - |
| [`tests/circuits/model_expression_precedence_direct_60.cir`](tests/circuits/model_expression_precedence_direct_60.cir) | ngspice | op | 18 | - |
| [`tests/circuits/model_temperature_0.cir`](tests/circuits/model_temperature_0.cir) | ngspice | ac, op | 10 | - |
| [`tests/circuits/model_temperature_27.cir`](tests/circuits/model_temperature_27.cir) | ngspice | ac, op | 10 | - |
| [`tests/circuits/model_temperature_60.cir`](tests/circuits/model_temperature_60.cir) | ngspice | ac, op | 10 | - |
| [`tests/circuits/mos1_nmos_ac.cir`](tests/circuits/mos1_nmos_ac.cir) | ngspice | ac | 4 | - |
| [`tests/circuits/mos1_nmos_dc_op.cir`](tests/circuits/mos1_nmos_dc_op.cir) | ngspice | op | 4 | - |
| [`tests/circuits/mos1_nmos_iv_sweep.cir`](tests/circuits/mos1_nmos_iv_sweep.cir) | ngspice | dc | 3 | - |
| [`tests/circuits/mos1_nmos_transient.cir`](tests/circuits/mos1_nmos_transient.cir) | ngspice | tran | 5 | - |
| [`tests/circuits/mos1_pmos_dc_op.cir`](tests/circuits/mos1_pmos_dc_op.cir) | ngspice | op | 4 | - |
| [`tests/circuits/mos2_nmos_ac.cir`](tests/circuits/mos2_nmos_ac.cir) | ngspice | ac | 4 | - |
| [`tests/circuits/mos2_nmos_dc_op.cir`](tests/circuits/mos2_nmos_dc_op.cir) | ngspice | op | 4 | - |
| [`tests/circuits/mos2_pmos_dc_op.cir`](tests/circuits/mos2_pmos_dc_op.cir) | ngspice | op | 4 | - |
| [`tests/circuits/mos3_diode_temperature_0.cir`](tests/circuits/mos3_diode_temperature_0.cir) | ngspice | ac, op | 12 | - |
| [`tests/circuits/mos3_diode_temperature_27.cir`](tests/circuits/mos3_diode_temperature_27.cir) | ngspice | ac, op | 12 | - |
| [`tests/circuits/mos3_diode_temperature_60.cir`](tests/circuits/mos3_diode_temperature_60.cir) | ngspice | ac, op | 12 | - |
| [`tests/circuits/mos3_nmos_ac.cir`](tests/circuits/mos3_nmos_ac.cir) | ngspice | ac | 4 | - |
| [`tests/circuits/mos3_nmos_dc_op.cir`](tests/circuits/mos3_nmos_dc_op.cir) | ngspice | op | 4 | - |
| [`tests/circuits/mos3_nmos_iv_sweep.cir`](tests/circuits/mos3_nmos_iv_sweep.cir) | ngspice | dc | 3 | - |
| [`tests/circuits/mos3_nmos_transient.cir`](tests/circuits/mos3_nmos_transient.cir) | ngspice | tran | 5 | - |
| [`tests/circuits/mos3_pmos_dc_op.cir`](tests/circuits/mos3_pmos_dc_op.cir) | ngspice | op | 4 | - |
| [`tests/circuits/mos9_nmos_ac.cir`](tests/circuits/mos9_nmos_ac.cir) | ngspice | ac | 4 | - |
| [`tests/circuits/mos9_nmos_dc_op.cir`](tests/circuits/mos9_nmos_dc_op.cir) | ngspice | op | 4 | - |
| [`tests/circuits/mos_model_node_collision.cir`](tests/circuits/mos_model_node_collision.cir) | ngspice | op | 10 | - |
| [`tests/circuits/nmos_cs_amp_ac.cir`](tests/circuits/nmos_cs_amp_ac.cir) | ngspice | ac | 4 | - |
| [`tests/circuits/nmos_iv.cir`](tests/circuits/nmos_iv.cir) | ngspice | op | 3 | - |
| [`tests/circuits/nmos_noise.cir`](tests/circuits/nmos_noise.cir) | ngspice | noise | 4 | - |
| [`tests/circuits/nmos_noise_tnoi2.cir`](tests/circuits/nmos_noise_tnoi2.cir) | ngspice | noise | 4 | - |
| [`tests/circuits/nmos_nqs_ac.cir`](tests/circuits/nmos_nqs_ac.cir) | ngspice | ac | 4 | - |
| [`tests/circuits/nmos_rbodymod.cir`](tests/circuits/nmos_rbodymod.cir) | ngspice | op | 3 | - |
| [`tests/circuits/nmos_rdsmod.cir`](tests/circuits/nmos_rdsmod.cir) | ngspice | op | 3 | - |
| [`tests/circuits/nmos_rgatemod.cir`](tests/circuits/nmos_rgatemod.cir) | ngspice | op | 3 | - |
| [`tests/circuits/nmos_single_bias.cir`](tests/circuits/nmos_single_bias.cir) | ngspice | op | 3 | - |
| [`tests/circuits/noise_gain_floor_above.cir`](tests/circuits/noise_gain_floor_above.cir) | ngspice | noise | 4 | - |
| [`tests/circuits/noise_gain_floor_below.cir`](tests/circuits/noise_gain_floor_below.cir) | ngspice | noise | 4 | - |
| [`tests/circuits/noise_gain_floor_boundary.cir`](tests/circuits/noise_gain_floor_boundary.cir) | ngspice | noise | 4 | - |
| [`tests/circuits/noise_gain_floor_zero.cir`](tests/circuits/noise_gain_floor_zero.cir) | ngspice | noise | 4 | - |
| [`tests/circuits/noise_ltra_lc_matched.cir`](tests/circuits/noise_ltra_lc_matched.cir) | ngspice | noise | 4 | - |
| [`tests/circuits/noise_tline_matched.cir`](tests/circuits/noise_tline_matched.cir) | ngspice | noise | 4 | - |
| [`tests/circuits/opa1632_test.cir`](tests/circuits/opa1632_test.cir) | ngspice | op, ac | 367 | - |
| [`tests/circuits/pulse_defaults.cir`](tests/circuits/pulse_defaults.cir) | ngspice | tran | 2 | - |
| [`tests/circuits/pwl_source.cir`](tests/circuits/pwl_source.cir) | ngspice | tran | 2 | - |
| [`tests/circuits/rc_ac.cir`](tests/circuits/rc_ac.cir) | ngspice | ac | 3 | - |
| [`tests/circuits/rc_lowpass.cir`](tests/circuits/rc_lowpass.cir) | ngspice | tran | 3 | - |
| [`tests/circuits/rc_lowpass_noise.cir`](tests/circuits/rc_lowpass_noise.cir) | ngspice | noise | 3 | - |
| [`tests/circuits/resistor_divider.cir`](tests/circuits/resistor_divider.cir) | ngspice | op | 3 | - |
| [`tests/circuits/resistor_divider_noise.cir`](tests/circuits/resistor_divider_noise.cir) | ngspice | noise | 3 | - |
| [`tests/circuits/resistor_m2.cir`](tests/circuits/resistor_m2.cir) | ngspice | op | 2 | - |
| [`tests/circuits/resistor_model.cir`](tests/circuits/resistor_model.cir) | ngspice | op | 3 | - |
| [`tests/circuits/resistor_noise_hot.cir`](tests/circuits/resistor_noise_hot.cir) | ngspice | noise | 3 | - |
| [`tests/circuits/resistor_rac.cir`](tests/circuits/resistor_rac.cir) | ngspice | ac | 3 | - |
| [`tests/circuits/resistor_temp.cir`](tests/circuits/resistor_temp.cir) | ngspice | op | 2 | - |
| [`tests/circuits/ring_osc_5stage.cir`](tests/circuits/ring_osc_5stage.cir) | ngspice | tran | 11 | - |
| [`tests/circuits/rlc_series.cir`](tests/circuits/rlc_series.cir) | ngspice | tran | 4 | - |
| [`tests/circuits/rlc_underdamped.cir`](tests/circuits/rlc_underdamped.cir) | ngspice | tran | 4 | - |
| [`tests/circuits/sens_divider.cir`](tests/circuits/sens_divider.cir) | ngspice | sens | 3 | - |
| [`tests/circuits/sffm_source.cir`](tests/circuits/sffm_source.cir) | ngspice | tran | 2 | - |
| [`tests/circuits/step_resistor.cir`](tests/circuits/step_resistor.cir) | ngspice | step, op | 3 | - |
| [`tests/circuits/switch_hysteresis.cir`](tests/circuits/switch_hysteresis.cir) | ngspice | tran | 4 | - |
| [`tests/circuits/tf_resistive_divider.cir`](tests/circuits/tf_resistive_divider.cir) | ngspice | tf | 4 | - |
| [`tests/circuits/tline_ac.cir`](tests/circuits/tline_ac.cir) | ngspice | ac | 4 | - |
| [`tests/circuits/tline_dc.cir`](tests/circuits/tline_dc.cir) | ngspice | op | 4 | - |
| [`tests/circuits/tline_ic.cir`](tests/circuits/tline_ic.cir) | ngspice | tran | 4 | - |
| [`tests/circuits/tline_ic_no_uic.cir`](tests/circuits/tline_ic_no_uic.cir) | ngspice | tran | 4 | - |
| [`tests/circuits/tlv3201_open_loop.cir`](tests/circuits/tlv3201_open_loop.cir) | ngspice | tran | 227 | - |
| [`tests/circuits/tlv3201_switching.cir`](tests/circuits/tlv3201_switching.cir) | ngspice | tran | 227 | - |
| [`tests/circuits/uic_current_integrator.cir`](tests/circuits/uic_current_integrator.cir) | ngspice | tran | 4 | - |
| [`tests/circuits/uic_resistor.cir`](tests/circuits/uic_resistor.cir) | ngspice | tran | 2 | - |
| [`tests/circuits/unused_model_name_collisions.cir`](tests/circuits/unused_model_name_collisions.cir) | ngspice | op | 5 | - |
| [`tests/circuits/vbic_ac.cir`](tests/circuits/vbic_ac.cir) | ngspice | ac | 8 | - |
| [`tests/circuits/vbic_delay_ac.cir`](tests/circuits/vbic_delay_ac.cir) | ngspice | ac | 32 | - |
| [`tests/circuits/vbic_delay_gear.cir`](tests/circuits/vbic_delay_gear.cir) | ngspice | tran | 32 | - |
| [`tests/circuits/vbic_delay_noise.cir`](tests/circuits/vbic_delay_noise.cir) | ngspice | noise | 5 | - |
| [`tests/circuits/vbic_delay_noise_pnp.cir`](tests/circuits/vbic_delay_noise_pnp.cir) | ngspice | noise | 5 | - |
| [`tests/circuits/vbic_delay_transient.cir`](tests/circuits/vbic_delay_transient.cir) | ngspice | tran | 32 | - |
| [`tests/circuits/vbic_delay_uic.cir`](tests/circuits/vbic_delay_uic.cir) | ngspice | tran | 32 | - |
| [`tests/circuits/vbic_gummel.cir`](tests/circuits/vbic_gummel.cir) | ngspice | dc | 3 | - |
| [`tests/circuits/vbic_model_syntax.cir`](tests/circuits/vbic_model_syntax.cir) | ngspice | op | 27 | - |
| [`tests/circuits/vbic_npn_dc.cir`](tests/circuits/vbic_npn_dc.cir) | ngspice | op | 4 | - |
| [`tests/circuits/vbic_pnp_dc.cir`](tests/circuits/vbic_pnp_dc.cir) | ngspice | op | 4 | - |
| [`tests/circuits/vbic_transient.cir`](tests/circuits/vbic_transient.cir) | ngspice | tran | 5 | - |
| [`tests/circuits/vdmos_internal_nodes.cir`](tests/circuits/vdmos_internal_nodes.cir) | ngspice | op | 4 | - |
| [`tests/circuits/vdmos_model_scope.cir`](tests/circuits/vdmos_model_scope.cir) | ngspice | op | 18 | - |
| [`tests/circuits/vdmos_model_temperature_0.cir`](tests/circuits/vdmos_model_temperature_0.cir) | ngspice | op | 18 | - |
| [`tests/circuits/vdmos_model_temperature_27.cir`](tests/circuits/vdmos_model_temperature_27.cir) | ngspice | op | 18 | - |
| [`tests/circuits/vdmos_model_temperature_60.cir`](tests/circuits/vdmos_model_temperature_60.cir) | ngspice | op | 18 | - |
| [`tests/circuits/vdmos_nmos_ac.cir`](tests/circuits/vdmos_nmos_ac.cir) | ngspice | ac | 4 | - |
| [`tests/circuits/vdmos_nmos_dc_op.cir`](tests/circuits/vdmos_nmos_dc_op.cir) | ngspice | op | 4 | - |
| [`tests/circuits/vdmos_nmos_iv_sweep.cir`](tests/circuits/vdmos_nmos_iv_sweep.cir) | ngspice | dc | 3 | - |
| [`tests/circuits/vdmos_nmos_noise.cir`](tests/circuits/vdmos_nmos_noise.cir) | ngspice | noise | 4 | - |
| [`tests/circuits/vdmos_pmos_dc_op.cir`](tests/circuits/vdmos_pmos_dc_op.cir) | ngspice | op | 4 | - |
| [`tests/circuits/vdmos_terminal_forms.cir`](tests/circuits/vdmos_terminal_forms.cir) | ngspice | op | 24 | - |
| [`tests/circuits/vdmos_thermal_isothermal.cir`](tests/circuits/vdmos_thermal_isothermal.cir) | ngspice | op | 4 | - |
| [`tests/circuits/vdmos_thermal_selfheat.cir`](tests/circuits/vdmos_thermal_selfheat.cir) | ngspice | op | 3 | - |
| [`tests/circuits/vdmos_thermal_selfheat_subckt.cir`](tests/circuits/vdmos_thermal_selfheat_subckt.cir) | ngspice | op | 3 | - |
| [`tests/circuits/vdmos_theta.cir`](tests/circuits/vdmos_theta.cir) | ngspice | op | 15 | - |

Devices: instances once the subcircuits defined in this case are expanded; a device from a library or a compiled model counts once.

## Notes

Left out:
- `tests/circuits/lm358_ns_test.cir`: needs tests/circuits/lm358_ns.lib, not redistributable
- `tests/circuits/rff70n06_op.cir.in`: needs @NEOSPICE_RFF70N06_LIBRARY@, not in the source tree
- `tests/circuits/ths4131_diff_amp.cir`: needs tests/circuits/ths4131.lib, not redistributable
- `tests/circuits/tlv3201_test.cir`: needs tests/circuits/tlv3201.lib, not redistributable

Generated by `python -m circref build`. Do not edit by hand.
