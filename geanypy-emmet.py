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
import gobject as GObject
import geany
from emmet.context import Context

def makedir(path):
    path = os.path.abspath(path)
    try:
        os.makedirs(path)
    except OSError as e:
        return False

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
    indicators = (geany.editor.INDICATOR_SEARCH, 1)
    file_types = ('HTML', 'PHP', 'XML', 'CSS')
    _highlight_tag = False

    def __init__(self):
        self.load_config()
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
                geany.ui_utils.set_statusbar("GeanyPy was not compiled with bindings support.Use: https://github.com/sagarchalise/geanypy")
        self.menu_item.set_submenu(imenu)
        self.menu_item.show()
        geany.signals.connect("editor-notify", self.on_editor_notify)
        geany.main_widgets.tools_menu.append(self.menu_item)

    def cleanup(self):
        self.menu_item.destroy()

    def load_config(self):
        self.cfg_path = os.path.join(geany.app.configdir, "plugins", "pyemmet.conf")
        self.cfg = SafeConfigParser()
        self.cfg.read(self.cfg_path)


    def save_config(self):
        GObject.idle_add(self.on_save_config_timeout)


    def on_save_config_timeout(self, data=None):
        self.cfg.write(open(self.cfg_path, 'w'))
        return False

    @property
    def highlight_tag(self):
        if self.cfg.has_section('general'):
            if self.cfg.has_option('general', 'highlight_tag'):
                return self.cfg.getboolean('general', 'highlight_tag')
        return self._highlight_tag

    @highlight_tag.setter
    def highlight_tag(self, value):
        self._highlight_tag = value
        if not self.cfg.has_section('general'):
            self.cfg.add_section('general')
        self.cfg.set('general', 'highlight_tag',
            str(self._use_rl_completer).lower())
        self.save_config()

    @staticmethod
    def prompt(title):
        abbr = geany.dialogs.show_input(_(title), title, geany.main_widgets.window)
        return abbr

    @staticmethod
    def check_filetype_and_get_contrib(file_types=None):
        if not file_types:
            file_types = EmmetPlugin.file_types
        cur_doc = geany.document.get_current()
        cur_file_type = cur_doc.file_type.name if cur_doc else None
        if cur_file_type in file_types:
            return {
                'cur_doc': cur_doc,
                'cur_doc_type': cur_file_type.lower() if cur_file_type != 'PHP' else 'html',
                'prompt': EmmetPlugin.prompt,
                'geanyIndicatorSearch': geany.editor.INDICATOR_SEARCH,
            }

    @staticmethod
    def run_emmet_action(action, contrib):
        ctx = Context(files=[os.path.join(BASE_PATH, 'editor.js')], ext_path=EXT_PATH, contrib=contrib)
        with ctx.js() as c:
            c.locals.pySetupEditorProxy()
            c.locals.pyRunAction(action)

    def on_action_activate(self, key_id, name):
        contrib = EmmetPlugin.check_filetype_and_get_contrib()
        if contrib:
            self.run_emmet_action(name, contrib)

    def on_editor_notify(self, g_obj, editor, nt):
        if self.highlight_tag:
            contrib = self.check_filetype_and_get_contrib(("PHP", "HTML", "XML"))
            if contrib:
                notification_codes = (geany.scintilla.UPDATE_UI, geany.scintilla.KEY)
                if nt.nmhdr.code in notification_codes:
                    for indicator in self.indicators:
                        editor.indicator_clear(indicator)
                    self.run_emmet_action("highlight_tag", contrib)

    def on_use_rl_completer_toggled(self, chk_btn, data=None):
		self.highlight_tag = chk_btn.get_active()

    def configure(self, dialog):
        vbox = Gtk.VBox(spacing=6)
		vbox.set_border_width(6)
        check = Gtk.CheckButton("Highlight Matching Tags")
		if self.highlight_tag:
			check.set_active(True)
		check.connect("toggled", self.on_highlight_tag_toggled)
        vbox.pack_start(check, True, True, 0)
        return vbox

    def show_configure(self):
        dialog = Gtk.Dialog("Configure Emmet Plugin",
							geany.main_widgets.window,
							gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
							(gtk.STOCK_CLOSE, gtk.RESPONSE_ACCEPT))

		dialog.set_has_separator(True)
		content_area = dialog.get_content_area()
		content_area.set_border_width(6)
		vbox = self.configure(dialog)
		content_area.pack_start(vbox, True, True, 0)
		content_area.show_all()
		dialog.run()
		dialog.destroy()
