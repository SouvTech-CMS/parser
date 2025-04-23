from datetime import datetime

def is_iso_utc_z_format(date_str):
    if not date_str.endswith('Z'):
        return False
    try:
        dt = datetime.fromisoformat(date_str[:-1] + '+00:00')
        return dt.utcoffset().total_seconds() == 0
    except ValueError:
        return False
