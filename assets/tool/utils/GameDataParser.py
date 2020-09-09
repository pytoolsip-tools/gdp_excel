import os;
import re;
import shutil;
import xlrd;
import json;
import hashlib;
import threading;

class SheetDataParser(object):
	DEFAULT_DATA_TYPE = "STRING";
	DATA_TYPE_DICT = {
		"STRING" : {"func": lambda s: str(s), "default": ""},
		"INT" : {"func": lambda s: int(s), "default": 0},
		"BOOL" : {"func": lambda s: bool(s), "default": False},
		"FLOAT" : {"func": lambda s: float(s), "default": 0},
	};

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
				typeFunc = self.DATA_TYPE_DICT[self.getTypeByKey(key)]["func"];
				if not row[idx]:
					val.append(self.getDefaultByKey(key));
				else:
					val.append(typeFunc(row[idx]));
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
	
	def getTypeByKey(self, key):
		return self.__typeDict.get(key, self.DEFAULT_DATA_TYPE);
	
	def getDefaultByKey(self, key):
		typeParams = self.DATA_TYPE_DICT[self.getTypeByKey(key)];
		defaultVal = typeParams["default"];
		if key in self.__defaultDict:
			try:
				defaultVal = typeParams["func"](self.__defaultDict[key]);
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
					ret = re.search("([a-zA-Z]+)\((.*)\)", typeStrip);
					if not ret:
						typeStr = typeStrip.upper();
						if typeStr in self.DATA_TYPE_DICT:
							self.__typeDict[key] = typeStr;
					else:
						typeStr = ret.group(1).upper();
						if typeStr in self.DATA_TYPE_DICT:
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
		if not os.path.exists(filePath):
			return "";
		with open(filePath, "rb") as f:
			return hashlib.md5(f.read()).hexdigest();
		return "";

	def parse(self, logger=None, progress=None, interrupt=None, callback=None):
		if not callable(logger):
			logger = self.outputLog;
		threading.Thread(target = self.parseByThread, args = (logger, progress, interrupt, callback)).start();
	
	def parseByThread(self, logger=None, progress=None, interrupt=None, callback=None):
		self.copyTemplate();
		if not os.path.exists(self.__dirPath):
			logger(f"Input path[{self.__dirPath}] is not non-existent!", "error");
			return;
		newMd5Map = {};
		md5Map = self.getDataCacheMap();
		dirPath = self.__dirPath.replace("\\", "/") + "/";
		parseFileList = [];
		for root, _, files in os.walk(self.__dirPath):
			for fileName in files:
				fullPath = os.path.join(root, fileName);
				fileMd5 = self.getMd5ByFilePath(fullPath);
				relativePath = fullPath.replace("\\", "/").replace(dirPath, "");
				if relativePath in md5Map and md5Map[relativePath].get("md5", "") == fileMd5:
					newMd5Map[relativePath] = md5Map[relativePath];
					data = md5Map[relativePath].get("data", "");
					if data:
						self.onSaveData(data);
				else:
					parseFileList.append((fullPath, fileMd5, relativePath));
		# 遍历需要解析的文件
		for i, fileInfo in enumerate(parseFileList):
			# 检测是否中断
			if callable(interrupt) and interrupt():
				# 保存MD5并执行完成回调
				self.setDataCacheMap(newMd5Map);
				if callable(callback):
					callback();
				return;
			# 解析文件
			fullPath, fileMd5, relativePath = fileInfo;
			dataParser = TableDataParser(fullPath, logger);
			if dataParser.isValid:
				logger(f"Try to parse file[{relativePath}]...");
				content = "";
				try:
					for sheet in dataParser.sheets:
						if not sheet.isValid:
							continue;
						data = self.onParse(sheet, logger);
						self.onSaveData(data);
						content += data;
						logger(f"Succeeded to parse sheet[{sheet.name}].");
					logger(f"Succeeded to parse file[{relativePath}].", "bold");
				except Exception as e:
					logger(f"Failed to parse file[{relativePath}]! Err->{e}", "error");
				newMd5Map[relativePath] = {"md5": fileMd5, "data": content};
			# 通知进度
			if callable(progress):
				progress((i + 1) / len(parseFileList));
		if callable(progress):
			progress(1);  # 完成解析
		# 保存MD5并执行完成回调
		self.setDataCacheMap(newMd5Map);
		if callable(callback):
			callback();
	
	def onSaveData(self, data):
		pass;

	def onParse(self, dataParser, logger):
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
