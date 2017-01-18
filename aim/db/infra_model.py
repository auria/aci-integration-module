# Copyright (c) 2016 Cisco Systems
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import sqlalchemy as sa
from sqlalchemy.dialects.mysql import VARCHAR

from aim.api import infra
from aim.db import model_base


class HostLink(model_base.Base, model_base.AttributeMixin):
    __tablename__ = 'aim_host_links'

    host_name = sa.Column(sa.String(128), primary_key=True)
    interface_name = sa.Column(sa.String(32), primary_key=True)
    interface_mac = sa.Column(sa.String(24))

    switch_id = sa.Column(sa.String(128))
    module = sa.Column(sa.String(128))
    port = sa.Column(sa.String(128))
    path = sa.Column(VARCHAR(512, charset='latin1'))


class HostLinkManager(object):

    """DB Model to manage all APIC DB interactions."""

    def __init__(self, aim_context, aim_manager):
        self.aim_context = aim_context
        self.aim_manager = aim_manager

    def add_hostlink(self, host, ifname, ifmac, swid, module, port, path):
        link = infra.HostLink(
            host_name=host, interface_name=ifname,
            interface_mac=ifmac, switch_id=swid, module=module, port=port,
            path=path)
        self.aim_manager.create(self.aim_context, link)

    def delete_hostlink(self, host, ifname):
        self.aim_manager.delete(
            self.aim_context, infra.HostLink(host_name=host,
                                             interface_name=ifname))

    # Leaving the following read methods as direct DB calls, apicapi expects
    # things like "count" to exist in the result.

    def get_hostlink(self, host, ifname):
        return self.aim_context.db_session.query(HostLink).filter_by(
            host_name=host, interface_name=ifname).first()

    def get_hostlinks_for_host_switchport(self, host, swid, module, port):
        return self.aim_context.db_session.query(HostLink).filter_by(
            host_name=host, switch_id=swid, module=module, port=port).all()

    def get_hostlinks_for_switchport(self, swid, module, port):
        return self.aim_context.db_session.query(HostLink).filter_by(
            switch_id=swid, module=module, port=port).all()

    def get_hostlinks(self):
        return self.aim_context.db_session.query(HostLink).all()

    def get_hostlinks_for_host(self, host):
        return self.aim_context.db_session.query(HostLink).filter_by(
            host_name=host).all()

    def get_switches(self):
        return self.aim_context.db_session.query(HostLink.switch_id).distinct()

    def get_modules_for_switch(self, swid):
        return self.aim_context.db_session.query(
            HostLink.module).filter_by(switch_id=swid).distinct()

    def get_ports_for_switch_module(self, swid, module):
        return self.aim_context.db_session.query(
            HostLink.port).filter_by(switch_id=swid, module=module).distinct()

    def get_switch_and_port_for_host(self, host):
        return self.aim_context.db_session.query(
            HostLink.switch_id, HostLink.module, HostLink.port).filter_by(
                host_name=host).distinct()