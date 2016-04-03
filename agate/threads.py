#!/usr/bin/env python

from concurrent import futures

from agate.configure import options


def threadify(func, data, *args, **kwargs):
    """
    Executes data processing across multiple threads.

    :code:`args` and :code:`kwargs` will be passed through to the data
    processing function.

    :param func:
        A function to be applied to each data item.
    :param data:
        A sequence of data to be chunked across multiple threads.
    """
    results = []

    if options['use_threads'] and options['thread_count'] > 1:
        len_data = len(data)
        chunk_size = len_data // options['thread_count'] + 1

        if chunk_size < options['min_thread_size']:
            chunk_size = options['min_thread_size']

        chunks = []
        i = 0

        while i < len_data:
            chunks.append(data[i:i + chunk_size])

            i += chunk_size

        if len(chunks) > 1:
            with futures.ThreadPoolExecutor(max_workers=options['thread_count']) as pool:
                threads = []

                for chunk in chunks:
                    threads.append(pool.submit(func, chunk, *args, **kwargs))

                futures.wait(threads, return_when=futures.FIRST_EXCEPTION)

                for thread in threads:
                    if thread.exception():
                        raise thread.exception()

                    results.extend(thread.result())
        else:
            results = func(data, *args, **kwargs)
    else:
        results = func(data, *args, **kwargs)

    return results
