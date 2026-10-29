"""Desk through Hermes, approach A/B/C. Only the SOUL and a fixed one-line task are given; no data prepped."""
import os, sys, time, json
from run_agent import AIAgent
sb = os.path.abspath(sys.argv[1]); ap = sys.argv[2]; HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(sb)
cfg = {"A": ("A/SOUL.md", ["file"]), "B": ("hh_B/SOUL.md", ["file", "terminal", "skills"]), "C": ("hh_C/SOUL.md", ["file", "desk"]), "D": ("hh_D/SOUL.md", ["file", "desk", "skills"]), "Dg": ("hh_Dg/SOUL.md", ["file", "desk", "skills"]), "Da": ("hh_Da/SOUL.md", ["file", "desk", "skills"]), "Dt": ("hh_Dt/SOUL.md", ["file", "desk", "skills"]), "Ds": ("hh_Ds/SOUL.md", ["file", "desk", "skills"]), "Dts": ("hh_Dts/SOUL.md", ["file", "desk", "skills"])}[ap]
if ap in ("C", "D", "Dg", "Da", "Dt", "Ds", "Dts"):  # the hermes CLI discovers plugins at startup; do the same for the programmatic agent
    from hermes_cli.plugins import discover_plugins; discover_plugins()
agent = AIAgent(model="LFM3-1.7B", base_url="http://127.0.0.1:8094/v1", api_key="local", enabled_toolsets=cfg[1],
                skip_memory=True, skip_context_files=(ap != "Da"),  # Da: auto_load is only honoured when context files are on
                ephemeral_system_prompt=open(os.path.join(HERE, cfg[0])).read(),
                max_iterations=40, save_trajectories=True, quiet_mode=True)
print("TOOLS", sorted(t["function"]["name"] for t in (agent.tools or [])), flush=True)
t = time.time(); r = agent.chat("Do all the jobs now. Reply DONE when finished.")
st = {k: getattr(agent, k) for k in dir(agent) if k.startswith("session_") and isinstance(getattr(agent, k), (int, float))}
print(r); print("STATS", json.dumps({"secs": round(time.time() - t), **st}))
