export class PointerInput {
  worldX = 90;
  down = false;
  private tapX = 0;
  private tapY = 0;
  private tapAt = 0;
  private lastY = 0;
  private readonly canvas: HTMLCanvasElement;
  private readonly worldW: number;
  private readonly worldH: number;

  constructor(canvas: HTMLCanvasElement, worldW: number, worldH: number) {
    this.canvas = canvas;
    this.worldW = worldW;
    this.worldH = worldH;
    const map = (event: PointerEvent): void => {
      const rect = this.canvas.getBoundingClientRect();
      const x = ((event.clientX - rect.left) / rect.width) * this.worldW;
      const y = ((event.clientY - rect.top) / rect.height) * this.worldH;
      this.worldX = Math.min(this.worldW - 8, Math.max(8, x));
      this.lastY = y;
    };

    this.canvas.addEventListener("pointerdown", (event) => {
      event.preventDefault();
      this.canvas.setPointerCapture(event.pointerId);
      this.down = true;
      map(event);
      this.tapX = this.worldX;
      this.tapY = this.lastY;
      this.tapAt = performance.now();
    });
    this.canvas.addEventListener("pointermove", (event) => {
      if (!this.down) return;
      event.preventDefault();
      map(event);
    });
    const end = (event: PointerEvent): void => {
      if (!this.down) return;
      event.preventDefault();
      map(event);
      this.down = false;
    };
    this.canvas.addEventListener("pointerup", end);
    this.canvas.addEventListener("pointercancel", end);
  }

  consumeTap(maxDist = 10, maxMs = 350): { x: number; y: number } | null {
    if (this.down) return null;
    if (performance.now() - this.tapAt > maxMs) return null;
    const dx = this.worldX - this.tapX;
    const dy = this.lastY - this.tapY;
    if (dx * dx + dy * dy > maxDist * maxDist) return null;
    this.tapAt = 0;
    return { x: this.tapX, y: this.tapY };
  }
}
