import json

path = r'C:\Users\Himanshu Raj\.gemini\antigravity-ide\brain\afa70e2a-e4fb-471e-85ea-1c5e0689d0c2\.system_generated\logs\transcript.jsonl'
with open(path, 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        if 'AUD-40dc60c19398' in line or 'test-asm' in line:
            try:
                obj = json.loads(line)
                step = obj.get("step_index")
                typ = obj.get("type")
                tool_calls = obj.get("tool_calls")
                content = str(obj.get("content", ""))
                thinking = str(obj.get("thinking", ""))
                print(f"--- Line {i} Step {step} Type {typ} ---")
                if content:
                    print("CONTENT:", content[:400])
                if thinking:
                    print("THINKING:", thinking[:400])
                if tool_calls:
                    print("TOOL CALLS:", tool_calls)
            except Exception as e:
                print("Error parsing line", i, e)
