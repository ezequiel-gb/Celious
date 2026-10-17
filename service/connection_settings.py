"""Pure connection identity resolution shared by startup and diagnostics."""
import re


def tunnel_id(config, profile):
    if 'tunnel_id' in config:
        value = config['tunnel_id']
    else:
        try:
            lines = profile.read_text('utf-8-sig').splitlines()
        except OSError:
            raise ValueError('Tunnel identity missing; review local config and the existing celious profile') from None
        values, section, sections = [], False, 0
        for line in lines:
            if line.strip() and not line.lstrip().startswith('#') and not line[0].isspace():
                section = line == 'control_plane:'
                sections += section
            if section and line.startswith('  tunnel_id:'):
                match = re.fullmatch(r'''  tunnel_id: *(?P<quote>["']?)(tunnel_[a-z0-9]{32})(?P=quote) *''', line)
                if not match:
                    raise ValueError('Invalid tunnel identity in the existing celious profile')
                values.append(match.group(2))
        if sections != 1 or len(values) != 1:
            raise ValueError('Tunnel identity missing or ambiguous; review the existing celious profile')
        value = values[0]
    if not isinstance(value, str) or not re.fullmatch(r'tunnel_[a-z0-9]{32}', value):
        raise ValueError('Invalid tunnel identity in local configuration')
    return value
