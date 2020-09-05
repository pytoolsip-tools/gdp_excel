# -*- coding: utf-8 -*-
# @Author: zhangjin09
# @Date:   2020-09-05 16:14:22
# @Last Modified by:   zhangjin09
# @Last Modified time: 2020-09-05 16:14:22

import wx;

from _Global import _GG;
from function.base import *;

class ContentViewUI(wx.Panel):
	"""docstring for ContentViewUI"""
	def __init__(self, parent, id = -1, curPath = "", viewCtr = None, params = {}):
		self.initParams(params);
		super(ContentViewUI, self).__init__(parent, id, pos = self.__params["pos"], size = self.__params["size"], style = self.__params["style"]);
		self._className_ = ContentViewUI.__name__;
		self._curPath = curPath;
		self.__viewCtr = viewCtr;

	def initParams(self, params):
		# 初始化参数
		self.__params = {
			"pos" : (0,0),
			"size" : (-1,-1),
			"style" : wx.BORDER_THEME,
		};
		for k,v in params.items():
			self.__params[k] = v;

	def getCtr(self):
		return self.__viewCtr;

	def initView(self):
		self.createControls(); # 创建控件
		self.initViewLayout(); # 初始化布局

	def createControls(self):
		# self.getCtr().createCtrByKey("key", self._curPath + "***View"); # , parent = self, params = {}
		self.createTitle();
		self.createParamsView();
		self.createParseBtn();
		self.createGauge();
		self.createOutput();
		pass;
		
	def initViewLayout(self):
		box = wx.BoxSizer(wx.VERTICAL);
		box.Add(self.__title, flag = wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, border = 10);
		box.Add(self.getCtr().getUIByKey("ParamsViewCtr"), flag = wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, border = 10);
		box.Add(self.__parseBtn, flag = wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, border = 10);
		box.Add(self.__gauge, flag = wx.ALIGN_CENTER|wx.BOTTOM, border = 10);
		box.Add(self.__output, flag = wx.ALIGN_CENTER|wx.BOTTOM, border = 10);
		self.SetSizerAndFit(box);

	def updateView(self, data):
		pass;

	def createTitle(self):
		self.__title = wx.StaticText(self, label = "游戏数据格式解析器——Excel");
		self.__title.SetFont(wx.Font(20, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD));
	
	def createParamsView(self):
		self.getCtr().createCtrByKey("ParamsViewCtr", self._curPath + "../ParamsView", params = {
			"size" : self.GetSize(),
			"choices" : list(self.getCtr().CODE_FORMAT_CHOICES.keys()),
		});

	def createParseBtn(self):
		self.__parseBtn = wx.Button(self, label = "开始解析游戏数据", size = (200, 40));
		self.__parseBtn.Bind(wx.EVT_BUTTON, self.onClickParseButton)

	def createGauge(self):
		self.__gauge = wx.Gauge(self, size = (self.GetSize()[0], 10), style = wx.GA_SMOOTH);

	def createOutput(self):
		self.__output = wx.TextCtrl(self, size = (self.GetSize().x, 400), value = "- 解析日志显示区 -", style = wx.TE_READONLY|wx.TE_MULTILINE|wx.TE_RICH);
		pass;
	
	def outputLog(self, text="", style="", isReset=False):
		if isReset:
			self.__output.SetValue("");
		if not text:
			return;
		text = f">> {text}\n";  # 末尾添加换行
		attr = None;
		if style == "normal":
			attr = wx.TextAttr(wx.Colour(100, 100, 100), font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL));
		elif style == "bold":
			attr = wx.TextAttr(wx.Colour(0, 0, 0), font = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD));
		elif style == "error":
			attr = wx.TextAttr(wx.Colour(255, 0, 0), font = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD));
		elif style == "warning":
			attr = wx.TextAttr(wx.Colour(218,165,32), font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD));
		# 添加富文本
		if attr:
			defaultStyle = self.__output.GetDefaultStyle();
			self.__output.SetDefaultStyle(attr);
			self.__output.AppendText(text);
			self.__output.SetDefaultStyle(defaultStyle);
		else:
			self.__output.AppendText(text);

	def showMessageDialog(self, message, caption = "提示", style = wx.OK):
		return wx.MessageDialog(self, message, caption = caption, style = style).ShowModal();
	
	def updateGauge(self, val=0):
		self.__gauge.SetValue(val * self.__gauge.GetRange());
	
	def onClickParseButton(self, event=None):
		if self.getCtr().isParsing:
			self.__parseBtn.SetLabel("停止解析游戏数据");
		else:
			self.__parseBtn.SetLabel("开始解析游戏数据");

		self.getCtr().onClickParseButton(event);
