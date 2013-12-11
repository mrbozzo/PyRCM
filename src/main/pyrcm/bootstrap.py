
import json
import os
import sys

PATHS = sys.path[:]
DEFAULT_FILE_PATH = 'pyrcm.conf'


def get_config(config_path=DEFAULT_FILE_PATH, paths=PATHS):
    """
    Get configuration file.
    """

    result = None
    if os.path.exists(config_path):
        result = json.load(config_path)
    else:
        for path in PATHS:
            full_config_path = os.path.join(path, config_path)
            if os.path.exists(full_config_path):
                result = json.load(full_config_path)
                break

    return result


BOOTSTRAP = 'bootstrap'
bootstrap = None

from pyrcm.factory import Factory


def get_bootstrap_component(renew=False):
    """
    Return current bootstrap component.
    """

    global bootstrap
    if bootstrap is None or renew:

        config = get_config()

        if config is not None:
            bootsrap_path = config[BOOTSTRAP]
            for path in PATHS:
                full_bootstrap_path = os.path.join(path, bootsrap_path)
                if os.path.exists(full_bootstrap_path):
                    bootstrap_config = json.load(full_bootstrap_path)
                    bootstrap = Factory.new_component(bootstrap_config)
                    break

    return bootstrap

from pyrcm.core import Reference, Service
from pyrcm.factory import FactoryManager
from pyrcm.binding import BindingManager
from pyrcm.parser.core import ParserManager


class Bootstrap(object):

    def __init__(self, factory, binding):
        pass

    @Reference(interface=FactoryManager)
    def set_factory(self, factory):
        self.factory = factory

    @Service(interface=FactoryManager)
    def get_factory(self):
        return self.factory

    @Reference(interface=BindingManager)
    def set_binding(self, binding):
        self.binding = binding

    @Service(interface=BindingManager)
    def get_binding(self):
        return self.binding

    @Reference(interface=ParserManager)
    def set_parser(self, parser):
        self.parser = parser

    @Service(interface=ParserManager)
    def get_parser(self):
        return self.binding
