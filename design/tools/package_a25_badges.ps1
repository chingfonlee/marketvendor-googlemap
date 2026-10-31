param([Parameter(Mandatory=$true)][string]$GeneratedPath,[string]$Version='v3')
$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Drawing
$root=Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$review=Join-Path $root 'design/assets/review/A25'
$raw=Join-Path $root "design/assets/generated/A25-badges-$Version.png"
Copy-Item -LiteralPath $GeneratedPath -Destination $raw
$im=[Drawing.Bitmap]::new($raw)
$out=[Drawing.Bitmap]::new(2244,2804,[Drawing.Imaging.PixelFormat]::Format24bppRgb)
$g=[Drawing.Graphics]::FromImage($out)
$g.InterpolationMode=[Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
$g.PixelOffsetMode=[Drawing.Drawing2D.PixelOffsetMode]::HighQuality
$attr=[Drawing.Imaging.ImageAttributes]::new()
$attr.SetWrapMode([Drawing.Drawing2D.WrapMode]::TileFlipXY)
$g.DrawImage($im,[Drawing.Rectangle]::new(0,0,2244,2804),0,0,$im.Width,$im.Height,[Drawing.GraphicsUnit]::Pixel,$attr)
$g.Dispose();$attr.Dispose()
$out.Save((Join-Path $review 'badge-candidate.png'),[Drawing.Imaging.ImageFormat]::Png)
$small=[Drawing.Bitmap]::new(1122,1402)
$g=[Drawing.Graphics]::FromImage($small);$g.DrawImage($out,0,0,1122,1402);$g.Dispose()
$small.Save((Join-Path $review 'badge-candidate-50pct.png'),[Drawing.Imaging.ImageFormat]::Png)
$script=Get-Content (Join-Path $root 'design/tools/make_asset_refs.py') -Raw
$layout=([regex]::Match($script,'"map_layout": \{"ui": \[(.*?)\],\s*"replace"',[Text.RegularExpressions.RegexOptions]::Singleline)).Groups[1].Value
$matches=[regex]::Matches($layout,'\((\d+), (\d+), (\d+), (\d+), "([^"]+)"\)')
if($matches.Count -ne 22){throw 'Expected 22 badge regions'}
$overlay=[Drawing.Bitmap]::new($small)
$g=[Drawing.Graphics]::FromImage($overlay)
$pen=[Drawing.Pen]::new([Drawing.Color]::Blue,2)
$font=[Drawing.Font]::new('Microsoft JhengHei',12)
$sheet=[Drawing.Bitmap]::new(880,720);$sg=[Drawing.Graphics]::FromImage($sheet);$sg.Clear([Drawing.Color]::White)
$regions=@()
for($i=0;$i -lt $matches.Count;$i++){
 $m=$matches[$i];$x=[int]$m.Groups[1].Value;$y=[int]$m.Groups[2].Value;$w=[int]$m.Groups[3].Value-$x;$h=[int]$m.Groups[4].Value-$y;$name=$m.Groups[5].Value
 $g.DrawRectangle($pen,$x,$y,$w,$h);$g.DrawString($name,$font,[Drawing.Brushes]::Blue,$x,$y)
 $tx=($i%6)*145;$ty=[math]::Floor($i/6)*180
 $sg.DrawString($name,$font,[Drawing.Brushes]::Black,$tx,$ty)
 $sg.DrawImage($small,[Drawing.Rectangle]::new($tx,($ty+25),120,120),$x,$y,$w,$h,[Drawing.GraphicsUnit]::Pixel)
 $regions+=@{name=$name;native_rectangle=@($x,$y,($x+$w),($y+$h))}
}
$g.Dispose();$sg.Dispose()
$overlay.Save((Join-Path $review 'badge-layout-overlay.png'),[Drawing.Imaging.ImageFormat]::Png)
$sheet.Save((Join-Path $review 'badge-zones-contact.png'),[Drawing.Imaging.ImageFormat]::Png)
@{width=$out.Width;height=$out.Height;opaque=$true;badge_region_count=$matches.Count;regions=$regions;generated_original_size=@($im.Width,$im.Height);sha256=(Get-FileHash (Join-Path $review 'badge-candidate.png') -Algorithm SHA256).Hash} | ConvertTo-Json -Depth 8 | Set-Content (Join-Path $review 'badge-technical-checks.json')
$small.Dispose();$overlay.Dispose();$sheet.Dispose();$out.Dispose();$im.Dispose();$pen.Dispose();$font.Dispose()
