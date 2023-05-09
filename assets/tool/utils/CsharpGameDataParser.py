import os;
import re;
import json;

from function.base import *;

CURRENT_PATH = os.path.dirname(os.path.realpath(__file__)); # 当前文件目录

GameDataParser = require(CURRENT_PATH, "GameDataParser", "GameDataParser");

class CsharpGameDataParser(GameDataParser):
	DATA_TYPE_CONFIG = {
		"STRING" : "string",
		"INT" : "Int64",
		"BOOL" : "bool",
		"FLOAT" : "double",
		"LIST<STRING>" : "string[]",
		"LIST<INT>" : "Int64[]",
		"LIST<BOOL>" : "bool[]",
		"LIST<FLOAT>" : "double[]",
	};

	def __init__(self, dirPath, outputPath, templatePath, collectionsPath):
		super(CsharpGameDataParser, self).__init__(dirPath, outputPath, templatePath);

		self.__collectionsPath = collectionsPath;
		if not os.path.exists(collectionsPath):
			os.makedirs(collectionsPath);

	def getDataListStr(self, dataList):
		dataJson = json.dumps(dataList, ensure_ascii=False);
		dataJsonRe = re.search("\[(.*)\]", dataJson);
		if dataJsonRe:
			return dataJsonRe.group(1);
		return dataJson;

	def getDataContent(self, className, keyTypeList, exportKeyList, valList):
		exportKeyListStr = self.getDataListStr(exportKeyList);
		valListStrList = [];
		for val in valList:
			valStrList = []
			for i, elemVal in enumerate(val):
				if isinstance(elemVal, list):
					keyType, key = keyTypeList[i];
					valStrList.append(f"{self.DATA_TYPE_CONFIG[keyType]} {{{self.getDataListStr(elemVal)}}}");
				else:
					valStrList.append(f"{self.getDataListStr(elemVal)}");
			valListStr = ", ".join(valStrList);
			valListStrList.append(f"					new {className}({valListStr})");
		valueListStr = ",\n".join(valListStrList);
	
		declareList = [];  # 声明列表
		paramList = [];  # 参数列表
		assignList = [];  # 赋值列表
		for keyType, key in keyTypeList:
			declareList.append(f"""		public {self.DATA_TYPE_CONFIG[keyType]} {key};""");
			paramList.append(f"""{self.DATA_TYPE_CONFIG[keyType]} {key}""");
			assignList.append(f"""			this.{key} = {key};""");
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
				m_data = new TableData<{className}>(new string[]{{{exportKeyListStr}}}, new {className}[]{{
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
			keyTypeList.append((sheet.getTypeByKey(key), key));
		dataContent = self.getDataContent(sheet.name + "TD", keyTypeList, sheet.exportKeyList, sheet.valList);
		return dataContent;

	def afterParse(self, validSheetNames, logger):
		for name in os.listdir(self.__collectionsPath):
			if not name.endswith("TD"):
				continue;
			sheetName = name[:-2];
			if sheetName in validSheetNames:
				continue;
			fullPath = os.path.join(self.__collectionsPath, name);
			if os.path.isfile(fullPath):
				os.remove(fullPath);
