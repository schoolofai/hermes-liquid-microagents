"""Desk through Hermes with one of the experiments/desk-skills/setups (default D_auto_load). Usage: run_desk_e2e.py SANDBOX SETUP. Only the SOUL and a fixed one-line task are given; no data prepped."""
import os, sys, time, json
from run_agent import AIAgent
sb = os.path.abspath(sys.argv[1]); ap = sys.argv[2]; HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(sb)
SETUPS = os.path.join(HERE, "..", "..", "experiments", "desk-skills", "setups")
TOOLS = {"A_prompt_only": ["file"], "B_skills_scripts": ["file", "terminal", "skills"], "C_custom_tools": ["file", "desk"]}
cfg = (os.path.join(ap, "SOUL.md"), TOOLS.get(ap, ["file", "desk", "skills"]))
if ap not in ("A_prompt_only", "B_skills_scripts"):  # the hermes CLI discovers plugins at startup; do the same for the programmatic agent
    from hermes_cli.plugins import discover_plugins; discover_plugins()
agent = AIAgent(model="LFM3-1.7B", base_url="http://127.0.0.1:8084/v1", api_key="local", enabled_toolsets=cfg[1],
                skip_memory=True, skip_context_files=(ap != "D_auto_load"),  # D_auto_load: auto_load is only honoured when context files are on
                ephemeral_system_prompt=open(os.path.join(SETUPS, cfg[0])).read(),
                max_iterations=40, save_trajectories=True, quiet_mode=True)
print("TOOLS", sorted(t["function"]["name"] for t in (agent.tools or [])), flush=True)
t = time.time(); r = agent.chat("Do all the jobs now. Reply DONE when finished.")
st = {k: getattr(agent, k) for k in dir(agent) if k.startswith("session_") and isinstance(getattr(agent, k), (int, float))}
print(r); print("STATS", json.dumps({"secs": round(time.time() - t), **st}))
