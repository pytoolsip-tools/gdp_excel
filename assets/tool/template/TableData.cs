using System.Collections.Generic;

public class TableData {
    // 根据导出的Key值获取【速度较快】
    public virtual T Get(string key, string index) {
        return null;
    }
    public virtual T[] GetAll(string key, string index) {
        return null;
    }
    public virtual T Get(int id, string index) {
        return null;
    }
    public virtual T[] GetAll(int id, string index) {
        return null;
    }
    
    // 在整个表的数据中查找【速度缓慢】
    public virtual T Find(string key, string index) {
        return null;
    }
    public virtual T[] FindAll(string key, string index) {
        return null;
    }
    public virtual T Find(int id, string index) {
        return null;
    }
    public virtual T[] FindAll(int id, string index) {
        return null;
    }
}
