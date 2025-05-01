import os;
import re;
import json;

from function.base import *;

CURRENT_PATH = os.path.dirname(os.path.realpath(__file__)); # 当前文件目录

GameDataParser = require(CURRENT_PATH, "GameDataParser", "GameDataParser");

class CsharpGameDataParser(GameDataParser):
	DATA_TYPE_CONFIG = {
		"TEXT" : "string",
		"STRING" : "string",
		"INT" : "Int64",
		"BOOL" : "bool",
		"FLOAT" : "double",

		"LIST<TEXT>" : "string[]",
		"LIST<STRING>" : "string[]",
		"LIST<INT>" : "Int64[]",
		"LIST<BOOL>" : "bool[]",
		"LIST<FLOAT>" : "double[]",

		"LIST2<TEXT>" : "string[,]",
		"LIST2<STRING>" : "string[,]",
		"LIST2<INT>" : "Int64[,]",
		"LIST2<BOOL>" : "bool[,]",
		"LIST2<FLOAT>" : "double[,]",

		"SET" : "TableSetData",
		"LIST<SET>" : "TableSetData[]",
	}

	def __init__(self, dirPath, outputPath, templatePath, collectionsPath):
		super(CsharpGameDataParser, self).__init__(dirPath, outputPath, templatePath);

		self.__collectionsPath = collectionsPath;
		if not os.path.exists(collectionsPath):
			os.makedirs(collectionsPath);

	def getDataListStr(self, dataList):
		dataJson = json.dumps(dataList, ensure_ascii=False);
		dataJsonRe = re.search("^\[(.*)\]$", dataJson);
		if dataJsonRe:
			return dataJsonRe.group(1);
		return dataJson;

	def getListDataValStr(self, keyType, keyTypeParams, val):
		if keyType == "SET":
			return f"new {self.DATA_TYPE_CONFIG[keyType]}({self.getSetDataValStr(keyTypeParams, val)})";
		elif keyType == "LIST<SET>":
			setTypeCfg = self.DATA_TYPE_CONFIG["SET"];
			dataListStr = ", ".join([f"new {setTypeCfg}({self.getSetDataValStr(keyTypeParams, subVal)})" for subVal in val]);
			return f"new {self.DATA_TYPE_CONFIG[keyType]}{{{dataListStr}}}";
		else:
			keyTypeRe = re.search("^LIST2<(.*)>$", keyType);
			if keyTypeRe:
				dataListStr = ", ".join([f"{{{self.getDataListStr(subVal)}}}" for subVal in val]);
			else:
				dataListStr = self.getDataListStr(val);
			return f"new {self.DATA_TYPE_CONFIG[keyType]}{{{dataListStr}}}";

	def getSetDataValStr(self, keyTypeParams, setVal):
		argList = [];
		for i, subVal in enumerate(setVal):
			valStr = self.getDataListStr([subVal])
			if keyTypeParams[i] in ("TEXT", "LIST<TEXT>", "LIST2<TEXT>"):
				argList.append(f"new TableSetArgData({i}, null, ()=>{{return _text_({valStr});}})");
			else:
				argList.append(f"new TableSetArgData({i}, {valStr}, null)");
		return ", ".join(argList);

	def getReturnKeyStr(self, keyType, key):
		if keyType in ("TEXT", "LIST<TEXT>", "LIST2<TEXT>"):
			return f"_text_(this._{key})";
		return f"this._{key}";

	def getDataContent(self, className, keyTypeList, exportKeyList, valList):
		dataKeyListStr = self.getDataListStr([kt[1] for kt in keyTypeList]);
		exportKeyListStr = self.getDataListStr(exportKeyList);
		valListStrList = [];
		for val in valList:
			valStrList = [];
			for i, elemVal in enumerate(val):
				if isinstance(elemVal, list):
					keyType, keyTypeParams = keyTypeList[i][0];
					valStrList.append(self.getListDataValStr(keyType, keyTypeParams, elemVal));
				else:
					valStrList.append(f"{self.getDataListStr(elemVal)}");
			valListStr = ", ".join(valStrList);
			valListStrList.append(f"					new {className}({valListStr})");
		valueListStr = ",\n".join(valListStrList);
	
		declareList = [];  # 声明列表
		paramList = [];  # 参数列表
		assignList = [];  # 赋值列表
		for keyTypeInfo, key in keyTypeList:
			keyType, _ = keyTypeInfo;
			returnKeyStr = self.getReturnKeyStr(keyType, key);
			declareList.append(f"""		{self.DATA_TYPE_CONFIG[keyType]} _{key}; public {self.DATA_TYPE_CONFIG[keyType]} {key} {{get {{return {returnKeyStr};}}}}""");
			paramList.append(f"""{self.DATA_TYPE_CONFIG[keyType]} {key}""");
			assignList.append(f"""			this._{key} = {key};""");
		declareListStr = "\n".join(declareList);
		paramListStr = ", ".join(paramList);
		assignListStr = "\n".join(assignList);

		return f"""using System;
using System.Collections.Generic;

namespace DH.TD {{
	public class {className} : TableRowData {{
{declareListStr}

		public {className}({paramListStr}) {{
{assignListStr}
		}}

		static TableData<{className}> m_data;
		public static TableData<{className}> TableData() {{
			if (m_data == null) {{
				m_data = new TableData<{className}>(new string[]{{{exportKeyListStr}}}, new string[]{{{dataKeyListStr}}}, new {className}[]{{
{valueListStr}
				}});
			}}
			return m_data;
		}}
	}}
}}
""";

	def onSaveData(self, sheetName, data):
		filePath = os.path.join(self.__collectionsPath, f"{sheetName}TD.cs");
		with open(filePath, "w+", encoding="utf-8") as f:
			f.write(data);

	def onParse(self, sheet, logger):
		keyTypeList = [];
		for key in sheet.keyList:
			keyTypeList.append((sheet.getTypeParamsByKey(key), key));
		dataContent = self.getDataContent(sheet.name + "TD", keyTypeList, sheet.exportKeyList, sheet.valList);
		return dataContent;

	def afterParse(self, validSheetNames, logger):
		for name in os.listdir(self.__collectionsPath):
			fileName = os.path.splitext(name)[0];
			if not fileName.endswith("TD"):
				continue;
			sheetName = fileName[:-2];
			if sheetName in validSheetNames:
				continue;
			fullPath = os.path.join(self.__collectionsPath, name);
			if os.path.isfile(fullPath):
				os.remove(fullPath);
				logger(f"Succeeded to remove file[{name}].");
