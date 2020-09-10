using System;
using System.Collections.Generic;

namespace TD {

    public class TemplateRowTD : TableRowData {
        public Int64 id;

        static TableData<TemplateRowTD> m_data;
        public static TableData<TemplateRowTD> TableData() {
            if (m_data == null) {
                string keyJson = "[\"id\"]";
                string exportKeyJson = "[\"id\"]";
                string valJson = "[[1001]]";
                m_data = new TableData<TemplateRowTD>(keyJson, exportKeyJson, valJson);
            }
            return m_data;
        }
    }

}
