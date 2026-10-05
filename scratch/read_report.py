import json

path = r'C:\Users\Himanshu Raj\.gemini\antigravity-ide\brain\afa70e2a-e4fb-471e-85ea-1c5e0689d0c2\.system_generated\logs\transcript.jsonl'
with open(path, 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        if i >= 1830:
            obj = json.loads(line)
            print(f"=== Line {i} Step {obj.get('step_index')} ===")
            print(obj.get('content', ''))
