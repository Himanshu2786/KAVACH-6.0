import os
import re
from pathlib import Path

root = Path(r"c:\Users\Himanshu Raj\OneDrive\Desktop\KHAALI KAVACH\KAVACH 6.0")

docs_to_check = [
    root / "README.md",
    root / "CHALLENGES_TO_SOLUTIONS.md",
    root / "KAVACH_DEVELOPER_DOCUMENTATION.md",
    root / "KAVACH_BACKEND_ARCHITECTURE.md",
    root / "KAVACH_DEPENDENCIES.md",
    root / "KAVACH_FILE_STRUCTURE.md",
    root / "KAVACH_KNOWLEDGE_ENGINE.md",
    root / "KAVACH_MASTER_CONTEXT.md",
    root / "KAVACH_MODULES.md",
    root / "KAVACH_OLLAMA_INTEGRATION.md",
    root / "KAVACH_RAG_ARCHITECTURE.md",
    root / "INFO" / "FINAL_WORKING_STATUS.md",
    root / "INFO" / "LIMITATIONS.md",
    root / "INFO" / "PS_26163_COMPLIANCE.md",
    root / "INFO" / "UI_CHANGELOG.md",
    root / "INFO" / "FEATURE_FILE_MAP.md",
    root / "INFO" / "ASSESSMENT_FLOW.md",
    root / "INFO" / "KAVACH_WORLD_MONITOR.md",
    root / "INFO" / "EVIDENCE_SYSTEM.md",
    root / "INFO" / "AI_SYSTEM.md",
]

prohibited_patterns = [
    (r"\bKAVACH 6\.0\b", "KAVACH 6.0 reference"),
    (r"\b100% secure\b", "100% secure claim"),
    (r"\bfully secure\b", "fully secure claim"),
    (r"5\.92\s*/\s*100", "5.92/100 scale error"),
]

issues = []

for doc in docs_to_check:
    if not doc.exists():
        issues.append(f"Missing doc: {doc}")
        continue
    content = doc.read_text(encoding="utf-8", errors="ignore")
    for pattern, desc in prohibited_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        # Exclude instances where it says "Zero references to KAVACH 6.0" or "Do NOT create KAVACH 6.0"
        if matches:
            for line_no, line in enumerate(content.splitlines(), start=1):
                if re.search(pattern, line, re.IGNORECASE):
                    if "zero references" in line.lower() or "do not create" in line.lower() or "no references" in line.lower():
                        continue
                    issues.append(f"{doc.name}:{line_no} - Found prohibited pattern: {desc} -> {line.strip()}")

print(f"Total checked files: {len(docs_to_check)}")
if issues:
    print(f"Found {len(issues)} issues:")
    for issue in issues:
        print("  -", issue)
else:
    print("[SUCCESS] Zero prohibited patterns found across maintained documentation!")
