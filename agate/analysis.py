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
    def __init__(self, func):
        self._name = func.__name__
        self._func = func
        self._next_analyses = []

    def _save_archive(self, state):
        path = '%s.pickle' % self._name

        archive = {
            'source': inspect.getsource(self._func),
            'state': state
        }

        with open(path, 'w') as f:
            pickle.dump(archive, f)

    def _load_archive(self):
        path = '%s.pickle' % self._name

        if not os.path.exists(path):
            return None

        with open(path) as f:
            archive = pickle.load(f)

        return archive

    def then(self, next_func):
        analysis = Analysis(next_func)

        self._next_analyses.append(analysis)

        return analysis

    def run(self, state={}, refresh=False):
        local_state = deepcopy(state)

        if refresh:
            self._func(local_state)
            self._save_archive(local_state)
        else:
            archive = self._load_archive()

            if not archive or inspect.getsource(self._func) != archive['source']:
                self._func(local_state)
                self._save_archive(local_state)

                refresh = True
            else:
                local_state = archive['state']

        for analysis in self._next_analyses:
            analysis.run(local_state, refresh)
