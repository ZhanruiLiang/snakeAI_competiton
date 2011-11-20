import datetime as DT
import sys
import bz2
class Tracker:
	def __init__(self, filename):
		self.filename = filename
		self.logfile = bz2.BZ2File(filename, 'w')
		self.logfile.write('----start at %s----\n'%(DT.datetime.today()))
		self.lines = []
	
	def log(self, message, pos):
		return
		log = '%s at %s\n'%(message, pos)
		self.lines.append(log)
		if len(self.lines) >= 10000:
			self.lines.pop(0)


	def save(self):
		self.logfile.flush()

	def close(self):
		self.logfile.writelines(self.lines)
		self.lines = []
		self.logfile.close()

		
