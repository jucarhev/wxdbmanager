# -*- coding: utf-8 -*- 

import json 
from model import *

class Controller( Model):

	Host_Name = ""
	User_Name = ""
	Password = ""
	Database_Name = ""

	
	def __init__( self ):
		pass

	def check_conn(self):
		self.variable_connection()
		r = self.connection()
		if r == None:
			return 1
		else:
			return r

	def get_databases(self):
		# Ok
		result = self.return_data("SHOW SCHEMAS")
		return result

	def get_tables(self, database):
		# Ok
		result = self.return_data("SHOW TABLES", database)
		return result

	def get_columns_from_table(self,table,database):
		# Ok
		result = self.return_data("SHOW COLUMNS FROM "+table+" IN "+database+";")
		return result

	def delete_data(self, table, database):
		pass
	
	def truncate(self, table, database):
		pass

	""" ========> Json files administrator """
	def read_json(self):
		json_data=open('connection.json')
		data = json.load(json_data)
		return data['conn']

	def variable_connection(self):
		json_data=open('connection.json')
		data = json.load(json_data)
		self.Host_Name = data['conn'][0]
		self.User_Name = data['conn'][1]
		self.Password = data['conn'][2]

	def write_json_connection(self):
		data_list = []
		data_list.append(self.Host_Name)
		data_list.append(self.User_Name)
		data_list.append(self.Password)
		data_list.append(self.Database_Name)

		data_json = {}
		json_data = json.dumps(data_list)
		data_json['conn'] = json.loads(json_data)

		json_data = json.dumps(data_json)
		decoded = json.loads(json_data)

		with open('connection.json', 'w') as outfile:
			json.dump(decoded, outfile)