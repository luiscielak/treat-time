import { AudioBus } from "./audio.ts";
import { Game } from "./game.ts";
import { PointerInput } from "./input.ts";
import { WORLD_H, WORLD_W, loadAtlas } from "./sprites.ts";
import "./style.css";

const canvas = document.querySelector<HTMLCanvasElement>("#game");
if (!canvas) throw new Error("Missing #game canvas");

const ctx = canvas.getContext("2d");
if (!ctx) throw new Error("Canvas 2D is not available");

canvas.width = WORLD_W;
canvas.height = WORLD_H;
ctx.imageSmoothingEnabled = false;

function fitCanvas(target: HTMLCanvasElement): void {
  const pad = 8;
  const scale = Math.max(
    1,
    Math.min(
      Math.floor((window.innerWidth - pad) / WORLD_W),
      Math.floor((window.innerHeight - pad) / WORLD_H),
    ),
  );
  target.style.width = `${WORLD_W * scale}px`;
  target.style.height = `${WORLD_H * scale}px`;
}

fitCanvas(canvas);
window.addEventListener("resize", () => fitCanvas(canvas));
window.addEventListener("orientationchange", () => fitCanvas(canvas));

const block = (event: Event): void => event.preventDefault();
document.addEventListener("gesturestart", block);
document.addEventListener("contextmenu", block);
document.addEventListener(
  "touchmove",
  (event) => {
    event.preventDefault();
  },
  { passive: false },
);

ctx.fillStyle = "#7ec8e3";
ctx.fillRect(0, 0, WORLD_W, WORLD_H);
ctx.fillStyle = "#3d2314";
ctx.fillRect(70, 154, 40, 4);

const atlas = await loadAtlas();
const audio = new AudioBus();
const input = new PointerInput(canvas, WORLD_W, WORLD_H);
const game = new Game(ctx, atlas, input, audio);

let last = performance.now();
const tick = (now: number): void => {
  const dt = Math.min(0.033, (now - last) / 1000);
  last = now;
  game.update(dt);
  game.draw();
  requestAnimationFrame(tick);
};
requestAnimationFrame(tick);
