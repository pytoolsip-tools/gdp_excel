# -*- coding: utf-8 -*-
# @Author: zhangjin09
# @Date:   2020-09-05 16:14:22
# @Last Modified by:   zhangjin09
# @Last Modified time: 2020-09-05 16:14:22
import os;
import wx;

from _Global import _GG;

from ContentViewUI import *;

CURRENT_PATH = os.path.dirname(os.path.realpath(__file__)); # 当前文件目录

CsharpGameDataParser = require(GetPathByRelativePath("../../", CURRENT_PATH), "utils", "CsharpGameDataParser");

def getRegisterEventMap(G_EVENT):
	return {
		# G_EVENT.TO_UPDATE_VIEW : "updateView",
	};

class ContentViewCtr(object):
	"""docstring for ContentViewCtr"""

	CODE_FORMAT_CHOICES = {
		"C#": "createCsharpGameDataParser",
	}

	def __init__(self, parent, params = {}):
		super(ContentViewCtr, self).__init__();
		self._className_ = ContentViewCtr.__name__;
		self._curPath = os.path.dirname(os.path.realpath(__file__)).replace("\\", "/") + "/";
		self.__CtrMap = {}; # 所创建的控制器
		self.initUI(parent, params); # 初始化视图UI
		self.registerEventMap(); # 注册事件
		self.bindBehaviors(); # 绑定组件
		# 解析数据的标记
		self.__isParsing = False;
		self.__isTryStopParsing = False;

	def __del__(self):
		self.__dest__();

	def __dest__(self):
		if not hasattr(self, "_unloaded_"):
			self._unloaded_ = True;
			self.__unload__();

	def __unload__(self):
		self.unregisterEventMap(); # 注销事件
		self.unbindBehaviors(); # 解绑组件
		self.delCtrMap(); # 銷毀控制器列表

	def delCtrMap(self):
		for key in self.__CtrMap:
			DelCtr(self.__CtrMap[key]);
		self.__CtrMap.clear();

	def initUI(self, parent, params):
		# 创建视图UI类
		self.__ui = ContentViewUI(parent, curPath = self._curPath, viewCtr = self, params = params);
		self.__ui.initView();

	def getUI(self):
		return self.__ui;

	"""
		key : 索引所创建控制类的key值
		path : 所创建控制类的路径
		parent : 所创建控制类的UI的父节点，默认为本UI
		params : 扩展参数
	"""
	def createCtrByKey(self, key, path, parent = None, params = {}):
		if not parent:
			parent = self.getUI();
		self.__CtrMap[key] = CreateCtr(path, parent, params = params);

	def getCtrByKey(self, key):
		return self.__CtrMap.get(key, None);

	def getUIByKey(self, key):
		ctr = self.getCtrByKey(key);
		if ctr:
			return ctr.getUI();
		return None;
		
	def registerEventMap(self):
		eventMap = getRegisterEventMap(_GG("EVENT_ID"));
		for eventId, callbackName in eventMap.items():
			_GG("EventDispatcher").register(eventId, self, callbackName);

	def unregisterEventMap(self):
		eventMap = getRegisterEventMap(_GG("EVENT_ID"));
		for eventId, callbackName in eventMap.items():
			_GG("EventDispatcher").unregister(eventId, self, callbackName);

	def bindBehaviors(self):
		pass;
		
	def unbindBehaviors(self):
		pass;
			
	def updateView(self, data):
		self.__ui.updateView(data);

	@property
	def isParsing(self):
		return self.__isParsing;
	
	def onClickParseButton(self, event):
		if self.__isTryStopParsing:
			return;
		if self.__isParsing:
			self.tryStopParsing();
		else:
			self.doParseData();
	
	def doParseData(self):
		# 重置界面相关UI
		self.getUI().outputLog(isReset = True);
		self.setProgress();
		# 获取解析参数
		params = self.getUIByKey("ParamsViewCtr").getParams();
		if not params:
			self.getUI().showMessageDialog("输入数据有误！");
			return;
		funcName = self.CODE_FORMAT_CHOICES[params["radio"]];
		if not hasattr(self, funcName):
			self.getUI().showMessageDialog("输入格式不存在！");
			return;
		# 开始解析数据
		self.outputLog("====== 开始数据解析 ======");
		self.__isParsing = True;
		# 处理解析逻辑
		gameDataParser = getattr(self, funcName)(params);
		gameDataParser.parse(logger=self.outputLog, progress=self.setProgress, interrupt=self.checkIsStopParsing, callback=self.stopParsing);
	
	def tryStopParsing(self):
		self.__isTryStopParsing = True;

	def stopParsing(self):
		self.__isTryStopParsing = False;
		self.__isParsing = False;
		self.outputLog("====== 结束数据解析 ======");
	
	def checkIsStopParsing(self):
		return self.__isTryStopParsing or not self.__isParsing;

	def createCsharpGameDataParser(self, params):
		templatePath = GetPathByRelativePath("../../template/csharp", CURRENT_PATH);
		collectionsPath = os.path.join(params["tgtPath"], "TDCollections.cs");
		return CsharpGameDataParser(params["srcPath"], params["tgtPath"], templatePath, collectionsPath);

	def outputLog(self, text, style=""):
		wx.CallAfter(self.getUI().outputLog, text, style);
		
	def setProgress(self, val=0):
		wx.CallAfter(self.getUI().updateGauge, val);