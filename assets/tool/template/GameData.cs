using System.Collections.Generic;

interface ITableData {
    // 根据导出的Key值获取【速度较快】
    T Get(string key, string index);
    T[] GetAll(string key, string index);
    
    // 在整个表的数据中查找【速度缓慢】
    T Find(string key, string index);
    T[] FindAll(string key, string index);
}

class GameData {
    Dictionary<string, ITableData> m_dataDict = new Dictionary<string, ITableData>();

    GameData m_instance;

    public static GameData Instance() {
        if (m_instance != null) {
            return m_instance;
        }
        m_instance = GameData();
        return m_instance;
    }

    public ITableData this[string name] {
        get {
            if (!this.m_dataDict.ContainsKey(name)) {
                this.m_dataDict.Add(name, GameDataCreater.Create(name));
            }
            return this.m_dataDict[name];
        }
    }

}