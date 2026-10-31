"""ROUND1: preserve market pixels; replace rectangular grounds with masked local plates."""
from pathlib import Path
import json, shutil
import numpy as np
import cv2
from PIL import Image,ImageDraw,ImageFilter,ImageOps
ROOT=Path(__file__).resolve().parents[2];R=ROOT/'design/assets/review/round1'
ps=json.loads((ROOT/'design/assets/review/A01-composite-patches.json').read_text(encoding='utf-8-sig'))
rec=json.loads((R/'generation-record.json').read_text(encoding='utf-8'))
base=Image.open(ROOT/'design/assets/review/A01-source-2x.png').convert('RGB')
old=Image.open(R/'before-map-taiwan-market.png').convert('RGB')
out=base.copy()
polys=[
[(0,75),(7,54),(49,23),(51,14),(60,12),(60,19),(198,18),(198,10),(207,12),(210,25),(231,49),(232,59),(244,64),(245,90),(238,97),(237,132),(217,134),(204,140),(9,139),(8,118),(1,105)],
[(68,7),(213,8),(219,20),(252,49),(269,53),(262,62),(267,64),(269,87),(265,99),(264,141),(216,145),(19,143),(7,136),(6,97),(0,90),(0,75),(11,61),(8,50),(32,46),(59,21),(62,11)],
[(68,26),(188,26),(189,20),(196,24),(195,35),(236,66),(242,65),(242,76),(248,84),(250,102),(244,117),(238,125),(238,141),(219,148),(13,152),(15,128),(7,108),(8,85),(17,80),(16,70),(40,54),(61,38),(62,27)],
[(10,1),(29,0),(35,8),(39,16),(39,22),(36,25),(36,52),(32,55),(6,55),(3,50),(3,24),(0,21),(2,12)],
[(8,0),(30,0),(38,8),(41,20),(37,24),(37,51),(31,55),(5,55),(2,48),(2,24),(0,20),(2,9)],
[(9,1),(30,1),(38,11),(40,20),(36,25),(37,55),(32,59),(5,59),(2,52),(2,25),(0,20),(2,10)],
[(10,1),(31,1),(39,11),(41,21),(37,27),(38,56),(32,59),(5,59),(2,53),(2,26),(0,21),(3,11)]
]
for i,p in enumerate(ps):
 x,y,w,h=p['dst']; x*=2;y*=2;w*=2;h*=2; box=(x,y,x+w,y+h)
 fg=old.crop(box)
 mask=Image.new('L',(w,h),0);ImageDraw.Draw(mask).polygon(polys[i],fill=255)
 # Preserve silhouette and content, soften only antialias edge; 6px feather is reserved for ground/shadow.
 mask=mask.filter(ImageFilter.GaussianBlur(.65))
 if i<3:
  full=Image.open(rec['backgrounds'][p['name']]['path']).convert('RGB').resize((w+160,h+160),Image.Resampling.LANCZOS)
  bg=full.crop((80,80,80+w,80+h))
  # No market exists in this generated background plate.
  # Do not Poisson-match against the original gate: its colored roof would leak
  # into the new ground. Match only the surrounding grass colors and feather
  # the local plate inward over 6px; pixels outside the rectangle stay original.
  yy,xx=np.indices((h,w));dist=np.minimum.reduce([xx,yy,w-1-xx,h-1-yy]).astype(float)
  transition=Image.fromarray(np.uint8(np.clip(dist/6,0,1)*255))
  bg=Image.composite(bg,base.crop(box),transition)
  # Restore original tree canopy in top-left strip; tree core and connecting outside pixels stay source-derived.
  tree=Image.new('L',(w,h),0);td=ImageDraw.Draw(tree)
  if i==0: td.polygon([(0,0),(39,0),(35,14),(26,22),(20,41),(0,56)],fill=255)
  if i==1: td.polygon([(0,0),(22,0),(22,15),(35,26),(23,35),(20,46),(0,43)],fill=255)
  # The source's southern top-center contains the old roof as well as tree;
  # retain the clean generated tree there rather than restoring the old gate.
  tree=tree.filter(ImageFilter.GaussianBlur(.8));bg=Image.composite(base.crop(box),bg,tree)
 else: bg=base.crop(box) # carts: original courtyard preserved, only cart silhouette is pasted
 # Preserve exact object pixels at their exact location; slight softness matching existing upscaled map.
 fg=fg.filter(ImageFilter.GaussianBlur(.6))
 merged=Image.composite(fg,bg,mask)
 # The outer scope remains the exact original patch rectangle.
 out.paste(merged,(x,y))
 mask.save(R/(p['name']+'-alpha.png'))
 rgba=fg.convert('RGBA');rgba.putalpha(mask);rgba.save(R/(p['name']+'-cutout.png'))
out.save(R/'A01-candidate.png')
# New dessert: preserve true generated alpha and fit its single silhouette to 80%.
dess=Image.open(rec['dessert']['path']).convert('RGBA');bb=dess.getchannel('A').point(lambda p:255 if p>8 else 0).getbbox()
dess=dess.crop(bb);dess=ImageOps.contain(dess,(102,102),Image.Resampling.LANCZOS)
final=Image.new('RGBA',(128,128),(0,0,0,0));final.alpha_composite(dess,((128-dess.width)//2,(128-dess.height)//2));final.save(R/'desserts-candidate.png')
# Comparison crops with exact 1:1 pixels.
widths=[p['dst'][2]*2+40 for p in ps];canvas=Image.new('RGB',(sum(widths),2*210+40),'white');d=ImageDraw.Draw(canvas);xx=0
for p,ww in zip(ps,widths):
 x,y,w,h=p['dst'];b=(x*2-20,y*2-20,(x+w)*2+20,(y+h)*2+20)
 d.text((xx,0),p['name'],fill='black');canvas.paste(old.crop(b),(xx,20));canvas.paste(out.crop(b),(xx,230));xx+=ww
canvas.save(R/'A01-seams-before-after-100pct.png')
out.resize((1122,1402),Image.Resampling.LANCZOS).save(R/'A01-candidate-50pct.png')
print('candidates ready')
