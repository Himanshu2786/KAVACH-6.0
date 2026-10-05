import os, re
frontend_dir = r'c:\Users\Himanshu Raj\OneDrive\Desktop\KHAALI KAVACH\KAVACH 6.0\frontend'
for root, dirs, files in os.walk(frontend_dir):
    if 'node_modules' in root or '.git' in root or 'dist' in root:
        continue
    for f in files:
        path = os.path.join(root, f)
        try:
            with open(path, 'r', encoding='utf-8') as fp:
                for idx, line in enumerate(fp, 1):
                    if re.search(r'overview', line, re.IGNORECASE):
                        rel = os.path.relpath(path, frontend_dir)
                        clean = line.strip().encode('ascii', 'replace').decode('ascii')
                        print(f'{rel}:{idx}: {clean}')
        except Exception:
            pass
