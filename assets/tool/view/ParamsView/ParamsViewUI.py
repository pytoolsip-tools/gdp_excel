# -*- coding: utf-8 -*-
# @Author: zhangjin09
# @Date:   2020-08-31 11:01:12
# @Last Modified by:   zhangjin09
# @Last Modified time: 2020-08-31 11:01:12

import wx;
import os;

from _Global import _GG;
from function.base import *;

from ui import DirInputView;

class ParamsViewUI(wx.Panel):
	"""docstring for ParamsViewUI"""
	def __init__(self, parent, id = -1, curPath = "", viewCtr = None, params = {}):
		self.initParams(params);
		super(ParamsViewUI, self).__init__(parent, id, pos = self.__params["pos"], size = self.__params["size"], style = self.__params["style"]);
		self._className_ = ParamsViewUI.__name__;
		self._curPath = curPath;
		self.__viewCtr = viewCtr;

	def initParams(self, params):
		# 初始化参数
		self.__params = {
			"pos" : (0,0),
			"size" : (-1,-1),
			"style" : wx.BORDER_THEME,
			"padding" : (0, 0), # 宽高的边距
			"choices" : [],
		};
		for k,v in params.items():
			self.__params[k] = v;

	def getCtr(self):
		return self.__viewCtr;
	
	@property
	def contentSize(self):
		width = self.GetSize().x - self.__params["padding"][0];
		height = self.GetSize().y - self.__params["padding"][1];
		return wx.Size(width, height);

	def initView(self):
		self.createControls(); # 创建控件
		self.initViewLayout(); # 初始化布局

	def createControls(self):
		# self.getCtr().createCtrByKey("key", self._curPath + "***View"); # , parent = self, params = {}
		self.createSrcDirInput();
		self.createTgtDirInput();
		self.createFormatRadioBox();
		
	def initViewLayout(self):
		box = wx.BoxSizer(wx.VERTICAL);
		box.Add(self.__srcDirInput, flag = wx.ALIGN_CENTER);
		box.Add(self.__tgtDirInput, flag = wx.ALIGN_CENTER|wx.TOP, border = 5);
		box.Add(self.__radioBox, flag = wx.ALIGN_CENTER, border = 5);
		self.SetSizerAndFit(box);

	def updateView(self, data):
		pass;

	def createSrcDirInput(self):
		self.__srcDirInput = wx.Panel(self, size = (self.GetSize().x, -1));
		tips = wx.StaticText(self.__srcDirInput, label = "- 请输入文件夹路径 -");
		tips.SetFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL));
		tips.SetForegroundColour("gray");
		def onInput(value, callback = None):
			ret, label = self.checkDirPath(value);
			if ret:
				_GG("CacheManager").setCache("selectedDirPath", value);
				tips.SetLabel("");
				tips.SetForegroundColour("gray");
			else:
				tips.SetLabel("- "+ label +" -");
				tips.SetForegroundColour(wx.Colour(255,36,36));
			# 更新布局
			srcDirInputSizer = self.__srcDirInput.GetSizer();
			if srcDirInputSizer:
				srcDirInputSizer.Layout();
			if callable(callback):
				return callback(value);
			pass;
		div = DirInputView(self.__srcDirInput, params = {
			"inputSize" : (self.contentSize.x - 80, 30),
			"inputValue" : _GG("CacheManager").getCache("selectedDirPath", ""),
			"buttonSize" : (80, 30),
			"buttonLabel" : "选择输入目录",
			"onInput" : onInput,
		});
		onInput(_GG("CacheManager").getCache("selectedDirPath", ""));
		# 布局
		box = wx.BoxSizer(wx.VERTICAL);
		box.Add(div, flag = wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM|wx.EXPAND, border = 5);
		box.Add(tips, flag = wx.ALIGN_CENTER|wx.BOTTOM, border = 5);
		self.__srcDirInput.SetSizerAndFit(box);
		# 缓存div
		self.__srcDirInput._div = div;
	
	def createTgtDirInput(self):
		self.__tgtDirInput = wx.Panel(self, size = (self.GetSize().x, -1));
		tips = wx.StaticText(self.__tgtDirInput, label = "- 输出路径（若为空则默认为上面的输入值） -");
		tips.SetFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL));
		tips.SetForegroundColour("gray");
		# 获取默认的输出路径
		outputPath = _GG("CacheManager").getCache("selectedOutputPath", "");
		if not outputPath:
			outputPath = _GG("CacheManager").getCache("selectedDirPath", "");
		def onInput(value, callback = None):
			ret, _ = self.checkDirPath(value);
			if ret:
				_GG("CacheManager").setCache("selectedOutputPath", value);
			if callable(callback):
				return callback(value);
		div = DirInputView(self.__tgtDirInput, params = {
			"inputSize" : (self.contentSize.x - 80, 30),
			"inputValue" : outputPath,
			"buttonSize" : (80, 30),
			"buttonLabel" : "选择输出目录",
			"onInput" : onInput,
		});
		# 布局
		box = wx.BoxSizer(wx.VERTICAL);
		box.Add(tips, flag = wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, border = 5);
		box.Add(div, flag = wx.ALIGN_CENTER|wx.BOTTOM|wx.EXPAND, border = 5);
		self.__tgtDirInput.SetSizerAndFit(box);
		# 缓存div
		self.__tgtDirInput._div = div;

	def createFormatRadioBox(self):
		self.__radioBox = wx.RadioBox(self, label = "导出格式", choices = self.__params.get("choices", []), style = wx.RA_SPECIFY_COLS);
		pass;

	def checkDirPath(self, dirPath):
		if not dirPath:
			return False, "输入路径不能为空";
		elif not os.path.exists(dirPath):
			return False, "输入路径不存在";
		elif not os.path.isdir(dirPath):
			return False, "输入路径不是文件夹";
		return True, "";

	def getParams(self):
		srcInput = self.__srcDirInput._div.getInputValue();
		ret, _ = self.checkDirPath(srcInput);
		if not ret:
			return None;
		tgtInput = self.__tgtDirInput._div.getInputValue();
		if not tgtInput:
			tgtInput = srcInput;
		return {
			"srcPath" : srcInput,
			"tgtPath" : tgtInput,
			"radio": self.__radioBox.GetStringSelection(),
		};