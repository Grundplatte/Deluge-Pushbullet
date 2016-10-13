#
# core.py
#
# Copyright (C) 2009 Grundplatte <grundplattexox@gmail.com>
#
# Basic plugin template created by:
# Copyright (C) 2008 Martijn Voncken <mvoncken@gmail.com>
# Copyright (C) 2007-2009 Andrew Resch <andrewresch@gmail.com>
# Copyright (C) 2009 Damien Churchill <damoxc@gmail.com>
#
# Deluge is free software.
#
# You may redistribute it and/or modify it under the terms of the
# GNU General Public License, as published by the Free Software
# Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# deluge is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with deluge.    If not, write to:
# 	The Free Software Foundation, Inc.,
# 	51 Franklin Street, Fifth Floor
# 	Boston, MA  02110-1301, USA.
#
#    In addition, as a special exception, the copyright holders give
#    permission to link the code of portions of this program with the OpenSSL
#    library.
#    You must obey the GNU General Public License in all respects for all of
#    the code used other than OpenSSL. If you modify file(s) with this
#    exception, you may extend this exception to your version of the file(s),
#    but you are not obligated to do so. If you do not wish to do so, delete
#    this exception statement from your version. If you delete this exception
#    statement from all source files in the program, then also delete it here.
#

from deluge.log import LOG as log
from deluge.plugins.pluginbase import CorePluginBase
import deluge.component as component
import deluge.configmanager
from deluge.core.rpcserver import export

from twisted.internet import defer
from twisted.internet import reactor
from pushbulletapi.pushbullet import PushBullet

DEFAULT_PREFS = {
    "pb_api_key":"",
    "pb_torrent_completed": True,
    "pb_torrent_added": True
}

class Core(CorePluginBase):
    def enable(self):
        self.config = deluge.configmanager.ConfigManager("pushbullet.conf", DEFAULT_PREFS)
        if self.config["pb_api_key"] is not "":
            self.p = PushBullet(self.config["pb_api_key"])

        d = defer.Deferred()
        reactor.callLater(2, self.register_callbacks)

        log.debug("PushBullet core plugin enabled!")

        return d

    def disable(self):
        self.unregister_callbacks()
        self.config.save()

    def update(self):
        pass

    def register_callbacks(self):
        event_manager = component.get("EventManager")
        event_manager.register_event_handler("TorrentAddedEvent", self.on_torrent_added)
        event_manager.register_event_handler("TorrentFinishedEvent", self.on_torrent_finished)
    
    def unregister_callbacks(self):
        event_manager = component.get("EventManager")
        event_manager.deregister_event_handler("TorrentFinishedEvent", self.on_torrent_finished)
        event_manager.deregister_event_handler("TorrentAddedEvent", self.on_torrent_added)

    def on_torrent_added(self, torrent_id):
        try:
          torrent = component.get("TorrentManager")[torrent_id]
          torrent_status = torrent.get_status({})

          message = _("Added Torrent \"%(name)s\"") % torrent_status
          
          d = defer.maybeDeferred(self.p.pushNoteGlobal, "Torrent Added", message)
          
          return d
        
        except Exception, e:
          log.error("error in alert %s" % e)

    def on_torrent_finished(self, torrent_id):
        try:
          torrent = component.get("TorrentManager")[torrent_id]
          torrent_status = torrent.get_status({})

          message = _("Finished Torrent \"%(name)s\"") % torrent_status
          
          d = defer.maybeDeferred(self.p.pushNoteGlobal, "Download Completed", message)
          
          return d

        except Exception, e:
          log.error("error in on_torrent_finished %s" % e)

    @export
    def set_config(self, config):
        """Sets the config dictionary"""
        for key in config.keys():
            self.config[key] = config[key]
        self.config.save()
        
        if self.config["pb_api_key"] is not "":
            self.p = PushBullet(self.config["pb_api_key"]);

    @export
    def get_config(self):
        """Returns the config dictionary"""
        return self.config.config
