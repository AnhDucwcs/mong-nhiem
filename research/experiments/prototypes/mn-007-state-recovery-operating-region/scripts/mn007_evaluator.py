import json
import sys
from pathlib import Path

def main():
    root = Path(__file__).parent.parent
    run_dir = root / "runs" / "calibration-run-0002"
    raw_path = run_dir / "raw_responses.jsonl"
    
    if not raw_path.exists():
        print("measurement/design blocked: raw_responses.jsonl not found")
        sys.exit(1)
        
    corpus_dir = root / "definition" / "calibration-corpus-v1"
    evaluators = []
    with open(corpus_dir / "evaluator-records.jsonl", "r", encoding="utf-8") as f:
        for line in f:
            evaluators.append(json.loads(line))
            
    # Reload strictly from persisted artifact
    raw_responses = []
    with open(raw_path, "r", encoding="utf-8") as f:
        for line in f:
            raw_responses.append(json.loads(line))
            
    if len(raw_responses) != 108:
        print("measurement/design blocked: persisted evidence does not contain 108 records")
        sys.exit(1)
        
    cells = ["e3-terminal", "e3-leading", "e5-terminal", "e5-leading", "e7-terminal", "e7-leading"]
    results = {c: {"P": 0, "C": 0} for c in cells}
    
    for raw in raw_responses:
        c_id = raw["case_id"]
        cell_name = "-".join(c_id.split("-")[3:5])
        ev = next(x for x in evaluators if x["case_id"] == c_id)
        
        results[cell_name]["P"] += 1
        
        content = raw.get("raw_response")
        score = 0
        if content is not None:
            content = content.strip()
            expected = ",".join(ev["expected_vector"])
            if content == expected:
                score = 1
                
        results[cell_name]["C"] += score
        
    print("Evaluation Results from Persisted Artifact:")
    print(json.dumps(results, indent=2))
    
    for c, stats in results.items():
        C = stats["C"]
        if C >= 17:
            stats["class"] = "ceiling"
        elif 15 <= C <= 16:
            stats["class"] = "usable"
        else:
            stats["class"] = "floor"
            
    print("Classification:")
    print(json.dumps(results, indent=2))
    
    usable = [(k, v) for k, v in results.items() if v["class"] == "usable"]
    if usable:
        print("usable operating region identified")
    else:
        print("no usable operating region in bounded landscape")

if __name__ == "__main__":
    main()
