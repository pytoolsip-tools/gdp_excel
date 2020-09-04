# -*- coding: utf-8 -*-
# @Author: JimZhang
# @Date:   2018-10-08 21:02:23
# @Last Modified by:   JimDreamHeart
# @Last Modified time: 2019-03-16 13:46:37

import wx;
import os;

from _Global import _GG;
from function.base import *;

from ui import DirInputView;

CODE_FORMAT_CHOICES = [
	"C#",
];

class MainViewUI(wx.ScrolledWindow):
	"""docstring for MainViewUI"""
	def __init__(self, parent, id = -1, curPath = "", viewCtr = None, params = {}):
		self.initParams(params);
		super(MainViewUI, self).__init__(parent, id, size = self.__params["size"], style = self.__params["style"]);
		self._className_ = MainViewUI.__name__;
		self._curPath = curPath;
		self.__viewCtr = viewCtr;
		self.bindEvents(); # 绑定事件
		self.SetBackgroundColour(self.__params["bgColour"]);
		# 初始化滚动条参数
		self.SetScrollbars(1, 1, *self.__params["size"]);

	def __del__(self):
		self.__dest__();

	def __dest__(self):
		if not hasattr(self, "_unloaded_"):
			self._unloaded_ = True;
			self.__unload__();

	def __unload__(self):
		self.unbindEvents();

	def initParams(self, params):
		# 初始化参数
		self.__params = {
			"size" : _GG("WindowObject").GetToolWinSize(),
			"style" : wx.BORDER_THEME,
			"bgColour" : wx.Colour(255,255,255),
		};
		for k,v in params.items():
			self.__params[k] = v;

	def getCtr(self):
		return self.__viewCtr;

	def bindEvents(self):
		_GG("WindowObject").BindEventToToolWinSize(self, self.onToolWinSize);

	def unbindEvents(self):
		_GG("WindowObject").UnbindEventToToolWinSize(self);

	def initView(self):
		self.createControls(); # 创建控件
		self.initViewLayout(); # 初始化布局
		self.resetScrollbars(); # 重置滚动条

	def createControls(self):
		# self.getCtr().createCtrByKey("key", self._curPath + "***View"); # , parent = self, params = {}
		self.createTitle();
		self.createParamsView();
		self.createParseBtn();
		self.createOutput();
		pass;
		
	def initViewLayout(self):
		box = wx.BoxSizer(wx.VERTICAL);
		box.Add(self.__title, flag = wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, border = 10);
		box.Add(self.getCtr().getUIByKey("ParamsViewCtr"), flag = wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, border = 10);
		box.Add(self.__parseBtn, flag = wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, border = 10);
		box.Add(self.__output, flag = wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, border = 10);
		self.SetSizerAndFit(box);

	def resetScrollbars(self):
		self.SetScrollbars(1, 1, self.GetSizer().GetSize().x, self.GetSizer().GetSize().y);

	def onToolWinSize(self, sizeInfo, event = None):
		self.SetSize(self.GetSize() + sizeInfo["preDiff"]);
		self.Refresh();
		self.Layout();

	def updateView(self, data):
		pass;

	def createTitle(self):
		self.__title = wx.StaticText(self, label = "游戏数据格式解析器——Excel");
		self.__title.SetFont(wx.Font(20, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD));
	
	def createParamsView(self):
		self.getCtr().createCtrByKey("ParamsViewCtr", self._curPath + "../view/ParamsView", params = {
			"size" : self.GetSize(),
			"choices" : CODE_FORMAT_CHOICES,
		});

	def createParseBtn(self):
		self.__parseBtn = wx.Button(self, label = "开始解析游戏数据", size = (200, 40));
		self.__parseBtn.Bind(wx.EVT_BUTTON, self.getCtr().onClickParseButton)

	def createOutput(self):
		self.__output = wx.TextCtrl(self, size = (self.GetSize().x, 400), value = "- 解析日志显示区 -", style = wx.TE_READONLY|wx.TE_MULTILINE|wx.TE_RICH);
		pass;

	def showMessageDialog(self, message, caption = "提示", style = wx.OK):
		return wx.MessageDialog(self, message, caption = caption, style = style).ShowModal();