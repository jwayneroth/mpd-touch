import logging
logger = logging.getLogger('fmu_logger')

MAIN_NAV = {
	'Home': ['/', 'cd'],
	'Library': ['/library', 'list'],
	'Radio': ['/radio', 'music'],
	'Settings': ['/settings', 'cog'],
	#'Controls': ['/controls', 'volume-down'],
}