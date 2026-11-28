# Xyce_Regression MEASURE

test | xyce | status: **complete**

## Source

- Authors: Sandia National Laboratories
- URL: https://github.com/Xyce/Xyce_Regression (commit `7bb7e98f0ed3a81a7d1cf1d10b68592107ed40b2`)
- Path: `Netlists/MEASURE`
- License: GPL-3.0-or-later

## Netlists

| file | dialect | analyses | devices | size | linear | portability | libraries |
|---|---|---|---|---|---|---|---|
| [`AverageTest.cir`](AverageTest.cir) | xyce | tran | 8 | tiny | yes | core | - |
| [`AverageTestInc.cir`](AverageTestInc.cir) | xyce | tran | 4 | tiny | yes | core | - |
| [`DefaultValOption.cir`](DefaultValOption.cir) | xyce | tran | 4 | tiny | yes | core | - |
| [`DerivativeATequalityTest.cir`](DerivativeATequalityTest.cir) | xyce | tran | 2 | tiny | yes | core | - |
| [`DerivativeMiscTest.cir`](DerivativeMiscTest.cir) | xyce | tran | 4 | tiny | yes | core | - |
| [`DerivativeTest.cir`](DerivativeTest.cir) | xyce | tran | 8 | tiny | yes | core | - |
| [`DerivativeVariableTest.cir`](DerivativeVariableTest.cir) | xyce | tran | 6 | tiny | yes | core | - |
| [`DuplicateMeasureNames.cir`](DuplicateMeasureNames.cir) | xyce | tran | 4 | tiny | yes | core | - |
| [`DutyTest.cir`](DutyTest.cir) | xyce | tran | 4 | tiny | yes | core | - |
| [`EquationEvalTest.cir`](EquationEvalTest.cir) | xyce | tran | 4 | tiny | yes | core | - |
| [`ErrorFuncTest.cir`](ErrorFuncTest.cir) | xyce | tran | 4 | tiny | yes | core | - |
| [`ErrorMessageTest.cir`](ErrorMessageTest.cir) | xyce | tran | 4 | tiny | yes | core | - |
| [`ErrorTest.cir`](ErrorTest.cir) | xyce | tran | 4 | tiny | yes | core | - |
| [`ErrorTestCurrentPowerExp.cir`](ErrorTestCurrentPowerExp.cir) | xyce | tran | 4 | tiny | yes | core | - |
| [`ExpressionSyntaxes.cir`](ExpressionSyntaxes.cir) | xyce | tran | 3 | tiny | yes | core | - |
| [`FindWhenTest.cir`](FindWhenTest.cir) | xyce | tran | 10 | small | yes | core | - |
| [`FindWhenTestInc.cir`](FindWhenTestInc.cir) | xyce | tran | 4 | tiny | yes | core | - |
| [`FindWhenVariableTest.cir`](FindWhenVariableTest.cir) | xyce | tran | 8 | tiny | yes | core | - |
| [`FourierTest.cir`](FourierTest.cir) | xyce | tran | 7 | tiny | no | core | - |
| [`FourierTestFromToTD.cir`](FourierTestFromToTD.cir) | xyce | tran | 2 | tiny | yes | core | - |
| [`FourierTest_measfail_one.cir`](FourierTest_measfail_one.cir) | xyce | tran | 7 | tiny | no | core | - |
| [`FourierTest_measfail_zero.cir`](FourierTest_measfail_zero.cir) | xyce | tran | 7 | tiny | no | core | - |
| [`FreqTest.cir`](FreqTest.cir) | xyce | tran | 4 | tiny | yes | core | - |
| [`FreqTestFromTo.cir`](FreqTestFromTo.cir) | xyce | tran | 4 | tiny | yes | core | - |
| [`IntegralTest.cir`](IntegralTest.cir) | xyce | tran | 8 | tiny | yes | core | - |
| [`LeadCurrentAndPowerTest.cir`](LeadCurrentAndPowerTest.cir) | xyce | tran | 2 | tiny | yes | core | - |
| [`LeadCurrentNotOnPrintLineTest.cir`](LeadCurrentNotOnPrintLineTest.cir) | xyce | tran | 14 | small | yes | core | - |
| [`MaxDiffTest.cir`](MaxDiffTest.cir) | xyce | tran | 4 | tiny | yes | core | - |
| [`MaxTest.cir`](MaxTest.cir) | xyce | tran | 6 | tiny | yes | core | - |
| [`MeasdgtOption.cir`](MeasdgtOption.cir) | xyce | tran | 2 | tiny | no | core | - |
| [`MeasfailOptionBogo.cir`](MeasfailOptionBogo.cir) | xyce | tran | 4 | tiny | yes | core | - |
| [`MeasfailOptionOne.cir`](MeasfailOptionOne.cir) | xyce | tran | 4 | tiny | yes | core | - |
| [`MeasfailOptionOneTrigTarg.cir`](MeasfailOptionOneTrigTarg.cir) | xyce | tran | 2 | tiny | yes | core | - |
| [`MeasfailOptionZero.cir`](MeasfailOptionZero.cir) | xyce | tran | 4 | tiny | yes | core | - |
| [`MeasfailOptionZeroTrigTarg.cir`](MeasfailOptionZeroTrigTarg.cir) | xyce | tran | 2 | tiny | yes | core | - |
| [`MeasoutOptionBogo.cir`](MeasoutOptionBogo.cir) | xyce | tran | 2 | tiny | yes | core | - |
| [`MeasoutOptionOne.cir`](MeasoutOptionOne.cir) | xyce | tran | 2 | tiny | yes | core | - |
| [`MeasoutOptionZero.cir`](MeasoutOptionZero.cir) | xyce | tran | 2 | tiny | yes | core | - |
| [`MeasprintOptionALL.cir`](MeasprintOptionALL.cir) | xyce | tran | 2 | tiny | yes | core | - |
| [`MeasprintOptionBOGO.cir`](MeasprintOptionBOGO.cir) | xyce | tran | 2 | tiny | yes | core | - |
| [`MeasprintOptionNONE.cir`](MeasprintOptionNONE.cir) | xyce | tran | 2 | tiny | yes | core | - |
| [`MeasprintOptionSTDOUT.cir`](MeasprintOptionSTDOUT.cir) | xyce | tran | 2 | tiny | yes | core | - |
| [`MinTest.cir`](MinTest.cir) | xyce | tran | 6 | tiny | yes | core | - |
| [`Off_TimeTest.cir`](Off_TimeTest.cir) | xyce | tran | 8 | tiny | yes | core | - |
| [`On_TimeTest.cir`](On_TimeTest.cir) | xyce | tran | 8 | tiny | yes | core | - |
| [`PPTest.cir`](PPTest.cir) | xyce | tran | 8 | tiny | yes | core | - |
| [`PrecisionTest.cir`](PrecisionTest.cir) | xyce | tran | 2 | tiny | no | core | - |
| [`PrintOptionTest.cir`](PrintOptionTest.cir) | xyce | tran | 10 | small | yes | core | - |
| [`QualifierExp.cir`](QualifierExp.cir) | xyce | tran | 4 | tiny | yes | core | - |
| [`RFCEquality.cir`](RFCEquality.cir) | xyce | tran | 4 | tiny | yes | core | - |
| [`RFCEqualityTrigTarg.cir`](RFCEqualityTrigTarg.cir) | xyce | tran | 4 | tiny | yes | core | - |
| [`RMSTest.cir`](RMSTest.cir) | xyce | tran | 8 | tiny | yes | core | - |
| [`RiseFallCrossTest.cir`](RiseFallCrossTest.cir) | xyce | tran | 2 | tiny | yes | core | - |
| [`RiseFallDelay.cir`](RiseFallDelay.cir) | xyce | tran | 8 | tiny | yes | core | - |
| [`RiseFallDelayFT.cir`](RiseFallDelayFT.cir) | xyce | tran | 6 | tiny | yes | core | - |
| [`RiseFallDelayMisc.cir`](RiseFallDelayMisc.cir) | xyce | tran | 6 | tiny | yes | core | - |
| [`RiseFallDelayValSyntax.cir`](RiseFallDelayValSyntax.cir) | xyce | tran | 2 | tiny | yes | core | - |
| [`TrigTargTest.cir`](TrigTargTest.cir) | xyce | tran | 6 | tiny | yes | core | - |
| [`WhenInterpolationTest.cir`](WhenInterpolationTest.cir) | xyce | tran | 6 | tiny | no | core | - |
| [`issue_221.cir`](issue_221.cir) | xyce | tran | 4 | tiny | yes | core | - |
| [`issue_221_measfail_one.cir`](issue_221_measfail_one.cir) | xyce | tran | 4 | tiny | yes | core | - |
| [`issue_221_measfail_zero.cir`](issue_221_measfail_zero.cir) | xyce | tran | 4 | tiny | yes | core | - |
| [`issue_277.cir`](issue_277.cir) | xyce | tran | 2 | tiny | yes | core | - |

Devices: instances once every subcircuit is expanded, those of libraries too; a compiled model counts once. Size, linear and portability: see the top README.

Generated by `python -m circref build`. Do not edit by hand.
