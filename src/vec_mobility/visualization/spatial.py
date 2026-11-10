"""Top and spatial previews using a generated road surface."""

from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import animation, patches
from matplotlib.lines import Line2D
from matplotlib.collections import PatchCollection
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
import pandas as pd
from .. import uav as mobility
from ..rsu import positions

COLORS = ["#d43b39", "#8b49bd", "#d28513"]


def quad(x, y, width, height, z=0):
    return [(x,y,z),(x+width,y,z),(x+width,y+height,z),(x,y+height,z)]


def render(scene_frames, output, animation_frames=80, background=None,
           recording_meta=None, snapshot_time=None, legacy=False):
    if not scene_frames:
        raise ValueError("No scene frames")
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    times = [f["time_s"] for f in scene_frames]
    rows = [dict(frame=i, x=v["x_m"], y=v["y_m"], velocity=v["vx_mps"],
                 width=v.get("length_m",8.0), height=v.get("width_m",2.0))
            for i,f in enumerate(scene_frames) for v in f["vehicles"]]
    df = pd.DataFrame(rows, columns=["frame", "x", "y", "velocity", "width", "height"])
    groups = {int(k):v for k,v in df.groupby("frame")}
    xs = [r["x_m"] for r in positions()]
    upper_lanes, lower_lanes = [], []
    if recording_meta is not None:
        meta = pd.read_csv(recording_meta).iloc[0]
        upper_lanes = [float(v) for v in str(meta.upperLaneMarkings).split(';')]
        lower_lanes = [float(v) for v in str(meta.lowerLaneMarkings).split(';')]
    lanes = upper_lanes + lower_lanes
    rsu_y = (min(lanes) + max(lanes)) / 2 if lanes else 17.85
    image_height = max(lanes) + 10 if lanes else 38.8
    road_image = plt.imread(background) if background is not None else None
    paths = [mobility.uav_positions(t) for t in np.linspace(0,250,600)]
    fig2, ax2 = plt.subplots(figsize=(15,6))
    fig3 = plt.figure(figsize=(13,6.4))
    ax3 = fig3.add_subplot(111, projection="3d", computed_zorder=False)

    def top(frame, show_uavs=True):
        ax2.clear()
        ax2.set_facecolor("#edf1f3")
        if road_image is not None:
            for tile in range(4):
                ax2.imshow(road_image,extent=(400*tile,400*(tile+1),0,image_height),
                           aspect='auto',alpha=.6,zorder=0)
        if legacy:
            ax2.axvline(400,color='white',linestyle='--',alpha=.3)
            ax2.axvline(1200,color='white',linestyle='--',alpha=.3)
        else:
            for lane in (8,12,16,21,25,29):
                ax2.axhline(lane,color="white",linestyle="--",linewidth=1)
        for i,x in enumerate(xs):
            if legacy:
                ax2.add_patch(patches.Ellipse((x,rsu_y),400,(max(lanes)-min(lanes))*3 if lanes else 60.87,
                                             edgecolor='cyan',facecolor='cyan',alpha=.25,linewidth=2,zorder=2))
            ax2.plot(x,rsu_y,'^',color='cyan',markeredgecolor='black',markersize=14,zorder=6)
            ax2.text(x,rsu_y-8,f'RSU {i}',ha='center',color='white',fontweight='bold',
                     bbox=dict(facecolor='blue',alpha=.5,pad=.5),fontsize=10,zorder=6)
        rows=groups.get(frame,df.iloc[:0])
        boxes, colors = [], []
        for row in rows.itertuples():
            boxes.append(patches.Rectangle((row.x,row.y),row.width,row.height))
            colors.append(('royalblue' if row.x<400 else 'cornflowerblue') if row.velocity>0
                          else ('crimson' if row.x>1200 else 'indianred'))
        ax2.add_collection(PatchCollection(boxes,facecolors=colors,edgecolors='black',linewidth=.5,zorder=10))
        if show_uavs:
            for i,u in enumerate(scene_frames[frame]['uavs']):
                ax2.plot([v[i]['x_m'] for v in paths],[v[i]['y_m'] for v in paths],color=COLORS[i],alpha=.5,linewidth=1,zorder=11)
                ax2.plot(u['x_m'],u['y_m'],marker='X',color=COLORS[i],markersize=12,
                         markeredgecolor='white',label=f'UAV {i+1}',zorder=12)
        if legacy:
            ax2.set(xlim=(0,1600),ylim=(image_height,0),xlabel='',ylabel='',
                    title='Full Uniform Coverage with Dynamic Speeds')
            ax2.text(.02,.9,f'Time: {times[frame]:.1f}s | Cars: {len(rows)}',transform=ax2.transAxes,
                     bbox=dict(facecolor='white',alpha=.7),zorder=15)
            fig2.subplots_adjust(left=.125,right=.9,bottom=.11,top=.88)
        else:
            ax2.set(xlim=(0,1600),ylim=(44,-6),xlabel='Road position x (m)',ylabel='Lateral position y (m)',title=f'Vehicle-UAV-RSU scene | t = {times[frame]:.1f} s | {len(rows)} vehicles')
            if show_uavs: ax2.legend(loc='upper right',ncol=3,framealpha=.95)
            fig2.tight_layout(pad=.7)

    def perspective(frame):
        ax3.clear()
        ax3.add_collection3d(Poly3DCollection([quad(0,0,1600,39)],facecolors='#e5e9ec',edgecolors='#9ca6ad',zorder=0))
        for y in (8,12,16,21,25,29):
            ax3.plot([0,1600],[y,y],[.2,.2],color='white',linewidth=1.2,linestyle='--',zorder=1)
        for i,x in enumerate(xs):
            ax3.plot([x,x],[rsu_y,rsu_y],[0,10],color='#237d81',linewidth=2,zorder=4)
            ax3.scatter([x],[rsu_y],[10],marker='^',s=35,color='#237d81',depthshade=False,zorder=5)
            ax3.text(x,rsu_y,16,f'R{i}',fontsize=9,color='#176165',zorder=6)
        rows=groups.get(frame,df.iloc[:0])
        for positive,color in [(True,'#376cc1'),(False,'#bb5151')]:
            subset=rows[rows.velocity.gt(0)==positive]
            polys=[quad(r.x,r.y,r.width,r.height,1.5) for r in subset.itertuples()]
            if polys: ax3.add_collection3d(Poly3DCollection(polys,facecolors=color,edgecolors='#333',linewidths=.25,zorder=3))
        for i,u in enumerate(scene_frames[frame]['uavs']):
            ax3.plot([v[i]['x_m'] for v in paths],[v[i]['y_m'] for v in paths],[v[i]['z_m'] for v in paths],color=COLORS[i],alpha=.5,linewidth=1.3,zorder=7)
            ax3.plot([u['x_m']]*2,[u['y_m']]*2,[0,u['z_m']],color=COLORS[i],linestyle=':',alpha=.65,zorder=7)
            ax3.scatter([u['x_m']],[u['y_m']],[0],s=20,color=COLORS[i],alpha=.3,depthshade=False,zorder=8)
            ax3.scatter([u['x_m']],[u['y_m']],[u['z_m']],marker='X',s=110,color=COLORS[i],edgecolor='white',depthshade=False,zorder=9)
        ax3.set(xlim=(0,1600),ylim=(-6,44),zlim=(0,130),xlabel='Road position x (m)',ylabel='Lateral y (m)',zlabel='Altitude (m)',xticks=[0,400,800,1200,1600],yticks=[0,20,40],zticks=[0,40,80,120])
        ax3.tick_params(axis='x',labelsize=10,pad=2)
        ax3.tick_params(axis='y',labelsize=9,pad=2)
        ax3.tick_params(axis='z',labelsize=10,pad=3)
        ax3.xaxis.labelpad=18
        ax3.xaxis.set_rotate_label(True)
        ax3.yaxis.labelpad=9
        ax3.zaxis.labelpad=9
        for axis in (ax3.xaxis,ax3.yaxis,ax3.zaxis):
            axis.set_pane_color((.98,.985,.99,1))
            axis._axinfo['grid']['color']=(.78,.81,.84,.48)
        ax3.set_box_aspect((4,1.25,1.6),zoom=1.06)
        ax3.view_init(elev=23,azim=-64)
        ax3.legend(handles=[Line2D([],[],marker='X',linestyle='',color=c,markersize=9,label=f'UAV {i+1}') for i,c in enumerate(COLORS)],loc='upper center',bbox_to_anchor=(.48,.86),ncol=3,frameon=False)
        ax3.text2D(.08,.82,f't = {times[frame]:.1f} s',transform=ax3.transAxes,color='#444',fontsize=10)
        fig3.subplots_adjust(left=-.08,right=1.02,bottom=-.10,top=1.14)

    snapshot = (min(range(len(times)),key=lambda i:abs(times[i]-snapshot_time))
                if snapshot_time is not None else min(len(scene_frames)-1, 200))
    if legacy:
        top(snapshot,show_uavs=False)
        fig2.savefig(output/'top_original.png',dpi=100)
        fig2.legend(handles=[Line2D([],[],marker='X',linestyle='',color=c,markersize=9,label=f'UAV {i+1}')
                             for i,c in enumerate(COLORS)],loc='upper center',bbox_to_anchor=(.52,1.0),ncol=3,frameon=False)
    top(snapshot)
    perspective(snapshot)
    fig2.savefig(output/"top_view.png", dpi=140)
    fig3.savefig(output/"spatial_view.png", dpi=140)
    stride = 2 if len(scene_frames)>1 else 1
    frames = list(range(0,len(scene_frames),stride))[:animation_frames]
    delta = times[frames[1]]-times[frames[0]] if len(frames)>1 else .2
    fps = 1/max(delta, .001)
    ani = animation.FuncAnimation(fig3,perspective,frames=frames,interval=1000/fps,blit=False)
    ani.save(output/"spatial_view.gif",writer=animation.PillowWriter(fps=fps),dpi=85)
    if legacy:
        top_ani = animation.FuncAnimation(fig2,top,frames=frames,interval=1000/fps,blit=False)
        top_ani.save(output/'top_view.gif',writer=animation.PillowWriter(fps=fps),dpi=85)
    plt.close(fig2)
    plt.close(fig3)
    print(f"Created top/spatial PNGs and GIF in {output.resolve()}")
