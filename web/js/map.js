// 地圖平面：底圖、預留層、縣市標籤、疊加物；縮放和拖曳（docs/LAYER_ARCHITECTURE.md §2、§6）。
// 只有 D 版才建立，清單版不下載底圖（docs/RESPONSIVE_LAYOUT.md §4.1）。

import { state, selectCounty, clearCounty } from "./state.js";
import { data, countyStats } from "./data.js";

const MIN = 1;
const MAX = 3;
const STEP = 1.25;
const DESKTOP_CARD_MIN = 565;  // 量到的地圖寬度 ≥ 565px 用桌機卡（RESPONSIVE_LAYOUT §3.4）
const HEADLINE_MIN = 400;      // 疊加物的第二個分界（§2.5）
const FADE_AT = 1.3;           // 放大到 1.3 倍以上標語和貓淡出
const ICONS = "assets/icons.svg";

let root, viewport, plane, baseLayer, labelsLayer, zoomIn, zoomOut, zoomReset;
const labelButtons = new Map();
let W = 0;
let H = 0;
let { scale, x, y } = state.zoom;

export function ensureMap(main) {
  if (root) return;
  root = main;
  build();
  bindPointer();
  new ResizeObserver(([entry]) => resize(entry.contentRect)).observe(root);
}

export function renderMap(s) {
  if (!root) return;
  for (const [county, btn] of labelButtons) {
    const selected = s.county === county;
    btn.setAttribute("aria-pressed", String(selected));
    btn.classList.toggle("dim", Boolean(s.county) && !selected);
  }
}

function build() {
  const [, , vw, vh] = data.labels.viewBox;
  const all = countyStats(null);
  root.innerHTML = `
    <div class="map-viewport" role="group" aria-label="縣市地圖">
      <div class="map-plane">
        <svg class="layer-base" viewBox="0 0 ${vw} ${vh}" aria-hidden="true">
          <image href="assets/${data.manifest.basemap}" width="${vw}" height="${vh}"/>
        </svg>
        <svg class="layer-future" viewBox="0 0 ${vw} ${vh}" aria-hidden="true"></svg>
        <div class="layer-labels" data-size="desktop"></div>
      </div>
    </div>
    <div class="map-overlay">
      <div class="overlay-headline" aria-hidden="true">
        <div class="headline-bubble">
          <span>全台 <span class="num">${all.markets}</span> 個市場</span>
          <span class="big"><span class="num">${all.vendors}</span> 家攤商</span>
          <span class="small">Google 地圖登錄進度</span>
        </div>
      </div>
      <div class="overlay-cat" aria-hidden="true"><img src="assets/mascots/cat-camera.webp" alt=""></div>
      <div class="overlay-controls">
        <div class="zoom-buttons">
          <button class="zoom-btn" type="button" data-zoom="in" aria-label="放大地圖"><svg class="icon"><use href="${ICONS}#plus"/></svg></button>
          <button class="zoom-btn" type="button" data-zoom="out" aria-label="縮小地圖"><svg class="icon"><use href="${ICONS}#minus"/></svg></button>
          <button class="zoom-btn" type="button" data-zoom="reset" aria-label="地圖回到全台（重設縮放，不清除篩選）" title="回到全台"><svg class="icon"><use href="${ICONS}#target"/></svg></button>
        </div>
        <button class="legend-toggle" type="button" aria-expanded="false" aria-controls="map-legend">ⓘ 圖例</button>
        <div class="legend" id="map-legend">
          <p>縣市標籤：</p>
          <ul>
            <li><span class="swatch"></span>有參與的縣市（${data.counties.length} 個）</li>
            <li><span class="swatch off"></span>未參與的縣市（無標籤）</li>
          </ul>
        </div>
      </div>
    </div>`;
  viewport = root.querySelector(".map-viewport");
  plane = root.querySelector(".map-plane");
  baseLayer = root.querySelector(".layer-base");
  labelsLayer = root.querySelector(".layer-labels");
  [zoomIn, zoomOut, zoomReset] = root.querySelectorAll(".zoom-btn");

  for (const { county, x: lx, y: ly } of data.labels.labels) {
    const st = countyStats(county);
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "county-label";
    btn.style.left = `${(lx / vw) * 100}%`;
    btn.style.top = `${(ly / vh) * 100}%`;
    btn.setAttribute("aria-label", `${county}，${st.markets} 個市場，${st.vendors} 家攤商`);
    btn.innerHTML = `
      <span class="label-head"><svg aria-hidden="true"><use href="${ICONS}#cart"/></svg>${county}</span>
      <span class="label-body" aria-hidden="true">
        <span class="label-full">${st.markets} 個市場<br>${st.vendors} 家攤商</span>
        <span class="label-compact">${st.markets} 市場・${st.vendors} 攤</span>
      </span>`;
    btn.addEventListener("click", () => selectCounty(county));
    labelsLayer.append(btn);
    labelButtons.set(county, btn);
  }

  zoomIn.addEventListener("click", () => zoomAt(W / 2, H / 2, scale * STEP));
  zoomOut.addEventListener("click", () => zoomAt(W / 2, H / 2, scale / STEP));
  zoomReset.addEventListener("click", () => zoomAt(0, 0, 1));
  const legendToggle = root.querySelector(".legend-toggle");
  const legend = root.querySelector(".legend");
  legendToggle.addEventListener("click", () => {
    const open = legend.classList.toggle("open");
    legendToggle.setAttribute("aria-expanded", String(open));
  });
  renderMap(state);
}

function resize({ width, height }) {
  if (W && width) {
    x *= width / W;
    y *= height / H;
  }
  W = width;
  H = height;
  // 依量到的地圖顯示寬度切換，不用螢幕解析度或媒體查詢（§3.4）
  labelsLayer.dataset.size = W >= DESKTOP_CARD_MIN ? "desktop" : "compact";
  root.dataset.tier = W >= DESKTOP_CARD_MIN ? "lg" : W >= HEADLINE_MIN ? "md" : "sm";
  apply();
}

function zoomAt(px, py, next) {
  next = Math.min(MAX, Math.max(MIN, next));
  x = px - (px - x) * (next / scale);
  y = py - (py - y) * (next / scale);
  scale = next;
  apply();
}

function apply() {
  // 地圖不能整個拖出畫面外：平面永遠蓋滿地圖框
  x = Math.min(0, Math.max(W - W * scale, x));
  y = Math.min(0, Math.max(H - H * scale, y));
  plane.style.transform = `translate(${x}px, ${y}px) scale(${scale})`;
  labelsLayer.style.setProperty("--inv", 1 / scale);  // 標籤維持固定螢幕大小
  // 淡出遮罩換算回平面座標，對齊地圖框
  const mask = baseLayer.style;
  mask.setProperty("--mx", `${-x / scale}px`);
  mask.setProperty("--my", `${-y / scale}px`);
  mask.setProperty("--mw", `${W / scale}px`);
  mask.setProperty("--mh", `${H / scale}px`);
  mask.setProperty("--mf", `${24 / scale}px`);
  root.classList.toggle("zoomed", scale >= FADE_AT);
  zoomIn.disabled = scale >= MAX;
  zoomOut.disabled = scale <= MIN;
  zoomReset.disabled = scale <= MIN;
  state.zoom = { scale, x, y };
}

function bindPointer() {
  const pointers = new Map();
  let dragging = false;
  let suppressClick = false;
  let start = null;
  let pinch = null;

  const local = (e) => {
    const r = viewport.getBoundingClientRect();
    return { x: e.clientX - r.left, y: e.clientY - r.top };
  };

  viewport.addEventListener("pointerdown", (e) => {
    if (e.button !== 0 && e.pointerType === "mouse") return;
    pointers.set(e.pointerId, local(e));
    suppressClick = false;
    if (pointers.size === 1) {
      start = { ...local(e), x0: x, y0: y };
    } else if (pointers.size === 2) {
      const [a, b] = [...pointers.values()];
      pinch = { dist: Math.hypot(a.x - b.x, a.y - b.y), scale0: scale };
      dragging = true;
      for (const id of pointers.keys()) viewport.setPointerCapture(id);
    }
  });

  viewport.addEventListener("pointermove", (e) => {
    if (!pointers.has(e.pointerId)) return;
    const p = local(e);
    pointers.set(e.pointerId, p);
    if (pinch && pointers.size === 2) {
      const [a, b] = [...pointers.values()];
      const dist = Math.hypot(a.x - b.x, a.y - b.y);
      zoomAt((a.x + b.x) / 2, (a.y + b.y) / 2, pinch.scale0 * (dist / pinch.dist));
      suppressClick = true;
      return;
    }
    if (!start) return;
    // 移動超過 4px 才算拖曳，這樣點標籤不會被吃掉
    if (!dragging && Math.hypot(p.x - start.x, p.y - start.y) > 4) {
      dragging = true;
      viewport.setPointerCapture(e.pointerId);
      viewport.classList.add("dragging");
    }
    if (dragging) {
      x = start.x0 + (p.x - start.x);
      y = start.y0 + (p.y - start.y);
      apply();
      suppressClick = true;
    }
  });

  const end = (e) => {
    pointers.delete(e.pointerId);
    if (pointers.size < 2) pinch = null;
    if (pointers.size === 0) {
      dragging = false;
      start = null;
      viewport.classList.remove("dragging");
    } else if (pointers.size === 1) {
      const [p] = pointers.values();
      start = { ...p, x0: x, y0: y };
    }
  };
  viewport.addEventListener("pointerup", end);
  viewport.addEventListener("pointercancel", end);

  // 點地圖空白處＝回到全台；拖曳結束的那一下不算
  viewport.addEventListener("click", (e) => {
    if (suppressClick) {
      e.stopPropagation();
      e.preventDefault();
      suppressClick = false;
      return;
    }
    if (!e.target.closest(".county-label")) clearCounty();
  }, true);

  viewport.addEventListener("wheel", (e) => {
    e.preventDefault();
    const p = local(e);
    zoomAt(p.x, p.y, scale * Math.exp(-e.deltaY * 0.0015));
  }, { passive: false });
}
