using System;
using System.Collections.Generic;

namespace DH.TD {

    public class TemplateRowTD : TableRowData {
        public Int64 id;

        public TemplateRowTD(Int64 id) {
            this.id = id;
        }

        static TableData<TemplateRowTD> m_data;
        public static TableData<TemplateRowTD> TableData() {
            if (m_data == null) {
                m_data = new TableData<TemplateRowTD>(new string[]{"id"}, new TemplateRowTD[]{
                    new TemplateRowTD(1001)
                });
            }
            return m_data;
        }
    }

}
