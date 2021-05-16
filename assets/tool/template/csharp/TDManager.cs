using System;
using System.Reflection;
using System.Collections.Generic;

namespace DH.TD {
    public class TDManager {
        static TDManager m_data;
        public static TDManager Instance {
            get {
                if (m_data == null) {
                    m_data = new TDManager();
                }
                return m_data;
            }
        }
        
        public static T Get<T>(object val) {
            return TDManager.Instance.single<T>("Get", val);
        }
        public static T Get<T>(object val, string key) {
            return TDManager.Instance.single<T>("Get", val, key);
        }
        
        public static T Find<T>(object val) {
            return TDManager.Instance.single<T>("Find", val);
        }
        public static T Find<T>(object val, string key) {
            return TDManager.Instance.single<T>("Find", val, key);
        }
        
        public static T[] GetAll<T>(object val) {
            return TDManager.Instance.multiple<T>("GetAll", val);
        }
        public static T[] GetAll<T>(object val, string key) {
            return TDManager.Instance.multiple<T>("GetAll", val, key);
        }
        
        public static T[] FindAll<T>(object val) {
            return TDManager.Instance.multiple<T>("FindAll", val);
        }
        public static T[] FindAll<T>(object val, string key) {
            return TDManager.Instance.multiple<T>("FindAll", val, key);
        }

        public static T[] All<T>() {
            return TDManager.Instance.multipleWithoutArgs<T>("All");
        }

        // 校验参数
        bool verifyArgs(object obj, ref object[] args) {
            if (args.Length == 0) {
                return false;
            }
            if (args.Length == 1) {
                string defaultKey = obj.GetType().GetProperty("DefaultKey").GetValue(obj).ToString();
                args = new object[]{args[0], defaultKey};
            }
            return true;
        }

        // 获取TableData
        object getTableData<T>(ref object[] args, bool isVerifyArgs=true) {
            Type dataType = typeof(T);
            MethodInfo methodInfo = dataType.GetMethod("TableData");
            if (methodInfo == null) {
                return null;
            }
            var obj = methodInfo.Invoke(null, null);
            if (isVerifyArgs && !verifyArgs(obj, ref args)) {
                return null;
            }
            return obj;
        }

        T single<T>(string method, params object[] args) {
            var obj = getTableData<T>(ref args);
            if (obj == null) {
                return default(T);
            }
            return (T) obj.GetType().GetMethod(method).Invoke(obj, args);
        }
        
        T[] multiple<T>(string method, params object[] args) {
            var obj = getTableData<T>(ref args);
            if (obj == null) {
                return new T[0];
            }
            return (T[]) obj.GetType().GetMethod(method).Invoke(obj, args);
        }

        T[] multipleWithoutArgs<T>(string method, params object[] args) {
            var obj = getTableData<T>(ref args, false);
            if (obj == null) {
                return new T[0];
            }
            return (T[]) obj.GetType().GetMethod(method).Invoke(obj, args);
        }
        
    }

    public class TableRowData {
        public void Init(object[] args, string[] keyList) {
            for (int i = 0; i < keyList.Length; i++) {
                if (i >= args.Length) {
                    break;
                }
                string key = keyList[i];
                FieldInfo field = GetType().GetField(key);
                if (field == null) {
                    continue;
                }
                field.SetValue(this, args[i]);
            }
        }

        public object this[string name]{
            get{
                FieldInfo fieldInfo = GetType().GetField(name);
                if (fieldInfo == null) {
                    return null;
                }
                return fieldInfo.GetValue(this);
            }
        }

        public T GetVal<T>(string name) {
            object obj = this[name];
            if (obj == null) {
                return default(T);
            }
            return (T) obj;
        }

        public List<object[]> GetKvList(string keyName, string ValName, int count) {
            List<object[]> kvList = new List<object[]>();
            for (int i = 0; i < count; i++) {
                object keyObj = this[string.Format("{0}_{1}", keyName, i+1)];
                if (keyObj == null) {
                    continue;
                }
                object valObj = this[string.Format("{0}_{1}", ValName, i+1)];
                if (valObj == null) {
                    continue;
                }
                kvList.Add(new object[] {keyObj, valObj});
            }
            return kvList;
        }

        public List<T> GetValList<T>(string name, int count, bool isIncludeNull=false) {
            List<T> valList = new List<T>();
            object obj;
            for (int i = 0; i < count; i++) {
                obj = this[string.Format("{0}_{1}", name, i+1)];
                if (obj != null) {
                    valList.Add(default(T));
                } else if (isIncludeNull) {
                    valList.Add((T) obj);
                }
            }
            return valList;
        }

    }

    public class TableData<T> where T:TableRowData {
        Dictionary<string, Dictionary<object, List<int>>> m_dataMap = new Dictionary<string, Dictionary<object, List<int>>>();

        List<T> m_data = new List<T>();

        string m_defaultKey = "id";
        string[] m_keyList = new string[0];
        string[] m_exportKeyList = new string[0];

        public string DefaultKey {
            get { return m_defaultKey; }
        }

        public TableData(string keyJson, string exportKeyJson, string valJson) {
            initKey(keyJson, exportKeyJson);
            initVal(valJson);
        }

        void initKey(string keyJson, string exportKeyJson) {
            // 解析key列表
            List<object> keyList = MiniJSON.Json.Deserialize(keyJson) as List<object>;
            if (keyList != null) {
                m_keyList = new string[keyList.Count];
                keyList.CopyTo(m_keyList);
            }
            // 解析导出的key列表
            List<object> exportKeyList = MiniJSON.Json.Deserialize(exportKeyJson) as List<object>;
            if (exportKeyList != null) {
                m_exportKeyList = new string[exportKeyList.Count];
                exportKeyList.CopyTo(m_exportKeyList);
            }
            // 设置默认key值
            if (m_exportKeyList.Length > 0) {
                m_defaultKey = m_exportKeyList[0];
            } else if (m_keyList.Length > 0) {
                m_defaultKey = m_keyList[0];
            }
        }

        void initVal(string valJson) {
            List<object> valList = MiniJSON.Json.Deserialize(valJson) as List<object>;
            foreach (List<object> val in valList) {
                T data = Activator.CreateInstance<T>();
                data.Init(val.ToArray(), m_keyList);
                m_data.Add(data);
                // 加入到dataMap
                addToDataMap(data, m_data.Count - 1);
            }
        }

        void addToDataMap(T data, int index) {
            foreach (string exportKey in m_exportKeyList) {
                if (!m_dataMap.ContainsKey(exportKey)) {
                    m_dataMap[exportKey] = new Dictionary<object, List<int>>();
                }
                object val = data[exportKey];
                if (val == null) {
                    continue;
                }
                if (!m_dataMap[exportKey].ContainsKey(val)) {
                    m_dataMap[exportKey][val] = new List<int>();
                }
                m_dataMap[exportKey][val].Add(index);
            }
        }

        object verifyType(object val) {
            Type valType = val.GetType();
            if (valType == typeof(Int16) || valType == typeof(Int32)) {
                return Int64.Parse(val.ToString());
            }
            return val;
        }

        // 根据导出的Key值获取【速度较快】
        public T Get(object val, string key) {
            if (m_dataMap.ContainsKey(key)) {
                val = verifyType(val);  // 校验类型
                if (m_dataMap[key].ContainsKey(val)) {
                    List<int> indexList = m_dataMap[key][val];
                    if (indexList.Count > 0) {
                        return m_data[indexList[0]];
                    }
                }
            }
            return null;
        }
        public T[] GetAll(object val, string key) {
            List<T> rowList = new List<T>();
            if (m_dataMap.ContainsKey(key)) {
                val = verifyType(val);  // 校验类型
                if (m_dataMap[key].ContainsKey(val)) {
                    List<int> indexList = m_dataMap[key][val];
                    if (indexList.Count > 0) {
                        foreach (int idx in indexList) {
                            rowList.Add(m_data[idx]);
                        }
                    }
                }
            }
            return rowList.ToArray();
        }
        
        // 在整个表的数据中查找【速度缓慢】
        public T Find(object val, string key) {
            T rowData = this.Get(val, key);
            if (rowData != null) {
                return rowData;
            }
            val = verifyType(val);  // 校验类型
            for (int i = 0; i < m_data.Count; i++) {
                if (m_data[i][key] == null) {
                    break;
                }
                if (m_data[i][key] == val) {
                    return m_data[i];
                }
            }
            return null;
        }
        public T[] FindAll(object val, string key) {
            T[] rowArray = this.GetAll(val, key);
            if (rowArray.Length > 0) {
                return rowArray;
            }
            List<T> rowList = new List<T>();
            val = verifyType(val);  // 校验类型
            for (int i = 0; i < m_data.Count; i++) {
                if (m_data[i][key] == null) {
                    break;
                }
                if (m_data[i][key] == val) {
                    rowList.Add(m_data[i]);
                }
            }
            return rowList.ToArray();
        }

        public T[] All() {
            return m_data.ToArray();
        }
    }
}
