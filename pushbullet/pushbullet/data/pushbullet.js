/*
Script: pushbulletplugin.js
    The client-side javascript code for the PushbulletPlugin plugin.

Copyright:
    (C) Grundplatte 2009 <grundplattexox@gmail.com>
    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 3, or (at your option)
    any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, write to:
        The Free Software Foundation, Inc.,
        51 Franklin Street, Fifth Floor
        Boston, MA  02110-1301, USA.

    In addition, as a special exception, the copyright holders give
    permission to link the code of portions of this program with the OpenSSL
    library.
    You must obey the GNU General Public License in all respects for all of
    the code used other than OpenSSL. If you modify file(s) with this
    exception, you may extend this exception to your version of the file(s),
    but you are not obligated to do so. If you do not wish to do so, delete
    this exception statement from your version. If you delete this exception
    statement from all source files in the program, then also delete it here.
*/

Ext.ns('Deluge.ux.preferences');

Deluge.ux.preferences.PushbulletPage = Ext.extend(Ext.Panel, {

    title: _('Pushbullet'),
    layout: 'fit',
    border: false,
        
    initComponent: function() {
        Deluge.ux.preferences.PushbulletPage.superclass.initComponent.call(this);

        this.form = this.add({
            xtype: 'form',
            layout: 'form',
            border: false,
            autoHeight: true
        });

        this.notifications = this.form.add({
            xtype: 'fieldset',
            border: false,
            title: _('Notification Settings'),
            autoHeight: true,
            defaultType: 'textfield',
            style: 'margin-top: 5px; margin-bottom: 0px; padding-bottom: 0px;',
            labelWidth: 200
        });

        this.torrent_add = this.notifications.add({
            xtype: "checkbox",
            fieldLabel: _('On Torrent Add'),
            name: 'pb_torrent_added',
            width: 80,
            value: true
        });
        
        this.torrent_complete = this.notifications.add({
            xtype: "checkbox",
            fieldLabel: _('On Torrent Complete'),
            name: 'pb_torrent_completed',
            width: 80,
            value: true
        });

        this.api_key = this.notifications.add({
            fieldLabel: _('API Key'),
            name: 'pb_api_key',
            width: 80
        });

        // update every time the preferences panel gets called
        deluge.preferences.on('show', this.updateConfig, this);
    },

    onOk: function() {
        this.onSave();
    },

    onSave: function() {
        // build settings object
        var config = { };

        config['pb_api_key'] = this.api_key.getValue();
        config['pb_torrent_added'] = this.torrent_add.getValue();
        config['pb_torrent_completed'] = this.torrent_complete.getValue();

        deluge.client.pushbullet.set_config(config);
    },

    updateConfig: function() {
        deluge.client.pushbullet.get_config({
            success: function(config) {
                this.torrent_add.setValue(config['pb_torrent_added']);
                this.torrent_complete.setValue(config['pb_torrent_completed']);
                this.api_key.setValue(config['pb_api_key']);
            },
            scope: this
        });
    }
});

Deluge.plugins.PushbulletPlugin = Ext.extend(Deluge.Plugin, {

	name: "Pushbullet",

	onDisable: function() {
        deluge.preferences.removePage(this.prefsPage);
	},

	onEnable: function() {
        this.prefsPage = deluge.preferences.addPage(new Deluge.ux.preferences.PushbulletPage());
	}
});

Deluge.registerPlugin('Pushbullet', Deluge.plugins.PushbulletPlugin);
