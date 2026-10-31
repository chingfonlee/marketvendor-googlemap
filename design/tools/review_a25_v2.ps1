param([Parameter(Mandatory=$true)][string]$Source,[string]$Version='01')
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
$root = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$review = Join-Path $root 'design/assets/review/A25/v2'
New-Item -ItemType Directory -Force $review | Out-Null
$original = [Drawing.Bitmap]::new($Source)
$candidate = [Drawing.Bitmap]::new(2244,2804,[Drawing.Imaging.PixelFormat]::Format24bppRgb)
$g = [Drawing.Graphics]::FromImage($candidate)
$g.Clear([Drawing.Color]::FromArgb(109,215,242))
$g.InterpolationMode = [Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
$g.DrawImage($original,[Drawing.Rectangle]::new(0,0,2244,2804))
$g.Dispose()
$candidate.Save((Join-Path $review 'candidate.png'),[Drawing.Imaging.ImageFormat]::Png)
$candidate.Save((Join-Path $root "design/assets/generated/A25-v2-$Version.png"),[Drawing.Imaging.ImageFormat]::Png)
$overlay = [Drawing.Bitmap]::new($candidate)
$g = [Drawing.Graphics]::FromImage($overlay)
$pen = [Drawing.Pen]::new([Drawing.Color]::FromArgb(230,20,80,220),5)
$font = [Drawing.Font]::new('Microsoft JhengHei',30)
$zones = @(@('臺北',1520,300),@('新北',1800,460),@('桃園',1120,520),@('新竹市',840,800),@('臺中',760,1200),@('臺南',660,1800),@('高雄',760,2000),@('臺東',1440,1900))
foreach($zone in $zones){
 $x=[int]$zone[1]-180; $y=[int]$zone[2]-115
 $g.DrawRectangle($pen,$x,$y,360,230)
 $g.DrawString([string]$zone[0],$font,[Drawing.Brushes]::DarkBlue,$x+10,$y+8)
}
$emptyPen=[Drawing.Pen]::new([Drawing.Color]::FromArgb(230,200,80,20),5)
$g.DrawRectangle($emptyPen,2,2,894,837)
$g.DrawRectangle($emptyPen,1683,2383,558,418)
$g.Dispose(); $overlay.Save((Join-Path $review 'label-layout-overlay.png'),[Drawing.Imaging.ImageFormat]::Png)
$reference=[Drawing.Bitmap]::new((Join-Path $root 'design/reference/map-v2/map-taiwan-clean.png'))
$comparison=[Drawing.Bitmap]::new(1683,741,[Drawing.Imaging.PixelFormat]::Format24bppRgb)
$g=[Drawing.Graphics]::FromImage($comparison); $g.Clear([Drawing.Color]::White)
$g.InterpolationMode=[Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
$smallFont=[Drawing.Font]::new('Arial',16)
$g.DrawString('REFERENCE',$smallFont,[Drawing.Brushes]::Black,8,6)
$g.DrawString('CANDIDATE',$smallFont,[Drawing.Brushes]::Black,569,6)
$g.DrawString('50% OVERLAY',$smallFont,[Drawing.Brushes]::Black,1130,6)
$g.DrawImage($reference,[Drawing.Rectangle]::new(0,40,561,701))
$g.DrawImage($candidate,[Drawing.Rectangle]::new(561,40,561,701))
$g.DrawImage($reference,[Drawing.Rectangle]::new(1122,40,561,701))
$matrix=[Drawing.Imaging.ColorMatrix]::new(); $matrix.Matrix33=0.5
$attributes=[Drawing.Imaging.ImageAttributes]::new(); $attributes.SetColorMatrix($matrix)
$g.DrawImage($candidate,[Drawing.Rectangle]::new(1122,40,561,701),0,0,2244,2804,[Drawing.GraphicsUnit]::Pixel,$attributes)
$g.Dispose(); $comparison.Save((Join-Path $review 'shape-comparison.png'),[Drawing.Imaging.ImageFormat]::Png)
$info=[ordered]@{width=$candidate.Width;height=$candidate.Height;pixel_format=$candidate.PixelFormat.ToString();opaque=$true;source_width=$original.Width;source_height=$original.Height;normalization='HighQualityBicubic resize to requested canvas; opaque RGB encoding only';label_box_size=@(360,230);candidate_sha256=(Get-FileHash (Join-Path $review 'candidate.png')).Hash;formal_asset_sha256=(Get-FileHash (Join-Path $root 'design/assets/final/map-taiwan-base.png')).Hash}
$info | ConvertTo-Json -Depth 4 | Set-Content (Join-Path $review 'technical-checks.json') -Encoding utf8
$original.Dispose();$candidate.Dispose();$overlay.Dispose();$reference.Dispose();$comparison.Dispose();$pen.Dispose();$font.Dispose();$emptyPen.Dispose();$smallFont.Dispose();$attributes.Dispose()
$info | ConvertTo-Json
