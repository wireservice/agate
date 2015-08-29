#!/usr/bin/env python

import bz2
from copy import deepcopy
import hashlib
import inspect
import os

try:
    import cPickle as pickle
except ImportError: # pragma: no cover
    import pickle

from agate.utils import memoize

class Analysis(object):
    """
    An Analysis is a function whose code configuration and output can be
    serialized to disk. When it is invoked again, if it's code has not changed
    the serialized output will be used rather than executing the code again.

    Implements a promise-like API so that Analyses can depend on one another.
    If a parent analysis is invalidated then all it's children will be as well.

    :param func: A callable that implements the analysis. Must accept a `data`
        argument that is the state inherited from its ancestors analysis.
    :param parent: The parent analysis of this one, if any.
    :param cache_dir: Where to stored the cache files for this analysis.
    """
    def __init__(self, func, parent=None, cache_dir='.agate'):
        self._name = func.__name__
        self._func = func
        self._parent = parent
        self._cache_dir = cache_dir
        self._next_analyses = []

    @memoize
    def _trace(self):
        """
        Returns the sequence of Analysis instances that lead to this one.
        """
        if self._parent:
            return self._parent._trace() + [self._name]

        return [self._name]

    @memoize
    def _fingerprint(self):
        """
        Generate a fingerprint for this analysis function.
        """
        hasher = hashlib.md5()

        trace = self._trace()
        hasher.update('\n'.join(trace).encode('utf-8'))

        source = inspect.getsource(self._func)
        hasher.update(source.encode('utf-8'))

        return hasher.hexdigest()

    @memoize
    def _cache_path(self):
        """
        Get the full cache path for the current fingerprint.
        """
        return os.path.join(self._cache_dir, '%s.cache' % self._fingerprint())

    def _check_cache(self):
        """
        Check if there exists a cache file for the current fingerprint.
        """
        return os.path.exists(self._cache_path())

    def _save_cache(self, data):
        """
        Save the output data for this analysis from its cache.
        """
        if not os.path.exists(self._cache_dir):
            os.makedirs(self._cache_dir)

        f = bz2.BZ2File(self._cache_path(), 'w')
        f.write(pickle.dumps(data))
        f.close()

    def _load_cache(self):
        """
        Load the output data for this analysis from its cache.
        """
        f = bz2.BZ2File(self._cache_path())
        data = pickle.loads(f.read())
        f.close()

        return data

    def then(self, next_func):
        """
        Create a new analysis which will run after this one has completed with
        access to the data it generated.

        :param func: A callable that implements the analysis. Must accept a
            `data` argument that is the state inherited from its ancestors
            analysis.
        """
        analysis = Analysis(next_func, parent=self, cache_dir=self._cache_dir)

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
            self._save_cache(local_data)
        else:
            fingerprint = self._fingerprint()

            if self._check_cache():
                print('Loaded from cache: %s' % self._name)

                local_data = self._load_cache()
            else:
                print('Running: %s' % self._name)

                local_data = deepcopy(data)

                self._func(local_data)
                self._save_cache(local_data)

                refresh = True

        for analysis in self._next_analyses:
            analysis.run(local_data, refresh)
