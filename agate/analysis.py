#!/usr/bin/env python

from copy import deepcopy
import inspect
import os
import pickle

class Analysis(object):
    """
    An Analysis is a function whose code configuration and output can be
    serialized to disk. When it is invoked again, if it's code has not changed
    the serialized output will be used rather than executing the code again.

    Implements a promise-like API so that Analyses can depend on one another.
    If a parent analysis is invalidated then all it's children will be as well.
    """
    def __init__(self, func, cache_path='.analysis'):
        self._name = func.__name__
        self._func = func
        self._cache_path = cache_path
        self._next_analyses = []

    def _save_signature(self):
        path = os.path.join(self._cache_path, '%s.signature.pickle' % self._name)

        if not os.path.exists(self._cache_path):
            os.makedirs(self._cache_path)

        with open(path, 'w') as f:
            pickle.dump(inspect.getsource(self._func), f)

    def _load_signature(self):
        path = os.path.join(self._cache_path, '%s.signature.pickle' % self._name)

        if not os.path.exists(path):
            return None

        with open(path) as f:
            signature = pickle.load(f)

        return signature

    def _save_state(self, state):
        path = os.path.join(self._cache_path, '%s.state.pickle' % self._name)

        if not os.path.exists(self._cache_path):
            os.makedirs(self._cache_path)

        with open(path, 'w') as f:
            pickle.dump(state, f)

    def _load_state(self):
        path = os.path.join(self._cache_path, '%s.state.pickle' % self._name)

        if not os.path.exists(path):
            return None

        with open(path) as f:
            state = pickle.load(f)

        return state

    def then(self, next_func):
        analysis = Analysis(next_func)

        self._next_analyses.append(analysis)

        return analysis

    def run(self, state={}, refresh=False):
        local_state = deepcopy(state)

        if refresh:
            print('Refreshing: %s' % self._name)

            self._func(local_state)
            self._save_signature()
            self._save_state(local_state)
        else:
            signature = self._load_signature()

            if not signature or inspect.getsource(self._func) != signature:
                print('Running: %s' % self._name)

                self._func(local_state)
                self._save_signature()
                self._save_state(local_state)

                refresh = True
            else:
                print('Loaded from cache: %s' % self._name)

                local_state = self._load_state()

        for analysis in self._next_analyses:
            analysis.run(local_state, refresh)
