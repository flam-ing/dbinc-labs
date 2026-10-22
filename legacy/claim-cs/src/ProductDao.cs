using System;
using System.Data;
using System.IO;
using System.Text;

namespace NuriClaim
{
    /// <summary>
    /// 상품 마스터.
    /// 원래 DB(TB_PRODUCT)에서 읽었는데 2012.03 이전 때 배치 서버에서 DB 접속이 막혀서 CSV로 바꿈 (임시)
    /// </summary>
    public class ProductDao
    {
        public static DataTable LoadProduct(string strPath)
        {
            DataTable dtPrd = new DataTable("TB_PRODUCT");

            StreamReader sr = new StreamReader(strPath, Encoding.Default);     // 엑셀에서 저장한 파일 (ANSI)
            string strLine = sr.ReadLine();
            string[] arrHead = strLine.Split(',');
            for (int i = 0; i < arrHead.Length; i++)
            {
                dtPrd.Columns.Add(arrHead[i]);
            }

            while ((strLine = sr.ReadLine()) != null)
            {
                if (strLine.Trim() == "") continue;
                try
                {
                    dtPrd.Rows.Add(strLine.Split(','));
                }
                catch
                {
                }
            }
            sr.Close();

            //string strSql = "SELECT * FROM TB_PRODUCT WHERE USE_YN = 'Y'";
            //SqlDataAdapter da = new SqlDataAdapter(strSql, modGlobal.DB_CONN);
            //da.Fill(dtPrd);

            return dtPrd;
        }

        public static DataRow FindProduct(DataTable dtPrd, string strPrdCd)
        {
            DataRow[] arrRow = dtPrd.Select("PRD_CD = '" + strPrdCd + "'");
            if (arrRow.Length > 0)
            {
                return arrRow[0];
            }
            return null;
        }
    }
}
