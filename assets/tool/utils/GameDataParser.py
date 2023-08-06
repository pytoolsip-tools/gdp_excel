import os;
import re;
import shutil;
import xlrd;
import json;
import hashlib;
import threading;


def convertDataList(val, raiseKey=""):
	try:
		val = val.strip();
		if val:
			return json.loads(val);
	except Exception:
		raise Exception(f"Failed to load data list by val[{val}]!!! [{raiseKey}]");
	return [];


def ConvertListData(val, typeFunc):
	dataList = convertDataList(val, raiseKey="List");
	return [typeFunc(data) for data in dataList];


def convertListDataByTypes(data, types):
	if not isinstance(data, list):
		raise Exception(f"Invalid convert list data[{data}] by types!");
	setData = [];
	for i, typeStr in enumerate(types):
		typeCfg = TABLE_DATA_TYPE_DICT[typeStr];
		if i < len(data):
			setData.append(typeCfg["func"](data[i]));
		else:
			setData.append(typeCfg["default"]);
	return setData;
	

def ConvertSetData(val, types, isList, raiseKey="Set"):
	dataList = convertDataList(val, raiseKey=raiseKey);
	if isList:
		setDataList = [];
		for data in dataList:
			setDataList.append(convertListDataByTypes(data, types));
		return setDataList;
	return convertListDataByTypes(dataList, types);


def ConvertList2Data(val, typeFunc):
	dataList = convertDataList(val, raiseKey="List2");
	colCnt = 0;
	for data in dataList:
		if colCnt <= 0:
			colCnt = len(data);
		if not isinstance(data, list) or len(data) != colCnt:
			raise Exception(f"Invalid convert list2 data[{data}]!");
		for i in range(len(data)):
			data[i] = typeFunc(data[i]);
	return dataList;


TABLE_DATA_DEFAULT_TYPE = "STRING";
TABLE_DATA_TYPE_DICT = {
	"STRING" : {"func": lambda val: str(val), "default": ""},
	"INT" : {"func": lambda val: int(val), "default": 0},
	"BOOL" : {"func": lambda val: bool(val), "default": False},
	"FLOAT" : {"func": lambda val: float(val), "default": 0},

	"LIST<STRING>" : {"func": lambda val: ConvertListData(val, str), "default": []},
	"LIST<INT>" : {"func": lambda val: ConvertListData(val, int), "default": []},
	"LIST<BOOL>" : {"func": lambda val: ConvertListData(val, bool), "default": []},
	"LIST<FLOAT>" : {"func": lambda val: ConvertListData(val, float), "default": []},

	"LIST2<STRING>" : {"func": lambda val: ConvertList2Data(val, str), "default": []},
	"LIST2<INT>" : {"func": lambda val: ConvertList2Data(val, int), "default": []},
	"LIST2<BOOL>" : {"func": lambda val: ConvertList2Data(val, bool), "default": []},
	"LIST2<FLOAT>" : {"func": lambda val: ConvertList2Data(val, float), "default": []},

	"SET" : {"func": lambda val, types: ConvertSetData(val, types, False, raiseKey="SET"), "default": None},
	"LIST<SET>" : {"func": lambda val, types: ConvertSetData(val, types, True, raiseKey="LIST<SET>"), "default": []},
};

class SheetDataParser(object):

	def __init__(self, sheet):
		super(SheetDataParser, self).__init__();
		self.__sheet = sheet;
		self.__startIndex = -1;
		self.__keyDict = {};
		self.__typeDict = {};
		self.__exportIdxList = [];
		self.__defaultDict = {};

		self.initKeyIndex();
		
	@property
	def isValid(self):
		if not self.name:
			return False;
		if not self.__keyDict:
			return False;
		return self.__startIndex > 0;
	
	@property
	def sheet(self):
		return self.__sheet;
	
	@property
	def name(self):
		ret = re.search(r".*\(([_a-zA-Z]+)\)$", self.sheet.name)
		if ret:
			return ret.group(1);
		return ""
		
	@property
	def idxList(self):
		idxList = list(self.__keyDict.keys());
		idxList.sort();
		return idxList;

	@property
	def keyList(self):
		keyList = [];
		for idx in self.idxList:
			keyList.append(self.__keyDict[idx]);
		return keyList;
		
	@property
	def exportKeyList(self):
		exportKeyList = [];
		for idx in self.__exportIdxList:
			exportKeyList.append(self.__keyDict[idx]);
		return exportKeyList;
		
	@property
	def valList(self):
		valList = [];
		if not self.isValid:
			return valList;
		idxList = self.idxList;
		for i in range(self.__startIndex, self.sheet.nrows):
			row = self.sheet.row_values(i);
			if self.checkIsAnnotated(row):
				continue;
			val = [];
			for idx in idxList:
				key = self.__keyDict[idx];
				typeStr, typeParams = self.getTypeParamsByKey(key);
				typeFunc = TABLE_DATA_TYPE_DICT[typeStr]["func"];
				if isinstance(row[idx], str) and not row[idx]:
					val.append(self.getDefaultByKey(key));
				else:
					if typeParams is None:
						val.append(typeFunc(self.convertVal(row[idx])));
					else:
						val.append(typeFunc(self.convertVal(row[idx]), typeParams));
			valList.append(val);
		return valList;

	@staticmethod
	def checkIsAnnotated(row):
		if re.search(r"^#.*", str(row[0])):
			return True;
		for val in row:
			if val:
				return False;
		return True;

	@staticmethod
	def convertVal(val):
		if isinstance(val, float) and int(val) == val:
			return int(val);  # 为了解决整数转字符串有误问题
		return val;
	
	def getTypeParams(self, typeStr):
		ret = re.search("(LIST<)?SET<([a-zA-Z,\s]+)>>?", typeStr);
		if ret:
			typeStrList = [typeStr.strip() for typeStr in ret.group(2).split(",")];
			if ret.group(1):
				return "LIST<SET>", typeStrList;
			return "SET", typeStrList;
		return typeStr, None;

	def getTypeParamsByKey(self, key):
		typeStr = self.__typeDict.get(key, TABLE_DATA_DEFAULT_TYPE);
		return self.getTypeParams(typeStr);

	def getDefaultByKey(self, key):
		typeStr, typeParams = self.getTypeParamsByKey(key);
		typeCfg = TABLE_DATA_TYPE_DICT[typeStr];
		defaultVal = typeCfg["default"];
		if key in self.__defaultDict:
			try:
				if typeParams is None:
					defaultVal = typeCfg["func"](self.__defaultDict[key]);
				else:
					defaultVal = typeCfg["func"](self.__defaultDict[key], typeParams);
			except Exception:
				pass
		return defaultVal;
	
	def initKeyIndex(self):
		startIdx = -1;
		exportIdxList = [];
		for idx in range(self.sheet.nrows):
			startIdx = idx + 1;
			row = self.sheet.row_values(idx);
			if self.checkIsAnnotated(row):
				continue;
			if not self.__keyDict:
				for i, val in enumerate(row):
					if not isinstance(val, str):
						continue;
					valStrip = val.strip();
					if valStrip == "*":
						if i not in exportIdxList:
							exportIdxList.append(i);
					elif valStrip:
						self.__keyDict[i] = valStrip;
						if not exportIdxList:
							exportIdxList.append(i);
				if self.__keyDict:
					for i in exportIdxList:
						if i in self.__keyDict:
							self.__exportIdxList.append(i);
					self.__exportIdxList.sort();
			else:
				for i, key in self.__keyDict.items():
					if not isinstance(row[i], str):
						continue;
					typeStrip = row[i].strip();
					ret = re.search("([a-zA-Z<>]+)\((.*)\)", typeStrip);
					if not ret:
						typeStr = typeStrip.upper();
						if self.getTypeParams(typeStr)[0] in TABLE_DATA_TYPE_DICT:
							self.__typeDict[key] = typeStr;
					else:
						typeStr = ret.group(1).upper();
						if self.getTypeParams(typeStr)[0] in TABLE_DATA_TYPE_DICT:
							self.__typeDict[key] = typeStr;
							self.__defaultDict[key] = ret.group(2);
				if self.__typeDict:
					break;
		self.__startIndex = startIdx;
	
	def convertKeyDict(self):
		newKeyDict = {};
		for i, key in self.__keyDict.items():
			ret = re.search(r"^([_a-zA-Z]+)\+\d*$", key);
			if ret:
				if key not in newKeyDict:
					newKeyDict[key] = [];
				newKeyDict[key].append(i);
			else:
				newKeyDict[key] = i;
		return newKeyDict;


class TableDataParser(object):
	def __init__(self, filePath, logger):
		super(TableDataParser, self).__init__();
		self.__filePath = filePath;
		self.__logger = logger;
		self.__workbook = None;
		self.__iterIndex = 0;

		self.initWorkbook();
	
	def initWorkbook(self):
		try:
			self.__workbook = xlrd.open_workbook(self.__filePath);
		except Exception as e:
			self.__logger(f"Failed to open workbook[{self.__filePath}]! Err-> {e}", "error");

	@property
	def isValid(self):
		return self.__workbook is not None;

	@property
	def filePath(self):
		return self.__filePath;

	def __iter__(self):
		self.__iterIndex = 0;
		return self;
	
	def __next__(self):
		if self.isValid and 0 <= self.__iterIndex < self.__workbook.nsheets:
			sheetData = SheetDataParser(self.__workbook.sheet_by_index(self.__iterIndex));
			self.__iterIndex += 1;
			if not sheetData.isValid:
				self.__logger(f"Invalid sheet data[{sheetData.sheet.name}]!", "warning");
				return self.__next__();
			return sheetData;
		else:
			raise StopIteration;

	@property
	def sheets(self):
		return iter(self);

class GameDataParser(object):
	MD5_MAP_FILE_NAME = "_excel_data_cache_map";

	def __init__(self, dirPath, outputPath, templatePath):
		super(GameDataParser, self).__init__();
		self.__dirPath = dirPath;
		self.__outputPath = outputPath;
		self.__templatePath = templatePath;
		self.verifyOutputPath();
	
	def verifyOutputPath(self):
		if not os.path.exists(self.__outputPath):
			os.makedirs(self.__outputPath);
	
	def copyTemplate(self):
		if not os.path.exists(self.__templatePath):
			return;
		for name in os.listdir(self.__templatePath):
			fullPath = os.path.join(self.__templatePath, name);
			if os.path.isdir(fullPath):
				shutil.copytree(fullPath, self.__outputPath);
			elif os.path.isfile(fullPath):
				shutil.copy(fullPath, self.__outputPath);
	
	def getDataCacheMap(self):
		md5MapPath = os.path.join(self.__outputPath, self.MD5_MAP_FILE_NAME+".json");
		if os.path.exists(md5MapPath):
			with open(md5MapPath, "r") as f:
				return json.loads(f.read());
		return {};
		
	def setDataCacheMap(self, cacheMap={}):
		md5MapPath = os.path.join(self.__outputPath, self.MD5_MAP_FILE_NAME+".json");
		with open(md5MapPath, "w") as f:
			f.write(json.dumps(cacheMap));

	def getMd5ByFilePath(self, filePath):
		if os.path.exists(filePath):
			with open(filePath, "rb") as f:
				return hashlib.md5(f.read()).hexdigest();
		return "";

	def parse(self, logger=None, progress=None, interrupt=None, callback=None, isUseCache=True):
		if not callable(logger):
			logger = self.outputLog;
		threading.Thread(target = self.__parseByThread__, args = (logger, progress, interrupt, callback, isUseCache)).start();
	
	def __parseByThread__(self, logger=None, progress=None, interrupt=None, callback=None, isUseCache=True):
		self.copyTemplate();
		if not os.path.exists(self.__dirPath):
			logger(f"Input path[{self.__dirPath}] is not non-existent!", "error");
			return;
		# 开始回调
		self.onStartParse();
		# 遍历的有效表名
		validSheetNames = [];
		# 解析数据
		newMd5Map = {};
		md5Map = {};
		if isUseCache:
			md5Map = self.getDataCacheMap();
		dirPath = self.__dirPath.replace("\\", "/") + "/";
		parseFileList = [];
		for root, _, files in os.walk(self.__dirPath):
			for fileName in files:
				fullPath = os.path.join(root, fileName);
				fileMd5 = self.getMd5ByFilePath(fullPath);
				relativePath = fullPath.replace("\\", "/").replace(dirPath, "");
				md5Data = md5Map.get(relativePath, {});
				if md5Data and md5Data.get("md5", "") == fileMd5:
					newMd5Map[relativePath] = md5Data;
					validSheetNames.extend(md5Data.get("sheets", []));
				else:
					parseFileList.append((fullPath, fileMd5, relativePath));
		# 遍历需要解析的文件
		for i, fileInfo in enumerate(parseFileList):
			# 检测是否中断
			if callable(interrupt) and interrupt():
				# 完成回调
				self.__onComplete__(newMd5Map, callback);
				return;
			# 解析文件
			fullPath, fileMd5, relativePath = fileInfo;
			dataParser = TableDataParser(fullPath, logger);
			if dataParser.isValid:
				logger(f"Try to parse file[{relativePath}]...");
				try:
					sheetNames = [];
					for sheet in dataParser.sheets:
						if not sheet.isValid:
							continue;
						sheetName = sheet.name;
						sheetNames.append(sheetName);
						validSheetNames.append(sheetName);
						data = self.onParse(sheet, logger);
						self.onSaveData(sheetName, data);
						logger(f"Succeeded to parse sheet[{sheetName}].");
					newMd5Map[relativePath] = {"md5": fileMd5, "sheets": sheetNames};
					logger(f"Succeeded to parse file[{relativePath}].", "bold");
				except Exception as e:
					logger(f"Failed to parse file[{relativePath}]! Err->{e}", "error");
			# 通知进度
			if callable(progress):
				progress((i + 1) / len(parseFileList));
		# 解析后回调
		self.afterParse(validSheetNames, logger);
		if callable(progress):
			progress(1);  # 完成解析
		# 完成回调
		self.__onComplete__(newMd5Map, callback);
	
	def __onComplete__(self, newMd5Map, callback):
		# 保存MD5并执行完成回调
		self.setDataCacheMap(newMd5Map);
		if callable(callback):
			callback();
		self.onComplete();
	
	def onStartParse(self):
		pass;
	
	def onComplete(self):
		pass;
	
	def onSaveData(self, sheetName, data):
		pass;

	def onParse(self, sheet, logger):
		pass;

	def afterParse(self, validSheetNames, logger):
		pass;

	def outputLog(self, text, style=""):
		prefix = ""
		if style == "normal":
			pass;
		elif style == "bold":
			prefix = "[Importance] ";
		elif style == "error":
			prefix = "[Error] ";
		elif style == "warning":
			prefix = "[Warning] ";
		# 输出日志
		print(prefix + text);
