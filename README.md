# Treat Time

A tiny mobile pixel-art treat catcher. Drag the Shih Tzu along the bottom of the park and catch falling snacks. Soap and vacuum puffs cost a life.

**Play:** [luiscielak.github.io/treat-time](https://luiscielak.github.io/treat-time/)

## Play locally

```bash
npm install
npm run dev
```

Open the local URL on your phone or in a portrait browser window. Tap **Play**, drag to move, and catch bones, heart biscuits, and tennis balls. Missed treats or caught hazards cost one of three lives.

## Build

```bash
npm run build
npm run preview
```

High score and mute are stored in `localStorage`. Pixel art lives in `public/sprites/` and can be regenerated with:

```bash
python3 scripts/generate_sprites.py
```
