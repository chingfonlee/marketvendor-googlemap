"""A25 v3: official county tracing, review guides, and explicit AI super-resolution.

Image content cleanup is done by image_gen. This tool fits the official county
geometry and produces the overlays requested in A25-v3-prompt.md.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

DEPS = Path.home() / '.codex/tmp/a25-v3-deps'
CV = Path.home() / '.codex/tmp/a25-v3-cv'
sys.path[:0] = [str(CV), str(DEPS)]
import cv2
import numpy as np
import shapefile
from PIL import Image, ImageDraw, ImageFont
from shapely import make_valid, set_precision
from shapely.geometry import shape, LineString, Polygon
from shapely.ops import unary_union, linemerge
from scipy.interpolate import RBFInterpolator
from scipy.spatial import cKDTree

ROOT = Path(__file__).resolve().parents[2]
REVIEW = ROOT / 'design/assets/review/A25/v3'
SOURCE = REVIEW / 'source'
V2 = REVIEW / 'v2-baseline.png'
FORMAL = ROOT / 'design/assets/final/map-taiwan-base.png'
W, H = 2244, 2804
ZONES = [('臺北', (1240,150,1660,350)), ('新北',(1690,540,2110,740)),
         ('桃園',(910,420,1330,620)), ('新竹市',(650,780,1070,980)),
         ('臺中',(550,1100,970,1300)), ('臺南',(350,1600,770,1800)),
         ('高雄',(490,1980,910,2180)), ('臺東',(1230,1800,1650,2000))]
EMPTY = [(0,0,880,740),(1680,2380,2244,2804)]

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def font(size):
    return ImageFont.truetype('C:/Windows/Fonts/msjh.ttc',size)

def land_mask(path):
    a = np.asarray(Image.open(path).convert('RGB')).astype(np.int16)
    r,g,b = a[:,:,0],a[:,:,1],a[:,:,2]
    m = ((r>b+25)&(g>b+20)).astype(np.uint8)*255
    m = cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((15,15),np.uint8))
    contours,_ = cv2.findContours(m,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    contour = max(contours,key=cv2.contourArea)
    result = np.zeros((H,W),np.uint8)
    cv2.drawContours(result,[contour],-1,255,cv2.FILLED)
    return result, contour

def polygons(geom):
    if geom.geom_type == 'Polygon': return [geom]
    if hasattr(geom,'geoms'):
        return [p for g in geom.geoms for p in polygons(g)]
    return []

def lines(geom):
    if geom.geom_type in ('LineString','LinearRing'): return [geom]
    if hasattr(geom,'geoms'): return [p for g in geom.geoms for p in lines(g)]
    return []

def layout(image, dst):
    image = image.copy().convert('RGB'); d = ImageDraw.Draw(image)
    for name,box in ZONES:
        d.rectangle(box,outline='#1558cb',width=5)
        d.text((box[0]+8,box[1]+8),name,font=font(32),fill='#123d9a')
    for box in EMPTY: d.rectangle(box,outline='#ca5b17',width=5)
    image.save(dst)

def prepare():
    REVIEW.mkdir(parents=True,exist_ok=True)
    counties = {}
    reader = shapefile.Reader(str(SOURCE/'county-official/COUNTY_MOI_1090820.shp'),encoding='utf-8')
    for row in reader.iterShapeRecords():
        name = row.record.as_dict()['COUNTYNAME']
        if name in ('連江縣','金門縣','澎湖縣'): continue
        # Normalize sub-metre coordinate noise so mathematically shared borders
        # do not disappear because of floating-point differences in the SHP.
        counties[name] = set_precision(max(polygons(make_valid(shape(row.shape.__geo_interface__))),key=lambda p:p.area),1e-6)
    mainland = max(polygons(unary_union(list(counties.values()))),key=lambda p:p.area)
    assert len(counties)==19
    mask, contour = land_mask(V2)
    ys=np.flatnonzero(mask.any(axis=1)); ymin,ymax=int(ys[0]),int(ys[-1])
    lonmin,latmin,lonmax,latmax = mainland.bounds
    xmin,xmax=np.where(mask)[1].min(),np.where(mask)[1].max()
    def affine(coords):
        a=np.asarray(coords)
        return np.stack([(a[:,0]-lonmin)/(lonmax-lonmin)*(xmax-xmin)+xmin,
                         (latmax-a[:,1])/(latmax-latmin)*(ymax-ymin)+ymin],axis=1)
    def coast_halves(coords):
        coords=np.asarray(coords)
        if np.array_equal(coords[0],coords[-1]): coords=coords[:-1]
        north=int(np.argmin(coords[:,1])); south=int(np.argmax(coords[:,1]))
        chain=np.concatenate([coords[north:],coords[:north]])
        south=(south-north)%len(coords)
        a=chain[:south+1]; b=np.concatenate([chain[south:],chain[:1]])[::-1]
        return sorted([a,b],key=lambda p:p[:,0].mean())
    def sample(chain,n=33):
        distance=np.r_[0,np.cumsum(np.linalg.norm(np.diff(chain,axis=0),axis=1))]
        t=np.linspace(0,distance[-1],n)
        return np.stack([np.interp(t,distance,chain[:,0]),np.interp(t,distance,chain[:,1])],axis=1)
    real_halves=coast_halves(affine(mainland.exterior.coords))
    target_halves=coast_halves(contour[:,0,:])
    controls=np.concatenate([sample(real_halves[0]),sample(real_halves[1])[1:-1]])
    targets=np.concatenate([sample(target_halves[0]),sample(target_halves[1])[1:-1]])
    fit=RBFInterpolator(controls,targets,kernel='thin_plate_spline',smoothing=2)
    def warp(coords): return fit(affine(coords))
    shore_tree=cKDTree(contour[:,0,:])
    # Shared boundaries are extracted from original polygons before simplification.
    # This preserves the real adjacency graph rather than inventing white lines.
    shared=[]; adjacency=[]
    names=list(counties)
    for i,name in enumerate(names):
        for other in names[i+1:]:
            edge=counties[name].boundary.intersection(counties[other].boundary)
            if edge.length < .0001: continue
            adjacency.append([name,other])
            if edge.geom_type=='MultiLineString': edge=linemerge(edge)
            for part in lines(edge):
                if part.length < .00002: continue
                part=part.simplify(.0005).segmentize(.001)
                points=warp(part.coords)
                for index in (0,-1):
                    from shapely.geometry import Point
                    if mainland.exterior.distance(Point(part.coords[index]))<.00002:
                        _,nearest=shore_tree.query(points[index]); points[index]=contour[nearest,0,:]
                indices=np.rint(points).astype(int)
                inside=(indices[:,0]>=0)&(indices[:,0]<W)&(indices[:,1]>=0)&(indices[:,1]<H)
                for index in range(len(points)):
                    if not inside[index] or mask[indices[index,1],indices[index,0]]==0:
                        _,nearest=shore_tree.query(points[index]); points[index]=contour[nearest,0,:]
                shared.append({'counties':[name,other],'points':points.round(3).tolist()})
    rings={}
    centers={}
    for name,poly in counties.items():
        p=poly.simplify(.0002,preserve_topology=True).segmentize(.001)
        rings[name]={'exterior':warp(p.exterior.coords).round(3).tolist(),
                     'holes':[warp(r.coords).round(3).tolist() for r in p.interiors]}
        center=poly.representative_point(); centers[name]=warp([[center.x,center.y]])[0].tolist()
    data={'source_shapefile':'COUNTY_MOI_1090820.shp','source_zip_sha256':sha(SOURCE/'county-official.zip'),
          'method':'Bounding-box affine registration followed by smooth thin-plate spline fit to 64 paired coastline controls; north/south tips and separate west/east coast arcs matched. Real shared boundaries retain their original adjacency.',
          'county_count':len(counties),'county_names':names,'adjacency':adjacency,'lines':shared,'rings':rings,'centers':centers,
          'note':'Geographic county topology preserved; illustration deformation is decorative, not survey-grade.'}
    (REVIEW/'county-fit.json').write_text(json.dumps(data,ensure_ascii=False),encoding='utf-8')
    guide=Image.new('RGB',(W,H),'#6dd7f2')
    guide.paste(Image.new('RGB',(W,H),'#d9eb9d'),(0,0),Image.fromarray(mask))
    d=ImageDraw.Draw(guide)
    d.line([tuple(x[0]) for x in contour],fill='#60402a',width=5)
    for item in shared: d.line([tuple(p) for p in item['points']],fill='#ffffff',width=5)
    guide.save(REVIEW/'county-tracing-guide.png')
    named=guide.copy(); d=ImageDraw.Draw(named)
    for name,center in centers.items():
        d.text(tuple(center),name,font=font(24),fill='#6e2d24',anchor='mm',stroke_width=2,stroke_fill='#fff8e6')
    named.save(REVIEW/'county-tracing-guide-named.png')
    layout(Image.open(V2),REVIEW/'v2-label-cleanup-guide.png')
    print(json.dumps({'counties':len(counties),'shared_lines':len(shared),'adjacent_pairs':len(adjacency),'guide':str(REVIEW/'county-tracing-guide.png')}))

def finish(raw):
    raw=Path(raw)
    generated=ROOT/'design/assets/generated'
    raw_image=Image.open(raw).convert('RGB')
    raw_image.save(generated/'A25-v3-01-raw.png')
    source_size=raw_image.size
    if source_size==(W,H):
        terrain=raw_image
        method='Native requested resolution; no upscaling'
    else:
        # FSRCNN learns the output luminance with convolutions and sub-pixel
        # reconstruction; this is not a bicubic-only resize.
        sr=cv2.dnn_superres.DnnSuperResImpl_create()
        sr.readModel(str(SOURCE/'FSRCNN_x2.pb')); sr.setModel('fsrcnn',2)
        a=cv2.cvtColor(np.asarray(raw_image),cv2.COLOR_RGB2BGR)
        passes=0
        while a.shape[1]<W or a.shape[0]<H:
            a=sr.upsample(a); passes+=1
        terrain=Image.fromarray(cv2.cvtColor(a,cv2.COLOR_BGR2RGB))
        pre_downsample_size=terrain.size
        if terrain.size!=(W,H): terrain=terrain.resize((W,H),Image.Resampling.LANCZOS)
        method=f'FSRCNN x2 learned neural super-resolution, {passes} pass(es); output before final size normalization {pre_downsample_size}; Lanczos used only for final downsampling if required'
    terrain.save(REVIEW/'terrain-ai-upscaled.png')
    data=json.loads((REVIEW/'county-fit.json').read_text(encoding='utf-8'))
    # The user explicitly requests tracing and fitting real county lines.
    # Draw these from the government geometry, not from a generated approximation.
    scale=3
    layer=Image.new('RGBA',(W*scale,H*scale),(0,0,0,0)); d=ImageDraw.Draw(layer)
    for item in data['lines']:
        points=[(round(p[0]*scale),round(p[1]*scale)) for p in item['points']]
        d.line(points,fill=(255,255,245,215),width=4*scale,joint='curve')
    layer=layer.resize((W,H),Image.Resampling.LANCZOS)
    original_land,_=land_mask(V2)
    barriers=np.asarray(layer)[:,:,3]>=100
    # Exclude one antialiased coastline pixel, which can otherwise connect two
    # counties through the external fringe despite both borders meeting shore.
    interior_land=cv2.erode(original_land,np.ones((3,3),np.uint8))
    region_n,region_labels,region_stats,_=cv2.connectedComponentsWithStats(((interior_land>0)&~barriers).astype(np.uint8),8)
    region_areas=sorted([int(a) for a in region_stats[1:,cv2.CC_STAT_AREA] if a>=100],reverse=True)
    candidate=Image.alpha_composite(terrain.convert('RGBA'),layer).convert('RGB')
    candidate.save(REVIEW/'candidate.png'); candidate.save(generated/'A25-v3-01.png')
    layout(candidate,REVIEW/'label-layout-overlay.png')
    check=candidate.copy(); d=ImageDraw.Draw(check)
    for item in data['lines']:
        d.line([tuple(p) for p in item['points']],fill='#df4b70',width=3)
    for name,center in data['centers'].items():
        d.text(tuple(center),name,font=font(25),fill='#6b1e30',anchor='mm',stroke_width=2,stroke_fill='#fff8e6')
    check.save(REVIEW/'county-border-overlay.png')
    # Review crop is 1 output pixel = 1 image pixel; never rescale the crops.
    crops=Image.new('RGB',(1280,680),'white'); d=ImageDraw.Draw(crops)
    d.text((12,8),'北端 100%（x=1200, y=80）',font=font(24),fill='#222222')
    d.text((652,8),'西南海岸 100%（x=320, y=1850）',font=font(24),fill='#222222')
    crops.paste(candidate.crop((1200,80,1840,720)),(0,40))
    crops.paste(candidate.crop((320,1850,960,2490)),(640,40))
    crops.save(REVIEW/'crop-100pct.png')
    sheet=Image.new('RGB',(1122,741),'white'); d=ImageDraw.Draw(sheet)
    d.text((12,6),'v2',font=font(24),fill='#222222'); d.text((573,6),'v3',font=font(24),fill='#222222')
    sheet.paste(Image.open(V2).resize((561,701),Image.Resampling.LANCZOS),(0,40))
    sheet.paste(candidate.resize((561,701),Image.Resampling.LANCZOS),(561,40))
    sheet.save(REVIEW/'v2-v3-diff.png')
    rectangles=[b for _,b in ZONES]
    overlap=lambda a,b: max(a[0],b[0])<min(a[2],b[2]) and max(a[1],b[1])<min(a[3],b[3])
    info={'native_generated_size':source_size,'delivered_size':candidate.size,'mode':candidate.mode,
          'upscale_method':method,'superres_model_sha256':sha(SOURCE/'FSRCNN_x2.pb'),
          'borders':'Official county polygons; shared edges only; 3x antialiased vector rasterization',
          'county_count':data['county_count'],'county_names':data['county_names'],
          'raster_county_regions_area_ge_100px':len(region_areas),'raster_region_areas':region_areas,'raster_check_coast_inset_px':1,
          'label_boxes':dict(ZONES),'label_boxes_overlap':any(overlap(a,b) for i,a in enumerate(rectangles) for b in rectangles[i+1:]),
          'label_boxes_overlap_upperleft':any(overlap(a,EMPTY[0]) for a in rectangles),
          'candidate_sha256':sha(REVIEW/'candidate.png'),'v2_formal_sha256':sha(V2),
          'current_formal_asset_sha256':sha(FORMAL),'baseline_path':str(V2.relative_to(ROOT)),
          'formal_asset_replaced':False}
    (REVIEW/'technical-checks.json').write_text(json.dumps(info,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(info,ensure_ascii=True,indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('mode',choices=['prepare','finish']); parser.add_argument('--raw')
    args=parser.parse_args()
    if args.mode=='prepare': prepare()
    else: finish(args.raw)
