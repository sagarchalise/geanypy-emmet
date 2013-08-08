try:
    from gi import pygtkcompat
except ImportError:
    pygtkcompat = None

if pygtkcompat is not None:
    pygtkcompat.enable() 
    pygtkcompat.enable_gtk(version='3.0')

import os
from gettext import gettext as _
import gtk as Gtk
import geany
from emmet.context import Context

def makedir(path):
    path=os.path.abspath(path)
    if os.path.isdir(path):
        return True
    else:
        if makedir(os.path.dirname(path)):
            os.makedirs(path)
            return True

BASE_PATH = os.path.abspath(os.path.dirname(__file__))
EXT_PATH = os.path.join(BASE_PATH, 'emmet_ext')
makedir(EXT_PATH)

actions = ("expand_abbreviation", "match_pair_inward", "match_pair_outward","wrap_with_abbreviation", "prev_edit_point", "next_edit_point", "insert_formatted_newline", "select_previous_item", "select_next_item", "matching_pair", "merge_lines", "toggle_comment", "split_join_tag", "remove_tag", "update_image_size", "evaluate_math_expression", "reflect_css_value", "insert_formatted_line_break_only", "encode_decode_data_url", "increment_number_by_1", "increment_number_by_10", "increment_number_by_01", "decrement_number_by_1", "decrement_number_by_10", "decrement_number_by_01")

def create_action_label():
    for action in actions:
        if action == "match_pair_outward":
            action = _("Match Tag Outward")
        elif action == "match_pair_inward":
            action = _("Match Tag Inward")
        elif action == "matching_pair":
            action = _("Go To Matching Pair")
        elif action == "increment_number_by_01":
            action = _("Increment Number by 0.1")
        elif action == "decrement_number_by_01":
            action = _("Decrement Number by 0.1")
        elif action == "prev_edit_point":
            action = _("Previous Edit Point")
        elif action == "split_join_tag":
            action = _("Split or Join Tag")
        elif action == "encode_decode_data_url":
            action = _("Encode/Decode image to data:URL")
        elif action == "reflect_css_value":
            action = _("Reflect CSS value")
        else:
            action = _(action.replace("_", " ").title())
        yield action

actions_dict = dict(zip([label for label in create_action_label()], actions))

class EmmetPlugin(geany.Plugin):

    __plugin_name__ = "Emmet"
    __plugin_version__ = "0.1"
    __plugin_description__ = "Emmet Plugin for geany."
    __plugin_author__ = "Sagar Chalise <chalisesagar@gmail.com>"

    def __init__(self):
        self.menu_item = Gtk.MenuItem(_("Emmet"))
        imenu = Gtk.Menu()
        for label in create_action_label():
            menu_item = Gtk.MenuItem(label)
            menu_item.connect("activate", self.on_action_activate, actions_dict[label])
            menu_item.show()
            imenu.append(menu_item)
            try:
                geany.bindings.register_binding("Emmet", label, self.on_action_activate, actions_dict[label])
            except AttributeError:
                geany.ui_utils.set_statusbar("GeanyPy was not compiled with keybindings support.")
        self.menu_item.set_submenu(imenu)
        self.menu_item.show()
        geany.main_widgets.tools_menu.append(self.menu_item)
        

    def cleanup(self):
        self.menu_item.destroy()

    @staticmethod
    def prompt(title):
        dialog = Gtk.Dialog(title, geany.main_widgets.window, Gtk.DIALOG_DESTROY_WITH_PARENT | Gtk.DIALOG_MODAL, (Gtk.STOCK_CANCEL, Gtk.RESPONSE_REJECT,
             Gtk.STOCK_OK, Gtk.RESPONSE_ACCEPT))
        dialog.set_default_size(300, -1)
        dialog.set_default_response(Gtk.RESPONSE_ACCEPT)
        content_area = dialog.get_content_area()
        entry = Gtk.Entry()
        vbox = Gtk.VBox(False, 0)
        vbox.pack_start(entry, True, True, 0)
        vbox.set_border_width(12)
        content_area.add(vbox)
        vbox.show_all()
        response = dialog.run()
        abbr = ''
        if response == Gtk.RESPONSE_ACCEPT:
            abbr = entry.get_text()
        dialog.destroy()
        return abbr

    @staticmethod
    def run_emmet_action(action):
        file_types = ('HTML', 'PHP', 'XML', 'CSS')
        cur_file_type = geany.document.get_current().file_type.name
        if cur_file_type in file_types:
            contrib = {
                'cur_doc': geany.document.get_current(),
                'cur_doc_type': cur_file_type.lower() if cur_file_type != 'PHP' else 'html',
                'prompt': EmmetPlugin.prompt
            }
            ctx = Context(files=[os.path.join(BASE_PATH, 'editor.js')], ext_path=EXT_PATH, contrib=contrib)
            with ctx.js() as c:
                c.locals.pySetupEditorProxy()
                c.locals.pyRunAction(action)
        
    def on_action_activate(self, key_id, name):
        self.run_emmet_action(name)