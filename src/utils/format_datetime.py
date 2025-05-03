from datetime import datetime

def is_iso_utc_z_format(date_str):
    if not date_str.endswith('Z'):
        return False
    try:
        dt = datetime.fromisoformat(date_str[:-1] + '+00:00')
        return dt.utcoffset().total_seconds() == 0
    except ValueError:
        return False


def iso_to_simple(iso_str: str):
    """iso8601 to dd.mm.YYYY"""
    if is_iso_utc_z_format(iso_str):
        dt = datetime.strptime(iso_str, "%Y-%m-%dT%H:%M:%SZ")
        return f"{dt.day:02d}.{dt.month:02d}.{dt.year}"
    return None
