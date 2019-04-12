#!/usr/bin/env python

# Read lirc output, in order to sense key presses on an IR remote.
# There are various Python packages that claim to do this but
# they tend to require elaborate setup and I couldn't get any to work.
# This approach requires a lircd.conf but does not require a lircrc.
# If irw works, then in theory, this should too.
# Based on irw.c, https://github.com/aldebaran/lirc/blob/master/tools/irw.c

import socket
import threading
import time

import logging
logger = logging.getLogger('fmu_logger')

SOCKPATH = "/var/run/lirc/lircd"

class Irw:
	def __init__(self, throttle=1):
		self.throttle = throttle
		self._running = False
		self._thread = None
		self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
		logger.debug('lircpoll starting on %s' % SOCKPATH)
		self.sock.connect(SOCKPATH)
		self.last_poll = (None, '00')
		self.last_key = (None, '00')

	def _run(self):
		self._running = True
		while self._running:
			self.poll()

	def run(self):
		if self._thread is not None:
			return

		self._thread = threading.Thread(target=self._run)

		self._thread.start()

	def last(self):
		lkk, lkr = self.last_key
		lpk, lpr = self.last_poll

		#print 'poll: %s %s' % (lpk, lpr)
		#print 'last: %s %s' % (lkk, lkr)

		# TODO: consecutive clicks will not trigger (lpr will be less than or equal to lpkr)
		# if no change since previous call, empty vars
		if lkk == lpk and lkr == lpr:
			self.last_key = (None, '00')
			self.last_poll = (None, '00')

		# if key is same, but repeat is different
		elif lkk == lpk:
			#if new repeat is more than last but under throttle, ignore
			if lpr > lkr and (int(lpr, 16) - int(lkr, 16) <= self.throttle):
				return None
			self.last_key = self.last_poll

		# key is different, we have new trigger
		else:
			self.last_key = self.last_poll
		return self.last_key[0]

	def next_key(self):
		while True:
			data = self.sock.recv(128)
			data = data.strip()
			if data:
				break

		words = data.split()
		return words[2], words[1]

	def poll(self):
		keyname, updown = self.next_key()
		self.last_poll = (keyname, updown)

if __name__ == "__main__":
	import signal

	irw = Irw(8)

	irw.run()

	while 1:
		try:
			last_key = irw.last()
			#if last_key is not None:
			print 'last key is %s ' % last_key
			time.sleep(.3)
		except KeyboardInterrupt:
			exit()
