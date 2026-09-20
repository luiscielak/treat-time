export const WORLD_W = 180;
export const WORLD_H = 320;
export const DOG_SIZE = 32;
export const ITEM_SIZE = 16;

export type Atlas = {
  dog: HTMLImageElement;
  items: HTMLImageElement;
  ui: HTMLImageElement;
  background: HTMLImageElement;
};

function loadImage(src: string): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const image = new Image();
    image.onload = () => resolve(image);
    image.onerror = () => reject(new Error(`Failed to load ${src}`));
    image.src = src;
  });
}

export async function loadAtlas(): Promise<Atlas> {
  const [dog, items, ui, background] = await Promise.all([
    loadImage("/sprites/shih-tzu.png"),
    loadImage("/sprites/items.png"),
    loadImage("/sprites/ui.png"),
    loadImage("/sprites/background.png"),
  ]);
  return { dog, items, ui, background };
}

export function blit(
  ctx: CanvasRenderingContext2D,
  image: HTMLImageElement,
  sx: number,
  sy: number,
  sw: number,
  sh: number,
  dx: number,
  dy: number,
): void {
  ctx.drawImage(image, sx, sy, sw, sh, Math.round(dx), Math.round(dy), sw, sh);
}

export function drawDog(
  ctx: CanvasRenderingContext2D,
  atlas: Atlas,
  frame: number,
  x: number,
  y: number,
): void {
  blit(ctx, atlas.dog, frame * DOG_SIZE, 0, DOG_SIZE, DOG_SIZE, x - DOG_SIZE / 2, y);
}

export function drawItem(
  ctx: CanvasRenderingContext2D,
  atlas: Atlas,
  kind: number,
  x: number,
  y: number,
): void {
  blit(ctx, atlas.items, kind * ITEM_SIZE, 0, ITEM_SIZE, ITEM_SIZE, x - ITEM_SIZE / 2, y - ITEM_SIZE / 2);
}

export function drawUiIcon(
  ctx: CanvasRenderingContext2D,
  atlas: Atlas,
  kind: number,
  x: number,
  y: number,
): void {
  blit(ctx, atlas.ui, kind * ITEM_SIZE, 0, ITEM_SIZE, ITEM_SIZE, x, y);
}
