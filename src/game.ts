import { AudioBus } from "./audio.ts";
import { drawText, textWidth } from "./font.ts";
import { PointerInput } from "./input.ts";
import {
  ITEM_SIZE,
  WORLD_H,
  WORLD_W,
  drawDog,
  drawItem,
  drawUiIcon,
  type Atlas,
} from "./sprites.ts";

const BEST_KEY = "treat-time-best";
const DOG_Y = 248;
const COMBO_WINDOW = 1.6;
const HIT_IFRAMES = 1.0;

type Screen = "title" | "play" | "over";
type Anim = "idle" | "hop" | "hit";

type Falling = {
  kind: number;
  hazard: boolean;
  x: number;
  y: number;
  vy: number;
};

type Particle = {
  x: number;
  y: number;
  vx: number;
  vy: number;
  life: number;
  color: string;
};

const PRAISE = ["YUM", "NICE", "GOOD DOG", "WOOF", "CATCH"];

export class Game {
  private screen: Screen = "title";
  private dogX = WORLD_W / 2;
  private items: Falling[] = [];
  private particles: Particle[] = [];
  private score = 0;
  private best = Number(localStorage.getItem(BEST_KEY) ?? 0);
  private lives = 3;
  private combo = 0;
  private comboLeft = 0;
  private spawnIn = 0.6;
  private hitLeft = 0;
  private hopLeft = 0;
  private bobT = 0;
  private shake = 0;
  private flash = 0;
  private praise = "";
  private praiseLeft = 0;
  private hintLeft = 3.2;
  private time = 0;

  private readonly ctx: CanvasRenderingContext2D;
  private readonly atlas: Atlas;
  private readonly input: PointerInput;
  private readonly audio: AudioBus;

  constructor(
    ctx: CanvasRenderingContext2D,
    atlas: Atlas,
    input: PointerInput,
    audio: AudioBus,
  ) {
    this.ctx = ctx;
    this.atlas = atlas;
    this.input = input;
    this.audio = audio;
  }

  startFromTitle(): void {
    this.audio.unlock();
    this.audio.start();
    this.resetPlay();
    this.screen = "play";
  }

  update(dt: number): void {
    this.time += dt;
    this.bobT += dt;
    if (this.shake > 0) this.shake = Math.max(0, this.shake - dt * 8);
    if (this.flash > 0) this.flash = Math.max(0, this.flash - dt);
    if (this.hopLeft > 0) this.hopLeft = Math.max(0, this.hopLeft - dt);
    if (this.hitLeft > 0) this.hitLeft = Math.max(0, this.hitLeft - dt);
    if (this.praiseLeft > 0) this.praiseLeft = Math.max(0, this.praiseLeft - dt);
    if (this.comboLeft > 0) {
      this.comboLeft -= dt;
      if (this.comboLeft <= 0) this.combo = 0;
    }

    this.updateParticles(dt);

    if (this.screen === "title") {
      this.followPointer(dt, 0.18);
      const tap = this.input.consumeTap();
      if (tap) {
        if (this.inMute(tap.x, tap.y)) this.audio.toggle();
        else if (this.inButton(tap.x, tap.y, 90, 214, 72, 22)) this.startFromTitle();
      }
      return;
    }

    if (this.screen === "over") {
      const tap = this.input.consumeTap();
      if (tap) {
        if (this.inMute(tap.x, tap.y)) this.audio.toggle();
        else if (this.inButton(tap.x, tap.y, 90, 214, 72, 22)) this.startFromTitle();
      }
      return;
    }

    const tap = this.input.consumeTap();
    if (tap && this.inMute(tap.x, tap.y)) this.audio.toggle();

    this.followPointer(dt, 1);
    this.hintLeft = Math.max(0, this.hintLeft - dt);
    this.spawnIn -= dt;
    if (this.spawnIn <= 0 && this.items.length < 4) {
      this.spawnItem();
      this.spawnIn = this.spawnDelay();
    }

    for (const item of this.items) item.y += item.vy * dt;

    const kept: Falling[] = [];
    for (const item of this.items) {
      if (this.overlapsDog(item)) {
        if (item.hazard) this.hurt();
        else this.catchTreat(item);
        continue;
      }
      if (item.y - ITEM_SIZE / 2 > WORLD_H) {
        if (!item.hazard) this.hurt(true);
        continue;
      }
      kept.push(item);
    }
    this.items = kept;
  }

  draw(): void {
    const ctx = this.ctx;
    const sx = this.shake > 0 ? Math.round((Math.random() - 0.5) * 2) : 0;
    const sy = this.shake > 0 ? Math.round((Math.random() - 0.5) * 2) : 0;
    ctx.imageSmoothingEnabled = false;
    ctx.clearRect(0, 0, WORLD_W, WORLD_H);
    ctx.save();
    ctx.translate(sx, sy);
    ctx.drawImage(this.atlas.background, 0, 0);

    const anim = this.anim();
    const frame = anim === "hit" ? 3 : anim === "hop" ? 2 : this.bobT % 0.7 < 0.35 ? 0 : 1;
    const dogY = DOG_Y + (anim === "hop" ? -2 : 0);
    drawDog(ctx, this.atlas, frame, this.dogX, dogY);

    if (this.screen === "play") {
      for (const item of this.items) drawItem(ctx, this.atlas, item.kind, item.x, item.y);
    }

    for (const particle of this.particles) {
      ctx.fillStyle = particle.color;
      ctx.fillRect(Math.round(particle.x), Math.round(particle.y), 2, 2);
    }

    ctx.restore();
    this.drawHud();
    if (this.flash > 0) {
      ctx.fillStyle = `rgba(255,255,255,${Math.min(0.28, this.flash)})`;
      ctx.fillRect(0, 0, WORLD_W, WORLD_H);
    }
  }

  private resetPlay(): void {
    this.dogX = WORLD_W / 2;
    this.items = [];
    this.particles = [];
    this.score = 0;
    this.lives = 3;
    this.combo = 0;
    this.comboLeft = 0;
    this.spawnIn = 0.7;
    this.hitLeft = 0;
    this.hopLeft = 0;
    this.hintLeft = 3.2;
    this.praise = "";
    this.praiseLeft = 0;
    this.flash = 0;
    this.shake = 0;
  }

  private followPointer(_dt: number, snap: number): void {
    if (this.input.down) {
      const target = this.input.worldX;
      this.dogX += (target - this.dogX) * (snap >= 1 ? 1 : 0.18);
    }
    this.dogX = Math.min(WORLD_W - 18, Math.max(18, this.dogX));
  }

  private spawnDelay(): number {
    return Math.max(0.55, 1.45 - this.score * 0.003);
  }

  private fallSpeed(hazard: boolean): number {
    const base = 34 + Math.min(56, this.score * 0.22);
    return hazard ? base * 0.64 : base;
  }

  private spawnItem(): void {
    const hazardChance = this.score < 20 ? 0 : 0.12 + Math.min(0.12, this.score * 0.001);
    const hazard = Math.random() < hazardChance;
    const kind = hazard ? 3 + (Math.random() < 0.5 ? 0 : 1) : Math.floor(Math.random() * 3);
    this.items.push({
      kind,
      hazard,
      x: 16 + Math.random() * (WORLD_W - 32),
      y: -10,
      vy: this.fallSpeed(hazard),
    });
  }

  private overlapsDog(item: Falling): boolean {
    const left = this.dogX - 16;
    const right = this.dogX + 16;
    const top = DOG_Y + 2;
    const bottom = DOG_Y + 26;
    const ix = item.x;
    const iy = item.y;
    return ix > left && ix < right && iy > top && iy < bottom;
  }

  private catchTreat(item: Falling): void {
    this.combo += 1;
    this.comboLeft = COMBO_WINDOW;
    this.score += 10 + (this.combo - 1) * 5;
    this.hopLeft = 0.22;
    this.flash = 0.08;
    this.audio.yip();
    this.burst(item.x, item.y, item.kind === 1 ? "#e85d75" : item.kind === 2 ? "#c8e85d" : "#f5e6c8");
    this.praise = PRAISE[(this.combo - 1) % PRAISE.length];
    this.praiseLeft = 0.7;
    if (this.score > this.best) {
      this.best = this.score;
      localStorage.setItem(BEST_KEY, String(this.best));
    }
  }

  private hurt(fromMiss = false): void {
    if (this.hitLeft > 0) return;
    this.lives -= 1;
    this.combo = 0;
    this.comboLeft = 0;
    this.hitLeft = HIT_IFRAMES;
    this.shake = 1;
    this.audio.ouch();
    this.burst(this.dogX, DOG_Y + 10, fromMiss ? "#fff6e8" : "#d4bce8");
    if (this.lives <= 0) {
      this.screen = "over";
      this.items = [];
      this.audio.over();
    }
  }

  private burst(x: number, y: number, color: string): void {
    for (let i = 0; i < 8; i++) {
      const angle = (Math.PI * 2 * i) / 8;
      this.particles.push({
        x,
        y,
        vx: Math.cos(angle) * (20 + Math.random() * 24),
        vy: Math.sin(angle) * (16 + Math.random() * 20) - 10,
        life: 0.35 + Math.random() * 0.2,
        color,
      });
    }
  }

  private updateParticles(dt: number): void {
    const next: Particle[] = [];
    for (const particle of this.particles) {
      particle.life -= dt;
      if (particle.life <= 0) continue;
      particle.x += particle.vx * dt;
      particle.y += particle.vy * dt;
      particle.vy += 40 * dt;
      next.push(particle);
    }
    this.particles = next;
  }

  private anim(): Anim {
    if (this.hitLeft > HIT_IFRAMES - 0.4) return "hit";
    if (this.hopLeft > 0) return "hop";
    return "idle";
  }

  private inMute(x: number, y: number): boolean {
    return x >= WORLD_W - 22 && y <= 22;
  }

  private inButton(x: number, y: number, cx: number, cy: number, w: number, h: number): boolean {
    return x >= cx - w / 2 && x <= cx + w / 2 && y >= cy - h / 2 && y <= cy + h / 2;
  }

  private drawHud(): void {
    const ctx = this.ctx;
    drawUiIcon(ctx, this.atlas, this.audio.muted ? 3 : 2, WORLD_W - 18, 4);

    if (this.screen === "title") {
      this.panel(24, 36, 132, 52);
      drawText(ctx, "TREAT TIME", 90, 44, "#3d2314", 2, "center");
      drawText(ctx, "CATCH THE SNACKS", 90, 66, "#8b5a2b", 1, "center");
      this.button(90, 214, "PLAY");
      if (this.best > 0) drawText(ctx, `BEST ${this.best}`, 90, 242, "#3d2314", 1, "center");
      drawText(ctx, "DRAG TO MOVE", 90, 292, "#3d2314", 1, "center");
      return;
    }

    ctx.fillStyle = "rgba(255,248,238,0.82)";
    ctx.fillRect(4, 4, 40, 16);
    drawText(ctx, String(this.score), 8, 7, "#3d2314", 2);
    for (let i = 0; i < 3; i++) {
      drawUiIcon(ctx, this.atlas, i < this.lives ? 0 : 1, 8 + i * 14, 22);
    }
    if (this.combo > 1) {
      drawText(ctx, `X${this.combo}`, 8, 38, "#e85d75", 1);
    }
    if (this.praiseLeft > 0) {
      drawText(ctx, this.praise, 90, 88, "#fff8ee", 1, "center");
    }
    if (this.screen === "play" && this.hintLeft > 0 && this.score === 0) {
      drawText(ctx, "DRAG TO CATCH", 90, 120, "#3d2314", 1, "center");
    }

    if (this.screen === "over") {
      this.panel(22, 78, 136, 88);
      drawText(ctx, "OH NO", 90, 88, "#3d2314", 2, "center");
      drawText(ctx, `SCORE ${this.score}`, 90, 112, "#8b5a2b", 1, "center");
      drawText(ctx, `BEST ${this.best}`, 90, 126, "#8b5a2b", 1, "center");
      this.button(90, 214, "AGAIN");
    }
  }

  private panel(x: number, y: number, w: number, h: number): void {
    const ctx = this.ctx;
    ctx.fillStyle = "rgba(255,248,238,0.88)";
    ctx.fillRect(x, y, w, h);
    ctx.fillStyle = "#3d2314";
    ctx.fillRect(x, y, w, 2);
    ctx.fillRect(x, y + h - 2, w, 2);
    ctx.fillRect(x, y, 2, h);
    ctx.fillRect(x + w - 2, y, 2, h);
  }

  private button(cx: number, cy: number, label: string): void {
    const ctx = this.ctx;
    const w = Math.max(64, textWidth(label, 2) + 16);
    const h = 22;
    const x = Math.round(cx - w / 2);
    const y = Math.round(cy - h / 2);
    ctx.fillStyle = "#d4924a";
    ctx.fillRect(x, y, w, h);
    ctx.fillStyle = "#3d2314";
    ctx.fillRect(x, y, w, 2);
    ctx.fillRect(x, y + h - 2, w, 2);
    ctx.fillRect(x, y, 2, h);
    ctx.fillRect(x + w - 2, y, 2, h);
    drawText(ctx, label, cx, y + 6, "#fff8ee", 2, "center");
  }
}
