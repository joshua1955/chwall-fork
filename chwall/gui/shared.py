import subprocess

from chwall.daemon import notify_daemon_if_any, notify_app_if_any, daemon_info
from chwall.utils import VERSION, read_config, cleanup_cache
from chwall.wallpaper import blacklist_wallpaper, pick_wallpaper
from chwall.gui.preferences import PrefDialog

import gi
gi.require_version("Gtk", "3.0")  # noqa: E402
from gi.repository import Gtk

import gettext
# Uncomment the following line during development.
# Please, be cautious to NOT commit the following line uncommented.
# gettext.bindtextdomain("chwall", "./locale")
gettext.textdomain("chwall")
_ = gettext.gettext


class ChwallGui:
    def __init__(self):
        self.config = read_config()
        self.app = None

    def daemon_info(self):
        return daemon_info(self.config)

    def on_change_wallpaper(self, widget, direction=False):
        pick_wallpaper(self.config, direction)
        notify_daemon_if_any()
        notify_app_if_any()

    def on_blacklist_wallpaper(self, widget):
        blacklist_wallpaper()
        self.on_change_wallpaper(widget)

    def run_chwall_component(self, _widget, component):
        if component == "daemon":
            # No need to fork, daemon already do that
            subprocess.run(["chwall-daemon"])
        else:
            subprocess.run(["chwall", "detach", component])

    def get_flags_if_app(self):
        if self.app is not None:
            # flags 3 = MODAL | DESTROY_WITH_PARENT
            return 3
        return 0

    def on_cleanup_cache(self, _widget):
        deleted = cleanup_cache()
        if deleted < 2:
            message = _("{number} broken cache entry has been removed")
        else:
            message = _("{number} broken cache entries have been removed")
        # flags 3 = MODAL | DESTROY_WITH_PARENT
        dialog = Gtk.MessageDialog(self.app, self.get_flags_if_app(),
                                   Gtk.MessageType.INFO, Gtk.ButtonsType.OK,
                                   _("Cache cleanup"))
        dialog.set_icon_name("chwall")
        dialog.format_secondary_text(message.format(number=deleted))
        dialog.run()
        dialog.destroy()

    def show_preferences_dialog(self, widget):
        prefwin = PrefDialog(self.app, self.get_flags_if_app(), self.config)
        prefwin.run()
        prefwin.destroy()

    def show_about_dialog(self, widget):
        about_dialog = Gtk.AboutDialog()
        about_dialog.set_destroy_with_parent(True)
        about_dialog.set_icon_name("chwall")
        about_dialog.set_name("Chwall")
        about_dialog.set_website("https://git.deparis.io/chwall/about")
        about_dialog.set_comments(_("Wallpaper Changer"))
        about_dialog.set_version(VERSION)
        about_dialog.set_copyright(_("Chwall is released under the WTFPL"))
        about_dialog.set_authors(["Étienne Deparis <etienne@depar.is>"])
        about_dialog.set_logo_icon_name("chwall")
        about_dialog.run()
        about_dialog.destroy()

    def kthxbye(self, *args):
        Gtk.main_quit()
