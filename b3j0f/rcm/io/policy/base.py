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

"""This module provides proxy selection policy classes.

A policy is a callable which takes in parameters:

- port: proxy port.
- resources: port resources.
- proxies: list of port proxies.
- name: method name being executed.
- args and kwargs: respectively method varargs and keywords.

And returns one proxy or a PolicyResultSet.

Here are types of selection proxies classes:

- AllPolicy: select all proxies.
- FirstPolicy: select the first proxy or an empty list of proxies.
- CountPolicy: select (random) proxies between [inf;sup].
- RandomPolicy: select one random proxy.
- RoundaboutPolicy: select iteratively a proxy among proxies. The first
    call select the first proxy. Second call, the second. When all
    proxies have been called once, the policy starts again with the first
    proxy.
"""

__all__ = [
    'Policy',
    'FirstPolicy', 'AllPolicy', 'CountPolicy', 'RandomPolicy',
    'RoundaboutPolicy'
]

from random import shuffle, choice

from sys import maxsize

from b3j0f.rcm.io.policy.core import PolicyResultSet


class PolicyConfiguration(object):
    """
    Policy configuration which contains both proxy selection and execution
    policies and is used by ports in order to specify a particular proxy
    processing.

    ``selection`` and ``execution`` policies implementation are determined by
    the port.
    """

    SELECTION = 'selection'
    EXECUTION = 'execution'

    __slots__ = (SELECTION, EXECUTION)

    def __init__(self, selection=None, execution=None):
        """
        :param dict selection: selection policies. Keys are routine names, and
            values are selection policy configuration.
        :param dict execution: execution policies. Keys are routine names, and
            values are execution policy configuration.
        """

        super(PolicyConfiguration, self).__init__()

        self.selection = selection
        self.execution = execution


class FirstPolicy(Policy):
    """Choose first value in specific parameter if parameter is
    PolicyResultSet, otherwise, return parameter.
    """

    def __call__(self, *args, **kwargs):

        result = super(FirstPolicy, self).__call__(*args, **kwargs)

        if isinstance(result, PolicyResultSet):
            result = result[0] if result else None

        return result


class AllPolicy(Policy):
    """Choose specific parameter.
    """


class CountPolicy(Policy):
    """Choose count parameters among proxies.

    Check than resources number are in an interval, otherwise, raise a
    CountError.
    """

    def __init__(self, inf=0, sup=maxsize, random=False, *args, **kwargs):

        super(CountPolicy, self).__init__(*args, **kwargs)

        self.inf = inf
        self.sup = sup
        self.random = random

    class CountError(Exception):
        """Handle CountPolicy errors.
        """

    def __call__(self, *args, **kwargs):

        result = super(CountPolicy, self).__call__(*args, **kwargs)

        if isinstance(result, PolicyResultSet):

            len_proxies = len(result)

            if len_proxies < self.inf:
                raise CountPolicy.CountError(
                    "param count {0} ({1}) must be greater than {2}."
                    .format(result, len_proxies, self.inf)
                )

            if self.random:  # choose randomly item
                result = list(result)
                shuffle(result)
                result = result[0: self.sup - self.inf]
            else:  # choose a slice of result
                result = result[self.inf:self.sup]

            # ensure result is a policy result set
            result = PolicyResultSet(result)

        return result


class RandomPolicy(Policy):
    """Choose one random item in specific parameter if parameter is a
    PolicyResultSet. Otherwise, Choose parameter.
    """

    def __call__(self, *args, **kwargs):

        result = super(RandomPolicy, self).__call__(*args, **kwargs)

        # do something only if result is a PolicyResultSet
        if isinstance(result, PolicyResultSet):
            if result:
                result = choice(result)
            else:
                result = None

        return result


class RoundaboutPolicy(Policy):
    """Choose iteratively Round about proxy resource policy.

    Select iteratively resources or None if sources is empty.
    """

    def __init__(self, *args, **kwargs):

        super(RoundaboutPolicy, self).__init__(*args, **kwargs)
        # initialize index
        self.index = 0

    def __call__(self, *args, **kwargs):

        result = super(RoundaboutPolicy, self).__call__(*args, **kwargs)

        if isinstance(result, PolicyResultSet):
            if result:  # increment index
                index = self.index
                self.index = (self.index + 1) % len(result)
                result = result[index]
            else:
                result = None

        return result
