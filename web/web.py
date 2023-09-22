from src.server.server import Server

import logging
logger = logging.getLogger('fmu_logger')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s_%(name)s_%(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

class Web(object):
	def __init__(self):
		logger.debug('Web::__init__')
		try:
			# f = open(os.devnull, 'w')
			# sys.stdout = sys.stderr = f
			self.server = Server()
		except Exception as e:
			logger.debug(e)

def main():
	web = Web()

if __name__ == "__main__":
	main()
	while True:
		pass