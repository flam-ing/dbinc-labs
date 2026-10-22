// =====================================================================
//  DailySettle.cs
//  매장 일일 정산 배치 (매일 06:00 작업 스케줄러에서 실행)
//
//  사용법: DailySettle.exe <주문 CSV> <상품 CSV> <영업일 yyyy-MM-dd>
//
//  2006.03  최초 작성 (.NET Framework 2.0, Visual Studio 2005)
//  2009.11  주문 파일 읽기 수정
//  2011.05  서버 이전 후 수정
//  2013.02  매장 코드 정리
//
//  ※ 교육용 가상 프로그램입니다. 회사, 매장, 상품, 금액은 모두 가상입니다.
// =====================================================================
using System;
using System.Collections;
using System.Globalization;
using System.IO;
using System.Threading;

namespace SettleBatch
{
    class DailySettle
    {
        // 상품 목록. 한 줄이 string[] { sku, name, stock }
        static ArrayList products = new ArrayList();

        // 매장 코드표
        static Hashtable storeNames = new Hashtable();

        static int Main(string[] args)
        {
            // 지우지 마시오 (2011.05)
            Thread.CurrentThread.CurrentCulture = new CultureInfo("ko-KR");

            if (args.Length < 3)
            {
                Console.WriteLine("USAGE: DailySettle <orders.csv> <products.csv> <yyyy-MM-dd>");
                return 1;
            }

            string ordersPath = args[0];
            string productsPath = args[1];
            string bizDate = args[2];

            if (!File.Exists(ordersPath))
            {
                Console.WriteLine("ERROR: FILE NOT FOUND " + ordersPath);
                return 2;
            }
            if (!File.Exists(productsPath))
            {
                Console.WriteLine("ERROR: FILE NOT FOUND " + productsPath);
                return 2;
            }

            storeNames["ST01"] = "본점";
            storeNames["ST02"] = "신촌점";
            storeNames["ST03"] = "대학로점";
            storeNames["ST04"] = "역삼점";
            storeNames["ST05"] = "역전점";

            try
            {
                // ---------------- 상품 읽기 ----------------
                StreamReader pr = new StreamReader(productsPath);
                string pline = pr.ReadLine(); // 첫 줄은 제목
                while ((pline = pr.ReadLine()) != null)
                {
                    if (pline.Trim() == "") continue;
                    string[] pf = pline.Split(',');
                    products.Add(pf);
                }
                pr.Close();

                int[] sold = new int[products.Count];

                // ---------------- 주문 읽기 ----------------
                // 열: order_id,order_dt,store,pay,sku,qty,unit_price,status,memo
                ArrayList orders = new ArrayList();
                ArrayList stores = new ArrayList();
                StreamReader sr = new StreamReader(ordersPath);
                string line = sr.ReadLine(); // 첫 줄은 제목
                while ((line = sr.ReadLine()) != null)
                {
                    try
                    {
                        string[] f = line.Split(',');

                        DateTime dt = DateTime.Parse(f[1]);
                        if (dt.Hour >= 23) dt = dt.AddDays(1);
                        if (dt.ToString("yyyy-MM-dd") != bizDate) continue;

                        if (!storeNames.ContainsKey(f[2])) continue;
                        if (f[8].ToUpper().IndexOf("TEST") >= 0) continue;

                        int qty = Convert.ToInt32(f[5]);
                        double price = Convert.ToDouble(f[6]);
                        string st = f[7];
                        if (st == "CXL") continue;

                        object[] o = new object[6];
                        o[0] = f[2];          // 매장
                        o[1] = f[3];          // 결제
                        o[2] = f[4];          // 상품
                        o[3] = qty;
                        o[4] = price * qty;   // 금액
                        o[5] = st;            // OK, RTN
                        orders.Add(o);

                        if (!stores.Contains(f[2])) stores.Add(f[2]);

                        int idx = FindProduct(f[4]);
                        if (idx >= 0)
                        {
                            if (st == "OK") sold[idx] = sold[idx] + qty;
                            if (st == "RTN") sold[idx] = sold[idx] - qty;
                        }
                    }
                    catch
                    {
                    }
                }
                sr.Close();

                // ---------------- 매장별 정산 ----------------
                stores.Sort();
                Hashtable cnt = new Hashtable();
                string sql = "";
                int tCnt = 0;
                double tSales = 0, tRtn = 0, tCard = 0, tCash = 0, tPoint = 0, tFee = 0, tNet = 0;

                Console.WriteLine("DAILY SETTLEMENT " + bizDate);
                Console.WriteLine("=====================================================================================");
                Console.WriteLine(String.Format("{0,-6}{1,5}{2,12}{3,10}{4,12}{5,10}{6,10}{7,8}{8,12}",
                    "STORE", "CNT", "SALES", "RETURN", "CARD", "CASH", "POINT", "FEE", "NET"));
                Console.WriteLine("-------------------------------------------------------------------------------------");

                for (int i = 0; i < stores.Count; i++)
                {
                    string s = (string)stores[i];
                    double sales = 0, rtn = 0, card = 0, cash = 0, point = 0;
                    cnt[s] = 0;

                    for (int j = 0; j < orders.Count; j++)
                    {
                        object[] o = (object[])orders[j];
                        if ((string)o[0] == s && (string)o[5] == "OK")
                        {
                            sales = sales + (double)o[4];
                            cnt[s] = (int)cnt[s] + 1;
                        }
                    }
                    for (int j = 0; j < orders.Count; j++)
                    {
                        object[] o = (object[])orders[j];
                        if ((string)o[0] == s && (string)o[5] == "RTN")
                        {
                            rtn = rtn + (double)o[4];
                        }
                    }
                    for (int j = 0; j < orders.Count; j++)
                    {
                        object[] o = (object[])orders[j];
                        if ((string)o[0] == s && (string)o[1] == "CARD" && (string)o[5] == "OK")
                        {
                            card = card + (double)o[4];
                        }
                    }
                    for (int j = 0; j < orders.Count; j++)
                    {
                        object[] o = (object[])orders[j];
                        if ((string)o[0] == s && (string)o[1] == "CASH" && (string)o[5] == "OK")
                        {
                            cash = cash + (double)o[4];
                        }
                    }
                    for (int j = 0; j < orders.Count; j++)
                    {
                        object[] o = (object[])orders[j];
                        if ((string)o[0] == s && (string)o[1] == "POINT" && (string)o[5] == "OK")
                        {
                            point = point + (double)o[4];
                        }
                    }

                    double fee = Math.Round(card * 0.025);
                    double net = sales - rtn - fee;

                    Console.WriteLine(String.Format("{0,-6}{1,5}{2,12}{3,10}{4,12}{5,10}{6,10}{7,8}{8,12}",
                        s, cnt[s], sales.ToString("#,##0"), rtn.ToString("#,##0"), card.ToString("#,##0"),
                        cash.ToString("#,##0"), point.ToString("#,##0"), fee.ToString("#,##0"), net.ToString("#,##0")));

                    sql = sql + "INSERT INTO TB_DAILY_SETTLE (BIZ_DT, STORE_CD, SALES_AMT, RTN_AMT, FEE_AMT, NET_AMT) VALUES ('"
                        + bizDate + "', '" + s + "', " + sales + ", " + rtn + ", " + fee + ", " + net + ");" + Environment.NewLine;

                    tCnt = tCnt + (int)cnt[s];
                    tSales = tSales + sales;
                    tRtn = tRtn + rtn;
                    tCard = tCard + card;
                    tCash = tCash + cash;
                    tPoint = tPoint + point;
                    tFee = tFee + fee;
                    tNet = tNet + net;
                }

                Console.WriteLine("-------------------------------------------------------------------------------------");
                Console.WriteLine(String.Format("{0,-6}{1,5}{2,12}{3,10}{4,12}{5,10}{6,10}{7,8}{8,12}",
                    "TOTAL", tCnt, tSales.ToString("#,##0"), tRtn.ToString("#,##0"), tCard.ToString("#,##0"),
                    tCash.ToString("#,##0"), tPoint.ToString("#,##0"), tFee.ToString("#,##0"), tNet.ToString("#,##0")));

                // ---------------- 재고 부족 ----------------
                Console.WriteLine();
                Console.WriteLine("LOW STOCK (< 5)");
                string low = "";
                for (int k = 0; k < products.Count; k++)
                {
                    string[] p = (string[])products[k];
                    int remain = Convert.ToInt32(p[2]) - sold[k];
                    if (remain < 5)
                    {
                        low = low + String.Format("{0,-10}{1,6}", p[0], remain) + Environment.NewLine;
                    }
                }
                if (low == "") low = "(none)" + Environment.NewLine;
                Console.Write(low);

                // ---------------- ERP 업로드용 SQL ----------------
                Console.WriteLine();
                Console.WriteLine("-- ERP UPLOAD");
                Console.Write(sql);
                Console.WriteLine("-- END");
            }
            catch (Exception ex)
            {
                Console.WriteLine("ERROR: " + ex.Message);
                return 9;
            }

            return 0;
        }

        static int FindProduct(string sku)
        {
            for (int i = 0; i < products.Count; i++)
            {
                string[] p = (string[])products[i];
                if (p[0] == sku) return i;
            }
            return -1;
        }
    }
}
