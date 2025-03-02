#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class SimpleWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="GTK Test")
        self.set_default_size(300, 200)
        self.set_border_width(10)
        
        # Create a label
        label = Gtk.Label(label="GTK is working correctly!")
        
        # Add the label to the window
        self.add(label)
        
        # Connect the destroy signal to quit the application
        self.connect("destroy", Gtk.main_quit)

# Create and show the window
win = SimpleWindow()
win.show_all()

# Start the GTK main loop
Gtk.main() 