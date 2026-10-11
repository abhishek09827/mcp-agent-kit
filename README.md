[mcp-agent-kit — developer screencast.html](https://github.com/user-attachments/files/33306334/mcp-agent-kit.developer.screencast.html)# mcp-agent-kit

`mcp-agent-kit` is an enterprise-grade scaffolding kit and runtime foundation that enables developers to build, validate, and ship a fully compliant, production-ready Model Context Protocol (MCP) server with Agent-to-Agent (A2A) protocol support and portable Agent Skill (`SKILL.md`) packaging in under 30 minutes. Built entirely with the Python standard library for zero runtime dependencies in the protocol core, it enforces strict stateless MCP specification compliance (version 2026-07-28), deterministic resource listing, schema design validation, dual-era negotiation, and automated tool-to-skill card mapping.

---
[Uploading mcp<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>mcp-agent-kit — screencast</title>
<style>
:root{--bg:#080A12;--sf:#111522;--ln:#252B3F;--tx:#F3F5FC;--t2:#A1A9BC;--cy:#72F5E5;--vi:#A78BFA;--am:#FFBE76;color-scheme:dark;box-sizing:border-box;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}
html,body{height:100%;margin:0;background:#030409;color:var(--tx);font:16px system-ui,sans-serif;overflow:hidden}
#wrap{position:relative;width:min(100vw,177.78vh);aspect-ratio:16/9;margin:0 auto;top:50%;transform:translateY(-50%);background:radial-gradient(120% 90% at 70% 0%,#10172c,#06080F 60%);overflow:hidden;container-type:inline-size}
#ide{position:absolute;inset:5% 5% 9%;display:grid;grid-template-columns:19% 1fr;grid-template-rows:5% 1fr;background:var(--bg);border:1px solid var(--ln);border-radius:.8cqw;box-shadow:0 3cqw 8cqw rgba(0,0,0,.6),0 0 0 1px rgba(114,245,229,.05);overflow:hidden;font:1.3cqw/1.65 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;will-change:transform}
#bar{grid-column:1/3;display:flex;align-items:center;gap:.6cqw;padding:0 1.2cqw;background:var(--sf);border-bottom:1px solid var(--ln);color:var(--t2);font-size:1.05cqw}
#bar i{width:.9cqw;height:.9cqw;border-radius:50%;background:#2a3350}#bar span{margin:0 auto}
#side{background:#0b0e1a;border-right:1px solid var(--ln);padding:1cqw 0;color:var(--t2);overflow:hidden;font-size:1.15cqw}
#side div{padding:.1cqw 1cqw;white-space:nowrap;opacity:0}#side div.on{opacity:1}#side div.act{background:#1a2140;color:var(--tx);box-shadow:inset .2cqw 0 var(--cy)}
#main{display:grid;grid-template-rows:60% 40%;min-height:0}
#ed{position:relative;border-bottom:1px solid var(--ln);overflow:hidden;min-height:0}
#tab{height:2.6cqw;display:flex;align-items:center;padding:0 1cqw;background:var(--sf);border-bottom:1px solid var(--ln);font-size:1.1cqw;color:var(--tx)}
#code{padding:.8cqw 0;overflow:hidden;white-space:pre}
.l{display:flex;min-height:1.65em}.l b{flex:0 0 3.2cqw;text-align:right;padding-right:1.2cqw;color:#3d4766;font-weight:400}.l.n{background:rgba(114,245,229,.06)}
#term{background:#070910;padding:.8cqw 1.2cqw;display:flex;flex-direction:column;justify-content:flex-end;overflow:hidden;white-space:pre-wrap;min-height:0;font-size:1.25cqw}
.k{color:var(--vi)}.s{color:var(--cy)}.c{color:#5d6786}.nm{color:var(--am)}.f{color:#8fb9ff}.ok{color:var(--cy)}.pr{color:var(--am)}.dim{color:var(--t2)}
.cur{display:inline-block;width:.6em;height:1.1em;background:var(--cy);vertical-align:text-bottom;opacity:.85}
#lt{position:absolute;left:5%;bottom:3.2%;font:600 1.8cqw system-ui;letter-spacing:-.01em;opacity:0;transition:opacity .5s;pointer-events:none}
#lt::before{content:"";display:inline-block;width:.8cqw;height:.8cqw;background:var(--cy);margin-right:1cqw;border-radius:50%}
#end{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;background:#06080F;opacity:0;pointer-events:none;text-align:center;transition:opacity 1s}
#end svg{width:11cqw;filter:drop-shadow(0 0 2cqw rgba(114,245,229,.35))}
#end h2{margin:1.6cqw 0 .4cqw;font-size:5cqw;letter-spacing:-.04em}#end p{margin:0;color:var(--t2);font-size:2cqw}
#end code{margin-top:2.6cqw;color:var(--cy);font:1.8cqw ui-monospace,monospace;border:1px solid var(--ln);padding:.8cqw 1.6cqw;border-radius:.4cqw}
#ui{position:absolute;left:0;right:0;bottom:0;display:flex;gap:10px;align-items:center;padding:8px 12px;background:linear-gradient(transparent,rgba(0,0,0,.75));z-index:5}
#ui button{background:none;border:1px solid #3a4260;color:var(--tx);border-radius:4px;padding:6px 12px;cursor:pointer;font:inherit;font-size:14px}
#ui button:focus-visible,#ui input:focus-visible{outline:2px solid var(--cy);outline-offset:2px}
#ui input{flex:1;accent-color:#72F5E5}#tm{font:13px ui-monospace,monospace;color:var(--t2);min-width:5.5em;text-align:right}
</style></head><body>
<div id="wrap" role="region" aria-label="mcp-agent-kit screencast, about 37 seconds, silent. A developer scaffolds an agent, validates it, adds a tool, and validates again.">
<div id="ide" aria-hidden="true"><div id="bar"><i></i><i></i><i></i><span>my_agent — mcp-agent-kit</span></div><div id="side"></div>
<div id="main"><div id="ed"><div id="tab"></div><div id="code"></div></div><div id="term"></div></div></div>
<div id="lt"></div>
<div id="end"><svg viewBox="0 0 200 200" aria-hidden="true"><path d="M100 20l66 38v84l-66 38-66-38V58z" fill="rgba(114,245,229,.06)" stroke="#72F5E5" stroke-width="3"/><path d="M100 20v160M34 58l132 84M166 58L34 142" stroke="#A78BFA" stroke-width="1.6"/><circle cx="100" cy="100" r="13" fill="#FFBE76"/></svg><h2>mcp-agent-kit</h2><p>Build the server. Ship the agent.</p><code>github.com/abhishek09827/mcp-agent-kit</code></div>
<div id="ui"><button id="pp">Pause</button><button id="rp">Replay</button><input id="sc" type="range" min="0" max="370" value="0" aria-label="Timeline"><span id="tm">0.0 / 37.0s</span></div>
</div>
<script>
(function(){
var T=37;function cl(x){return Math.max(0,Math.min(1,x))}function sm(x){return x*x*(3-2*x)}
function esc(s){return s.replace(/&/g,'&amp;').replace(/</g,'&lt;')}
function hl(s){return esc(s).replace(/(#.*$)|("[^"]*")|\b(def|from|import|as|return|True|False|None)\b|\b(\d+)\b|\b([A-Za-z_]\w*)(?=\()/g,function(m,c,st,kw,n,f){return c?'<span class="c">'+c+'</span>':st?'<span class="s">'+st+'</span>':kw?'<span class="k">'+kw+'</span>':n?'<span class="nm">'+n+'</span>':'<span class="f">'+f+'</span>'})}
/* terminal script (outputs are real captured output of the repo's CLI and validate.py) */
var TM=[];function cmd(at,p,t,cps){TM.push({k:'c',at:at,p:p,t:t,cps:cps})}function out(at,t,c){TM.push({k:'o',at:at,t:t,c:c||''})}
var DEV='~/dev $ ',AG='my_agent $ ',VAL=['✓ MCP server/discover responds correctly','✓ tools/list is deterministically ordered','✓ all tool schemas pass design rules','✓ A2A agent.json is valid','✓ SKILL.md portable core is valid','✓ dual-era client probe works against local server'];
cmd(.6,DEV,'python -m mcp_agent_kit my_agent --desc "Use when computing text statistics. Do not use for editing documents."',34);
out(4.2,"Scaffolding MCP agent 'my_agent' into 'my_agent'...",'dim');out(4.7,"✓ Agent 'my_agent' successfully created in 'my_agent'.",'ok');out(5.1,'Next steps:','dim');out(5.25,'  cd my_agent','dim');out(5.4,'  python validate.py','dim');
cmd(8.9,DEV,'cd my_agent',14);cmd(10.1,AG,'python validate.py',16);VAL.forEach(function(v,i){out(11.6+i*.4,v,'ok')});
cmd(28.3,AG,'python validate.py',16);VAL.forEach(function(v,i){out(29.8+i*.35,v,'ok')});
/* tree */
var TR=[[6.4,0,'my_agent/'],[6.6,1,'SKILL.md'],[6.75,1,'README.md'],[6.9,1,'server.py'],[7.05,1,'validate.py'],[7.2,1,'client_test.py'],[7.35,1,'a2a/'],[7.5,2,'agent.json'],[7.65,2,'server.py'],[7.8,1,'tools/'],[7.95,2,'__init__.py'],[8.1,2,'example.py'],[16.2,2,'word_count.py']];
/* editor files */
var F={};function stat(file,at,txt){F[file]=F[file]||[];txt.split('\n').forEach(function(l){F[file].push({t:l,at:at,d:0})})}
function typ(file,start,cps,txt){F[file]=F[file]||[];var n=0;txt.split('\n').forEach(function(l){F[file].push({t:l,at:start+n/cps,d:Math.max(.05,l.length/cps),n:1});n+=l.length+1})}
stat('tools/example.py',14,'TOOL_DEFINITION = {\n    "name": "calculate_metrics",\n    "description": "Use when analyzing numerical series or computing aggregate metrics. Do not use for unstructured text parsing.",\n    "inputSchema": {\n        "type": "object",\n        "properties": {\n            "metric_type": {"type": "string", "enum": ["mean", "sum", "max", "min"]},\n            "values": {"type": "array", "items": {"type": "number"}},\n        },\n        "required": ["values"],\n    },\n    "annotations": {"readOnlyHint": True, "destructiveHint": False},\n    "handler": calculate_metrics,\n}');
typ('tools/word_count.py',16.6,120,'from typing import Any, Dict\n\n\ndef word_count(arguments: Dict[str, Any]) -> Dict[str, Any]:\n    text = arguments.get("text", "")\n    return {"words": len(text.split())}\n\n\nTOOL_DEFINITION = {\n    "name": "word_count",\n    "description": "Use when counting words in a piece of text. Do not use for editing or rewriting text.",\n    "inputSchema": {\n        "type": "object",\n        "properties": {"text": {"type": "string", "description": "Text to count words in"}},\n        "required": ["text"],\n    },\n    "annotations": {"readOnlyHint": True, "destructiveHint": False},\n    "handler": word_count,\n}');
stat('server.py',22.6,'from tools.example import TOOL_DEFINITION');typ('server.py',23,70,'from tools.word_count import TOOL_DEFINITION as WORD_COUNT');
stat('server.py',22.6,'\n\ndef create_server(legacy_mode: bool = False) -> MCPServer:\n    # ⋯ MCPServer setup and example tool registration');
typ('server.py',24.4,150,'    srv.tools.register(\n        name=WORD_COUNT["name"],\n        description=WORD_COUNT["description"],\n        input_schema=WORD_COUNT["inputSchema"],\n        annotations=WORD_COUNT["annotations"],\n        handler=WORD_COUNT["handler"],\n    )');
stat('server.py',22.6,'\n    return srv');
var SCH=[[14,'tools/example.py'],[16.2,'tools/word_count.py'],[22.6,'server.py']];
/* captions and camera */
var LT=[[.6,6.2,'Scaffold an agent with one command'],[8.9,14,'Validate the generated project'],[14.2,28,'Add your own tool, register it in server.py'],[28.3,32.8,'Validate again']];
var CAM=[[0,1,50,50],[.3,1.55,50,100],[6,1.55,50,100],[6.6,1.5,0,35],[8.6,1.55,50,100],[13.8,1.5,70,0],[22.4,1.5,60,18],[28,1.55,50,100],[32.6,1,50,50],[37,1,50,50]];
var ide=document.getElementById('ide'),side=document.getElementById('side'),code=document.getElementById('code'),tab=document.getElementById('tab'),term=document.getElementById('term'),lt=document.getElementById('lt'),end=document.getElementById('end');
side.innerHTML=TR.map(function(r){return '<div style="padding-left:'+(1+r[1]*1.1)+'cqw">'+(r[2].slice(-1)=='/'?'▾ ':'')+esc(r[2])+'</div>'}).join('');var sd=side.children;
function cam(t){for(var i=0;i<CAM.length-1;i++){var a=CAM[i],b=CAM[i+1];if(t<=b[0]){var x=sm(cl((t-a[0])/(b[0]-a[0])));return[a[1]+(b[1]-a[1])*x,a[2]+(b[2]-a[2])*x,a[3]+(b[3]-a[3])*x]}}return[1,50,50]}
function render(t){
 var c=cam(t);ide.style.transformOrigin=c[1]+'% '+c[2]+'%';ide.style.transform='scale('+c[0]+')';
 /* terminal */
 var h=[],last=null;TM.forEach(function(r){if(t<r.at)return;if(r.k=='c'){var n=Math.floor((t-r.at)*r.cps),done=n>=r.t.length;var line='<span class="pr">'+r.p+'</span>'+esc(r.t.slice(0,n));h.push(line+(done?'':'<span class="cur"></span>'));last=done?r:null}else h.push('<span class="'+r.c+'">'+esc(r.t)+'</span>')});
 var typing=TM.some(function(r){return r.k=='c'&&t>=r.at&&(t-r.at)*r.cps<r.t.length});var lastc=TM.filter(function(r){return r.k=='c'&&t>=r.at}).pop();
 var lr=TM.filter(function(r){return t>=r.at}).pop(),lastIsCmd=lr&&lr.k=='c'&&!typing&&lr.t=='cd my_agent';
 term.innerHTML=h.slice(-12).join('\n')+(lastIsCmd||!h.length?'<span class="pr">'+(h.length?AG:DEV)+'</span><span class="cur"></span>':'');
 /* tree */
 var act='';SCH.forEach(function(s){if(t>=s[0])act=s[1]});
 var AI={'tools/example.py':11,'tools/word_count.py':12,'server.py':3}[act];TR.forEach(function(r,i){sd[i].className=(t>=r[0]?'on':'')+(act&&i==AI?' act':'')});
 /* editor */
 if(!act){tab.textContent='';code.innerHTML=''}else{tab.textContent=act;var L=F[act]||[],html='';L.forEach(function(l,i){if(t<l.at)return;var txt=l.t,typing=false;if(l.d){var x=cl((t-l.at)/l.d);txt=l.t.slice(0,Math.floor(x*l.t.length));typing=x<1}html+='<div class="l'+(l.n?' n':'')+'"><b>'+(i+1)+'</b><span>'+hl(txt)+(typing?'<span class="cur"></span>':'')+'</span></div>'});code.innerHTML=html}
 /* lower third + end */
 var cap='';LT.forEach(function(l){if(t>=l[0]&&t<l[1])cap=l[2]});lt.textContent=cap;lt.style.opacity=cap?1:0;end.style.opacity=t>33.2?1:0;
}
var t=0,play=true,last=performance.now(),sc=document.getElementById('sc'),tm=document.getElementById('tm'),pp=document.getElementById('pp');
if(matchMedia('(prefers-reduced-motion: reduce)').matches){play=false;pp.textContent='Play';t=0}
function tick(n){var dt=(n-last)/1000;last=n;if(play){t+=dt;if(t>=T){t=T;play=false;pp.textContent='Play'}}render(t);sc.value=t*10;tm.textContent=t.toFixed(1)+' / '+T+'.0s';requestAnimationFrame(tick)}
pp.onclick=function(){if(t>=T)t=0;play=!play;pp.textContent=play?'Pause':'Play'};
document.getElementById('rp').onclick=function(){t=0;play=true;pp.textContent='Pause'};
sc.oninput=function(){t=sc.value/10;play=false;pp.textContent='Play'};
requestAnimationFrame(tick);
})();
</script></body></html>
-agent-kit — developer screencast.html…]()



## Quick Start (5 Lines)

```bash
pip install mcp-agent-kit
create-mcp-agent my_agent
cd my_agent
python validate.py
python server.py
```

---

## End-to-End Demo Walkthrough (with Real Outputs)

Follow these step-by-step instructions to scaffold, validate, test, and run an MCP agent end-to-end.

### Step 1: Scaffold a New Agent
Run the generator CLI to create a new agent (e.g. `demo_agent`):

```bash
python -m mcp_agent_kit demo_agent --desc "Use when computing numerical metrics and data summaries. Do not use for unstructured text parsing."
```

**Terminal Output:**
```text
Scaffolding MCP agent 'demo_agent' into 'demo_agent'...
✓ Agent 'demo_agent' successfully created in 'demo_agent'.
Next steps:
  cd demo_agent
  python validate.py
```

---

### Step 2: Run Compliance Validation
Navigate into the agent directory and execute `validate.py`:

```bash
cd demo_agent
python validate.py
```

**Terminal Output:**
```text
✓ MCP server/discover responds correctly
✓ tools/list is deterministically ordered
✓ all tool schemas pass design rules
✓ A2A agent.json is valid
✓ SKILL.md portable core is valid
✓ dual-era client probe works against local server
```

---

### Step 3: Run the Dual-Era Probe Client Test
Verify client negotiation and tool execution via `client_test.py`:

```bash
python client_test.py
```

**Terminal Output:**
```text
..
----------------------------------------------------------------------
Ran 2 tests in 0.000s

OK
```

---

### Step 4: Test Stateless MCP 2026-07-28 Server via Stdio
Send raw JSON-RPC requests to `server.py` over stdin. Notice every request independently carries `_meta`:

#### Request A: Discovery (`server/discover`)
**Stdin Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "server/discover",
  "params": {
    "_meta": {
      "protocolVersion": "2026-07-28",
      "clientCapabilities": {},
      "clientInfo": {"name": "demo-client", "version": "1.0.0"}
    }
  }
}
```

**Stdout Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "resultType": "complete",
    "serverInfo": {
      "name": "demo_agent",
      "version": "1.0.0"
    },
    "supportedVersions": [
      "2026-07-28"
    ],
    "capabilities": {
      "tools": {"listChanged": false},
      "resources": {"subscribe": false, "listChanged": false},
      "prompts": {"listChanged": false}
    },
    "ttlMs": 3600000,
    "cacheScope": "workspace"
  }
}
```

#### Request B: Tool Execution (`tools/call`)
**Stdin Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "_meta": {
      "protocolVersion": "2026-07-28",
      "clientCapabilities": {},
      "clientInfo": {"name": "demo-client", "version": "1.0.0"}
    },
    "name": "calculate_metrics",
    "arguments": {
      "metric_type": "mean",
      "values": [12.5, 45.0, 78.5, 92.0]
    }
  }
}
```

**Stdout Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "resultType": "complete",
    "serverInfo": {
      "name": "demo_agent",
      "version": "1.0.0"
    },
    "content": [
      {
        "type": "text",
        "text": "{\"metric\": \"mean\", \"value\": 57.0, \"count\": 4}"
      }
    ],
    "isError": false
  }
}
```

---

### Step 5: Test A2A Agent Card & Task Lifecycle API
Start the HTTP server on port 8000:

```bash
python a2a/server.py 8000
```

#### A. Fetch the Agent Card
```bash
curl -s http://localhost:8000/.well-known/agent.json
```

**HTTP 200 Response:**
```json
{
  "schemaVersion": "1.0",
  "name": "demo_agent",
  "description": "Use when computing numerical metrics and data summaries. Do not use for unstructured text parsing.",
  "url": "http://localhost:8000/a2a",
  "version": "1.0.0",
  "skills": [
    {
      "id": "calculate_metrics",
      "name": "calculate_metrics",
      "description": "Use when analyzing numerical series or computing aggregate metrics. Do not use for unstructured text parsing.",
      "inputModes": ["data", "text"],
      "outputModes": ["data", "text"],
      "parameters": {
        "type": "object",
        "properties": {
          "metric_type": {"type": "string", "enum": ["mean", "sum", "max", "min"]},
          "values": {"type": "array", "items": {"type": "number"}}
        },
        "required": ["values"]
      }
    }
  ],
  "capabilities": {
    "streaming": true,
    "pushNotifications": false
  }
}
```

#### B. Send a Task (`POST /a2a/tasks/send`)
```bash
curl -s -X POST http://localhost:8000/a2a/tasks/send \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user",
        "parts": [
          {"type": "text", "text": "Compute quarterly summary metrics"},
          {"type": "data", "data": {"quarter": "Q3", "values": [100, 200, 300]}}
        ]
      }
    ]
  }'
```

**HTTP 200 Response:**
```json
{
  "taskId": "task_e8ca2985820b",
  "status": "completed"
}
```

#### C. Query Task Status and Output Artifact (`GET /a2a/tasks/{id}`)
```bash
curl -s http://localhost:8000/a2a/tasks/task_e8ca2985820b
```

**HTTP 200 Response:**
```json
{
  "taskId": "task_e8ca2985820b",
  "status": "completed",
  "messages": [
    {
      "role": "user",
      "parts": [
        {"type": "text", "text": "Compute quarterly summary metrics"},
        {"type": "data", "data": {"quarter": "Q3", "values": [100, 200, 300]}}
      ]
    }
  ],
  "artifacts": [
    {
      "name": "task_output",
      "type": "data",
      "data": {
        "status": "success",
        "processed_parts": 1
      }
    }
  ],
  "created_at": 1791728650.129,
  "updated_at": 1791728650.130
}
```

---

### Step 6: Run Comprehensive Test Suite
Run the 20-test automated compliance and unit testing suite:

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

**Terminal Output:**
```text
test_artifact_returned_on_completion (test_a2a.TestA2A.test_artifact_returned_on_completion) ... ok
test_input_required_pause_and_resume (test_a2a.TestA2A.test_input_required_pause_and_resume) ... ok
test_mcp_tools_to_a2a_skills_mapping (test_a2a.TestA2A.test_mcp_tools_to_a2a_skills_mapping) ... ok
test_task_lifecycle_submitted_to_working_to_completed (test_a2a.TestA2A.test_task_lifecycle_submitted_to_working_to_completed) ... ok
test_allowlisted_peer_timeout_stays_unavailable (test_mcp_client.TestMCPClient.test_allowlisted_peer_timeout_stays_unavailable) ... ok
test_allowlisted_peer_valid_initialize_selects_legacy (test_mcp_client.TestMCPClient.test_allowlisted_peer_valid_initialize_selects_legacy) ... ok
test_ambiguous_signal_fails_closed_without_allowlist (test_mcp_client.TestMCPClient.test_ambiguous_signal_fails_closed_without_allowlist) ... ok
test_collision_produces_prefixed_name_never_silent_overwrite (test_mcp_client.TestMCPClient.test_collision_produces_prefixed_name_never_silent_overwrite) ... ok
test_recognized_modern_errors_never_trigger_initialize (test_mcp_client.TestMCPClient.test_recognized_modern_errors_never_trigger_initialize) ... ok
test_every_request_repeats_meta_independently (test_mcp_server.TestMCPServer.test_every_request_repeats_meta_independently) ... ok
test_list_results_stable_regardless_of_insertion_order (test_mcp_server.TestMCPServer.test_list_results_stable_regardless_of_insertion_order) ... ok
test_server_never_initiates_request (test_mcp_server.TestMCPServer.test_server_never_initiates_request) ... ok
test_stdio_loop (test_mcp_server.TestMCPServer.test_stdio_loop) ... ok
test_tool_call_returns_isError_true_on_executor_failure (test_mcp_server.TestMCPServer.test_tool_call_returns_isError_true_on_executor_failure) ... ok
test_unsupported_protocol_version_error (test_mcp_server.TestMCPServer.test_unsupported_protocol_version_error) ... ok
test_scaffold_creates_complete_working_structure (test_scaffolder.TestScaffolder.test_scaffold_creates_complete_working_structure) ... ok
test_description_length_and_pattern_checks (test_skill.TestSkillPackage.test_description_length_and_pattern_checks) ... ok
test_generate_skill_markdown_creates_compliant_output (test_skill.TestSkillPackage.test_generate_skill_markdown_creates_compliant_output) ... ok
test_skill_name_matches_directory (test_skill.TestSkillPackage.test_skill_name_matches_directory) ... ok
test_unknown_runtime_extensions_rejected_in_portable_core (test_skill.TestSkillPackage.test_unknown_runtime_extensions_rejected_in_portable_core) ... ok

----------------------------------------------------------------------
Ran 20 tests in 0.033s

OK
```

---

## Architecture

```
+=============================================================================+
|                      Host Environment / AI Assistant                        |
|             (Claude Desktop, Claude Code, Anthropic API, Custom Host)       |
+=============================================================================+
        |                                   |                           |
        | [Stateless JSON-RPC]              | [REST / Task Lifecycle]   | [Progressive Disclosure]
        | (stdio transport)                 | (HTTP /a2a)               | (Agent Skill)
        v                                   v                           v
+-----------------------+       +-----------------------+   +-----------------+
|   MCP Server Core     |       |   A2A Task Server     |   |    SKILL.md     |
|   (Stateless 2026)    |       |       (v1.0)          |   | (Portable Core) |
+-----------------------+       +-----------------------+   +-----------------+
| - server/discover     |       | - /.well-known/agent  |   | - Frontmatter   |
| - tools/list & call   |<----->| - tasks/send (Parts)  |   | - Workflows     |
| - resources/list&read | Auto- | - tasks/{id}          |   | - Tool index    |
| - prompts/list & get  | Map   | - Artifacts pipeline  |   |                 |
| - input_required mode |       | - input_required pause|   |                 |
+-----------------------+       +-----------------------+   +-----------------+
        |
        +-----------------------------------+
                                            v
                        +---------------------------------------+
                        |       Compliant Tool Schemas          |
                        | - snake_case names                    |
                        | - "Use when X. Do not use for Y."     |
                        | - readOnlyHint / destructiveHint      |
                        | - Deterministic alphabetical order    |
                        +---------------------------------------+
```

---

## How to Add a New Tool (3 Steps)

### Step 1: Define the function & schema in `tools/`
Create a new file in `tools/` (e.g., `tools/user_ops.py`):

```python
from typing import Any, Dict

def get_user_profile(arguments: Dict[str, Any]) -> Dict[str, Any]:
    user_id = arguments["user_id"]
    return {"user_id": user_id, "status": "active", "tier": "enterprise"}

TOOL_DEFINITION = {
    "name": "get_user_profile",
    "description": "Use when retrieving user profile details by ID. Do not use for updating account settings.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "user_id": {"type": "string", "description": "Unique user ID"}
        },
        "required": ["user_id"]
    },
    "annotations": {
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    },
    "handler": get_user_profile
}
```

### Step 2: Register the tool in `server.py`
In `server.py`, register the tool definition with the server engine:

```python
from tools.user_ops import TOOL_DEFINITION as USER_TOOL

srv.tools.register(
    name=USER_TOOL["name"],
    description=USER_TOOL["description"],
    input_schema=USER_TOOL["inputSchema"],
    annotations=USER_TOOL["annotations"],
    handler=USER_TOOL["handler"]
)
```

### Step 3: Verify with `validate.py`
```bash
python validate.py
```

---

## How to Install in Claude Desktop

Add your server configuration to your `claude_desktop_config.json`:

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "my_agent": {
      "command": "python",
      "args": ["/absolute/path/to/my_agent/server.py"]
    }
  }
}
```

---

## How to Install as Agent Skill in Claude Code

Run this single command to install as a project-level or global Agent Skill:

```bash
mkdir -p ~/.claude/skills && cp SKILL.md ~/.claude/skills/my_agent.md
```

Or for project-level scope in your repository:

```bash
mkdir -p .claude/skills && cp SKILL.md .claude/skills/my_agent.md
```

---

## Validation Engine (`validate.py`)

Run the complete compliance suite with a single command:

```bash
python validate.py
```

### Example Output

```text
✓ MCP server/discover responds correctly
✓ tools/list is deterministically ordered
✓ all tool schemas pass design rules
✓ A2A agent.json is valid
✓ SKILL.md portable core is valid
✓ dual-era client probe works against local server
```

If a tool violates schema rules (e.g. missing annotations or improper description formatting), the validator detects and reports it with granular diagnostics:

```text
✗ notes_delete missing readOnlyHint or destructiveHint (at least one must be true)
```

---

## What `mcp-agent-kit` Implements

### 1. Stateless MCP Specification (2026-07-28)
- **Zero Stateful Coupling**: Every JSON-RPC request must carry a valid `_meta` block (`protocolVersion`, `clientCapabilities`, `clientInfo`) and is validated independently without session reuse.
- **Envelope Contracts**: Every successful response includes `resultType: "complete"` and server identity (`serverInfo`).
- **Input Required Protocol**: Handlers needing interaction yield `resultType: "input_required"`. The server never initiates unsolicited requests to the client.
- **Deterministic Alphabetical Sorting**: All collections (`tools/list`, `resources/list`, `prompts/list`) are deterministically sorted.
- **Stdio Rules**: JSON-RPC is strictly emitted to `stdout` with newline flushing; diagnostics and logs are written exclusively to `stderr`.

### 2. Dual-Era Probe Client & Namespace Merger
- **Probing State Machine**: Starts with modern `server/discover`.
- **Fail-Closed Security**: Recognized modern errors (`-32020`, `-32021`, `-32022`) correct and retry without falling back to initialize. Ambiguous signals fail closed unless explicitly allowlisted.
- **Multi-Server Namespace Merging**: Colliding tool names are prefixed (`server/tool_name`), avoiding silent overwrites while preserving local names.

### 3. A2A Protocol (Agent-to-Agent v1.0)
- Auto-generates `/.well-known/agent.json` from registered tools.
- Task lifecycle management: `submitted` → `working` → `completed` | `failed` | `input_required`.
- Rich message parts (`text`, `file`, `data`) and typed output artifacts upon completion.

### 4. Portable Agent Skill (`SKILL.md`)
- YAML frontmatter with strict portable core validation (`name` matches directory, `description` 20–1024 characters with `"Use when X. Do not use for Y."` pattern).
- Zero unknown runtime extensions.

---

## Architecture Boundaries (What NOT to Build)

- **Authentication**: Zero hardcoded auth in core protocol. To add auth, attach a bearer token validator in `a2a/server.py` or middleware headers in `MCPServer._dispatch`.
- **Database**: Zero database dependencies. In-memory task and state stores are provided with cleanly documented swap points (`TaskManager.task_executor`).
- **Dependencies**: Protocol core uses Python standard library only (`json`, `dataclasses`, `http.server`, `re`, `sys`). Flask is optional: `pip install mcp-agent-kit[a2a]`.

---

## Specification References

- [Model Context Protocol (MCP) Specification 2026-07-28](https://spec.modelcontextprotocol.io)
- [Agent-to-Agent (A2A) Protocol Specification v1.0](https://a2a-protocol.org)
- [Portable Agent Skill Specification](https://docs.anthropic.com/en/docs/agents-and-tools)

---
