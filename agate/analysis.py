#!/usr/bin/env python

import bz2
from copy import deepcopy
import hashlib
import inspect
import os

try:
    import cPickle as pickle
except ImportError:
    import pickle

class Analysis(object):
    """
    An Analysis is a function whose code configuration and output can be
    serialized to disk. When it is invoked again, if it's code has not changed
    the serialized output will be used rather than executing the code again.

    Implements a promise-like API so that Analyses can depend on one another.
    If a parent analysis is invalidated then all it's children will be as well.

    :param func: The analysis function. Must accept a `data` argument that
        is the state inherited from ancestors analysis.
    :param cache_path: Where to stored the cache files for this analysis.
    """
    def __init__(self, func, cache_path='.agate'):
        self._name = func.__name__
        self._func = func
        self._cache_path = cache_path
        self._next_analyses = []

    def _fingerprint(self):
        """
        Generate a fingerprint for this analysis function.
        """
        hasher = hashlib.md5()
        source = inspect.getsource(self._func)
        hasher.update(source)

        return hasher.hexdigest()

    def _save_fingerprint(self):
        """
        Save the fingerprint of this analysis function to its cache.
        """
        path = os.path.join(self._cache_path, '%s.fingerprint' % self._name)

        if not os.path.exists(self._cache_path):
            os.makedirs(self._cache_path)

        with open(path, 'w') as f:
            f.write(self._fingerprint())

    def _load_fingerprint(self):
        """
        Load the fingerprint of this analysis function from its cache.
        """
        path = os.path.join(self._cache_path, '%s.fingerprint' % self._name)

        if not os.path.exists(path):
            return None

        with open(path) as f:
            fingerprint = f.read()

        return fingerprint

    def _save_data(self, data):
        """
        Save the output data for this analysis from its cache.
        """
        path = os.path.join(self._cache_path, '%s.data' % self._name)

        if not os.path.exists(self._cache_path):
            os.makedirs(self._cache_path)

        with open(path, 'w') as f:
            f.write(bz2.compress(pickle.dumps(data)))

    def _load_data(self):
        """
        Load the output data for this analysis from its cache.
        """
        path = os.path.join(self._cache_path, '%s.data' % self._name)

        if not os.path.exists(path):
            return None

        with open(path) as f:
            data = pickle.loads(bz2.decompress(f.read()))

        return data

    def then(self, next_func):
        """
        Create a new analysis which will run after this one has completed with
        access to the data it generated.

        :param func: The analysis function. Must accept a `data` argument that
            is the state inherited from ancestors analysis.
        """
        analysis = Analysis(next_func)

        self._next_analyses.append(analysis)

        return analysis

    def run(self, data={}, refresh=False):
        """
        Execute this analysis and its descendents. There are four possible
        execution scenarios:

        1. This analysis has never been run. Run it and cache the results.
        2. This analysis is the child of a parent analysis which was run, so it
           must be run because its inputs may have changed. Cache the result.
        3. This analysis has been run, its parents were loaded from cache and
           its fingerprints match. Load the cached result.
        4. This analysis has been run and its parents were loaded from cache,
           but its fingerprints do not match. Run it and cache updated results.

        :param data: The input "state" from the parent analysis, if any.
        :param refresh: Flag indicating if this analysis must refresh because
            one of its ancestors did.
        """
        if refresh:
            print('Refreshing: %s' % self._name)

            local_data = deepcopy(data)

            self._func(local_data)
            self._save_fingerprint()
            self._save_data(local_data)
        else:
            if self._fingerprint() != self._load_fingerprint():
                print('Running: %s' % self._name)

                local_data = deepcopy(data)

                self._func(local_data)
                self._save_fingerprint()
                self._save_data(local_data)

                refresh = True
            else:
                print('Loaded from cache: %s' % self._name)

                local_data = self._load_data()

        for analysis in self._next_analyses:
            analysis.run(local_data, refresh)
