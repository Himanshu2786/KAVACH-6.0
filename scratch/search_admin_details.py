import json

path = r'C:\Users\Himanshu Raj\.gemini\antigravity-ide\brain\afa70e2a-e4fb-471e-85ea-1c5e0689d0c2\.system_generated\logs\transcript.jsonl'
with open(path, 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        if 1630 <= i <= 1682:
            try:
                obj = json.loads(line)
                step = obj.get("step_index")
                typ = obj.get("type")
                thinking = str(obj.get("thinking", ""))
                content = str(obj.get("content", ""))
                if "ADMIN001" in thinking or "ADMIN001" in content:
                    print(f"--- Line {i} Step {step} ---")
                    if thinking:
                        print("THINKING:", thinking[:400])
                    if content:
                        print("CONTENT:", content[:400])
            except Exception:
                pass
