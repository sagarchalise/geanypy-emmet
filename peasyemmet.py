import os
from configparser import SafeConfigParser
from gettext import gettext as _
from gi.repository import Gtk, GObject
from gi.repository import Geany
from gi.repository import GeanyScintilla
from gi.repository import Peasy
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

actions = ("expand_abbreviation", "match_pair_inward", "match_pair_outward",
            "wrap_with_abbreviation", "prev_edit_point", "next_edit_point",
            "insert_formatted_newline", "select_previous_item", "select_next_item",
            "matching_pair", "merge_lines", "toggle_comment", "split_join_tag",
            "remove_tag", "update_image_size", "evaluate_math_expression",
            "reflect_css_value", "insert_formatted_line_break_only",
            "encode_decode_data_url", "increment_number_by_1", "increment_number_by_10",
            "increment_number_by_01", "decrement_number_by_1", "decrement_number_by_10",
            "decrement_number_by_01")

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

class EmmetPlugin(Peasy.Plugin, Peasy.PluginConfigure):
    __gtype_name__ = "Emmet"
    indicators = (Geany.Indicator.SEARCH, 1)
    file_types = ('HTML', 'PHP', 'XML', 'CSS')
    __highlight_tag = False
    __show_editor_menu = False
    __show_specific_menu = False
    editor_menu = None
    specific_menu = None
    tools_menu = None

    def do_enable(self):
        o = self.geany_plugin.geany_data.object
        self.load_config()
        self.check_main_menu()
        self.check_editor_menu()
        signals = ('document-reload', 'document-save', 'document-activate', 'document-close', 'document-open')
        for signal in signals:
            o.connect(signal, self.on_document_notify)
        o.connect("editor-notify", self.on_editor_notify)

    def do_disable(self):
        if self.show_editor_menu and self.editor_menu:
            self.editor_menu.destroy()
        if self.show_specific_menu and self.specific_menu:
            self.specific_menu.destroy()
        else:
            self.tools_menu.destroy()

    def load_config(self):
        self.cfg_path = os.path.join(self.geany_plugin.geany_data.app.configdir, "plugins", "pyemmet.conf")
        self.cfg = SafeConfigParser()
        self.cfg.read(self.cfg_path)

    def save_config(self):
        GObject.idle_add(self.on_save_config_timeout)

    def on_save_config_timeout(self, data=None):
        self.cfg.write(open(self.cfg_path, 'w'))
        return False

    def set_tools_menu(self):
        self.tools_menu = Gtk.MenuItem(_("Emmet"))
        imenu = self.populate_menu()
        self.tools_menu.set_submenu(imenu)
        self.tools_menu.show()
        self.set_menu_sensitivity()
        self.geany_plugin.geany_data.main_widgets.tools_menu.append(self.tools_menu)

    def set_editor_menu(self):
        indexes = (0, 3, 9)
        self.editor_menu = Gtk.MenuItem(_("Emmet"))
        imenu = Gtk.Menu()
        for index in indexes:
            menu_item = Gtk.MenuItem(_(actions[index].replace("_", " ").title()))
            menu_item.connect("activate", self.on_action_activate, actions[index])
            menu_item.show()
            imenu.append(menu_item)
        self.editor_menu.set_submenu(imenu)
        self.editor_menu.show()
        self.set_menu_sensitivity()
        self.geany_plugin.geany_data.main_widgets.editor_menu.append(self.editor_menu)

    def set_menu_sensitivity(self, flag=False):
        if self.editor_menu:
            self.editor_menu.set_sensitive(flag)
        if self.specific_menu:
            self.specific_menu.set_sensitive(flag)
        if self.tools_menu:
            self.tools_menu.set_sensitive(flag)

    @staticmethod
    def get_geany_menubar(main_widget_window):
        """ Very hackish  way to get menubar. """
        m = Geany.ui_lookup_widget(main_widget_window, 'menubar1')
        #  geany.ui_utils.lookup_widget(geany.main_widgets.window, 'meubar1')
        #  m = geany.main_widgets.window.get_child().get_children()[0].get_children()[0]
        if isinstance(m, Gtk.MenuBar):
            return m

    def set_specific_menu(self):
        self.specific_menu = Gtk.MenuItem(_("Emmet"))
        imenu = self.populate_menu()
        self.specific_menu.set_submenu(imenu)
        self.specific_menu.show()
        menubar = self.get_geany_menubar(self.geany_plugin.geany_data.main_widgets.window)
        self.set_menu_sensitivity()
        if menubar:
            menubar.append(self.specific_menu)

    def on_document_notify(self, user_data, doc):
        self.check_filetype_and_get_contrib(doc)

    def check_editor_menu(self):
        if not self.editor_menu and self.show_editor_menu:
            self.set_editor_menu()
        elif not self.show_editor_menu and self.editor_menu:
            self.geany_plugin.geany_data.main_widgets.editor_menu.remove(self.editor_menu)
            self.editor_menu.destroy()
            self.editor_menu = None

    def check_main_menu(self):
        if not self.specific_menu and self.show_specific_menu:
            self.set_specific_menu()
            if self.tools_menu:
                self.geany_plugin.geany_data.main_widgets.tools_menu.remove(self.tools_menu)
                self.tools_menu.destroy()
                self.tools_menu = None
        elif not self.show_specific_menu and self.specific_menu:
            self.set_tools_menu()
            mb = self.get_geany_menubar(self.geany_plugin.geany_data.main_widgets.window)
            if mb:
                mb.remove(self.specific_menu)
            self.specific_menu.destroy()
            self.specific_menu = None


    def populate_menu(self):
        imenu = Gtk.Menu()
        # Proxy keybinding [has errors]
        emmet_key = None
        if hasattr(self, 'set_key_group'):
            emmet_key = self.set_key_group("emmet", len(actions), self.on_key_activate)
        key_code = 0
        for label in create_action_label():
            menu_item = Gtk.MenuItem(label)
            menu_item.connect("activate", self.on_action_activate, actions_dict[label])
            menu_item.show()
            imenu.append(menu_item)
            if emmet_key:
                emmet_key.add_key_item(key_id=key_code, key=0, mod=0, name=actions[key_code], label=label)
            key_code += 1
        return imenu

    @property
    def highlight_tag(self):
        if self.cfg.has_section('general'):
            if self.cfg.has_option('general', 'highlight_tag'):
                return self.cfg.getboolean('general', 'highlight_tag')
        return self.__highlight_tag

    @highlight_tag.setter
    def highlight_tag(self, value):
        self.__highlight_tag = value
        if not self.cfg.has_section('general'):
            self.cfg.add_section('general')
        self.cfg.set('general', 'highlight_tag',
            str(self.__highlight_tag).lower())
        self.save_config()

    @property
    def show_editor_menu(self):
        if self.cfg.has_section('general'):
            if self.cfg.has_option('general', 'show_editor_menu'):
                return self.cfg.getboolean('general', 'show_editor_menu')
        return self.__show_editor_menu

    @show_editor_menu.setter
    def show_editor_menu(self, value):
        self.__show_editor_menu = value
        if not self.cfg.has_section('general'):
            self.cfg.add_section('general')
        self.cfg.set('general', 'show_editor_menu',
            str(self.__show_editor_menu).lower())
        self.save_config()

    @property
    def show_specific_menu(self):
        if self.cfg.has_section('general'):
            if self.cfg.has_option('general', 'show_specific_menu'):
                return self.cfg.getboolean('general', 'show_specific_menu')
        return self.__show_specific_menu

    @show_specific_menu.setter
    def show_specific_menu(self, value):
        self.__show_specific_menu = value
        if not self.cfg.has_section('general'):
            self.cfg.add_section('general')
        self.cfg.set('general', 'show_specific_menu',
            str(self.__show_specific_menu).lower())
        self.save_config()

    @staticmethod
    def prompt(title):
        abbr = Geany.dialog_show_input(_(title), None, None)
        return abbr


    def check_filetype_and_get_contrib(self, doc=None):
        cur_doc = doc or Geany.Document.get_current()
        cur_file_type = cur_doc.file_type.name if cur_doc else None
        if cur_file_type in self.file_types:
            sel = Geany.encodings_convert_to_utf8(cur_doc.editor.sci.get_selection_contents(), -1)
            content = Geany.encodings_convert_to_utf8(cur_doc.editor.sci.get_contents(-1), -1)
            self.set_menu_sensitivity(True)
            return {
                'cur_doc': cur_doc,
                'cur_doc_type': cur_file_type.lower() if cur_file_type != 'PHP' else 'html',
                'prompt': self.prompt,
                'cur_content':  content[0],
                'cur_selection': sel[0],
                'tab_used': cur_doc.editor.indent_type == Geany.IndentType.TABS,
                'tab_width': cur_doc.editor.indent_width,
                'geanyIndicatorSearch': Geany.Indicator.SEARCH,
            }
        else:
            self.set_menu_sensitivity()

    @staticmethod
    def run_emmet_action(action, contrib):
        ctx = Context(files=[os.path.join(BASE_PATH, 'editor.js')], ext_path=EXT_PATH, contrib=contrib)
        with ctx.js() as c:
            c.locals.pySetupEditorProxy()
            c.locals.pyRunAction(action)

    def on_key_activate(self, key_id):
        self.on_action_activate(key_id, actions[key_id])

    def on_action_activate(self, key_id, name):
        contrib = self.check_filetype_and_get_contrib()
        if contrib:
            self.run_emmet_action(name, contrib)

    def on_editor_notify(self, g_obj, editor, nt):
        if self.highlight_tag:
            contrib = self.check_filetype_and_get_contrib(editor.document)
            if contrib:
                notification_codes = (GeanyScintilla.SCN_UPDATEUI, GeanyScintilla.SCN_KEY)
                if nt.nmhdr.code in notification_codes:
                    for indicator in self.indicators:
                        editor.indicator_clear(indicator)
                    self.run_emmet_action("highlight_tag", contrib)
        else:
            for indicator in self.indicators:
                editor.indicator_clear(indicator)

    def on_highlight_tag_toggled(self, chk_btn, data=None):
        self.highlight_tag = chk_btn.get_active()

    def on_editor_menu_toggled(self, chk_btn, data=None):
        self.show_editor_menu = chk_btn.get_active()
        self.check_editor_menu()

    def on_specific_menu_toggled(self, chk_btn, data=None):
        self.show_specific_menu = chk_btn.get_active()
        self.check_main_menu()

    def configure(self, dialog):
        vbox = Gtk.VBox(spacing=6)
        vbox.set_border_width(6)
        check_highlight = Gtk.CheckButton(_("Highlight Matching Tags"))
        if self.highlight_tag:
            check_highlight.set_active(True)
        check_highlight.connect("toggled", self.on_highlight_tag_toggled)
        check_editor_menu = Gtk.CheckButton(_("Show some actions on editor menu"))
        if self.show_editor_menu:
            check_editor_menu.set_active(True)
        check_editor_menu.connect("toggled", self.on_editor_menu_toggled)
        check_specific_menu = Gtk.CheckButton(_("Attach menu to menubar rather than tools menu."))
        if self.show_specific_menu:
            check_specific_menu.set_active(True)
        check_specific_menu.connect("toggled", self.on_specific_menu_toggled)
        vbox.pack_start(check_highlight, True, True, 0)
        vbox.pack_start(check_editor_menu, True, True, 0)
        vbox.pack_start(check_specific_menu, True, True, 0)
        return vbox