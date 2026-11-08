from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
W,H=1600,700
im=Image.new('RGB',(W,H),'white'); d=ImageDraw.Draw(im)
fontdir=Path(r'C:/Windows/Fonts')
font=ImageFont.truetype(str(fontdir/'arial.ttf'),24)
small=ImageFont.truetype(str(fontdir/'arial.ttf'),18)
bold=ImageFont.truetype(str(fontdir/'arialbd.ttf'),30)
d.text((W//2,20),'Conceptual TTC plots and provisional critical limit',font=bold,fill='#172554',anchor='mt')
for panel,title,curve,color in [
 (0,'Longitudinal closing conflict',[(0,3.1),(1,2.8),(2,2.2),(3,1.65),(4,1.22),(5,0.85),(6,1.0),(7,1.35),(8,1.9),(9,2.5)],'#1769aa'),
 (1,'Lateral / crossing conflict',[(0,3.0),(1,2.7),(2,2.3),(3,1.85),(4,1.45),(5,1.15),(6,0.72),(7,0.55),(8,0.82),(9,1.35)],'#c2410c')]:
 x0=90+panel*790; y0=110; pw=670; ph=480
 d.text((x0+pw//2,y0),title,font=bold,fill='#111827',anchor='mt')
 left=x0+75; top=y0+60; right=x0+pw-20; bottom=y0+ph-70
 # axes
 d.line((left,top,left,bottom),fill='#374151',width=3); d.line((left,bottom,right,bottom),fill='#374151',width=3)
 # y: 0 to 4, x 0 to 9
 def pt(t,v): return (left+t/9*(right-left), bottom-v/4*(bottom-top))
 # grid and labels
 for v in range(5):
  y=pt(0,v)[1]; d.line((left,y,right,y),fill='#e5e7eb',width=1); d.text((left-12,y),str(v),font=small,fill='#374151',anchor='rm')
 for t in range(10):
  x=pt(t,0)[0]; d.line((x,bottom,x,bottom+6),fill='#374151',width=2); d.text((x,bottom+12),str(t),font=small,fill='#374151',anchor='mt')
 lim_y=pt(0,1.5)[1]; d.line((left,lim_y,right,lim_y),fill='#b91c1c',width=3); d.text((right-2,lim_y-28),'1.5 s provisional limit',font=small,fill='#b91c1c',anchor='rt')
 pts=[pt(t,v) for t,v in curve]; d.line(pts,fill=color,width=5)
 for x,y in pts: d.ellipse((x-5,y-5,x+5,y+5),fill=color)
 d.text(((left+right)//2,bottom+44),'Time in video (s)',font=font,fill='#111827',anchor='mt')
 d.text((x0+15,(top+bottom)//2),'TTC (s)',font=font,fill='#111827',anchor='mm')
d.text((W//2,H-8),'Illustrative curves only: not measured project or NH-48 observations. Confirm thresholds with local validation.',font=small,fill='#4b5563',anchor='ms')
out=Path('critical_ttc_concept.png'); im.save(out,dpi=(180,180)); print(out.resolve())
