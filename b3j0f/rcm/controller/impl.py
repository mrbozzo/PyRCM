# -*- coding: utf-8 -*-

# --------------------------------------------------------------------
# The MIT License (MIT)
#
# Copyright (c) 2015 Jonathan Labéjof <jonathan.labejof@gmail.com>
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

"""Contains Impl component definition.
"""

__all__ = [
    'ImplController',
    'ImplAnnotation', 'ParameterizedImplAnnotation', 'Context',
    'getter_name', 'setter_name'
]

from b3j0f.rcm.core import Component
from b3j0f.controller.core import Controller
from b3j0f.annotation import Annotation
from b3j0f.utils.version import basestring
from b3j0f.utils.path import lookup

from inspect import isclass


class ImplController(Controller):
    """Impl Controller which uses a class in order to instantiate a component
    business implementation.
    """

    CLS = '_cls'  #: cls field name
    IMPL = '_impl'  #: impl field name

    __slots__ = (CLS, IMPL, ) + Controller.__slots__

    def __init__(self, cls=None, *args, **kwargs):
        """
        :param cls: class to use.
        :type cls: str or type
        :param dict named_ports: named ports.
        """

        super(ImplController, self).__init__(*args, **kwargs)

        self.cls = cls

    def renew_impl(self, component=None, cls=None, params={}):
        """Instantiate business element and returns it.

        :param cls: new cls to use. If None, use self.cls.
        :type cls: type or str
        :param dict params: new impl parameters.
        :return: new impl.
        """
        # save prev impl
        prev_impl = self.impl
        # save cls
        self.cls = cls
        # save impl and result
        result = self.impl = self._cls(**params)
        # apply business annotations on impl
        if isinstance(component, Component):
            ImplAnnotation.apply(
                component=component, impl=self.impl, prev_impl=prev_impl
            )

        return result

    @property
    def cls(self):
        """Get self cls.
        """

        return self._cls

    @cls.setter
    def cls(self, value):
        """Change of cls.

        :param value: new class to use.
        :type value: str or type.
        :raises: TypeError in case of value is not a class.
        """
        # if value is a str, try to find the right class
        if isinstance(value, basestring):
            value = lookup(value)
        # update value only if value is a class
        if isclass(value):
            self._cls = value
            self._impl = None  # and nonify the impl
        else:  # raise TypeError if value is not a class
            raise TypeError('value {0} must be a class'.format(value))

    @property
    def impl(self):
        return self._impl

    @impl.setter
    def impl(self, value):

        # update cls
        self.cls = value.__class__
        # and impl
        self._impl = value


class ImplAnnotation(Annotation):
    """Annotation dedicated to Impl implementations.
    """

    def apply_on(
        self, component, impl, prev_impl=None, attr=None, prev_attr=None
    ):
        """Callback when Impl component renew its implementation.

        :param Component component: business implementation component.
        :param impl: component business implementation.
        :param prev_impl: previous component business implementation.
        :param attr: business implementation attribute.
        :param prev_attr: previous business implementation attribute.
        """

        raise NotImplementedError()

    @classmethod
    def apply(cls, component, impl, prev_impl=None, check=None):
        """Apply all cls annotations on component and impl.

        :param Component component: business implementation component.
        :param impl: component business implementation.
        :param prev_impl: previous component business implementation.
        :param check: check function which takes in parameter an annotation in
        order to do annotation.apply_on. If None, annotations are applied.
        """

        annotations = cls.get_annotations(impl)
        for annotation in annotations:
            if check is None or check(annotation):
                annotation.apply_on(
                    component=component, impl=impl, prev_impl=prev_impl
                )

        for field in dir(impl):
            attr = getattr(impl, field)
            prev_attr = getattr(prev_impl, field, None)
            annotations = cls.get_annotations(field, ctx=impl)
            for annotation in annotations:
                if check is None or check(annotation):
                    annotation.apply_on(
                        component=component, impl=impl, prev_impl=prev_impl,
                        attr=attr, prev_attr=prev_attr
                    )


class ParameterizedImplAnnotation(ImplAnnotation):
    """Abstract annotation which takes in parameter a param in order to inject
    a resource with a dedicated parameter name in a routine.
    """

    PARAM = 'param'  #: param field name

    __slots__ = (PARAM, ) + ImplAnnotation.__slots__

    def __init__(self, param=None, *args, **kwargs):

        super(Context, self).__init__(*args, **kwargs)

        self.param = param

    def get_resource(
        self, component, impl, prev_impl=None, attr=None, prev_attr=None
    ):
        """Get a resource to inject in a routine call in the scope of a
        component, impl, prev_impl, attr and prev_attr.

        :param Component component: business implementation component.
        :param impl: component business implementation.
        :param prev_impl: previous component business implementation.
        :param attr: business implementation attribute.
        :param prev_attr: previous business implementation attribute.
        """

        return component

    def apply_on(
        self, component, impl, prev_impl=None, attr=None, prev_attr=None,
        *args, **kwargs
    ):
        # get the right resource to inject
        resource = self.get_resource(
            component=component, impl=impl, prev_impl=prev_impl,
            attr=attr, prev_attr=prev_attr
        )
        # identify the right target element to inject resource
        target = impl if attr is None else attr
        # inject the resource in the target
        if self.param is None:
            try:
                target(resource)
            except TypeError:
                target()
        else:
            kwargs = {self.param: resource}
            target(**kwargs)


class Context(ParameterizedImplAnnotation):
    """Annotation dedicated to inject a port in a component implementation
    related to the method.
    """

    NAME = 'name'  #: port name field name

    __slots__ = (NAME, ) + ParameterizedImplAnnotation.__slots__

    def __init__(self, name, *args, **kwargs):

        super(Context, self).__init__(*args, **kwargs)

        self.name = name

    @property
    def name(self):

        return self._name

    @name.setter
    def name(self, value):

        self._name = value

    def get_resource(self, component, *args, **kwargs):

        # resource corresponds to a component port or the component if port
        # name does not exist
        port_name = self.name
        result = component if port_name is None else component[port_name]
        return result


class Impl(Context):
    """Annotation dedicated to inject an ImplController in an implementation.
    """

    __slots__ = Context.__slots__

    def __init__(self, name=ImplController.get_name(), *args, **kwargs):

        super(Impl, self).__init__(name=name, *args, **kwargs)


def _accessor_name(accessor, prefix):
    """Get accessor name which could contain prefix.
    """

    result = accessor.__name__

    if result.startswith(prefix):
        result = result[len(prefix):]
        if result and result[0] == '_':
            result = result[1:]

    return result


def getter_name(getter):
    """Get getter name.
    """

    return _accessor_name('get')


def setter_name(setter):
    """Get setter name.
    """

    return _accessor_name('set')
