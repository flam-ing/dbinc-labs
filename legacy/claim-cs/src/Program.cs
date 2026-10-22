// ======================================================================
//  ClaimReview.exe  -  보험금 청구 자동 심사 배치
//
//  사용법 : ClaimReview.exe <청구 CSV> <상품 CSV> <기준일 yyyyMMdd>
//  실행   : 매일 07:30 작업 스케줄러 (CLAIM_REVIEW)
//
//  2004.06  VB6 심사 프로그램 (외주)
//  2012.03  배치 부분 C# 이전 (.NET Framework 4.0 / VS2010)    정민호
//  2012.05  서버 이전 장애 - 날짜 문화권 고정                   정민호
//  2013.06  결과 파일 저장 막음 (화면 출력만)                    정민호
//  2013.08  근골격계(M) 지급률 70%                               이서연
//  2014.02  재보험 사전 통지 기준 변경                           이서연
//
//  ※ 교육용 가상 프로그램입니다. 회사, 상품, 금액, 규정은 모두 가상입니다.
// ======================================================================
using System;
using System.Data;
using System.Globalization;
using System.IO;
using System.Threading;

namespace NuriClaim
{
    class Program
    {
        static int Main(string[] args)
        {
            #region 초기화

            // !!! 지우지 말 것 !!!  2012.05 서버 이전 장애 (위키 참고)
            Thread.CurrentThread.CurrentCulture = new CultureInfo("en-US");

            if (args.Length < 3 || args[2].Length != 8)
            {
                Console.WriteLine("USAGE: ClaimReview <claims.csv> <products.csv> <yyyyMMdd>");
                return 1;
            }

            string strClaimPath = args[0];
            string strPrdPath = args[1];
            modGlobal.g_strBaseDt = args[2];

            if (File.Exists(strClaimPath) == false)
            {
                Console.WriteLine("ERROR: FILE NOT FOUND " + strClaimPath);
                return 2;
            }
            if (File.Exists(strPrdPath) == false)
            {
                Console.WriteLine("ERROR: FILE NOT FOUND " + strPrdPath);
                return 2;
            }

            #endregion

            try
            {
                modGlobal.g_dtBase = DateTime.ParseExact(modGlobal.g_strBaseDt, "yyyyMMdd", null);

                #region 상품 읽기
                DataTable dtPrd = ProductDao.LoadProduct(strPrdPath);
                #endregion

                PrintHeader();

                #region 청구 읽기, 심사
                StreamReader sr = new StreamReader(strClaimPath);
                string strLine = sr.ReadLine();     // 첫 줄은 제목
                while ((strLine = sr.ReadLine()) != null)
                {
                    string[] arrCol = strLine.Split(',');
                    if (arrCol.Length < 10) goto NEXT_LINE;     // VB: GoTo NextLine

                    string strResult = "";
                    int intRsn = 0;
                    decimal decPay = 0;

                    try
                    {
                        strResult = ClaimJudge.Judge(arrCol, dtPrd, ref intRsn, ref decPay);
                    }
                    catch
                    {
                        // VB: On Error Resume Next
                        strResult = "MANUAL";
                        intRsn = 90;
                        decPay = 0;
                    }

                    PrintLine(arrCol, strResult, intRsn, decPay);
                    AddCount(strResult, decPay);

                NEXT_LINE:
                    modGlobal.g_intLineNo = modGlobal.g_intLineNo + 1;
                }
                sr.Close();
                #endregion

                //' 2013.06 결과 파일 막음. 작업 스케줄러가 화면 출력을 받아서 심사 화면에 올림
                //StreamWriter sw = new StreamWriter(modGlobal.OUT_DIR + "result_" + modGlobal.g_strBaseDt + ".csv", false, Encoding.Default);
                //sw.Write(modGlobal.g_sbOut.ToString());
                //sw.Close();

                PrintSummary();
            }
            catch (Exception ex)
            {
                Console.WriteLine("ERROR: " + ex.Message);
                return 9;
            }

            return 0;
        }

        static void PrintHeader()
        {
            Console.WriteLine("CLAIM REVIEW  BASE_DT " + modGlobal.g_strBaseDt);
            Console.WriteLine("============================================================");
            Console.WriteLine(String.Format("{0,-10}{1,-7}{2,-6}{3,12}{4,12}  {5,-7}{6}",
                "CLM_NO", "PRD", "DX", "CLM_AMT", "PAY_AMT", "RESULT", "RSN"));
            Console.WriteLine("------------------------------------------------------------");
        }

        static void PrintLine(string[] arrCol, string strResult, int intRsn, decimal decPay)
        {
            Console.WriteLine(String.Format("{0,-10}{1,-7}{2,-6}{3,12}{4,12}  {5,-7}{6}",
                arrCol[0], arrCol[2], arrCol[3], modCommon.FmtAmt(modCommon.ToDec(arrCol[5])),
                modCommon.FmtAmt(decPay), strResult, intRsn.ToString("00")));
        }

        static void AddCount(string strResult, decimal decPay)
        {
            int intIdx = 0;
            if (strResult == "AUTO") intIdx = 0;
            else if (strResult == "PART") intIdx = 1;
            else if (strResult == "REJECT") intIdx = 2;
            else intIdx = 3;

            modGlobal.g_arrCnt[intIdx] = modGlobal.g_arrCnt[intIdx] + 1;
            modGlobal.g_arrAmt[intIdx] = modGlobal.g_arrAmt[intIdx] + decPay;
        }

        static void PrintSummary()
        {
            string[] arrName = new string[] { "AUTO", "PART", "REJECT", "MANUAL" };
            int intTotCnt = 0;
            decimal decTotAmt = 0;

            Console.WriteLine("------------------------------------------------------------");
            Console.WriteLine(String.Format("{0,-8}{1,6}{2,15}", "RESULT", "CNT", "PAY_AMT"));
            for (int i = 0; i < 4; i++)
            {
                Console.WriteLine(String.Format("{0,-8}{1,6}{2,15}", arrName[i], modGlobal.g_arrCnt[i], modCommon.FmtAmt(modGlobal.g_arrAmt[i])));
                intTotCnt = intTotCnt + modGlobal.g_arrCnt[i];
                decTotAmt = decTotAmt + modGlobal.g_arrAmt[i];
            }
            Console.WriteLine(String.Format("{0,-8}{1,6}{2,15}", "TOTAL", intTotCnt, modCommon.FmtAmt(decTotAmt)));
        }
    }
}
