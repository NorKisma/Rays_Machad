
import re

def find_missing_translations(po_file_path):
    with open(po_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by entries
    entries = re.split(r'\n\n', content)
    missing = []
    
    for entry in entries:
        msgid_match = re.search(r'msgid "(.*)"', entry)
        msgstr_match = re.search(r'msgstr "(.*)"', entry)
        flags_match = re.search(r'#, fuzzy', entry)
        
        if msgid_match and msgstr_match:
            msgid = msgid_match.group(1)
            msgstr = msgstr_match.group(1)
            if not msgstr or flags_match:
                missing.append(msgid)
    
    return missing

if __name__ == "__main__":
    ar_missing = find_missing_translations('/var/www/RaysTech/rays_machad_mgmt/app/translations/so/LC_MESSAGES/messages.po')
    print(f"Arabic missing: {len(ar_missing)}")
    for m in ar_missing[:50]:
        print(f" - {m}")
