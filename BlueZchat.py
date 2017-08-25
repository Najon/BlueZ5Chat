#!/usr/bin/python
from optparse import OptionParser, make_option
import os
import sys
import uuid
import dbus
import dbus.service
import dbus.mainloop.glib

from gi.repository import GObject
BUF_SIZE = 1024
from gi.repository import GLib

class BlueZChat(dbus.service.Object):
	fd = -1

	@dbus.service.method("org.bluez.Profile1",
					in_signature="", out_signature="")
	def Release(self):
		print("Release")
		mainloop.quit()

	@dbus.service.method("org.bluez.Profile1",
					in_signature="", out_signature="")
	def Cancel(self):
		print("Cancel")

	def stdin_cb(self, fd, condition):
		line = fd.readline().strip()
		os.write(self.fd, line)
                sys.stdout.write('you> ')
                sys.stdout.flush()
		return True

        def get_device_name(self, path):
            device = dbus.Interface(bus.get_object("org.bluez", path), "org.bluez.Device1")
            props = dbus.Interface(bus.get_object("org.bluez", path),
                                   "org.freedesktop.DBus.Properties")
            return props.Get("org.bluez.Device1", "Name")

	def bt_cb(self, fd, cond):
		if cond & GLib.IO_IN:
			line = os.read(fd, BUF_SIZE).strip()
			print("\r%s> %s" % (self.participant,line))
                sys.stdout.write('you> ')
                sys.stdout.flush()
		return True

	@dbus.service.method("org.bluez.Profile1",
				in_signature="oha{sv}", out_signature="")
	def NewConnection(self, path, fd, properties):
		self.fd = fd.take()
                self.participant = self.get_device_name(path)
		print("Participant has joined the chat %s" % self.participant)
		try:
			self.io_id = GLib.io_add_watch(self.fd, GLib.IO_IN, self.bt_cb)
                        GLib.io_add_watch(sys.stdin, GLib.IO_IN, self.stdin_cb)
		except Exception as e:
			print ("Exception %s" % e)
                sys.stdout.write('you> ')
                sys.stdout.flush()

	@dbus.service.method("org.bluez.Profile1",
				in_signature="o", out_signature="")
	def RequestDisconnection(self, path):
		print("Participant has leaved the chat(%s)" % (path))

		if (self.fd > 0):
			os.close(self.fd)
			self.fd = -1
def connect_error_cb(e):
        print e
        sys.exit(1)
def connect_cb():
        pass

def connect_chat_server(path):
	device = dbus.Interface(bus.get_object("org.bluez", path), "org.bluez.Device1")
	device.ConnectProfile("e9c9a032-1243-4b0a-a8c1-f20ba8d79b13",
				reply_handler=connect_cb,
				error_handler=connect_error_cb)

def connect_to_server():
        bluez_chat_servers = list()
        bluez_chat_servers_names = list()
        manager = dbus.Interface(bus.get_object("org.bluez", "/"),
					"org.freedesktop.DBus.ObjectManager")

        objects = manager.GetManagedObjects()

        all_devices = (str(path) for path, interfaces in objects.iteritems() if
					"org.bluez.Device1" in interfaces.keys())
        i = 0
        for dev_path in all_devices:
	        dev = objects[dev_path]
	        properties = dev["org.bluez.Device1"]
	        if properties["UUIDs"].count(uuid) != 0:
		        print ("%d: %s" % (i, properties["Name"]))
		        bluez_chat_servers.append(dev_path)
		        bluez_chat_servers_names.append(properties["Name"])
        if len(bluez_chat_servers) == 0:
	        print "Please check that you are paired with a BluezChat server"
        elif len(bluez_chat_servers) == 1:
	        print "Found one server: %s, do you want to connect ?" % bluez_chat_servers_names[0]
	        reply = raw_input('yes/no: ')
	        if reply == "yes":
		        connect_chat_server(bluez_chat_servers[0])
        else:
	        print "Which server do you want to connect to ?"
	        reply = raw_input('number ?')
	        num = 0
	        try:
		        num = Integer(reply)
		        print "connecting to %s" % bluez_chat_servers_names[num]
	        except:
		        print "wrong number"
		        sys.exit(1)
	        connect_chat_server(bluez_chat_servers[num])

if __name__ == '__main__':
	dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        opts = dict()
	bus = dbus.SystemBus()
        path = "/bluez5/chat/example"
        #random uuid
        uuid = "e9c9a032-1243-4b0a-a8c1-f20ba8d79b13"
	manager = dbus.Interface(bus.get_object("org.bluez",
				"/org/bluez"), "org.bluez.ProfileManager1")

	option_list = [
			make_option("-c", "--client",
					action="store_const",
					const="client", dest="role"),
			make_option("-s", "--server",
					action="store_const",
					const="server", dest="role"),
			]
        mainloop = GObject.MainLoop()
        parser = OptionParser(option_list=option_list)
        (options, args) = parser.parse_args()
        chat = BlueZChat(bus, path)
        if (options.role):
		opts["Role"] = options.role
        if options.role == "server":
		print "Bluez5 Chat example Server"
        elif options.role == "client":
		print "Bluez5 Chat example Client"
        else:
            print "One should act as a server the other one as a client"
            print "take a look at the help"
            sys.exit(1)
        # Well don't know so much but the default '6' didn't works,
        # I have to check bluez and bluetooth doc
        opts["Channel"] = dbus.UInt16(10)
        opts["Name"] = "BlueZChat"
        manager.RegisterProfile(path, uuid, opts)
        if options.role == "client":
            GObject.timeout_add(100,connect_to_server)
        mainloop.run()
