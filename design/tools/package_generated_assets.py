"""Package generated images at manifest dimensions without changing artwork."""
from pathlib import Path
import json, shutil, hashlib
from PIL import Image, ImageOps
ROOT = Path(__file__).resolve().parents[2]
REVIEW = ROOT / "design/assets/review"
manifest = {a["id"]: a for a in json.loads((ROOT / "design/asset-briefs/manifest.json").read_text(encoding="utf-8"))}
records = json.loads((REVIEW / "generation-records.json").read_text(encoding="utf-8"))
checks=[]
for r in records:
    a=manifest[r["id"]]
    src=Path(r["source"])
    slug=r.get("category")
    ident=a["id"]+("-"+slug if slug else "")
    raw=ROOT/"design/assets/generated"/(ident+".png")
    if not raw.exists(): shutil.copy2(src,raw)
    im=Image.open(src).convert("RGBA")
    w,h=a["output"]["width"],a["output"]["height"]
    transparent=a["output"]["background"]=="透明"
    if transparent and a["id"]!="A22":
        bbox=im.getchannel("A").point(lambda p:255 if p>8 else 0).getbbox()
        if bbox: im=im.crop(bbox)
        inset=0.10 if a["id"]=="A18" else 0.02
        fit=ImageOps.contain(im,(round(w*(1-2*inset)),round(h*(1-2*inset))),Image.Resampling.LANCZOS)
        out=Image.new("RGBA",(w,h),(0,0,0,0))
        out.alpha_composite(fit,((w-fit.width)//2,(h-fit.height)//2))
    else:
        out=im.resize((w,h),Image.Resampling.LANCZOS)
    if not transparent: out=out.convert("RGB")
    rel=a["deliver_to"].replace("<品類>",slug or "<品類>")
    dest=ROOT/rel if a["id"]!="A01" else REVIEW/"map-taiwan-market-candidate.png"
    dest.parent.mkdir(parents=True,exist_ok=True)
    if dest.exists():
        existing=Image.open(dest)
        if existing.size!=out.size or existing.mode!=out.mode or existing.tobytes()!=out.tobytes():
            raise RuntimeError(f"Refuse to overwrite different existing asset: {dest}")
    else: out.save(dest)
    result=Image.open(dest)
    alpha=result.convert("RGBA").getchannel("A")
    corners=[alpha.getpixel(p) for p in [(0,0),(w-1,0),(0,h-1),(w-1,h-1)]]
    checks.append({"id":ident,"path":dest.relative_to(ROOT).as_posix(),"size":list(result.size),"expected":[w,h],"size_pass":result.size==(w,h),"mode":result.mode,"corners_alpha":corners,"background_pass":all(x==0 for x in corners) if transparent else alpha.getextrema()==(255,255),"sha256":hashlib.sha256(dest.read_bytes()).hexdigest()})
(REVIEW/"technical-checks.json").write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"packaged":len(checks),"technical_pass":sum(x["size_pass"] and x["background_pass"] for x in checks)}))
