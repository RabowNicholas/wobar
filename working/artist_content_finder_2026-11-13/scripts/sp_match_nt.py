# Title normaliser shared with sp_match.py (copied, so sp_match.py stays untouched).
import re
def nt(s):
    s = s.lower(); s = re.sub(r'\((original|extended|radio|vip|clean|dirty)[^)]*\)', '', s)
    s = re.sub(r'\b(original mix|extended mix|feat\.?.*|ft\..*)$', '', s)
    return re.sub(r'[^a-z0-9]+', ' ', s).strip()
