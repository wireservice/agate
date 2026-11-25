import json
import os
import subprocess
import sys
from io import StringIO

import pytest

import agate


@pytest.mark.parametrize('newline', [False, True])
def test_json_path_round_trip_with_a_non_utf8_default(tmp_path, newline):
    path = tmp_path / 'unicode.json'
    script = r"""
import sys
import agate
text = 'caf\u00e9 \u4e2d\u6587 \U0001f984'
table = agate.Table([[text]], ['text'], [agate.Text()])
table.to_json(sys.argv[1], newline=sys.argv[2] == 'True')
"""
    env = dict(os.environ, PYTHONUTF8='0', PYTHONCOERCECLOCALE='0', LC_ALL='C')
    completed = subprocess.run([sys.executable, '-X', 'utf8=0', '-c', script, str(path), str(newline)],
                               env=env, capture_output=True, text=True)
    assert completed.returncode == 0, completed.stderr
    result = agate.Table.from_json(path, newline=newline)
    assert result.rows[0]['text'] == 'café 中文 🦄'
    decoded = json.loads(path.read_text(encoding='utf-8'))
    assert (decoded if newline else decoded[0])['text'] == result.rows[0]['text']


def test_json_file_like_output_keeps_unicode():
    stream = StringIO()
    table = agate.Table([['café']], ['text'], [agate.Text()])
    table.to_json(stream)
    assert not stream.closed
    assert json.loads(stream.getvalue()) == [{'text': 'café'}]
