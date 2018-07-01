import os 
import psutil

class sysmon:

	def __init__(self):
		self.classname="sysmon"

	# Return CPU temperature as a character string
	def _get_temperature(self):
    		res = os.popen('vcgencmd measure_temp').readline()
    		return(res.replace("temp=","").replace("'C\n",""))


	def get_cpu_info(self):
		""" CPU information. Returns temperature and load """
		retval={'token':'S', 'class':self.classname}
        	retval['temp'] = self._get_temperature()
        	retval['load'] = psutil.cpu_percent()
		return(retval)

	def get_ram_info(self):
        	""" RAM information, Returns memory information in kb """
		retval={'token':'R', 'class':self.classname}
        	ram = psutil.virtual_memory()
        	retval['total'] = ram.total
        	retval['used'] = ram.used
        	retval['free'] = ram.free
		return(retval)

        def get_disk_info(self):
                """ Disk information, Returns disk information in kb """
                retval={'token':'D', 'class':self.classname}
                disk = psutil.disk_usage('/')
                retval['total'] = disk.total
                retval['used'] = disk.used
                retval['free'] = disk.free
                return(retval)

if __name__ == "__main__":

	si=sysmon()

	

	print (si.get_cpu_info())

	print (si.get_ram_info())
	print (si.get_disk_info())

