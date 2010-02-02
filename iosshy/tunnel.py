# -*- coding: utf-8 -*-

import paramiko, select, SocketServer
from threading import Thread
from subprocess import Popen
from PyQt4.QtCore import QObject, pyqtSignal

class ForwardServer(SocketServer.ThreadingTCPServer):
	daemon_threads = True
	allow_reuse_address = True

class Handler(SocketServer.BaseRequestHandler):
	def handle(self):
		try:
			chan = self.ssh_transport.open_channel('direct-tcpip', (self.chain_host, self.chain_port), self.request.getpeername())
		except Exception, e:
			return

		if chan is None:
			return

		#verbose('Connected! Tunnel open %r -> %r -> %r' % (self.request.getpeername(), chan.getpeername(), (self.chain_host, self.chain_port)))
		while True:
			r, w, x = select.select([self.request, chan], [], [])
			if self.request in r:
				data = self.request.recv(1024)
				if len(data) == 0:
					break
				chan.send(data)
			if chan in r:
				data = chan.recv(1024)
				if len(data) == 0:
					break
				self.request.send(data)
		chan.close()
		self.request.close()

class TunnelThread(Thread):
	def __init__(self, ssh_server, local_port, ssh_port=22, remote_host="localhost", remote_port=None, username=None, password=None):
		Thread.__init__(self)
		if remote_port is None:
			remote_port = local_port
		self.local_port = local_port
		self.remote_host = remote_host
		self.remote_port = remote_port

		self.ssh_client = paramiko.SSHClient()
		self.ssh_client.load_system_host_keys()
		self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		self.ssh_client.connect(ssh_server, ssh_port, username=username, password=password, look_for_keys=True)

		transport = self.ssh_client.get_transport()

		class SubHandler(Handler):
			chain_host = remote_host
			chain_port = remote_port
			ssh_transport = transport
		self.ffwd_server = ForwardServer(('', self.local_port), SubHandler)

	def run(self):
		self.ffwd_server.serve_forever()

	def join(self):
		if self.ffwd_server is not None:
			self.ffwd_server.shutdown()
		self.ssh_client.close()
		del self.ffwd_server
		del self.ssh_client
		Thread.join(self)

class CommandThread(Thread, QObject):
	terminated = pyqtSignal()

	def __init__(self, command):
		Thread.__init__(self)
		QObject.__init__(self)
		self.pipe = Popen(command, shell=True)

	def run(self):
		self.pipe.communicate()
		self.terminated.emit()

from PyQt4.QtGui import QAction, QListWidgetItem, QSystemTrayIcon
from PyQt4.QtCore import Qt

class Tunnel(object):
	def __init__(self, parent):
		self._thread = None
		self._commandThread = None
		self._parent = parent
		self._name = "New Tunnel"
		self.host = "localhost"
		self._localPort = None
		self._port = 80
		self.username = "root"
		self.password = None
		self.command = None
		self.autoClose = False
		self._action = QAction(self._name, self._parent.tray.menu)
		self._action.setCheckable(True)
		self._action.toggled.connect(self.toggle)
		self._item = QListWidgetItem(self._name, self._parent.listTunnels)

	def _validatePort(self, port):
		try:
			if type(port) is str:
				port = port.strip()
			port = int(port)
		except:
			return None
		else:
			return port if 0 < port < 65536 else None

	def getAction(self):
		return self._action

	def getItem(self):
		return self._item

	def getName(self):
		return self._name

	def setName(self, name):
		self._name = name
		self._action.setText(name)
		self._item.setText(name)

	def getPort(self):
		return self._port

	def setPort(self, port):
		port = self._validatePort(port)
		if port is not None:
			self._port = port

	def getLocalPort(self):
		return self._localPort

	def setLocalPort(self, port):
		self._localPort = self._validatePort(port)

	name = property(getName, setName)
	port = property(getPort, setPort)
	localPort = property(getLocalPort, setLocalPort)
	action = property(getAction)
	item = property(getItem)

	def readSettings(self, settings):
		settings.beginGroup(self.name)
		self.host = settings.value("host", "localhost")
		self.localPort = settings.value("localPort", None)
		self.port = settings.value("port", None)
		self.username = settings.value("username", "root")
		self.password = settings.value("password", None)
		self.command = settings.value("command", None)
		self.autoClose = settings.value("autoClose", False)
		settings.endGroup()

	def writeSettings(self, settings):
		settings.beginGroup(self.name)
		settings.setValue("host", self.host)
		if self.localPort is not None:
			settings.setValue("localPort", self.localPort)
		settings.setValue("port", self.port)
		settings.setValue("username", self.username)
		if self.password is not None:
			settings.setValue("password", self.password)
		if self.command is not None:
			settings.setValue("command", self.command)
		settings.setValue("autoClose", self.autoClose)
		settings.endGroup()

	def toggle(self, openTunnel):
		if openTunnel:
			openTunnel = self._thread is None
		if openTunnel:
			self.open_()
		else:
			self.close()

	def open_(self):
		try:
			self._thread = TunnelThread(username=self.username, password=self.password, ssh_server=self.host, local_port=self.localPort, remote_port=self.port)
		except paramiko.BadHostKeyException as message:
			self.close()
			self._parent.tray.showMessage(self.name, str(message), QSystemTrayIcon.Warning)
		except Exception as e:
			print e
			self.close()
		else:
			self._parent.tray.showMessage(self.name, "Tunnel active")

		if self._thread is not None:
			self._thread.start()
			if self.command is not None:
				command = self.command
				try:
					command = command.format(port=self.localPort)
				except: pass
				try:
					self._commandThread = CommandThread(command)
					if self.autoClose:
						self._commandThread.terminated.connect(self.close)
					self._commandThread.start()
				except:
					self._commandThread = None
					if self.autoClose:
						self.close()

	def close(self):
		if self._thread is not None:
			self._parent.tray.showMessage(self.name, "Closing tunnel")
			if self._commandThread is not None:
				self._commandThread.join()
				self._commandThread = None
			self._thread.join()
			self._thread = None
		self._action.setChecked(False)