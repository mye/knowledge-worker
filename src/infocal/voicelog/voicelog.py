import re
import sqlite3
import time
from datetime import datetime, timedelta, timezone
from typing import Generator, Iterable, Tuple

_HEADER_PATTERN = re.compile(r"^==== Captured on (.+) ====$")
_VOICELOG_PATTERN = re.compile(
    r"\[(\d{2}:\d{2}:\d{2}\.\d{3}) --> (\d{2}:\d{2}:\d{2}\.\d{3})\]\s+(.+)"
)


def voicelog_sqlite(voicelog_lines: Iterable[str], conn: sqlite3.Connection) -> None:
    """Store a voicelog stream in the database."""

    _ensure_tables_exist(conn)
    parsed_lines_gen = _parse_voicelog_lines(voicelog_lines)
    censored_transcripts = _censor_voicelog(parsed_lines_gen)
    for v in censored_transcripts:
        _insert_voicelog(conn, [v])


def _ensure_utc_native(dt):
    if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
        offset = -time.timezone
        if time.localtime().tm_isdst:
            offset += 3600  # Add an hour if DST is in effect
        offset = timedelta(hours=offset // 3600, minutes=(offset % 3600) // 60)
        dt = datetime.now(timezone(offset))
    return dt.astimezone(timezone.utc)


def _str_to_timedelta(time_str: str) -> timedelta:
    """Convert a time string in the format "HH:MM:SS.sss" to a timedelta object.

    Raises:
        ValueError: If the time string is not in the expected format.

    Example:
        >>> str_to_timedelta("00:01:35.568")
        datetime.timedelta(seconds=95, microseconds=568000)

        >>> str_to_timedelta("01:00:00.000")
        datetime.timedelta(seconds=3600)
    """
    try:
        hours, minutes, seconds = map(float, time_str.split(":"))
        return timedelta(hours=hours, minutes=minutes, seconds=seconds)
    except ValueError:
        raise ValueError("Invalid time string format. Expected 'HH:MM:SS.sss'")


def _parse_voicelog_line(line: str) -> Tuple[str, timedelta, timedelta]:
    """Returns content and relative start, end times from a voicelog line.

    Args:
        line (str): A line containing two relative start and end times and text,
        formatted as "[00:00:20.098 --> 00:00:26.818]   text."

    Returns:
        Text content and relative start and end timedelta objects.

    Throws:
        ValueError: If the line is not a valid voicelog line.

    Example:
        >>> parse_voicelog_line("[00:01:35.568 --> 00:02:03.908]   Hello, world!")
        ('Hello, world!',
         datetime.timedelta(seconds=95, microseconds=568000),
         datetime.timedelta(seconds=123, microseconds=908000))
    """
    match = re.match(_VOICELOG_PATTERN, line)

    if not match:
        raise ValueError("Invalid voicelog line format.")

    start, end, text = match.groups()
    return text, _str_to_timedelta(start), _str_to_timedelta(end)


def _parse_header_line(header_line: str) -> datetime:
    """Returns the datetime object from a voicelog header line.

    Throws:
        ValueError: If the line is not a valid voicelog header line.

    Example:
        >>> parse_header_line("==== Captured on Saturday, 26 August 2023, 13:50:48 ====")
        datetime.datetime(2023, 8, 26, 13, 50, 48)
    """
    if match := re.match(_HEADER_PATTERN, header_line):
        return datetime.strptime(match.group(1), "%A, %d %B %Y, %H:%M:%S")
    raise ValueError("Invalid voicelog header line format.")


def _parse_voicelog_lines(
    lines: Iterable[str],
) -> Generator[Tuple[str, datetime, datetime], None, None]:
    """Yields text content and start and end time from voicelog.
    Ignores lines that are not valid voicelog lines.

    Args:
        lines (Iterable[str]): An iterable of voicelog lines.

    Example:
        >>> lines = [
        ...     "==== Captured on Saturday, 26 August 2023, 13:50:48 ====",
        ...     "[00:01:35.568 --> 00:02:03.908]   Hello, world!",
        ...     "[00:02:03.908 --> 00:02:10.368]   This is a test.",
        ... ]
        >>> for entry in voicelog_lines(lines):
        ...     print(entry.end - entry.start, entry.content)
        0:00:28.340000 Hello, world!
        0:00:06.460000 This is a test.
    """
    base_date = datetime.now(timezone.utc)
    for line in lines:
        line = line.strip()
        try:
            match line:
                case _ if _HEADER_PATTERN.match(line):
                    base_date = _ensure_utc_native(_parse_header_line(line))
                case _ if _VOICELOG_PATTERN.match(line):
                    content, start, end = _parse_voicelog_line(line)
                    yield (content, base_date + start, base_date + end)
                case _:
                    continue
        except ValueError:
            continue


def _ensure_tables_exist(conn: sqlite3.Connection) -> None:
    conn.execute(
        """CREATE TABLE IF NOT EXISTS voicelog (
            text TEXT NOT NULL,
            start INTEGER NOT NULL,
            end INTEGER NOT NULL,
            PRIMARY KEY (start, end)
        );"""
    )
    conn.execute(
        """CREATE INDEX IF NOT EXISTS voicelog_start_end_idx
        ON voicelog (start, end);"""
    )


def _insert_voicelog(
    conn: sqlite3.Connection, batch: Iterable[tuple[str, datetime, datetime]]
):
    INSERT_SQL = """INSERT OR IGNORE INTO voicelog (text, start, end)
        VALUES (?, ?, ?);"""
    batch_timestamped = [
        (text, int(start.timestamp()), int(end.timestamp()))
        for text, start, end in batch
    ]
    with conn:
        conn.executemany(INSERT_SQL, batch_timestamped)


def _is_censored(text: str) -> bool:
    """TODO: find a better way to do this."""
    banned_word = text.strip() in {
        "[Silence]",
        "[silence]",
        "[clears throat]",
        "Silence.",
        "*silence*",
        "[cough]",
        "Thank you.",
        "Okay.",
        "[BLANK_AUDIO]",
    }
    short_incomplete = len(text) < 6 and text.endswith("...")
    bracketed = text.startswith("[") and text.endswith("]")
    return banned_word or short_incomplete or bracketed


def _censor_voicelog(voicelog: Iterable[tuple[str, datetime, datetime]]):
    """Yields only uncensored voicelog entries."""
    last_text = ""
    for v in voicelog:
        if not _is_censored(v[0]) and v[0] != last_text:
            last_text = v[0]
            yield v
