# 依 map-taiwan-base.labels.json 在底圖上畫出縣市標籤預覽（審查用，不改正式底圖）
# 樣式照總覽完成圖：白色圓角卡片、內縮的藍色圓角標頭（攤車圖示＋縣市全名）、下方深藍數字。
# -Variant desktop：數字兩行；mobile：數字一行、標頭不放圖示。
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
function Brush($r, $g2, $b) { [Drawing.SolidBrush]::new([Drawing.Color]::FromArgb($r, $g2, $b)) }
# 攤車圖示：粉白條紋遮雨棚＋白色店面（只是預覽，網頁用 icons.svg）
function Stall([float]$x, [float]$y, [float]$s) {
  $g.FillRectangle([Drawing.Brushes]::White, $x + 0.12 * $s, $y + 0.42 * $s, 0.76 * $s, 0.5 * $s)
  $g.FillRectangle((Brush 70 90 140), $x + 0.25 * $s, $y + 0.6 * $s, 0.5 * $s, 0.12 * $s)
  for ($i = 0; $i -lt 4; $i++) {
    $b = if ($i % 2 -eq 0) { Brush 242 139 168 } else { [Drawing.Brushes]::White }
    $g.FillRectangle($b, $x + $i * 0.25 * $s, $y + 0.08 * $s, 0.25 * $s, 0.34 * $s)
  }
}
$blue = Brush 22 96 190
$navy = Brush 23 32 64
$fmt = [Drawing.StringFormat]::new(); $fmt.Alignment = 'Center'; $fmt.LineAlignment = 'Center'
if ($Variant -eq 'desktop') { $pad = 4; $headH = 34; $nameF = 18; $bodyF = 15; $icon = 22 } else { $pad = 3; $headH = 24; $nameF = 13; $bodyF = 11; $icon = 0 }
$w = $size.px[0] * $u; $h = $size.px[1] * $u
foreach ($l in $cfg.labels) {
  $x = $l.x * $k - $w / 2; $y = $l.y * $k - $h / 2
  $c = $cfg.preview_counts.($l.county)
  $g.FillPath([Drawing.SolidBrush]::new([Drawing.Color]::FromArgb(70, 10, 50, 90)), (RoundRect $x ($y + 3 * $u) $w $h (12 * $u)))
  $card = RoundRect $x $y $w $h (12 * $u)
  $g.FillPath([Drawing.Brushes]::White, $card)
  $g.DrawPath([Drawing.Pen]::new([Drawing.Color]::FromArgb(205, 222, 240), [float](1.2 * $u)), $card)
  $hx = $x + $pad * $u; $hy = $y + $pad * $u; $hw = $w - 2 * $pad * $u; $hh = $headH * $u
  $g.FillPath($blue, (RoundRect $hx $hy $hw $hh (9 * $u)))
  $f1 = [Drawing.Font]::new('Microsoft JhengHei', [float]($nameF * $u), [Drawing.FontStyle]::Bold, [Drawing.GraphicsUnit]::Pixel)
  $f2 = [Drawing.Font]::new('Microsoft JhengHei', [float]($bodyF * $u), [Drawing.FontStyle]::Bold, [Drawing.GraphicsUnit]::Pixel)
  if ($icon -gt 0) {
    $tw = $g.MeasureString($l.county, $f1).Width
    $gap = 4 * $u; $total = $icon * $u + $gap + $tw
    $ix = $hx + ($hw - $total) / 2
    Stall $ix ($hy + ($hh - $icon * $u) / 2) ($icon * $u)
    $g.DrawString($l.county, $f1, [Drawing.Brushes]::White, [Drawing.RectangleF]::new($ix + $icon * $u + $gap - 0.15 * $tw, $hy, $tw * 1.3, $hh), $fmt)
  } else {
    $g.DrawString($l.county, $f1, [Drawing.Brushes]::White, [Drawing.RectangleF]::new($hx, $hy, $hw, $hh), $fmt)
  }
  $body = [Drawing.RectangleF]::new($x, $hy + $hh, $w, $y + $h - ($hy + $hh))
  if ($Variant -eq 'desktop') { $text = "$($c[0]) 個市場`n$($c[1]) 家攤商" } else { $text = "$($c[0]) 市場・$($c[1]) 攤" }
  $g.DrawString($text, $f2, $navy, $body, $fmt)
}
$pen = [Drawing.Pen]::new([Drawing.Color]::FromArgb(230, 230, 110, 20), [float](4 * $k)); $pen.DashStyle = 'Dash'
foreach ($p in $cfg.reserved.PSObject.Properties) {
  $b = $p.Value
  $g.DrawRectangle($pen, $b[0] * $k, $b[1] * $k, ($b[2] - $b[0]) * $k, ($b[3] - $b[1]) * $k)
}
$g.Dispose()
$img.Save($Out, [Drawing.Imaging.ImageFormat]::Png)
"saved $Out"
