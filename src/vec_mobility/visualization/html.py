"""Self-contained HTML playback, with no external runtime assets."""

import json
from pathlib import Path
from ..config import ROAD_LENGTH, NUM_RSUS, RSU_Y, RSU_Z


def export_view(frames, output, synthetic=False, rsus=None):
    payload = dict(frames=frames, road_length=ROAD_LENGTH, synthetic=synthetic,
                   rsus=rsus if rsus is not None else [dict(id=f"R{i}", x_m=(i+0.5)*ROAD_LENGTH/NUM_RSUS, y_m=RSU_Y, z_m=RSU_Z) for i in range(NUM_RSUS)])
    # Escape HTML-significant characters even when input identifiers are untrusted.
    data = json.dumps(payload, allow_nan=False).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    html = VIEW.replace("__SCENE_DATA__", data)
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html, encoding="utf-8")
    print(f"Created {output.resolve()} ({len(frames)} frames)")
    if not synthetic:
        print("Contains input trajectory coordinates. Keep this output private unless redistribution is permitted.")


VIEW = r'''<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Vehicle-UAV-RSU Trajectory Playback</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#f6f8fa;color:#20252b;font:14px Arial,sans-serif}
header,main{max-width:1300px;margin:auto;padding:20px}header{border-bottom:1px solid #d5dade}h1{font-size:22px;margin:0 0 10px}
.legend{display:flex;gap:22px;flex-wrap:wrap}.vehicle{color:#007d88}.uav{color:#c34448}.rsu{color:#65703b}
canvas{display:block;width:100%;height:460px;background:white;border:1px solid #d5dade}
.controls{display:flex;align-items:center;gap:16px;margin:16px 0;flex-wrap:wrap}input[type=range]{flex:1;min-width:160px}
button,select{padding:8px;border:1px solid #aab2bb;background:white;border-radius:4px}output{font-variant-numeric:tabular-nums;min-width:130px}
@media(max-width:600px){canvas{height:380px}header,main{padding:12px}}
</style>
<header><h1>Vehicle-UAV-RSU Trajectory Playback</h1><div class="legend"><span class="vehicle">Vehicle</span><span class="uav">UAV</span><span class="rsu">RSU</span><span id="source"></span></div></header>
<main><canvas id="view"></canvas><div class="controls"><button id="play" title="Play or pause" aria-label="Play or pause">&#9654;</button><input id="seek" aria-label="Time" type="range" min="0" value="0"><select id="speed" aria-label="Playback speed"><option value="1">1x</option><option value="2">2x</option><option value="4">4x</option></select><output id="clock"></output></div></main>
<script id="data" type="application/json">__SCENE_DATA__</script><script>
const s=JSON.parse(document.getElementById('data').textContent), frames=s.frames;
const canvas=document.getElementById('view'), ctx=canvas.getContext('2d'), seek=document.getElementById('seek'), play=document.getElementById('play');
let index=0,playing=false,elapsed=frames[0].time_s,last=null;
seek.max=frames.length-1;
document.getElementById('source').textContent=s.synthetic?'Synthetic vehicle example':'Local input trajectories';
function draw(){
 const w=canvas.clientWidth,h=canvas.clientHeight,dpr=devicePixelRatio||1;canvas.width=w*dpr;canvas.height=h*dpr;ctx.scale(dpr,dpr);
 const left=48,right=w-22,x=v=>left+v/s.road_length*(right-left),top=h*.28,side=h*.87;
 ctx.font='12px Arial';ctx.fillStyle='#333';ctx.fillText('Top view (x, y)',12,24);ctx.fillText('Side view (x, altitude)',12,h*.55);
 ctx.fillStyle='#edf2f3';ctx.fillRect(left,top-42,right-left,84);
 for(let i=0;i<=6;i++){ctx.strokeStyle='#d8dce0';ctx.beginPath();ctx.moveTo(x(i*s.road_length/6),45);ctx.lineTo(x(i*s.road_length/6),h-27);ctx.stroke();}
 ctx.strokeStyle='#7c858c';ctx.beginPath();ctx.moveTo(left,side);ctx.lineTo(right,side);ctx.stroke();
 const f=frames[index];
 for(const r of s.rsus){ctx.fillStyle='#65703b';ctx.fillRect(x(r.x_m)-4,top+(r.y_m-17.85)*2-4,8,8);ctx.fillText(r.id,x(r.x_m)-8,top-52);ctx.fillRect(x(r.x_m)-4,side-r.z_m-4,8,8);}
 for(const v of f.vehicles){if(v.x_m<0||v.x_m>s.road_length)continue;ctx.fillStyle=v.vx_mps>0?'#376cc1':'#bb5151';const length=(v.length_m||8)*(right-left)/s.road_length,width=(v.width_m||2)*2;ctx.fillRect(x(v.x_m),top+(v.y_m-17.85)*2,length,width);ctx.fillRect(x(v.x_m),side-5,length,4);}
 for(const u of f.uavs){ctx.fillStyle='#c34448';for(const yy of [top+(u.y_m-17.85)*2,side-u.z_m]){ctx.beginPath();ctx.moveTo(x(u.x_m),yy-6);ctx.lineTo(x(u.x_m)+5,yy+4);ctx.lineTo(x(u.x_m)-5,yy+4);ctx.closePath();ctx.fill();}ctx.fillText(u.id,x(u.x_m)+7,side-u.z_m);}
 ctx.fillStyle='#555';ctx.fillText('0 m',left,h-8);ctx.fillText(s.road_length+' m',right-50,h-8);
 document.getElementById('clock').textContent=f.time_s.toFixed(2)+' s | '+f.vehicles.length+' vehicles';seek.value=index;
}
play.onclick=()=>{if(index===frames.length-1){index=0;elapsed=frames[0].time_s;}playing=!playing;play.innerHTML=playing?'&#10074;&#10074;':'&#9654;';draw();};
seek.oninput=()=>{index=+seek.value;elapsed=frames[index].time_s;draw();};
function tick(now){if(last!==null&&playing){elapsed+=(now-last)/1000*+document.getElementById('speed').value;while(index+1<frames.length&&frames[index+1].time_s<=elapsed)index++;if(index===frames.length-1){playing=false;play.innerHTML='&#9654;';}draw();}last=now;requestAnimationFrame(tick);}
window.addEventListener('resize',draw);draw();requestAnimationFrame(tick);
</script></html>'''
