# 依 map-taiwan-base.labels.json 在底圖上畫出縣市標籤預覽（審查用，不改正式底圖）
# -Variant desktop：名稱＋兩行數字；mobile：名稱＋一行數字。標籤以螢幕固定大小換算成地圖單位。
param(
  [ValidateSet('desktop', 'mobile')][string]$Variant = 'desktop',
  [string]$Out = ''
)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
$root = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
if (-not $Out) { $Out = "design/assets/review/A25/v3-user/label-overlay-$Variant.png" }
if (-not [IO.Path]::IsPathRooted($Out)) { $Out = Join-Path $root $Out }
$cfg = Get-Content (Join-Path $root 'design/assets/final/map-taiwan-base.labels.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$base = [Drawing.Bitmap]::new((Join-Path $root 'design/assets/final/map-taiwan-base.png'))
$size = $cfg.label_size.$Variant
$k = $base.Width / $cfg.viewBox[2]          # 地圖單位 → 底圖像素
$u = $size.units[0] / $size.px[0] * $k       # 螢幕 1px → 底圖像素
$img = [Drawing.Bitmap]::new($base.Width, $base.Height)
$g = [Drawing.Graphics]::FromImage($img)
$g.SmoothingMode = 'AntiAlias'; $g.TextRenderingHint = 'AntiAliasGridFit'
$g.DrawImage($base, 0, 0, $base.Width, $base.Height)

function RoundRect([float]$x, [float]$y, [float]$w, [float]$h, [float]$r) {
  $p = [Drawing.Drawing2D.GraphicsPath]::new()
  $p.AddArc($x, $y, 2 * $r, 2 * $r, 180, 90); $p.AddArc($x + $w - 2 * $r, $y, 2 * $r, 2 * $r, 270, 90)
  $p.AddArc($x + $w - 2 * $r, $y + $h - 2 * $r, 2 * $r, 2 * $r, 0, 90); $p.AddArc($x, $y + $h - 2 * $r, 2 * $r, 2 * $r, 90, 90)
  $p.CloseFigure(); return $p
}
$blue = [Drawing.Color]::FromArgb(37, 99, 235)
$navy = [Drawing.Color]::FromArgb(30, 41, 90)
$fmt = [Drawing.StringFormat]::new(); $fmt.Alignment = 'Center'; $fmt.LineAlignment = 'Center'
if ($Variant -eq 'desktop') { $headH = 34; $nameF = 18; $bodyF = 14 } else { $headH = 24; $nameF = 14; $bodyF = 11 }
$w = $size.px[0] * $u; $h = $size.px[1] * $u; $r = 10 * $u
foreach ($l in $cfg.labels) {
  $x = $l.x * $k - $w / 2; $y = $l.y * $k - $h / 2
  $c = $cfg.preview_counts.($l.county)
  $name = $l.county -replace '[市縣]$', ''
  $shadow = RoundRect ($x + 3 * $u) ($y + 4 * $u) $w $h $r
  $g.FillPath([Drawing.SolidBrush]::new([Drawing.Color]::FromArgb(60, 0, 40, 80)), $shadow)
  $card = RoundRect $x $y $w $h $r
  $g.FillPath([Drawing.Brushes]::White, $card)
  $g.SetClip($card); $g.FillRectangle([Drawing.SolidBrush]::new($blue), $x, $y, $w, $headH * $u); $g.ResetClip()
  $g.DrawPath([Drawing.Pen]::new($blue, [float](2.5 * $u)), $card)
  $f1 = [Drawing.Font]::new('Microsoft JhengHei', [float]($nameF * $u), [Drawing.FontStyle]::Bold, [Drawing.GraphicsUnit]::Pixel)
  $f2 = [Drawing.Font]::new('Microsoft JhengHei', [float]($bodyF * $u), [Drawing.FontStyle]::Bold, [Drawing.GraphicsUnit]::Pixel)
  $g.DrawString($name, $f1, [Drawing.Brushes]::White, [Drawing.RectangleF]::new($x, $y, $w, $headH * $u), $fmt)
  $body = [Drawing.RectangleF]::new($x, $y + $headH * $u, $w, $h - $headH * $u)
  if ($Variant -eq 'desktop') { $text = "$($c[0]) 個市場`n$($c[1]) 家攤商" } else { $text = "$($c[0]) 市場・$($c[1]) 攤" }
  $g.DrawString($text, $f2, [Drawing.SolidBrush]::new($navy), $body, $fmt)
}
$pen = [Drawing.Pen]::new([Drawing.Color]::FromArgb(230, 230, 110, 20), [float](4 * $k)); $pen.DashStyle = 'Dash'
foreach ($p in $cfg.reserved.PSObject.Properties) {
  $b = $p.Value
  $g.DrawRectangle($pen, $b[0] * $k, $b[1] * $k, ($b[2] - $b[0]) * $k, ($b[3] - $b[1]) * $k)
}
$g.Dispose()
$img.Save($Out, [Drawing.Imaging.ImageFormat]::Png)
"saved $Out"
