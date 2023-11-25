"""
Test that parse_header updates the timestamp correction factor correctly.
Test that parse_timestamp returns a corrected timestamp.
Test that parsed_lines only yields valid timestamped lines.
Test that _update_base_time correctly modifies base_time.
Test that _parse_timestamp uses base_time for correct timestamp adjustment.
Test that parsed_lines yields only valid, timestamp-adjusted lines.


Verify that the function raises a ValueError when passed an invalid voicelog line.
Verify that the timedelta objects for start and end times are non-negative and that the end time is greater than or equal to the start time.
Confirm that the text content returned by the function matches the text in the original line.
Test with edge cases such as the minimum and maximum possible time values to ensure the function handles them correctly.

"""

import sqlite3

import pytest

from infocal import voicelog_sqlite


@pytest.fixture
def voicelog_whisper_medium():
    with open("tests/voicelog/fixtures/voicelog_whisper_medium.txt", "r") as f:
        return f.readlines()


@pytest.fixture
def in_memory_conn():
    conn = sqlite3.connect(":memory:")
    yield conn
    conn.close()


def test_voicelog_sink(voicelog_whisper_medium, in_memory_conn):
    voicelog_sqlite(voicelog_whisper_medium, in_memory_conn)
    num_expected_entries = 23
    num_actual_entries = in_memory_conn.execute(
        "SELECT COUNT(*) FROM voicelog;"
    ).fetchone()[0]
    all_text = in_memory_conn.execute("SELECT text FROM voicelog;").fetchall()
    print(all_text)
    assert num_actual_entries == num_expected_entries
