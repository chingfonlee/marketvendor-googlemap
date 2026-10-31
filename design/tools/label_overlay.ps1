# 依 map-taiwan-base.labels.json 在底圖上畫出標籤框，輸出審查用疊圖（不改正式底圖）
param([string]$Out = 'design/assets/review/A25/v3-user/label-overlay.png', [double]$BoxW = 0, [double]$BoxH = 0)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
$root = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$cfg = Get-Content (Join-Path $root 'design/assets/final/map-taiwan-base.labels.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$base = [Drawing.Bitmap]::new((Join-Path $root 'design/assets/final/map-taiwan-base.png'))
$k = $base.Width / $cfg.viewBox[2]
$img = [Drawing.Bitmap]::new($base.Width, $base.Height)
$g = [Drawing.Graphics]::FromImage($img)
$g.SmoothingMode = 'AntiAlias'; $g.TextRenderingHint = 'AntiAliasGridFit'
$g.DrawImage($base, 0, 0, $base.Width, $base.Height)
if ($BoxW -le 0) { $BoxW = $cfg.label_box[0] }; if ($BoxH -le 0) { $BoxH = $cfg.label_box[1] }
$w = $BoxW * $k; $h = $BoxH * $k
$fill = [Drawing.SolidBrush]::new([Drawing.Color]::FromArgb(235, 37, 99, 235))
$font = [Drawing.Font]::new('Microsoft JhengHei', [float](26 * $k), [Drawing.FontStyle]::Bold)
$fmt = [Drawing.StringFormat]::new(); $fmt.Alignment = 'Center'; $fmt.LineAlignment = 'Center'
foreach ($l in $cfg.labels) {
  $r = [Drawing.RectangleF]::new($l.x * $k - $w / 2, $l.y * $k - $h / 2, $w, $h)
  $g.FillRectangle($fill, $r)
  $g.DrawString($l.short, $font, [Drawing.Brushes]::White, $r, $fmt)
}
$pen = [Drawing.Pen]::new([Drawing.Color]::FromArgb(230, 230, 110, 20), [float](4 * $k))
$pen.DashStyle = 'Dash'
foreach ($p in $cfg.reserved.PSObject.Properties) {
  $b = $p.Value
  $g.DrawRectangle($pen, $b[0] * $k, $b[1] * $k, ($b[2] - $b[0]) * $k, ($b[3] - $b[1]) * $k)
}
$g.Dispose()
if (-not [IO.Path]::IsPathRooted($Out)) { $Out = Join-Path $root $Out }
$img.Save($Out, [Drawing.Imaging.ImageFormat]::Png)
"saved $Out"
