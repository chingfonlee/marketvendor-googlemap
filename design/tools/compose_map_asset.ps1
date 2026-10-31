# Composite imagegen-created market details only inside the brief's fixed boxes.
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
$rootPath = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$sourcePath = Join-Path $rootPath 'design/reference/map-v2/map-taiwan-clean.png'
$generatedPath = Join-Path $rootPath 'design/assets/generated/A01.png'
$sourceImage = [System.Drawing.Bitmap]::new($sourcePath)
$generatedImage = [System.Drawing.Bitmap]::new($generatedPath)
$canvas = [System.Drawing.Bitmap]::new(2244,2804,[System.Drawing.Imaging.PixelFormat]::Format24bppRgb)
$graphics = [System.Drawing.Graphics]::FromImage($canvas)
$graphics.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
$graphics.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality
$imageAttributes = [System.Drawing.Imaging.ImageAttributes]::new()
$imageAttributes.SetWrapMode([System.Drawing.Drawing2D.WrapMode]::TileFlipXY)
$graphics.DrawImage($sourceImage,[System.Drawing.Rectangle]::new(0,0,2244,2804),0,0,$sourceImage.Width,$sourceImage.Height,[System.Drawing.GraphicsUnit]::Pixel,$imageAttributes)
$imageAttributes.Dispose()
$canvas.Save((Join-Path $rootPath 'design/assets/review/A01-source-2x.png'),[System.Drawing.Imaging.ImageFormat]::Png)
# source crop and destination in native 1122x1402 coordinates.
$patches = @(
    @{name='traditional-north'; src=@(566,182,180,94); dst=@(595,180,127,72)},
    @{name='traditional-central'; src=@(382,561,168,92); dst=@(395,560,137,78)},
    @{name='traditional-south'; src=@(330,915,176,103); dst=@(350,920,132,82)},
    @{name='night-east-cart-red'; src=@(825,441,42,43); dst=@(841,447,20,28)},
    @{name='night-east-cart-blue'; src=@(910,445,45,39); dst=@(940,447,21,28)},
    @{name='night-west-cart-red'; src=@(310,812,43,52); dst=@(331,815,21,30)},
    @{name='night-west-cart-blue'; src=@(450,818,45,46); dst=@(460,815,21,30)}
)
foreach ($p in $patches) {
    $s=$p.src; $d=$p.dst
    $destRect=[System.Drawing.Rectangle]::new(($d[0]*2),($d[1]*2),($d[2]*2),($d[3]*2))
    $graphics.DrawImage($generatedImage,$destRect,$s[0],$s[1],$s[2],$s[3],[System.Drawing.GraphicsUnit]::Pixel)
}
$graphics.Dispose()
$destPath=Join-Path $rootPath 'design/assets/final/map-taiwan-market.png'
if (Test-Path -LiteralPath $destPath) { throw "Refusing to overwrite $destPath" }
$canvas.Save($destPath,[System.Drawing.Imaging.ImageFormat]::Png)
$canvas.Dispose(); $sourceImage.Dispose(); $generatedImage.Dispose()
$patches | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $rootPath 'design/assets/review/A01-composite-patches.json') -Encoding utf8
Write-Output $destPath
