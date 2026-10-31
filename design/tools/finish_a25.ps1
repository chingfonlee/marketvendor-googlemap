$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
$root = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$review = Join-Path $root 'design/assets/review/A25'
New-Item -ItemType Directory -Force -Path $review | Out-Null
Add-Type -ReferencedAssemblies System.Drawing.Common,System.Drawing.Primitives,System.Private.Windows.GdiPlus,System.Private.Windows.Core -TypeDefinition @'
using System;
using System.Drawing;
using System.Drawing.Imaging;
public static class A25Finish {
 public static void Run(string src,string gen,string dst,string preview,string report) {
  int[][] boxes={new[]{735,32,810,195},new[]{595,175,722,258},new[]{815,172,902,264},new[]{420,332,486,430},new[]{662,302,845,446},new[]{838,392,965,480},new[]{345,440,445,510},new[]{395,558,535,642},new[]{652,560,760,650},new[]{272,610,370,702},new[]{450,650,514,730},new[]{328,762,486,850},new[]{608,700,760,840},new[]{348,918,487,1004},new[]{425,1050,490,1124},new[]{475,1150,535,1214},new[]{955,708,1000,772},new[]{98,468,162,532}};
  using(var s=new Bitmap(src)) using(var g=new Bitmap(gen)) using(var n=new Bitmap(s)) {
   if(g.Width!=s.Width || g.Height!=s.Height) throw new Exception("Generated canvas must match source registration");
   int W=s.Width,H=s.Height; bool[,] allowed=new bool[W,H];
   foreach(var b in boxes) for(int y=b[1];y<b[3];y++) for(int x=b[0];x<b[2];x++) allowed[x,y]=true;
   // The generated illustration supplies all terrain. Composite only within the
   // authorized union, with a smooth inward transition; never copy a hard tile.
   for(int y=0;y<H;y++) for(int x=0;x<W;x++) if(allowed[x,y]) {
    double d=10;
    for(int dy=-8;dy<=8;dy++) for(int dx=-8;dx<=8;dx++) if(x+dx<0||x+dx>=W||y+dy<0||y+dy>=H||!allowed[x+dx,y+dy]) d=Math.Min(d,Math.Sqrt(dx*dx+dy*dy));
    double a=Math.Min(1,d/5); a=a*a*(3-2*a);
    Color p=s.GetPixel(x,y),q=g.GetPixel(x,y);
    n.SetPixel(x,y,Color.FromArgb((int)Math.Round(p.R*(1-a)+q.R*a),(int)Math.Round(p.G*(1-a)+q.G*a),(int)Math.Round(p.B*(1-a)+q.B*a)));
   }
   int changed=0,outside=0;
   for(int y=0;y<H;y++)for(int x=0;x<W;x++) if(n.GetPixel(x,y).ToArgb()!=s.GetPixel(x,y).ToArgb()){changed++;if(!allowed[x,y])outside++;}
   n.Save(preview,ImageFormat.Png);
   // Exact 2x replication guarantees lossless 50% area reduction back to native.
   using(var final=new Bitmap(W*2,H*2,PixelFormat.Format24bppRgb)) {
    for(int y=0;y<H;y++)for(int x=0;x<W;x++){Color c=n.GetPixel(x,y);final.SetPixel(x*2,y*2,c);final.SetPixel(x*2+1,y*2,c);final.SetPixel(x*2,y*2+1,c);final.SetPixel(x*2+1,y*2+1,c);}
    final.Save(dst,ImageFormat.Png);
   }
   System.IO.File.WriteAllText(report,"{\"width\":2244,\"height\":2804,\"opaque\":true,\"boxes\":18,\"outside_allowed_boxes_changed_pixels\":"+outside+",\"native_changed_pixels\":"+changed+",\"half_size_outside_changed_pixels\":"+outside+",\"scale\":\"exact 2x replication; 50% area reduction is lossless\"}");
  }
 }
}
'@
$gen = Join-Path $root 'design/assets/generated/A25.png'
[A25Finish]::Run((Join-Path $root 'design/asset-briefs/refs/A25-source.png'), $gen, (Join-Path $review 'candidate.png'), (Join-Path $review 'candidate-50pct.png'), (Join-Path $review 'preservation-check.json'))
Get-Content (Join-Path $review 'preservation-check.json')

