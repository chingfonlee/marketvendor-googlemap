"""Audit delivery dimensions/alpha and original-map preservation; create review artifacts."""
from pathlib import Path
import json, hashlib, html, math
from datetime import datetime, timezone, timedelta
import numpy as np
import cv2
from PIL import Image, ImageOps, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[2]
R=ROOT/"design/assets/review"
manifest=json.loads((ROOT/"design/asset-briefs/manifest.json").read_text(encoding="utf-8"))
slugs=["vegetables","fruit","meat","seafood","deli","snacks","drinks","desserts","dry-goods","flowers"]
checks=[]
for a in manifest:
    for slug in (slugs if a["id"]=="A18" else [None]):
        path=ROOT/a["deliver_to"].replace("<品類>",slug or "<品類>")
        im=Image.open(path)
        w,h=a["output"]["width"],a["output"]["height"]
        alpha=im.convert("RGBA").getchannel("A")
        corners=[alpha.getpixel(p) for p in [(0,0),(w-1,0),(0,h-1),(w-1,h-1)]]
        transparent=a["output"]["background"]=="透明"
        bbox=alpha.point(lambda p:255 if p>8 else 0).getbbox()
        coverage=round(max((bbox[2]-bbox[0])/w,(bbox[3]-bbox[1])/h),3) if bbox else 0
        checks.append(dict(id=a["id"]+("-"+slug if slug else ""),path=path.relative_to(ROOT).as_posix(),size=list(im.size),size_pass=im.size==(w,h),background_pass=all(x==0 for x in corners) if transparent else alpha.getextrema()==(255,255),corners_alpha=corners,subject_extent=coverage,sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
base=np.array(Image.open(R/"A01-source-2x.png").convert("RGB"))
final=np.array(Image.open(ROOT/"design/assets/final/map-taiwan-market.png").convert("RGB"))
mask=np.zeros(base.shape[:2],bool)
boxes=[(595,180,722,252),(395,560,532,638),(350,920,482,1002),(840,395,962,477),(330,765,482,847)]
for x0,y0,x1,y1 in boxes: mask[y0*2:y1*2,x0*2:x1*2]=True
diff=np.any(base!=final,axis=2)
outside=int((diff & ~mask).sum())
source=np.array(Image.open(ROOT/"design/reference/map-v2/map-taiwan-clean.png").convert("RGB"))
half=np.array(Image.fromarray(final).resize((1122,1402),Image.Resampling.LANCZOS))
samples=[(940,500),(920,620),(840,730),(790,850),(740,990),(580,1160),(510,1270),(420,1150),(330,1040),(250,950),(230,840),(180,760),(260,630),(310,510),(390,420),(470,310),(540,180),(660,110),(900,140),(970,200)]
shifts=[]
for x,y in samples:
    tile=source[y-10:y+11,x-10:x+11]
    search=half[y-14:y+15,x-14:x+15]
    score=cv2.matchTemplate(search,tile,cv2.TM_SQDIFF_NORMED)
    _,_,loc,_=cv2.minMaxLoc(score)
    shifts.append(dict(point=[x,y],dx=loc[0]-4,dy=loc[1]-4))
mapcheck=dict(outside_allowed_boxes_changed_pixels=outside,all_other_buildings_and_coastline_exact_against_source_2x=outside==0,native_50pct_sample_shifts=shifts,max_sample_displacement=max(math.hypot(s["dx"],s["dy"]) for s in shifts),boxes_native=boxes)
(R/"map-preservation-check.json").write_text(json.dumps(mapcheck,indent=2),encoding="utf-8")
(R/"technical-checks.json").write_text(json.dumps(checks,indent=2),encoding="utf-8")
Image.blend(Image.fromarray(source),Image.fromarray(half),.5).save(R/"A01-overlay-50pct.png")
# Gallery uses the actual delivered files.
cards=[]
for c in checks:
    cards.append('<article><h2>'+c["id"]+'</h2><a href="../final/'+html.escape(c["path"].split("design/assets/final/")[1])+'"><div class="preview"><img src="../final/'+html.escape(c["path"].split("design/assets/final/")[1])+'"></div></a><p>'+html.escape(c["path"].split("/")[-1])+' · '+str(c["size"][0])+' × '+str(c["size"][1])+'</p></article>')
page='<!doctype html><html lang="zh-Hant"><meta charset="utf-8"><title>市場素材總覽</title><style>body{margin:32px;background:#fff8e6;color:#3b2a1a;font:16px system-ui}h1{font-size:28px}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:20px}article{border:1px solid #d6c9b8;border-radius:12px;padding:16px;background:white}h2{font-size:18px;margin:0 0 10px}.preview{height:240px;display:flex;align-items:center;justify-content:center;background:repeating-conic-gradient(#eee 0% 25%,#fff 0% 50%) 0/20px 20px}.preview img{max-width:100%;max-height:100%;object-fit:contain}p{font-size:13px}a{color:inherit}</style><h1>台灣市場素材 · 32 張</h1><p>點擊圖片可開啟原尺寸 PNG。棋盤格僅用來顯示透明背景。</p><div class="grid">'+''.join(cards)+'</div></html>'
(R/"index.html").write_text(page,encoding="utf-8")
# Contact sheet is a review artifact, not a generated deliverable.
font=ImageFont.truetype("C:/Windows/Fonts/arial.ttf",16)
sheet=Image.new("RGB",(1280,math.ceil(len(checks)/4)*250),"#fff8e6")
draw=ImageDraw.Draw(sheet)
for i,c in enumerate(checks):
    x=(i%4)*320;y=(i//4)*250
    im=Image.open(ROOT/c["path"]).convert("RGBA")
    thumb=ImageOps.contain(im,(300,205),Image.Resampling.LANCZOS)
    sheet.paste(thumb,(x+(320-thumb.width)//2,y+25+(205-thumb.height)//2),thumb)
    draw.text((x+10,y+4),c["id"]+"  "+str(c["size"][0])+"x"+str(c["size"][1]),font=font,fill="#3b2a1a")
sheet.save(R/"contact-sheet.jpg",quality=92)
print(json.dumps(dict(files=len(checks),size_alpha_pass=sum(c["size_pass"] and c["background_pass"] for c in checks),map_outside_changed_pixels=outside,max_native_map_shift=mapcheck["max_sample_displacement"]),ensure_ascii=False))
