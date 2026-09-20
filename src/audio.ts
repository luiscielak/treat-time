const MUTE_KEY = "treat-time-mute";

export class AudioBus {
  muted = localStorage.getItem(MUTE_KEY) === "1";
  private ctx: AudioContext | null = null;

  toggle(): boolean {
    this.muted = !this.muted;
    localStorage.setItem(MUTE_KEY, this.muted ? "1" : "0");
    return this.muted;
  }

  unlock(): void {
    this.ensure().catch(() => undefined);
  }

  yip(): void {
    this.tone(720, 0.07, "square", 0.07);
    this.tone(980, 0.08, "square", 0.05, 0.06);
  }

  ouch(): void {
    this.tone(220, 0.16, "sawtooth", 0.08);
    this.tone(140, 0.18, "triangle", 0.07, 0.05);
  }

  over(): void {
    this.tone(330, 0.14, "square", 0.06);
    this.tone(247, 0.16, "square", 0.06, 0.12);
    this.tone(196, 0.28, "triangle", 0.08, 0.26);
  }

  start(): void {
    this.tone(523, 0.08, "square", 0.05);
    this.tone(659, 0.08, "square", 0.05, 0.08);
    this.tone(784, 0.12, "square", 0.06, 0.16);
  }

  private async ensure(): Promise<AudioContext | null> {
    if (this.muted) return null;
    const Ctor = window.AudioContext || (window as typeof window & { webkitAudioContext?: typeof AudioContext }).webkitAudioContext;
    if (!Ctor) return null;
    if (!this.ctx) this.ctx = new Ctor();
    if (this.ctx.state === "suspended") await this.ctx.resume();
    return this.ctx;
  }

  private tone(
    freq: number,
    duration: number,
    type: OscillatorType,
    gain: number,
    delay = 0,
  ): void {
    void this.ensure().then((ctx) => {
      if (!ctx) return;
      const now = ctx.currentTime + delay;
      const osc = ctx.createOscillator();
      const amp = ctx.createGain();
      osc.type = type;
      osc.frequency.setValueAtTime(freq, now);
      amp.gain.setValueAtTime(0.0001, now);
      amp.gain.exponentialRampToValueAtTime(gain, now + 0.01);
      amp.gain.exponentialRampToValueAtTime(0.0001, now + duration);
      osc.connect(amp);
      amp.connect(ctx.destination);
      osc.start(now);
      osc.stop(now + duration + 0.02);
    });
  }
}
