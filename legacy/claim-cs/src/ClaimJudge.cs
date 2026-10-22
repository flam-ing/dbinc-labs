using System;
using System.Data;

namespace NuriClaim
{
    /// <summary>
    /// 청구 심사 (VB6 frmJudge.cmdJudge_Click 의 계산 부분을 옮김)
    /// </summary>
    public class ClaimJudge
    {
        /// <summary>
        /// 청구 1건 심사. 결과(AUTO/PART/REJECT/MANUAL) 리턴. 사유 코드, 지급액은 ref 로 돌려줌
        /// </summary>
        public static string Judge(string[] arrCol, DataTable dtPrd, ref int intRsn, ref decimal decPay)
        {
            string strResult = "";

            // 열: CLM_NO,POL_NO,PRD_CD,DX_CD,HOSP_DAYS,CLM_AMT,JOIN_DT,ACC_DT,PREV_CNT,RCV_CH
            string strClmNo = arrCol[0];
            string strPolNo = arrCol[1];
            string strPrdCd = arrCol[2];
            string strDxCd = arrCol[3];
            int intDays = modCommon.ToInt(arrCol[4]);
            decimal decClmAmt = modCommon.ToDec(arrCol[5]);
            string strJoinDt = arrCol[6];
            string strAccDt = arrCol[7];
            int intPrevCnt = modCommon.ToInt(arrCol[8]);
            //string strRcvCh = arrCol[9];

            DataRow drPrd = ProductDao.FindProduct(dtPrd, strPrdCd);

            if (drPrd == null)
            {
                strResult = "REJECT";
                intRsn = 31;
            }
            else
            {
                if (drPrd["SALE_YN"].ToString() == "N")
                {
                    // 단종 상품은 일단 사람이 봄
                    strResult = "MANUAL";
                    intRsn = 32;
                }
                else
                {
                    string strKey = strPolNo + "|" + strAccDt + "|" + strDxCd;
                    if (modGlobal.g_htDup.ContainsKey(strKey))
                    {
                        strResult = "REJECT";
                        intRsn = 41;
                    }
                    else
                    {
                        modGlobal.g_htDup.Add(strKey, strClmNo);

                        DateTime dtJoin = modCommon.ToDate(strJoinDt);
                        DateTime dtAcc = modCommon.ToDate(strAccDt);
                        string strType = drPrd["PRD_TYPE"].ToString();
                        decimal decLimit = Convert.ToDecimal(drPrd["LIMIT_AMT"]);

                        if ((modGlobal.g_dtBase - dtAcc).Days > 1095)
                        {
                            strResult = "REJECT";
                            intRsn = 24;
                        }
                        else if (intPrevCnt >= 3)
                        {
                            strResult = "MANUAL";
                            intRsn = 52;
                        }
                        else
                        {
                            #region 실손 (SL)
                            if (strType == "SL")
                            {
                                bool blnInjury = false;
                                if (strDxCd.StartsWith("S") || strDxCd.StartsWith("T")) blnInjury = true;
                                //'Select Case Left(strDxCd, 1)
                                //'    Case "S", "T"
                                //'        blnInjury = True
                                //'End Select

                                int intWait = 90;
                                if (dtJoin < new DateTime(2012, 4, 1)) intWait = 60;

                                if (blnInjury == false && (dtAcc - dtJoin).Days < intWait)
                                {
                                    strResult = "REJECT";
                                    intRsn = 21;
                                }
                                else if (blnInjury == true && (dtAcc - dtJoin).Days <= 30)
                                {
                                    strResult = "MANUAL";
                                    intRsn = 53;
                                }
                                else
                                {
                                    decimal decSelf = Convert.ToDecimal(drPrd["SELF_AMT"]);
                                    if (strPrdCd == "SL00")
                                    {
                                        // 2004년 상품. 자기부담 없음
                                        decSelf = 0;
                                    }

                                    if (strDxCd.Substring(0, 1) == "M")
                                    {
                                        // 2013.08 근골격계 지급률 70% (보상팀 요청)
                                        decPay = Math.Round((decimal)((double)(decClmAmt - decSelf) * 0.7));
                                    }
                                    else
                                    {
                                        double dblRate = Convert.ToDouble(drPrd["PAY_RATE"]);
                                        decPay = (decimal)((double)(decClmAmt - decSelf) * dblRate);
                                        decPay = Math.Truncate(decPay / 10) * 10;      // 10원 미만 절사
                                    }

                                    if (decPay <= 0)
                                    {
                                        strResult = "REJECT";
                                        intRsn = 25;
                                    }
                                    else if (decPay > decLimit)
                                    {
                                        strResult = "PART";
                                        intRsn = 11;
                                        decPay = decLimit;
                                    }
                                    else
                                    {
                                        strResult = "AUTO";
                                        intRsn = 0;
                                    }
                                }
                            }
                            #endregion
                            #region 입원 일당 (HS)
                            else if (strType == "HS")
                            {
                                bool blnInjury = false;
                                if (strDxCd.StartsWith("S") || strDxCd.StartsWith("T")) blnInjury = true;

                                int intWait = 90;
                                if (dtJoin < new DateTime(2012, 4, 1)) intWait = 60;

                                if (blnInjury == false && (dtAcc - dtJoin).Days < intWait)
                                {
                                    strResult = "REJECT";
                                    intRsn = 21;
                                }
                                else if (blnInjury == true && (dtAcc - dtJoin).Days < 30)     // 가입 30일 이내 사고
                                {
                                    strResult = "MANUAL";
                                    intRsn = 53;
                                }
                                else if (intDays <= 3)
                                {
                                    strResult = "REJECT";
                                    intRsn = 23;
                                }
                                else
                                {
                                    int intPayDays = intDays - 3;
                                    if (intPayDays > decLimit)          // 일당 상품은 LIMIT_AMT 가 일수
                                    {
                                        intPayDays = (int)decLimit;
                                        strResult = "PART";
                                        intRsn = 11;
                                    }
                                    else
                                    {
                                        strResult = "AUTO";
                                        intRsn = 0;
                                    }
                                    decPay = intPayDays * Convert.ToDecimal(drPrd["DAY_AMT"]);
                                    //'lngPay = (intDays - 3) * 30000
                                }
                            }
                            #endregion
                            #region 진단 (DG)
                            else if (strType == "DG")
                            {
                                if (strDxCd.StartsWith("C") || strDxCd.StartsWith("D0"))
                                {
                                    // 암은 가입 1년 면책
                                    DateTime dtOneYear;
                                    try
                                    {
                                        dtOneYear = DateTime.Parse((dtJoin.Year + 1).ToString() + "-" + dtJoin.Month.ToString() + "-" + dtJoin.Day.ToString());
                                    }
                                    catch
                                    {
                                        dtOneYear = dtJoin.AddDays(366);
                                    }

                                    if (dtAcc < dtOneYear)
                                    {
                                        strResult = "REJECT";
                                        intRsn = 22;
                                    }
                                    else
                                    {
                                        double dblRate = 1.0;
                                        if (strDxCd == "C73") dblRate = 0.2;                  // 갑상선암
                                        else if (strDxCd.StartsWith("D0")) dblRate = 0.1;     // 제자리암

                                        decPay = (decimal)((double)decLimit * dblRate);
                                        decPay = Math.Truncate(decPay / 10) * 10;

                                        if (dblRate < 1)
                                        {
                                            strResult = "PART";
                                            intRsn = 12;
                                        }
                                        else
                                        {
                                            strResult = "AUTO";
                                            intRsn = 0;
                                        }
                                    }
                                }
                                else
                                {
                                    strResult = "REJECT";
                                    intRsn = 26;
                                }
                            }
                            #endregion
                        }
                    }
                }
            }

            // 재보험 사전 통지 (지급 예정액 기준) - 2014.02 300만 -> 500만
            if ((strResult == "AUTO" || strResult == "PART") && decPay >= 5000000)
            {
                strResult = "MANUAL";
                intRsn = 51;
            }

            if (strResult == "REJECT" || strResult == "MANUAL") decPay = 0;

            return strResult;
        }
    }
}
