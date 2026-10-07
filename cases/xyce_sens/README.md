# Xyce_Regression SENS

test | xyce | status: **complete**

## Source

- Authors: Sandia National Laboratories
- URL: https://github.com/Xyce/Xyce_Regression (commit `7bb7e98f0ed3a81a7d1cf1d10b68592107ed40b2`)
- Path: `Netlists/SENS`
- License: GPL-3.0-or-later

## Netlists

| file | dialect | analyses | devices | size | linear | portability | libraries |
|---|---|---|---|---|---|---|---|
| [`150nm_nmos.cir`](150nm_nmos.cir) | xyce | dc, sens | 9 | tiny | no | specific (analysis sens) | - |
| [`150nm_nmosFD.cir`](150nm_nmosFD.cir) | xyce | dc, sens | 9 | tiny | no | specific (analysis sens) | - |
| [`150nm_nmos_deviceFD.cir`](150nm_nmos_deviceFD.cir) | xyce | dc, sens | 9 | tiny | no | specific (analysis sens) | - |
| [`150nm_nmos_oldFD.cir`](150nm_nmos_oldFD.cir) | xyce | dc, sens | 9 | tiny | no | specific (analysis sens) | - |
| [`150nm_pmos.cir`](150nm_pmos.cir) | xyce | dc, sens | 9 | tiny | no | specific (analysis sens) | - |
| [`150nm_pmosFD.cir`](150nm_pmosFD.cir) | xyce | dc, sens | 9 | tiny | no | specific (analysis sens) | - |
| [`ampSens.cir`](ampSens.cir) | xyce | op, dc, sens, op | 7 | tiny | no | specific (analysis sens) | - |
| [`ampSensAdj.cir`](ampSensAdj.cir) | xyce | op, dc, sens, op | 7 | tiny | no | specific (analysis sens) | - |
| [`ampSensAdj_aztec.cir`](ampSensAdj_aztec.cir) | xyce | op, dc, sens, op | 7 | tiny | no | specific (analysis sens) | - |
| [`ampSensAdj_belos.cir`](ampSensAdj_belos.cir) | xyce | op, dc, sens, op | 7 | tiny | no | specific (analysis sens) | - |
| [`ampSensFD.cir`](ampSensFD.cir) | xyce | dc | 133 | medium | no | core | - |
| [`ampSensFDa.cir`](ampSensFDa.cir) | xyce | dc | 133 | medium | no | core | - |
| [`ampSensFDb.cir`](ampSensFDb.cir) | xyce | dc | 133 | medium | no | core | - |
| [`ampSensFDc.cir`](ampSensFDc.cir) | xyce | dc | 133 | medium | no | core | - |
| [`ampSens_10v.cir`](ampSens_10v.cir) | xyce | dc, sens, op | 7 | tiny | no | specific (analysis sens) | - |
| [`ampSens_fbh.cir`](ampSens_fbh.cir) | xyce | dc, sens | 7 | tiny | no | specific (analysis sens) | - |
| [`ampSens_fbhFD.cir`](ampSens_fbhFD.cir) | xyce | dc, sens | 7 | tiny | no | specific (analysis sens) | - |
| [`ampSens_fbhPNP.cir`](ampSens_fbhPNP.cir) | xyce | dc, sens | 7 | tiny | no | specific (analysis sens) | - |
| [`ampSens_fbhPNPFD.cir`](ampSens_fbhPNPFD.cir) | xyce | dc, sens | 7 | tiny | no | specific (analysis sens) | - |
| [`ampSens_hicum.cir`](ampSens_hicum.cir) | xyce | dc, sens | 7 | tiny | no | specific (analysis sens) | - |
| [`ampSens_hicumFD.cir`](ampSens_hicumFD.cir) | xyce | dc, sens | 7 | tiny | no | specific (analysis sens) | - |
| [`ampSens_hicumL0.cir`](ampSens_hicumL0.cir) | xyce | dc, sens | 7 | tiny | no | specific (analysis sens) | - |
| [`ampSens_hicumL0FD.cir`](ampSens_hicumL0FD.cir) | xyce | dc, sens | 7 | tiny | no | specific (analysis sens) | - |
| [`ampSens_mextram.cir`](ampSens_mextram.cir) | xyce | dc, sens | 7 | tiny | no | specific (analysis sens) | - |
| [`ampSens_mextramFD.cir`](ampSens_mextramFD.cir) | xyce | dc, sens | 7 | tiny | no | specific (analysis sens) | - |
| [`ampSens_mextramPNP.cir`](ampSens_mextramPNP.cir) | xyce | dc, sens | 7 | tiny | no | specific (analysis sens) | - |
| [`ampSens_mextramPNPFD.cir`](ampSens_mextramPNPFD.cir) | xyce | dc, sens | 7 | tiny | no | specific (analysis sens) | - |
| [`ampSens_op.cir`](ampSens_op.cir) | xyce | op, sens, op | 7 | tiny | no | specific (analysis sens) | - |
| [`ampSens_vbic.cir`](ampSens_vbic.cir) | xyce | dc, sens | 7 | tiny | no | specific (analysis sens) | - |
| [`ampSens_vbicFD.cir`](ampSens_vbicFD.cir) | xyce | dc, sens | 7 | tiny | no | specific (analysis sens) | - |
| [`ampSens_vbicPNPdefault.cir`](ampSens_vbicPNPdefault.cir) | xyce | dc, sens | 7 | tiny | no | specific (analysis sens) | - |
| [`ampSens_vbicPNPdefaultFD.cir`](ampSens_vbicPNPdefaultFD.cir) | xyce | dc, sens | 7 | tiny | no | specific (analysis sens) | - |
| [`bsim3Inv.cir`](bsim3Inv.cir) | xyce | tran, sens | 9 | tiny | no | specific (analysis sens) | - |
| [`bsim3Inv_newFD.cir`](bsim3Inv_newFD.cir) | xyce | tran, sens | 9 | tiny | no | specific (analysis sens) | - |
| [`bsim3Inv_oldFD.cir`](bsim3Inv_oldFD.cir) | xyce | tran, sens | 9 | tiny | no | specific (analysis sens) | - |
| [`bsim4_issue694.cir`](bsim4_issue694.cir) | xyce | tran, sens | 4 | tiny | no | specific (analysis sens) | - |
| [`bsim4_issue694_FD.cir`](bsim4_issue694_FD.cir) | xyce | tran | 8 | tiny | no | core | - |
| [`bsim4_issue694_ref.cir`](bsim4_issue694_ref.cir) | xyce | tran, sens | 4 | tiny | no | specific (analysis sens) | - |
| [`bsim6invAdjoint.cir`](bsim6invAdjoint.cir) | xyce | tran, sens | 12 | small | no | specific (analysis sens) | - |
| [`bsim6invAdjointForceAnalytic.cir`](bsim6invAdjointForceAnalytic.cir) | xyce | tran, sens | 12 | small | no | specific (analysis sens) | - |
| [`bsim6invAdjointNewFD.cir`](bsim6invAdjointNewFD.cir) | xyce | tran, sens | 12 | small | no | specific (analysis sens) | - |
| [`bsim6invAdjointTrap.cir`](bsim6invAdjointTrap.cir) | xyce | tran, sens | 12 | small | no | specific (analysis sens) | - |
| [`bsim6invAdjointTrapNewFD.cir`](bsim6invAdjointTrapNewFD.cir) | xyce | tran, sens | 12 | small | no | specific (analysis sens) | - |
| [`bsim6invDirect.cir`](bsim6invDirect.cir) | xyce | tran, sens | 4 | tiny | no | specific (analysis sens) | - |
| [`bsim6invDirectFD.cir`](bsim6invDirectFD.cir) | xyce | tran, sens | 4 | tiny | no | specific (analysis sens) | - |
| [`bug1092sonA.cir`](bug1092sonA.cir) | xyce | tran, sens | 12 | small | no | specific (analysis sens) | - |
| [`bug1092sonB.cir`](bug1092sonB.cir) | xyce | tran, sens | 12 | small | no | specific (analysis sens) | - |
| [`bug669a.cir`](bug669a.cir) | xyce | dc, sens | 2 | tiny | yes | specific (analysis sens) | - |
| [`bug669b.cir`](bug669b.cir) | xyce | dc, sens | 2 | tiny | yes | specific (analysis sens) | - |
| [`bug702son.cir`](bug702son.cir) | xyce | dc, sens | 3 | tiny | yes | specific (analysis sens) | - |
| [`bug772sonA.cir`](bug772sonA.cir) | xyce | tran, sens | 2 | tiny | yes | specific (analysis sens) | - |
| [`bug772sonB.cir`](bug772sonB.cir) | xyce | tran, sens | 2 | tiny | yes | specific (analysis sens) | - |
| [`bug797Adjoint.cir`](bug797Adjoint.cir) | xyce | tran, sens | 5 | tiny | no | specific (analysis sens) | - |
| [`bug797Direct.cir`](bug797Direct.cir) | xyce | tran, sens | 5 | tiny | no | specific (analysis sens) | - |
| [`bugs799_and_842A.cir`](bugs799_and_842A.cir) | xyce | sens, tran | 5 | tiny | no | specific (analysis sens) | - |
| [`bugs799_and_842D.cir`](bugs799_and_842D.cir) | xyce | sens, tran | 5 | tiny | no | specific (analysis sens) | - |
| [`comparator.cir`](comparator.cir) | xyce | dc, sens | 22 | small | no | specific (analysis sens) | - |
| [`devLevelParams_ipulse.cir`](devLevelParams_ipulse.cir) | xyce | tran, sens | 8 | tiny | yes | specific (analysis sens) | - |
| [`devLevelParams_ipwl.cir`](devLevelParams_ipwl.cir) | xyce | tran, sens | 8 | tiny | yes | specific (analysis sens) | - |
| [`devLevelParams_isffm.cir`](devLevelParams_isffm.cir) | xyce | tran, sens | 2 | tiny | yes | specific (analysis sens) | - |
| [`devLevelParams_isin.cir`](devLevelParams_isin.cir) | xyce | tran, sens | 2 | tiny | yes | specific (analysis sens) | - |
| [`devLevelParams_vpulse.cir`](devLevelParams_vpulse.cir) | xyce | tran, sens | 5 | tiny | yes | specific (analysis sens) | - |
| [`devLevelParams_vpwl.cir`](devLevelParams_vpwl.cir) | xyce | tran, sens | 5 | tiny | yes | specific (analysis sens) | - |
| [`devLevelParams_vsffm.cir`](devLevelParams_vsffm.cir) | xyce | tran, sens | 5 | tiny | yes | specific (analysis sens) | - |
| [`devLevelParams_vsin.cir`](devLevelParams_vsin.cir) | xyce | tran, sens | 5 | tiny | yes | specific (analysis sens) | - |
| [`diodeTran.cir`](diodeTran.cir) | xyce | sens, tran | 4 | tiny | no | specific (analysis sens) | - |
| [`diodeTranAdjoint.cir`](diodeTranAdjoint.cir) | xyce | sens, tran | 4 | tiny | no | specific (analysis sens) | - |
| [`diodeTranAdjointScaled.cir`](diodeTranAdjointScaled.cir) | xyce | sens, tran | 4 | tiny | no | specific (analysis sens) | - |
| [`diodeTranAdjointTrap.cir`](diodeTranAdjointTrap.cir) | xyce | sens, tran | 4 | tiny | no | specific (analysis sens) | - |
| [`diodeTranFD.cir`](diodeTranFD.cir) | xyce | tran | 36 | small | no | core | - |
| [`diodeTranForAdjoint.cir`](diodeTranForAdjoint.cir) | xyce | sens, tran | 4 | tiny | no | specific (analysis sens) | - |
| [`diodeTranScaled.cir`](diodeTranScaled.cir) | xyce | sens, tran | 4 | tiny | no | specific (analysis sens) | - |
| [`diodeTranTrap.cir`](diodeTranTrap.cir) | xyce | sens, tran | 4 | tiny | no | specific (analysis sens) | - |
| [`diode_adjoint.cir`](diode_adjoint.cir) | xyce | sens, dc | 4 | tiny | no | specific (analysis sens) | - |
| [`diode_direct.cir`](diode_direct.cir) | xyce | sens, dc | 4 | tiny | no | specific (analysis sens) | - |
| [`dummyDiodeTran.cir`](dummyDiodeTran.cir) | xyce | tran | 4 | tiny | no | core | - |
| [`dummyDiodeTran2.cir`](dummyDiodeTran2.cir) | xyce | tran | 4 | tiny | no | core | - |
| [`dummyDiodeTran3.cir`](dummyDiodeTran3.cir) | xyce | tran | 4 | tiny | no | core | - |
| [`dummyDiodeTranScaled.cir`](dummyDiodeTranScaled.cir) | xyce | tran | 4 | tiny | no | core | - |
| [`dummy_bugs799_and_842.cir`](dummy_bugs799_and_842.cir) | xyce | tran | 5 | tiny | no | core | - |
| [`dummy_devLevelParams_ipulse.cir`](dummy_devLevelParams_ipulse.cir) | xyce | tran | 8 | tiny | yes | core | - |
| [`dummy_devLevelParams_ipwl.cir`](dummy_devLevelParams_ipwl.cir) | xyce | tran | 8 | tiny | yes | core | - |
| [`dummy_devLevelParams_isffm.cir`](dummy_devLevelParams_isffm.cir) | xyce | tran | 2 | tiny | yes | core | - |
| [`dummy_devLevelParams_isin.cir`](dummy_devLevelParams_isin.cir) | xyce | tran | 2 | tiny | yes | core | - |
| [`dummy_devLevelParams_vpulse.cir`](dummy_devLevelParams_vpulse.cir) | xyce | tran | 5 | tiny | yes | core | - |
| [`dummy_devLevelParams_vpwl.cir`](dummy_devLevelParams_vpwl.cir) | xyce | tran | 5 | tiny | yes | core | - |
| [`dummy_devLevelParams_vsffm.cir`](dummy_devLevelParams_vsffm.cir) | xyce | tran | 5 | tiny | yes | core | - |
| [`dummy_devLevelParams_vsin.cir`](dummy_devLevelParams_vsin.cir) | xyce | tran | 5 | tiny | yes | core | - |
| [`dummy_ipulse.cir`](dummy_ipulse.cir) | xyce | tran | 8 | tiny | yes | core | - |
| [`dummy_ipwl.cir`](dummy_ipwl.cir) | xyce | tran | 8 | tiny | yes | core | - |
| [`dummy_isffm.cir`](dummy_isffm.cir) | xyce | tran | 2 | tiny | yes | core | - |
| [`dummy_isin.cir`](dummy_isin.cir) | xyce | tran | 2 | tiny | yes | core | - |
| [`dummy_vpulse.cir`](dummy_vpulse.cir) | xyce | tran | 5 | tiny | yes | core | - |
| [`dummy_vpwl.cir`](dummy_vpwl.cir) | xyce | tran | 5 | tiny | yes | core | - |
| [`dummy_vsffm.cir`](dummy_vsffm.cir) | xyce | tran | 5 | tiny | yes | core | - |
| [`dummy_vsin.cir`](dummy_vsin.cir) | xyce | tran | 5 | tiny | yes | core | - |
| [`fddevLevelParams_ipulse.cir`](fddevLevelParams_ipulse.cir) | xyce | tran, sens | 8 | tiny | yes | specific (analysis sens) | - |
| [`fddevLevelParams_ipulse2.cir`](fddevLevelParams_ipulse2.cir) | xyce | tran | 64 | small | yes | core | - |
| [`fddevLevelParams_ipwl.cir`](fddevLevelParams_ipwl.cir) | xyce | tran, sens | 8 | tiny | yes | specific (analysis sens) | - |
| [`fddevLevelParams_isffm.cir`](fddevLevelParams_isffm.cir) | xyce | tran, sens | 2 | tiny | yes | specific (analysis sens) | - |
| [`fddevLevelParams_isffm2.cir`](fddevLevelParams_isffm2.cir) | xyce | tran | 12 | small | yes | core | - |
| [`fddevLevelParams_isin.cir`](fddevLevelParams_isin.cir) | xyce | tran, sens | 2 | tiny | yes | specific (analysis sens) | - |
| [`fddevLevelParams_isin2.cir`](fddevLevelParams_isin2.cir) | xyce | tran | 14 | small | yes | core | - |
| [`fddevLevelParams_vpulse.cir`](fddevLevelParams_vpulse.cir) | xyce | tran, sens | 5 | tiny | yes | specific (analysis sens) | - |
| [`fddevLevelParams_vpwl.cir`](fddevLevelParams_vpwl.cir) | xyce | tran, sens | 5 | tiny | yes | specific (analysis sens) | - |
| [`fddevLevelParams_vsffm.cir`](fddevLevelParams_vsffm.cir) | xyce | tran, sens | 5 | tiny | yes | specific (analysis sens) | - |
| [`fddevLevelParams_vsin.cir`](fddevLevelParams_vsin.cir) | xyce | tran, sens | 5 | tiny | yes | specific (analysis sens) | - |
| [`fdipulse.cir`](fdipulse.cir) | xyce | tran, sens | 8 | tiny | yes | specific (analysis sens) | - |
| [`fdipulse2.cir`](fdipulse2.cir) | xyce | tran | 64 | small | yes | core | - |
| [`fdipwl.cir`](fdipwl.cir) | xyce | tran, sens | 8 | tiny | yes | specific (analysis sens) | - |
| [`fdipwl2.cir`](fdipwl2.cir) | xyce | tran | 64 | small | yes | core | - |
| [`fdisffm.cir`](fdisffm.cir) | xyce | tran, sens | 2 | tiny | yes | specific (analysis sens) | - |
| [`fdisffm2.cir`](fdisffm2.cir) | xyce | tran | 12 | small | yes | core | - |
| [`fdisin.cir`](fdisin.cir) | xyce | tran, sens | 2 | tiny | yes | specific (analysis sens) | - |
| [`fdisin2.cir`](fdisin2.cir) | xyce | tran | 14 | small | yes | core | - |
| [`fdvpulse.cir`](fdvpulse.cir) | xyce | tran, sens | 5 | tiny | yes | specific (analysis sens) | - |
| [`fdvpwl.cir`](fdvpwl.cir) | xyce | tran, sens | 5 | tiny | yes | specific (analysis sens) | - |
| [`fdvsffm.cir`](fdvsffm.cir) | xyce | tran, sens | 5 | tiny | yes | specific (analysis sens) | - |
| [`fdvsin.cir`](fdvsin.cir) | xyce | tran, sens | 5 | tiny | yes | specific (analysis sens) | - |
| [`fullWaveDummy.cir`](fullWaveDummy.cir) | xyce | tran, sens | 6 | tiny | no | specific (analysis sens) | - |
| [`fullWaveRectDiode.cir`](fullWaveRectDiode.cir) | xyce | tran, sens | 6 | tiny | no | specific (analysis sens) | - |
| [`fullWaveRectDiodeAdjoint.cir`](fullWaveRectDiodeAdjoint.cir) | xyce | tran, sens | 6 | tiny | no | specific (analysis sens) | - |
| [`fullWaveRectDiodeAnalytic.cir`](fullWaveRectDiodeAnalytic.cir) | xyce | tran, sens | 6 | tiny | no | specific (analysis sens) | - |
| [`fullWaveRectDiodeDirect.cir`](fullWaveRectDiodeDirect.cir) | xyce | tran, sens | 6 | tiny | no | specific (analysis sens) | - |
| [`fullWaveRectDiodeNewFD.cir`](fullWaveRectDiodeNewFD.cir) | xyce | tran, sens | 6 | tiny | no | specific (analysis sens) | - |
| [`fullWaveRectDiodeOldFD.cir`](fullWaveRectDiodeOldFD.cir) | xyce | tran, sens | 6 | tiny | no | specific (analysis sens) | - |
| [`gummel_n.cir`](gummel_n.cir) | xyce | dc, sens | 5 | tiny | no | specific (analysis sens) | - |
| [`gummel_nFD.cir`](gummel_nFD.cir) | xyce | dc, sens | 5 | tiny | no | specific (analysis sens) | - |
| [`gummel_n_110.cir`](gummel_n_110.cir) | xyce | dc, sens | 5 | tiny | no | specific (analysis sens) | - |
| [`gummel_n_110FD.cir`](gummel_n_110FD.cir) | xyce | dc, sens | 5 | tiny | no | specific (analysis sens) | - |
| [`gummel_n_111.cir`](gummel_n_111.cir) | xyce | dc, sens | 5 | tiny | no | specific (analysis sens) | - |
| [`gummel_n_111FD.cir`](gummel_n_111FD.cir) | xyce | dc, sens | 5 | tiny | no | specific (analysis sens) | - |
| [`gummel_nmos_xyce.cir`](gummel_nmos_xyce.cir) | xyce | dc, sens | 5 | tiny | no | specific (analysis sens) | - |
| [`gummel_nmos_xyceFD.cir`](gummel_nmos_xyceFD.cir) | xyce | dc, sens | 5 | tiny | no | specific (analysis sens) | - |
| [`gummel_p.cir`](gummel_p.cir) | xyce | dc, sens | 5 | tiny | no | specific (analysis sens) | - |
| [`gummel_pFD.cir`](gummel_pFD.cir) | xyce | dc, sens | 5 | tiny | no | specific (analysis sens) | - |
| [`gummel_p_110.cir`](gummel_p_110.cir) | xyce | dc, sens | 5 | tiny | no | specific (analysis sens) | - |
| [`gummel_p_110FD.cir`](gummel_p_110FD.cir) | xyce | dc, sens | 5 | tiny | no | specific (analysis sens) | - |
| [`gummel_p_111.cir`](gummel_p_111.cir) | xyce | dc, sens | 5 | tiny | no | specific (analysis sens) | - |
| [`gummel_p_111FD.cir`](gummel_p_111FD.cir) | xyce | dc, sens | 5 | tiny | no | specific (analysis sens) | - |
| [`gummel_pmos_xyce.cir`](gummel_pmos_xyce.cir) | xyce | dc, sens | 5 | tiny | no | specific (analysis sens) | - |
| [`gummel_pmos_xyceFD.cir`](gummel_pmos_xyceFD.cir) | xyce | dc, sens | 5 | tiny | no | specific (analysis sens) | - |
| [`inverter_event.cir`](inverter_event.cir) | xyce | tran, sens | 15 | small | no | specific (analysis sens) | - |
| [`ipulse.cir`](ipulse.cir) | xyce | tran, sens | 8 | tiny | yes | specific (analysis sens) | - |
| [`ipwl.cir`](ipwl.cir) | xyce | tran, sens | 8 | tiny | yes | specific (analysis sens) | - |
| [`isffm.cir`](isffm.cir) | xyce | tran, sens | 2 | tiny | yes | specific (analysis sens) | - |
| [`isin.cir`](isin.cir) | xyce | tran, sens | 2 | tiny | yes | specific (analysis sens) | - |
| [`issue729.cir`](issue729.cir) | xyce | dc, sens | 3 | tiny | yes | specific (analysis sens) | - |
| [`issue729Ref.cir`](issue729Ref.cir) | xyce | dc, sens | 3 | tiny | yes | specific (analysis sens) | - |
| [`missingSensFunction.cir`](missingSensFunction.cir) | xyce | tran, sens | 3 | tiny | yes | specific (analysis sens) | - |
| [`nlMutIndSens1.cir`](nlMutIndSens1.cir) | xyce | tran, sens | 6 | tiny | yes | specific (analysis sens) | - |
| [`nlMutIndSens1_FD.cir`](nlMutIndSens1_FD.cir) | xyce | tran | 12 | small | yes | core | - |
| [`nlMutIndSens2.cir`](nlMutIndSens2.cir) | xyce | tran, sens | 6 | tiny | yes | specific (analysis sens) | - |
| [`nlMutIndSens2_FD.cir`](nlMutIndSens2_FD.cir) | xyce | tran | 12 | small | yes | core | - |
| [`psp_asym_nmos_idvg0_FD_SENS.cir`](psp_asym_nmos_idvg0_FD_SENS.cir) | xyce | dc, step, sens | 9 | tiny | no | specific (analysis sens) | - |
| [`psp_asym_nmos_idvg0_SENS.cir`](psp_asym_nmos_idvg0_SENS.cir) | xyce | dc, step, sens | 9 | tiny | no | specific (analysis sens) | - |
| [`psp_asym_pmos_idvg0_FD_SENS.cir`](psp_asym_pmos_idvg0_FD_SENS.cir) | xyce | dc, step, sens | 9 | tiny | no | specific (analysis sens) | - |
| [`psp_asym_pmos_idvg0_SENS.cir`](psp_asym_pmos_idvg0_SENS.cir) | xyce | dc, step, sens | 9 | tiny | no | specific (analysis sens) | - |
| [`rc1000TranAdjGear.cir`](rc1000TranAdjGear.cir) | xyce | tran, sens | 2002 | large | yes | specific (analysis sens) | - |
| [`res.cir`](res.cir) | xyce | dc, sens | 3 | tiny | yes | specific (analysis sens) | - |
| [`sensCapGear.cir`](sensCapGear.cir) | xyce | tran, sens | 2 | tiny | yes | specific (analysis sens) | - |
| [`sensCapGearAdj.cir`](sensCapGearAdj.cir) | xyce | tran, sens | 3 | tiny | yes | specific (analysis sens) | - |
| [`sensCapGearAdjNewFD.cir`](sensCapGearAdjNewFD.cir) | xyce | tran, sens | 3 | tiny | yes | specific (analysis sens) | - |
| [`sensCapGearAdjOrder1.cir`](sensCapGearAdjOrder1.cir) | xyce | tran, sens | 3 | tiny | yes | specific (analysis sens) | - |
| [`sensCapGear_baseline.cir`](sensCapGear_baseline.cir) | xyce | tran, sens | 2 | tiny | yes | specific (analysis sens) | - |
| [`sensCapGear_baseline_copy.cir`](sensCapGear_baseline_copy.cir) | xyce | tran, sens | 2 | tiny | yes | specific (analysis sens) | - |
| [`sensCapGear_forceDeviceFD.cir`](sensCapGear_forceDeviceFD.cir) | xyce | tran, sens | 2 | tiny | yes | specific (analysis sens) | - |
| [`sensCapGear_global.cir`](sensCapGear_global.cir) | xyce | tran, sens | 2 | tiny | yes | specific (analysis sens) | - |
| [`sensCapGear_global2.cir`](sensCapGear_global2.cir) | xyce | tran, sens | 2 | tiny | yes | specific (analysis sens) | - |
| [`sensCapGear_global_curlybrace.cir`](sensCapGear_global_curlybrace.cir) | xyce | tran, sens | 2 | tiny | yes | specific (analysis sens) | - |
| [`sensCapGear_numerical.cir`](sensCapGear_numerical.cir) | xyce | tran, sens | 2 | tiny | yes | specific (analysis sens) | - |
| [`sensCapGear_oldFD.cir`](sensCapGear_oldFD.cir) | xyce | tran, sens | 2 | tiny | yes | specific (analysis sens) | - |
| [`sensCapTrapAdj.cir`](sensCapTrapAdj.cir) | xyce | tran, sens | 3 | tiny | yes | specific (analysis sens) | - |
| [`sensCapTrapAdjNewFD.cir`](sensCapTrapAdjNewFD.cir) | xyce | tran, sens | 3 | tiny | yes | specific (analysis sens) | - |
| [`sensCapTrapAdjOrder1.cir`](sensCapTrapAdjOrder1.cir) | xyce | tran, sens | 3 | tiny | yes | specific (analysis sens) | - |
| [`sensCapTrapOrder1.cir`](sensCapTrapOrder1.cir) | xyce | tran, sens | 2 | tiny | yes | specific (analysis sens) | - |
| [`sensCapTrapOrder2.cir`](sensCapTrapOrder2.cir) | xyce | tran, sens | 2 | tiny | yes | specific (analysis sens) | - |
| [`transLineStepDataGlobalPar.cir`](transLineStepDataGlobalPar.cir) | xyce | tran, sens, step | 11 | small | yes | specific (analysis sens) | - |
| [`twoObj.cir`](twoObj.cir) | xyce | dc, sens, op | 7 | tiny | no | specific (analysis sens) | - |
| [`twoObjFD.cir`](twoObjFD.cir) | xyce | dc | 133 | medium | no | core | - |
| [`vpulse.cir`](vpulse.cir) | xyce | tran, sens | 5 | tiny | yes | specific (analysis sens) | - |
| [`vpwl.cir`](vpwl.cir) | xyce | tran, sens | 5 | tiny | yes | specific (analysis sens) | - |
| [`vsffm.cir`](vsffm.cir) | xyce | tran, sens | 5 | tiny | yes | specific (analysis sens) | - |
| [`vsin.cir`](vsin.cir) | xyce | tran, sens | 5 | tiny | yes | specific (analysis sens) | - |
| [`vsrcSensTest.cir`](vsrcSensTest.cir) | xyce | tran, sens | 3 | tiny | yes | specific (analysis sens) | - |
| [`vsrcSensTest2.cir`](vsrcSensTest2.cir) | xyce | tran, sens | 3 | tiny | yes | specific (analysis sens) | - |

Devices: instances once the subcircuits defined in this case are expanded; a device from a library or a compiled model counts once. Size, linear and portability: see the top README.

Generated by `python -m circref build`. Do not edit by hand.
