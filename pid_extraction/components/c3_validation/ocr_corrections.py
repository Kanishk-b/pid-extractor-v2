import re

COMMON_MISTAKES = {
    '0': 'O', 'O': '0',
    '1': 'I', 'I': '1',
    '8': 'B', 'B': '8',
    '5': 'S', 'S': '5',
    '6': 'G', 'G': '6',
    '2': 'Z', 'Z': '2'
}

def get_correction_candidates(tag: str, pattern: re.Pattern) -> str | None:
    """Attempts single-character substitutions. Returns the first valid correction."""
    chars = list(tag)
    for i, char in enumerate(chars):
        if char in COMMON_MISTAKES:
            original = chars[i]
            chars[i] = COMMON_MISTAKES[original]
            candidate = "".join(chars)
            if pattern.match(candidate):
                return candidate
            chars[i] = original # revert
    return None