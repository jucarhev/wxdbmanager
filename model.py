import mysql.connector

class Model( ):

	def __init__( self ):
		pass

	def connection(self):
		try:
			self.connection = mysql.connector.connect(host=self.Host_Name,user=self.User_Name,password=self.Password,database=self.Database_Name)
			self.cursor = self.connection.cursor()
		except mysql.connector.Error as e:
			return e

	def close(self):
		self.connection.close()
		self.cursor.close()

	def execute_sql(self, sql, database):
		try:
			self.connection = mysql.connector.connect(host=self.Host_Name,user=self.User_Name,password=self.Password,database=database)
			self.cursor = self.connection.cursor()

			self.cursor.execute(sql)
			r = self.connection.commit()
			self.close()
			return r
		except mysql.connector.Error as e:
			return e

	def return_data(self,sql,database=''):
		try:
			self.connection = mysql.connector.connect(host=self.Host_Name,user=self.User_Name,password=self.Password, database=database)
			self.cursor = self.connection.cursor()
			self.cursor.execute(sql)
			data = self.cursor.fetchall()
			
			self.close()
			return data
		except mysql.connector.Error as e:
			return e