$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Drawing
$root=Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$review=Join-Path $root 'design/assets/review/A25/shape-revision'
$files=@('design/asset-briefs/refs/A25-source.png','design/assets/review/A25/shape-revision/before-map-taiwan-base.png','design/assets/review/A25/badge-candidate.png')
$labels=@('REFERENCE','PREVIOUS - REJECTED SHAPE','REVISED')
$sheet=[Drawing.Bitmap]::new(1344,600)
$g=[Drawing.Graphics]::FromImage($sheet);$g.Clear([Drawing.Color]::White)
$g.InterpolationMode=[Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
$font=[Drawing.Font]::new('Arial',13)
for($i=0;$i -lt 3;$i++){
 $im=[Drawing.Bitmap]::new((Join-Path $root $files[$i]))
 $g.DrawString($labels[$i],$font,[Drawing.Brushes]::Black,($i*448+10),5)
 $g.DrawImage($im,[Drawing.Rectangle]::new(($i*448),35,448,560))
 $im.Dispose()
}
$g.Dispose();$font.Dispose()
$sheet.Save((Join-Path $review 'reference-before-after.png'),[Drawing.Imaging.ImageFormat]::Png)
$sheet.Dispose()
