import json

path = r'C:\Users\Himanshu Raj\.gemini\antigravity-ide\brain\afa70e2a-e4fb-471e-85ea-1c5e0689d0c2\.system_generated\logs\transcript.jsonl'
with open(path, 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        if 'ADMIN001' in line and ('render' in line.lower() or 'production' in line.lower() or '401' in line):
            try:
                obj = json.loads(line)
                step = obj.get("step_index")
                typ = obj.get("type")
                content = str(obj.get("content", ""))
                thinking = str(obj.get("thinking", ""))
                print(f"--- Line {i} Step {step} Type {typ} ---")
                if content:
                    print("CONTENT:", content[:500])
                if thinking:
                    print("THINKING:", thinking[:500])
            except Exception as e:
                pass
