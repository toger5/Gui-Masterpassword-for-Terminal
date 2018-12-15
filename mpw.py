#!/usr/bin/python
import gi
import sys
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, Gio, GLib
import subprocess
import json
import os
css = b"""
.transparent{
	background-color: rgba (100%,100%,100%, 0.8);
}
entry{
    background-color: rgba (70%, 70%, 70%, 0.5);
	font: 40px "Cantarell Light";
    margin: 20px;
    padding: 10px;
}
.big_font{
    background-color: rgba (0, 0, 0, 0);
    font: 40px "Cantarell Light";
}
treeview{
    background-color: rgba (100%,100%,100%, 0);
    font: 30px "Cantarell Light";
    -treeview-tree-line-pattern: '\x01\x01';
    -treeview-grid-line-width: 10;
    -treeview-odd-row-color: rgba(90%,90%,90%,1);
}

"""
#all this treeview shit does not work although it should! wtf...
style_provider = Gtk.CssProvider()
style_provider.load_from_data(css)

Gtk.StyleContext.add_provider_for_screen(
    Gdk.Screen.get_default(),
    style_provider,
    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
)


full_name = "Florian"


def get_conf_path():
    return os.path.expanduser("~/.mpw.d/"+full_name+".mpsites.json")

def get_conf():
    print("path: ", get_conf_path())
    if os.path.exists(get_conf_path()):
        print("file exists")
        with open(get_conf_path(), "r") as conf_file:
            print("json load")
            return json.load(conf_file)

class LoginWindow(Gtk.ApplicationWindow):

    def __init__(self, app):
        Gtk.Window.__init__(self, title="Master Password", application=app)
        self.app = app
        self.box = Gtk.VBox()
        self.add(self.box)

        self.name_box = Gtk.HBox(spacing= 20)
        self.box.pack_start(self.name_box, True, False, 0)

        n_label = Gtk.Label(label="Name: ")
        n_label.set_halign(Gtk.Align.END)
        self.name_box.pack_start(n_label, True, True, 0)

        self.name_label = Gtk.Label(label=full_name)
        self.name_label.get_style_context().add_class("big_font")
        self.name_label.set_halign(Gtk.Align.START)
        self.name_box.pack_start(self.name_label, True, True, 0)

        self.input_entry = Gtk.Entry()
        self.input_entry.set_size_request(600,0)
        self.input_entry.set_visibility(False)
        self.input_entry.connect("activate", self.on_entry_activate)
        self.box.pack_start(self.input_entry, True, True, 0)
    def on_entry_activate(self, widget):
        self.app.pwd_cache = self.input_entry.get_text()
        self.close()
        self.app.activate()


class PwdWindow(Gtk.ApplicationWindow):

    def __init__(self, app):
        self.app = app
        self.store = Gtk.ListStore(str, int, str) #name, times used, date of last use
        print("window init")
        Gtk.Window.__init__(self, title="Master Password", application=app)
        self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
#        self.hbox = Gtk.HBox()
#        self.add(self.hbox)
        self.get_style_context().add_class("transparent")
        self.vbox = Gtk.VBox()
        self.add(self.vbox)
#        self.hbox.pack_start(self.vbox, True, False,0)

        #self.button = Gtk.Button(label="test button")
        #self.button.connect("clicked", self.on_button_clicked)
        #self.box.pack_start(self.button,True,True, 0)

        self.input_entry = Gtk.Entry()
 #       self.in
        self.input_entry.connect("activate", self.on_entry_activate)
        self.input_entry.connect("changed", self.sort_pages)
        self.input_entry.get_style_context().add_class("big_font")
        self.input_entry.set_size_request(800,0)
        self.input_entry.props.valign = Gtk.Align.CENTER
        self.input_entry.props.halign = Gtk.Align.CENTER
        self.vbox.pack_start(self.input_entry, True, False, 0)
        #self.scroll = Gtk.ScrolledView()
        self.site_list = Gtk.TreeView(self.store)
        
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Title", renderer, text=0)
        self.site_list.append_column(column)
        self.site_list.set_size_request(800,300)
        self.site_list.props.halign = Gtk.Align.CENTER
        renderer.props.xalign = 0.5
        self.site_list.props.headers_visible = False
        self.site_list.set_grid_lines(Gtk.TreeViewGridLines(1))
#        self.site_list.get_style_context().add_class("transparent")
#        self.site_list.props.homogeneous = False
#        self.site_list.set_max_children_per_line(1)
        self.vbox.pack_start(self.site_list, True, True,0)
        self.site_list.connect("row_activated", self.on_row_activated)
        
    def load_sites(self):
        config_data = get_conf()
        print("data: ", config_data)
        if config_data:
            for site in config_data["sites"]:
                print("added label ", site)
                self.store.append([site, config_data["sites"][site]["uses"], config_data["sites"][site]["last_used"]])
#                lbl = Gtk.Label(label=site)
#                lbl.get_style_context().add_class("big_font")
#                self.site_list.add(lbl)
        self.sort_pages()
        self.show_all()
        #self.scroll.add(self.site_list) 
        
    def get_pwd(self, page):
        return subprocess.check_output(["mpw","-u", full_name, "-t", "x", "-M", self.app.pwd_cache, "-q", page]).decode()
    
    def sort_pages(self, widget = None, event = None):
        if self.input_entry.get_text_length() == 0 and event == None:
            self.store.set_sort_column_id(2, Gtk.SortType.DESCENDING)
        else:
            self.store.set_sort_func(0, self.string_sort_func)
            self.store.set_sort_column_id(0,Gtk.SortType.ASCENDING)
    def string_sort_func(self, model, a, b, user_data):
        for i in range(self.input_entry.get_text_length()):
            if len(model[a][0]) - 1 >= i and len(model[b][0]) - 1 >= i and model[b][0][i] == model[a][0][i] == self.input_entry.get_text()[i]:
                pass
            elif len(model[a][0]) - 1 >= i and model[a][0][i] == self.input_entry.get_text()[i]: 
                return -1
            elif len(model[b][0]) - 1 >= i and model[b][0][i] == self.input_entry.get_text()[i]:                
                return 1
        return 0

    def on_entry_activate(self, widget):
#        print("activated")
        page = self.input_entry.get_text()
#        print("generatiKey_escng password for: " + full_name + " site: " + page)
        self.clipboard.set_text(self.get_pwd(page), -1)
        self.hide() 
    def on_row_activated(self, tree_view, path, column):
        page = self.store[self.store.get_iter(path)][0]
        self.clipboard.set_text(self.get_pwd(page), -1)
        self.hide() 
    def do_key_release_event(self, event):
        if event.keyval == Gdk.KEY_Escape:
            self.hide()



class Application(Gtk.Application):
    def __init__(self, *args, **kwargs):
        self.pwd_cache = None
        print('app started')
        super().__init__(*args, application_id="org.gtk.mpw",
                         flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE,
                         **kwargs)
        self.window = None
        self.initial_window = None
        self.add_main_option("show", ord("s"), GLib.OptionFlags.NONE,
                             GLib.OptionArg.NONE, "Command line test", None)

    def do_activate(self):
        print("activated")
        # We only allow a single window and raise any existing ones
        if self.pwd_cache == None:
            initial_window = LoginWindow(self)
            initial_window.show_all()
            return
        if not self.window:
            print("wnd created")
            self.window = PwdWindow(self)
            self.window.set_decorated(False)
            # Windows are associated with the application
            # when the last one is closed the application shuts down
            self.window.load_sites()
            self.window.show_all()
        self.window.present()
        print("load sites") 
        self.window.maximize()

    def do_command_line(self, command_line):
        options = command_line.get_options_dict()
        # convert GVariantDict -> GVariant -> dict
        options = options.end().unpack()
        print("command line: ", options)

        if "show" in options:
            # This is printed on the main instance
            print("Test argument recieved: %s" % options["show"])

        self.activate()
        return 0

    def on_about(self, action, param):
        about_dialog = Gtk.AboutDialog(transient_for=self.window, modal=True)
        about_dialog.present()

    def on_quit(self, action, param):
        print("self")
        quit.quit()


if __name__ == "__main__":
    print("r")
    app = Application()
    app.run(sys.argv)


