# -*- coding: utf-8 -*- 

import wx
import wx.xrc
import wx.aui
import sys, os

from controller import Controller


class main ( wx.Frame ):
	""" Principal class """

	controller = Controller()

	is_connect = False
	
	def __init__( self, parent ):

		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 500,300 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

		path = os.path.abspath("./img/logo_db.png")
		icon = wx.Icon(path, wx.BITMAP_TYPE_PNG)
		self.SetIcon(icon)

		self.check_connection()
		
		self.m_menubar1 = wx.MenuBar( 0 )
		self.m_menu1 = wx.Menu()
		self.m_menubar1.Append( self.m_menu1, u"File" ) 
		
		self.SetMenuBar( self.m_menubar1 )
		
		self.m_toolBar1 = self.CreateToolBar( wx.TB_HORIZONTAL, wx.ID_ANY ) 
		self.Connection_tool = self.m_toolBar1.AddLabelTool( wx.ID_ANY, u"tool", wx.Bitmap( u"img/db.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, wx.EmptyString, wx.EmptyString, None ) 
		
		self.m_toolBar1.Realize() 
		
		bSizer1 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.tree = wx.TreeCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TR_DEFAULT_STYLE )
		bSizer1.Add( self.tree, 1, wx.ALL|wx.EXPAND, 5 )

		self.notebook = wx.aui.AuiNotebook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.aui.AUI_NB_DEFAULT_STYLE )
		self.m_panel1 = wx.Panel( self.notebook, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		
		bSizer1.Add( self.notebook, 5, wx.EXPAND |wx.ALL, 5  )
		
		self.SetSizer( bSizer1 )
		self.Layout()
		
		self.Centre( wx.BOTH )
		self.SetSize((800,600))
		self.SetTitle("WxDBManager")
		self.Show()

		self.Bind(wx.EVT_TOOL,self.conection_manager,self.Connection_tool)

	def check_connection(self):
		print("# Verificanco conexion")
		m = self.controller.check_conn()
		if m == 1:
			#wx.MessageBox("ok", 'Info',wx.OK | wx.ICON_INFORMATION)
			print("Ok")
			self.is_connect = True
		else:
			wx.MessageBox(str(m), 'Info',wx.OK | wx.ICON_INFORMATION)

	def conection_manager(self, evt):
		NewBD = Dialog_Connection(self)
		NewBD.ShowModal()
		NewBD.Destroy()



class Dialog_Connection ( wx.Dialog ):

	controller = Controller()
	is_save = False

	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Administrator", pos = wx.DefaultPosition, size = wx.Size( 300,220 ), style = wx.DEFAULT_DIALOG_STYLE )

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

		bSizer1 = wx.BoxSizer( wx.VERTICAL )

		self.m_staticText1 = wx.StaticText( self, wx.ID_ANY, u"Conecction", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText1.Wrap( -1 )

		self.m_staticText1.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, wx.EmptyString ) )

		bSizer1.Add( self.m_staticText1, 0, wx.ALIGN_CENTER|wx.ALL, 5 )

		gSizer1 = wx.GridSizer( 0, 2, 0, 0 )

		self.m_staticText2 = wx.StaticText( self, wx.ID_ANY, u"HostName:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText2.Wrap( -1 )

		gSizer1.Add( self.m_staticText2, 0, wx.ALL, 5 )

		self.txtHostname = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		gSizer1.Add( self.txtHostname, 0, wx.ALL, 5 )

		self.m_staticText3 = wx.StaticText( self, wx.ID_ANY, u"UserName:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText3.Wrap( -1 )

		gSizer1.Add( self.m_staticText3, 0, wx.ALL, 5 )

		self.txtUsername = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		gSizer1.Add( self.txtUsername, 0, wx.ALL, 5 )

		self.m_staticText4 = wx.StaticText( self, wx.ID_ANY, u"Password:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText4.Wrap( -1 )

		gSizer1.Add( self.m_staticText4, 0, wx.ALL, 5 )

		self.txtPassword = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		gSizer1.Add( self.txtPassword, 0, wx.ALL, 5 )

		bSizer1.Add( gSizer1, 1, wx.EXPAND, 5 )

		bSizer2 = wx.BoxSizer( wx.HORIZONTAL )

		self.btnSave = wx.Button( self, wx.ID_ANY, u"Save", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer2.Add( self.btnSave, 0, wx.ALL, 5 )

		self.btnTest = wx.Button( self, wx.ID_ANY, u"Test", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer2.Add( self.btnTest, 0, wx.ALL, 5 )


		bSizer1.Add( bSizer2, 1, wx.ALL|wx.EXPAND, 5 )


		self.SetSizer( bSizer1 )
		self.Layout()

		self.Centre( wx.BOTH )

		self.Bind(wx.EVT_BUTTON, self.Save, self.btnSave)
		self.Bind(wx.EVT_BUTTON, self.Test, self.btnTest)

	def Save(self, evt):
		self.controller.Host_Name = self.txtHostname.GetValue()
		self.controller.User_Name = self.txtUsername.GetValue()
		self.controller.Password = self.txtPassword.GetValue()

		self.controller.write_json_connection()
		self.is_save = True

	def Test(self, evt):
		if self.is_save == False:
			wx.MessageBox("Save data" , 'Info',wx.OK | wx.ICON_INFORMATION)
		else:
			r = self.controller.check_conn()
			if r == 1:
				wx.MessageBox("Success" , 'Info',wx.OK | wx.ICON_INFORMATION)
			else:
				wx.MessageBox(str(r) , 'Info',wx.OK | wx.ICON_INFORMATION)




app = wx.App()
main(None)
app.MainLoop()
