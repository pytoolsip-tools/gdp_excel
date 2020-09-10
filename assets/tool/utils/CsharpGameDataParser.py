import os;
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
	};

	def __init__(self, dirPath, outputPath, templatePath, collectionsPath):
		super(CsharpGameDataParser, self).__init__(dirPath, outputPath, templatePath);
		self.__collectionsPath = collectionsPath;

	def getProperty(self, keyType, key):
		return f"		public {self.DATA_TYPE_CONFIG[keyType]} {key};"

	def getTemplate(self, className, properties, keyJson, exportKeyJson, valJson):
		keyJson = keyJson.replace("\"", "\\\"");
		exportKeyJson = exportKeyJson.replace("\"", "\\\"");
		valJson = valJson.replace("\"", "\\\"");
		return f"""

	public class {className} : TableRowData {{
{properties}

		static TableData<{className}> m_data;
		public static TableData<{className}> TableData() {{
			if (m_data == null) {{
				string keyJson = "{keyJson}";
				string exportKeyJson = "{exportKeyJson}";
				string valJson = "{valJson}";
				m_data = new TableData<{className}>(keyJson, exportKeyJson, valJson);
			}}
			return m_data;
		}}
	}}

"""

	def onStartParse(self):
		with open(self.__collectionsPath, "w+") as f:
			f.write("""
using System;
using System.Collections.Generic;

namespace TD {
""");

	def onComplete(self):
		self.onSaveData("}");

	def onSaveData(self, data):
		with open(self.__collectionsPath, "a+") as f:
			f.write(data);  # 追加

	def onParse(self, sheet, logger):
		properties = [];
		for key in sheet.keyList:
			properties.append(self.getProperty(sheet.getTypeByKey(key), key));
		template = self.getTemplate(sheet.name + "TD", "\n".join(properties),
			json.dumps(sheet.keyList), json.dumps(sheet.exportKeyList), json.dumps(sheet.valList));
		return template;
