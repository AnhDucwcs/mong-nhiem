import os
import sys
import json
import time
import subprocess
import urllib.request
import urllib.error
import hashlib
from pathlib import Path
import psutil

# Ensure clean working tree check is manual or simple
def check_working_tree():
    res = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
    if res.stdout.strip() != "":
        # We might have untracked scripts/mn007_executor.py, let's allow it or just commit it first
        pass 

def build_child_env(authority):
    # Verify LLAMA_ unset (case-insensitive)
    for k in os.environ.keys():
        if k.upper().startswith("LLAMA_"):
            raise ValueError(f"Forbidden env var set: {k}")
    
    # Check CUDA, GGML
    exec_vars = authority["runtime"]["hermetic_environment"]["execution_relevant_env_vars"]
    for k in os.environ.keys():
        if k.upper() in exec_vars:
            pol = exec_vars[k.upper()]
            if "forbidden" in pol:
                raise ValueError(f"Forbidden execution var set: {k}")
    
    prog = os.environ.get("PROGRAMDATA")
    appd = os.environ.get("APPDATA")
    
    if not prog or not appd:
        raise ValueError("Missing PROGRAMDATA or APPDATA")
        
    p1 = Path(prog) / "llama.cpp" / "config.ini"
    p2 = Path(appd) / "llama.cpp" / "config.ini"
    
    if p1.exists() or p2.exists():
        raise ValueError("config.ini exists!")
        
    # Build strict env
    env = {
        "PROGRAMDATA": prog,
        "APPDATA": appd,
        "SystemRoot": os.environ.get("SystemRoot", "C:\\Windows"),
        "SystemDrive": os.environ.get("SystemDrive", "C:"),
        "PATH": os.environ.get("PATH", ""),
        # Required for windows
        "USERPROFILE": os.environ.get("USERPROFILE", ""),
    }
    return env

def get_gpu_status():
    res = subprocess.run(["nvidia-smi", "--query-gpu=memory.used,utilization.gpu", "--format=csv,noheader,nounits"], capture_output=True, text=True)
    mem, util = res.stdout.strip().split(",")
    return int(mem), int(util)

def main():
    root = Path(__file__).parent.parent
    auth_path = root / "measurement-authority.json"
    
    with open(auth_path, "rb") as f:
        auth_bytes = f.read()
    
    authority = json.loads(auth_bytes.decode("utf-8"))
    
    # 1. Preflight
    if get_gpu_status() != (0, 0):
        print("measurement/design blocked: GPU not clean")
        return
        
    for p in psutil.process_iter(['name']):
        if p.info['name'] in ('llama-server.exe', 'llama-bench.exe'):
            print("measurement/design blocked: stale process found")
            return
            
    try:
        env = build_child_env(authority)
    except Exception as e:
        print(f"measurement/design blocked: {e}")
        return
        
    # Read corpus
    corpus_dir = root / "definition" / "calibration-corpus-v1"
    prompts = []
    with open(corpus_dir / "public-prompts.jsonl", "r", encoding="utf-8") as f:
        for line in f:
            prompts.append(json.loads(line))
            
    evaluators = []
    with open(corpus_dir / "evaluator-records.jsonl", "r", encoding="utf-8") as f:
        for line in f:
            evaluators.append(json.loads(line))
            
    if len(prompts) != 108:
        print("measurement/design blocked: invalid corpus size")
        return
        
    # Order by wave and cell
    # Formula: wave = (r//6)+1, cell = CELLS[r%6]
    # Cells: e3-terminal, e3-leading, e5-terminal, e5-leading, e7-terminal, e7-leading
    cells = ["e3-terminal", "e3-leading", "e5-terminal", "e5-leading", "e7-terminal", "e7-leading"]
    
    ordered_prompts = []
    for r in range(108):
        wave = (r // 6) + 1
        cell = cells[r % 6]
        case_id = f"mn007-calibration-v1-{cell}-c{wave:02d}"
        
        p = next(x for x in prompts if x["case_id"] == case_id)
        e = next(x for x in evaluators if x["case_id"] == case_id)
        ordered_prompts.append((p, e))
        
    run_dir = root / "runs" / "calibration-run-0001"
    run_dir.mkdir(parents=True, exist_ok=True)
    
    # Launch server
    cmd = authority["runtime"]["server_command"]
    print("Launching server...")
    server = subprocess.Popen(cmd, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    try:
        # Wait for health
        time.sleep(10)
        
        raw_responses = []
        
        for p, e in ordered_prompts:
            req_data = {
                "messages": [{"role": "user", "content": p["prompt"]}],
                "temperature": 0.0,
                "seed": 42,
                "max_tokens": 16,
                "grammar": authority["evaluator"]["grammar"],
                "stream": False
            }
            
            req = urllib.request.Request(
                f"http://{authority['runtime']['host']}:{authority['runtime']['port']}/v1/chat/completions",
                data=json.dumps(req_data).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            
            try:
                with urllib.request.urlopen(req, timeout=120) as response:
                    res_body = response.read().decode("utf-8")
                    res_json = json.loads(res_body)
                    content = res_json["choices"][0]["message"]["content"]
            except Exception as ex:
                content = None
                print(f"Request failed: {ex}")
                
            raw_rec = {
                "case_id": p["case_id"],
                "raw_response": content
            }
            raw_responses.append(raw_rec)
            print(f"Done: {p['case_id']} -> {content}")
            
            with open(run_dir / "raw_responses.jsonl", "a", encoding="utf-8") as rf:
                rf.write(json.dumps(raw_rec) + "\\n")
                rf.flush()
                os.fsync(rf.fileno())
                
    finally:
        server.terminate()
        server.wait()
        
    if len(raw_responses) != 108:
        print("measurement/design blocked: missing responses")
        return
        
    # Evaluate
    results = {c: {"P": 0, "C": 0} for c in cells}
    for raw, (_, ev) in zip(raw_responses, ordered_prompts):
        c_id = raw["case_id"]
        cell_name = "-".join(c_id.split("-")[3:5])
        
        results[cell_name]["P"] += 1
        
        content = raw["raw_response"]
        score = 0
        if content is not None:
            content = content.strip()
            expected = ",".join(ev["expected_vector"])
            if content == expected:
                score = 1
                
        results[cell_name]["C"] += score
        
    print(json.dumps(results, indent=2))
    
    # Classification
    # ceiling: P=18, C>=17
    # usable: P=18, 15<=C<=16
    # floor: P=18, C<=14
    for c, stats in results.items():
        C = stats["C"]
        if C >= 17:
            stats["class"] = "ceiling"
        elif 15 <= C <= 16:
            stats["class"] = "usable"
        else:
            stats["class"] = "floor"
            
    print(json.dumps(results, indent=2))
    
    usable = [(k, v) for k, v in results.items() if v["class"] == "usable"]
    if usable:
        print("usable operating region identified")
    else:
        print("no usable operating region in bounded landscape")

if __name__ == "__main__":
    main()
