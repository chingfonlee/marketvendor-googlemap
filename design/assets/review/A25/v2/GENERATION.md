# A25 v2 生成紀錄

- 日期：2026-10-31（Asia/Taipei）。
- 工具：內建 `image_gen.imagegen`，不透明背景。
- 任務來源：`design/asset-briefs/A25-v2-prompt.md`。附件儀表板僅供整體風格參考。
- 第一次輸入：`design/reference/map-v2/map-taiwan-clean.png`，作為編輯目標，保留本島輪廓、位置及界線。
- 第一次原始輸出：`C:/Users/user/.codex/generated_images/01a191e7-7fe8-7741-9dc9-325495f5be19/exec-81d58bec-e7cc-45cf-93ba-9dd692e3beae.png`。
- 第二次輸入：第一張候選圖及其標籤疊圖；疊圖只作為清空區域的導引，不是成品內容。
- 第二次生成在使用者要求停止修改後中止等待，沒有採用其輸出；正式交付仍是第一張候選圖。
- 成品只做尺寸正規化與 RGB 編碼，不以程式修改插畫內容。原始輸出保留。

## 第一次實際提示詞

```text
Use case: precise-object-edit. Create A25 v2, a quiet hand-drawn Taiwan web app base map. EDIT THE PROVIDED MAP. Preserve its MAIN ISLAND coastline, exact silhouette, tilt, proportions and placement: north upper right, pointed south at bottom, curved west coast. Output target 2244x2804 portrait matching reference aspect ratio. Remove ALL offshore islands and ALL existing contents from land and sea except mainland coast and the decorative white county border network. Replace land with pale light-green flat plains, much lighter and less detailed. Land contains ONLY one SMALL snowcapped mountain just east of center (around x1450 y1450 at target resolution), 3 or 4 low soft green hill groups and about 20 sparse tiny round trees. County borders follow reference locations, thin soft creamy white, understated. Sandy coastline with thin white surf. NO buildings, temples, towers, landmarks, bridges, lakes, waterfalls, rock spires, roads or icons. Sea bright turquoise #6DD7F2 with very faint wave strokes, much calmer than reference. Exactly four SMALL sea decorations: one whale near lower left x250 y2200, one sailboat near right edge x2040 y2180 (above bottom-right reserved corner), two soft clouds at upper-right edge x2140 y100 and lower-left edge x100 y2590. No other sea objects. Upper left rectangle x0-898 y0-841 must be absolutely empty uniform turquoise sea with no waves/clouds/objects. Bottom-right rectangle x1683-2244 y2383-2804 must be absolutely empty sea. Keep flat low-detail clear label footprints centered at (1520,300),(1800,460),(1120,520),(840,800),(760,1200),(660,1800),(760,2000),(1440,1900), each about 360x230 px: no trees/hills/mountains there. These coordinates guide composition only: do NOT draw labels/rectangles/text. Warm friendly cute Taiwanese illustration, dark-brown rounded outlines #3B2A1A, flat soft cel shading, cream sand #FFF8E6. NO text letters numbers pins markers UI logos watermarks. Reference main island must not widen or enlarge in the north. All offshore islets must disappear. Deliver only the illustration, full opaque RGB.
```

## 第二次實際提示詞

```text
Precise object edit of image 1 only. Image 2 is a GUIDE showing protected empty label areas in blue rectangles; DO NOT reproduce any colored rectangles or text from image 2. Keep the main Taiwan coastline, size, position, island silhouette, sea, sand, borders, whale, sailboat, snow mountain and style EXACTLY unchanged. Corrections: remove EVERY tree, hill, mountain, bush or grass tuft inside EACH of the 8 blue guide rectangles. Replace those objects with smoothly matching pale green flat land; preserve thin white county lines. Especially remove northern hills under Taoyuan, southwest hills under Kaohsiung, and the trees inside Taipei, New Taipei, Hsinchu, Taichung, Taitung. All 8 blue label rectangles must be empty flat pale green or existing coastal sea. Preserve calm empty sea at top left and bottom right; no added objects. Keep 3 small gentle hill groups total but ONLY outside the blue rectangles; move the two removed hills to clear central interior areas outside every rectangle if necessary. Keep the ONE snow mountain as is. Remove the SMALL extra cloud below the large upper-right cloud, leaving only TWO cloud groups overall: one at extreme upper right and one at extreme lower left. Total sea decorations exactly FOUR: these two cloud groups, one lower-left whale, one right-edge sailboat. No islands. No buildings. No text numbers labels rectangles UI pins marks watermark. Deliver the CLEAN map only, same aspect and silhouette and decorative border network.
```
