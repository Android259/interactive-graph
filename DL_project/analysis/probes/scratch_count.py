# One-off: rebuilds a run's ModelConfig from its test_metrics report and counts how many
# parameters the discovered HardConcrete gate widths would remove from that model.
import sys, os, json, re
sys.path.insert(0, "training")
sys.path.insert(0, ".")
import torch
from read_configuration import ModelConfig
from architecture.interaction_classification import InteractionClassification
from architecture.mlp_utils import HardConcreteGate

metrics = "test_metrics/bbp_nps3mlp_dpt01_gm_mlpplm1lopt/groups_scp2/test_metrics_20260723_225857_3331866parameters_4_8_1_0.0001_16_96.txt"

# ---- parse config section ----
conf = ModelConfig()
discovered = {}
with open(metrics) as f:
    for line in f:
        if line.startswith("total:") or line.startswith("per_protein"):
            pass
        if line.startswith("discovered_widths:"):
            discovered = json.loads(line.split(":",1)[1].strip())
            continue
        m = re.match(r"^([a-zA-Z_][A-Za-z0-9_]*): (.*)$", line.rstrip("\n"))
        if not m: continue
        k, v = m.group(1), m.group(2).strip()
        if not hasattr(conf, k): continue
        cur = getattr(conf, k)
        if v == 'None':
            try: setattr(conf, k, None)
            except AttributeError: pass
            continue
        try:
            if isinstance(cur, bool):
                nv = v not in ("0","False","false")
            elif isinstance(cur, int) and not isinstance(cur, bool):
                nv = int(float(v)) if v not in ("None","") else cur
            elif isinstance(cur, float):
                nv = float(v) if v not in ("None","inf") else cur
            elif isinstance(cur, list):
                nv = json.loads(v) if v.startswith("[") else cur
            elif isinstance(cur, dict):
                nv = json.loads(v) if v.startswith("{") else {}
            else:
                nv = v.strip('"')
        except Exception:
            continue
        try:
            setattr(conf, k, nv)
        except AttributeError:
            pass

conf.mlp_widths = {}   # opt used full widths
model = InteractionClassification(conf)
total = sum(p.numel() for p in model.parameters())
print("total params (full):", total)

# ---- map each gate -> producer/consumer Linear ----
# build parent -> ordered children
from collections import defaultdict
children_of = {}
for name, mod in model.named_modules():
    kids = list(mod.named_children())
    if kids:
        children_of[name] = kids

def find_seq_parent(gate_name):
    parent = gate_name.rsplit(".",1)[0]
    idx = gate_name.rsplit(".",1)[1]
    return parent, idx

saved = 0
matched = 0
rows = []
for gname, g in model.named_modules():
    if not isinstance(g, HardConcreteGate): continue
    parent, gidx = find_seq_parent(gname)
    try: gidx = int(gidx)
    except: continue
    kids = children_of.get(parent, [])
    # index within parent
    lin_before = [(int(i), c) for i,c in kids if i.isdigit() and int(i)<gidx and isinstance(c, torch.nn.Linear)]
    lin_after  = [(int(i), c) for i,c in kids if i.isdigit() and int(i)>gidx and isinstance(c, torch.nn.Linear)]
    if not lin_before: continue
    pidx, prod = max(lin_before, key=lambda t:t[0])
    prod_path = f"{parent}.{pidx}"
    if prod_path not in discovered: 
        continue
    kept = discovered[prod_path]
    Wfull = prod.out_features
    cons = min(lin_after, key=lambda t:t[0])[1] if lin_after else None
    d = (Wfull-kept)*(prod.in_features+1)                 # producer rows+bias
    if cons is not None:
        d += (Wfull-kept)*(cons.out_features)             # consumer cols
    saved += d
    matched += 1
    rows.append((prod_path, Wfull, kept, d, cons.out_features if cons else None))

print(f"matched gates: {matched}/{len(discovered)}")
print(f"{'site':32} {'full':>5} {'kept':>5} {'saved':>8} {'cons_out':>8}")
for r in sorted(rows, key=lambda x:-x[3]):
    print(f"{r[0]:32} {r[1]:5d} {r[2]:5d} {r[3]:8d} {str(r[4]):>8}")
print("total saved:", saved)
print("FINAL params after zeroing:", total - saved)
print(f"reduction: {saved/total*100:.1f}%")
