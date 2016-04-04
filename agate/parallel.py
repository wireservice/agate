#!/usr/bin/env python

from concurrent import futures

from agate.configure import options


def parallelize(func, data, *args, **kwargs):
    """
    Executes data processing across multiple threads or processes.

    :code:`args` and :code:`kwargs` will be passed through to the data
    processing function.

    :param func:
        A function to be applied to each data item.
    :param data:
        A sequence of data to be chunked across multiple workers.
    """
    results = []

    if not options['parallel_executor'] or options['parallel_workers'] <= 1:
        return func(data, *args, **kwargs)

    len_data = len(data)
    chunk_size = len_data // options['parallel_workers'] + 1

    if chunk_size < options['parallel_min_size']:
        chunk_size = options['parallel_min_size']

    chunks = []
    i = 0

    while i < len_data:
        chunks.append(data[i:i + chunk_size])

        i += chunk_size

    if len(chunks) <= 1:
        return func(data, *args, **kwargs)

    with options['parallel_executor'](max_workers=options['parallel_workers']) as pool:
        threads = []

        for chunk in chunks:
            threads.append(pool.submit(func, chunk, *args, **kwargs))

        futures.wait(threads, return_when=futures.FIRST_EXCEPTION)

        for thread in threads:
            if thread.exception():
                raise thread.exception()

            results.extend(thread.result())

    return results
