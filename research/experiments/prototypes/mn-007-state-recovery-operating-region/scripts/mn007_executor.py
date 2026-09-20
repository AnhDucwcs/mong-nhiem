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
from datetime import datetime, timezone

def check_working_tree():
    res = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
    if res.stdout.strip() != "":
        print("measurement/design blocked: Working tree is dirty. Clean rerun requires a clean git state.")
        sys.exit(1)
    
    res_hash = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True)
    return res_hash.stdout.strip()

def build_child_env(authority):
    for k in os.environ.keys():
        if k.upper().startswith("LLAMA_"):
            raise ValueError(f"Forbidden env var set: {k}")
    
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
        
    env = {
        "PROGRAMDATA": prog,
        "APPDATA": appd,
        "SystemRoot": os.environ.get("SystemRoot", "C:\\Windows"),
        "SystemDrive": os.environ.get("SystemDrive", "C:"),
        "PATH": os.environ.get("PATH", ""),
        "USERPROFILE": os.environ.get("USERPROFILE", ""),
    }
    return env

def get_gpu_status():
    res = subprocess.run(["nvidia-smi", "--query-gpu=memory.used,utilization.gpu", "--format=csv,noheader,nounits"], capture_output=True, text=True)
    mem, util = res.stdout.strip().split(",")
    return int(mem), int(util)

def main():
    git_head = check_working_tree()
    
    root = Path(__file__).parent.parent
    auth_path = root / "measurement-authority.json"
    
    with open(auth_path, "rb") as f:
        auth_bytes = f.read()
    authority = json.loads(auth_bytes.decode("utf-8"))
    
    if get_gpu_status() != (0, 0):
        print("measurement/design blocked: GPU not clean")
        sys.exit(1)
        
    for p in psutil.process_iter(['name']):
        if p.info['name'] in ('llama-server.exe', 'llama-bench.exe'):
            print("measurement/design blocked: stale process found")
            sys.exit(1)
            
    try:
        env = build_child_env(authority)
    except Exception as e:
        print(f"measurement/design blocked: {e}")
        sys.exit(1)
        
    corpus_dir = root / "definition" / "calibration-corpus-v1"
    prompts = []
    with open(corpus_dir / "public-prompts.jsonl", "r", encoding="utf-8") as f:
        for line in f:
            prompts.append(json.loads(line))
            
    if len(prompts) != 108:
        print("measurement/design blocked: invalid corpus size")
        sys.exit(1)
        
    cells = ["e3-terminal", "e3-leading", "e5-terminal", "e5-leading", "e7-terminal", "e7-leading"]
    
    ordered_prompts = []
    for r in range(108):
        wave = (r // 6) + 1
        cell = cells[r % 6]
        case_id = f"mn007-calibration-v1-{cell}-c{wave:02d}"
        p = next(x for x in prompts if x["case_id"] == case_id)
        ordered_prompts.append(p)
        
    run_dir = root / "runs" / "calibration-run-0002"
    if run_dir.exists():
        print("measurement/design blocked: calibration-run-0002 already exists")
        sys.exit(1)
    run_dir.mkdir(parents=True)
    
    metadata = {
        "git_head": git_head,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "authority_sha256": hashlib.sha256(auth_bytes).hexdigest(),
        "request_count": 108
    }
    with open(run_dir / "run_metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    
    cmd = authority["runtime"]["server_command"]
    print("Launching server...")
    server = subprocess.Popen(cmd, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    raw_path = run_dir / "raw_responses.jsonl"
    actual_requests = 0
    try:
        time.sleep(10)
        for p in ordered_prompts:
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
            
            with open(raw_path, "a", encoding="utf-8") as rf:
                rf.write(json.dumps(raw_rec) + "\n")
                rf.flush()
                os.fsync(rf.fileno())
            
            actual_requests += 1
            print(f"Persisted: {p['case_id']}")
                
    finally:
        server.terminate()
        server.wait()
        
    if actual_requests != 108:
        print(f"measurement/design blocked: incomplete execution ({actual_requests}/108)")
        sys.exit(1)
        
    print(f"Execution complete. Evidence persisted to {raw_path}.")
    print("Run `python scripts/mn007_evaluator.py` to evaluate the persisted artifact.")

if __name__ == "__main__":
    main()
