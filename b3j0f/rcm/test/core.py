#!/usr/bin/env python
# -*- coding: utf-8 -*-

# --------------------------------------------------------------------
# The MIT License (MIT)
#
# Copyright (c) 2014 Jonathan Labéjof <jonathan.labejof@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# --------------------------------------------------------------------

from unittest import main

from b3j0f.utils.ut import UTCase
from b3j0f.rcm.core import Component


class ComponentTest(UTCase):

    class TestPort(Component):

        def __init__(self, componentest, *args, **kwargs):
            super(ComponentTest.TestPort, self).__init__(*args, **kwargs)
            self.componentest = componentest

        def bind(self, component, port_name, *args, **kwargs):

            self.componentest.bindcount -= 1

        def unbind(self, component, port_name, *args, **kwargs):

            self.componentest.unbindcount -= 1

    def setUp(self):

        self.component = Component()
        self.named_ports = {
            'test': ComponentTest.TestPort(self),
            'example': ComponentTest.TestPort(self),
            'component': Component(),
            'one': 1,
            'none': None
        }
        self.number_of_testport = len(
            [
                port for port in self.named_ports.values()
                if isinstance(port, ComponentTest.TestPort)
            ]
        )
        self.bindcount = self.number_of_testport
        self.unbindcount = self.number_of_testport

    def test_generated_id(self):
        """
        Test generated ids.
        """

        count = 5000

        ids = set()
        for i in range(count):
            ids.add(Component().id)

        self.assertEqual(len(ids), count)

    def test_id(self):
        """
        Test specific id.
        """

        testid = 'test'
        ctest = Component(_id=testid)
        self.assertEqual(ctest.id, testid)

        exampleid = 'example'
        cexample = Component(_id=exampleid)
        self.assertEqual(cexample.id, exampleid)

        self.assertNotEqual(cexample.id, ctest.id)

    def _test_existing_ports(self):
        """
        Test named ports.

        :param init: initialization function.
        """

        self.assertEqual(len(self.component), len(self.named_ports))
        for name in self.named_ports:
            self.assertIn(name, self.component)
            port = self.component[name]
            self.assertIs(port, self.named_ports[name])

        self.assertEqual(self.bindcount, 0)
        self.assertEqual(self.unbindcount, self.number_of_testport)

    def _init_component_with_ports(self):
        """
        Fill self component with self ports.
        """

        self.component = Component(**self.named_ports)
        self._test_existing_ports()

    def test_clear(self):
        """
        Test clear method.
        """

        self._init_component_with_ports()
        self.component.clear()
        self.assertEqual(len(self.component), 0)
        self.assertEqual(self.bindcount, 0)
        self.assertEqual(self.unbindcount, 0)

    def test_setdefault(self):
        """
        Test setdefault.
        """

        bindcount = self.number_of_testport

        # test setdefault
        for index, name in enumerate(self.named_ports):
            port = self.named_ports[name]
            p = self.component.setdefault(name, port)
            self.assertIs(port, p)
            if isinstance(port, ComponentTest.TestPort):
                bindcount -= 1
            self.assertEqual(self.bindcount, bindcount)
            self.assertEqual(self.unbindcount, self.number_of_testport)
            p = self.component.setdefault(name, port)
            self.assertIs(port, p)
            self.assertEqual(self.bindcount, bindcount)
            self.assertEqual(self.unbindcount, self.number_of_testport)

    def test_init_ports(self):
        """
        Test to init ports.
        """

        self._init_component_with_ports()

    def test_update_ports(self):
        """
        Test to update ports.
        """

        self.component.update(self.named_ports)
        self._test_existing_ports()

    def test_bind_ports(self):
        """
        Test to bind ports.
        """

        for name in self.named_ports:
            port = self.named_ports[name]
            self.component[name] = port
        self._test_existing_ports()

    def test_unbind_port(self):
        """
        Test to unbind ports.
        """

        self._init_component_with_ports()

        for name in self.named_ports:
            self.assertIn(name, self.component)
            del self.component[name]
            self.assertNotIn(name, self.component)

        self.assertEqual(len(self.component), 0)

    def test_get_ports_default(self):
        """
        Test get_ports method without parameters.
        """

        self._init_component_with_ports()

        ports = self.component.get_ports()

        self.assertEqual(ports, self.named_ports)

    def test_get_ports_name(self):
        """
        Test get_ports method with name.
        """

        self._init_component_with_ports()

        for name in self.named_ports:
            ports = self.component.get_ports(names=name)
            self.assertEqual(len(ports), 1)
            self.assertIn(name, ports)

    def test_get_ports_names(self):
        """
        Test get_ports method with names.
        """

        self._init_component_with_ports()
        names = self.named_ports.keys()[1:]
        ports = self.component.get_ports(names=names)

        self.assertEqual(len(ports), len(self.named_ports) - 1)
        for name in names:
            self.assertIn(name, ports)

    def test_get_ports_type(self):
        """
        Test get_ports method with type.
        """

        self._init_component_with_ports()

        _type = ComponentTest.TestPort
        ports = self.component.get_ports(types=_type)

        self.assertEqual(len(ports), self.number_of_testport)
        for name in ports:
            port = ports[name]
            self.assertTrue(isinstance(port, _type))

    def test_get_ports_types(self):
        """
        Test get_ports method with types.
        """

        self._init_component_with_ports()

        types = []

        for name in self.named_ports:
            port = self.named_ports[name]
            if not isinstance(port, Component):
                types.append(port.__class__)

        self.assertTrue(types)
        ports = self.component.get_ports(types=types)

        self.assertEqual(len(ports), len(types))

        for name in ports:
            port = ports[name]
            self.assertFalse(isinstance(port, Component))

    def test_get_ports_select(self):
        """
        Test get_ports method with a combination of names and types.
        """

        self._init_component_with_ports()

        components_count = len(
            [
                port for port in self.named_ports.values()
                if isinstance(port, Component)
            ]
        )

        ports = self.component.get_ports(
            select=lambda name, port: isinstance(port, Component)
        )

        self.assertEqual(len(ports), components_count)

if __name__ == '__main__':
    main()
