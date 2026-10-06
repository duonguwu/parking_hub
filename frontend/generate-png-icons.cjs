const fs = require('fs');
const path = require('path');
const zlib = require('zlib');

function crc32(buf) {
  let table = new Uint32Array(256);
  for (let i = 0; i < 256; i++) {
    let c = i;
    for (let j = 0; j < 8; j++) {
      c = (c & 1) ? (0xedb88320 ^ (c >>> 1)) : (c >>> 1);
    }
    table[i] = c;
  }
  let crc = 0xffffffff;
  for (let i = 0; i < buf.length; i++) {
    crc = table[(crc ^ buf[i]) & 0xff] ^ (crc >>> 8);
  }
  return (crc ^ 0xffffffff) >>> 0;
}

function createChunk(type, data) {
  const len = data.length;
  const buf = Buffer.alloc(8 + len + 4);
  buf.writeUInt32BE(len, 0);
  buf.write(type, 4, 4, 'ascii');
  data.copy(buf, 8);
  const typeAndData = buf.subarray(4, 8 + len);
  const crc = crc32(typeAndData);
  buf.writeUInt32BE(crc, 8 + len);
  return buf;
}

function generateParkingHubPNG(width, height, isMaskable = false) {
  const rowSize = width * 4;
  const rawData = Buffer.alloc(height * (1 + rowSize));

  // Colors: primary #0284c7 (2, 132, 199), dark #0369a1 (3, 105, 161), white (255, 255, 255), sky (56, 189, 248)
  const cornerRadius = isMaskable ? 0 : width * 0.22;

  for (let y = 0; y < height; y++) {
    const rowOffset = y * (1 + rowSize);
    rawData[rowOffset] = 0; // Filter: None

    for (let x = 0; x < width; x++) {
      const pxOffset = rowOffset + 1 + x * 4;

      // Rounded rect check
      let inBounds = true;
      if (!isMaskable) {
        const dx = x < cornerRadius ? cornerRadius - x : (x > width - cornerRadius ? x - (width - cornerRadius) : 0);
        const dy = y < cornerRadius ? cornerRadius - y : (y > height - cornerRadius ? y - (height - cornerRadius) : 0);
        if (dx > 0 && dy > 0 && Math.sqrt(dx * dx + dy * dy) > cornerRadius) {
          inBounds = false;
        }
      }

      if (!inBounds) {
        rawData[pxOffset] = 0;
        rawData[pxOffset + 1] = 0;
        rawData[pxOffset + 2] = 0;
        rawData[pxOffset + 3] = 0;
        continue;
      }

      // Background gradient
      const gradT = (x + y) / (width + height);
      const rBg = Math.round(2 * (1 - gradT) + 3 * gradT);
      const gBg = Math.round(132 * (1 - gradT) + 105 * gradT);
      const bBg = Math.round(199 * (1 - gradT) + 161 * gradT);

      // Normalized coordinates [0, 1]
      const nx = x / width;
      const ny = y / height;

      // Draw 'P' symbol
      // Vertical stem: nx in [0.33, 0.46], ny in [0.25, 0.75]
      // Top bar: nx in [0.33, 0.64], ny in [0.25, 0.38]
      // Middle bar: nx in [0.33, 0.64], ny in [0.46, 0.58]
      // Loop right arc: center around (0.60, 0.415)
      let isP = false;

      // Stem
      if (nx >= 0.33 && nx <= 0.46 && ny >= 0.25 && ny <= 0.75) {
        isP = true;
      }
      // Top bar
      if (nx >= 0.33 && nx <= 0.62 && ny >= 0.25 && ny <= 0.38) {
        isP = true;
      }
      // Middle bar
      if (nx >= 0.33 && nx <= 0.62 && ny >= 0.46 && ny <= 0.58) {
        isP = true;
      }
      // Right loop arc
      const loopCx = 0.58;
      const loopCy = 0.415;
      const loopRx = 0.17;
      const loopRy = 0.165;
      const dLoop = Math.pow((nx - loopCx) / loopRx, 2) + Math.pow((ny - loopCy) / loopRy, 2);
      const loopInnerRx = 0.07;
      const loopInnerRy = 0.065;
      const dInner = Math.pow((nx - loopCx) / loopInnerRx, 2) + Math.pow((ny - loopCy) / loopInnerRy, 2);

      if (nx >= 0.50 && dLoop <= 1.0 && dInner >= 0.9) {
        isP = true;
      }

      // Signal beacon dot at bottom right (0.68, 0.68)
      const dotDx = (nx - 0.68);
      const dotDy = (ny - 0.68);
      const dotDist = Math.sqrt(dotDx * dotDx + dotDy * dotDy);
      let isDot = false;
      let isDotCore = false;

      if (dotDist <= 0.08) {
        isDot = true;
        if (dotDist <= 0.035) isDotCore = true;
      }

      if (isP || isDotCore) {
        rawData[pxOffset] = 255;
        rawData[pxOffset + 1] = 255;
        rawData[pxOffset + 2] = 255;
        rawData[pxOffset + 3] = 255;
      } else if (isDot) {
        rawData[pxOffset] = 56;
        rawData[pxOffset + 1] = 189;
        rawData[pxOffset + 2] = 248;
        rawData[pxOffset + 3] = 255;
      } else {
        rawData[pxOffset] = rBg;
        rawData[pxOffset + 1] = gBg;
        rawData[pxOffset + 2] = bBg;
        rawData[pxOffset + 3] = 255;
      }
    }
  }

  // Compress IDAT
  const compressed = zlib.deflateSync(rawData);

  // Build PNG Buffer
  const signature = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);

  const ihdrData = Buffer.alloc(13);
  ihdrData.writeUInt32BE(width, 0);
  ihdrData.writeUInt32BE(height, 4);
  ihdrData[8] = 8; // 8-bit
  ihdrData[9] = 6; // RGBA
  ihdrData[10] = 0; // Deflate
  ihdrData[11] = 0; // Filter
  ihdrData[12] = 0; // Non-interlaced
  const ihdrChunk = createChunk('IHDR', ihdrData);

  const idatChunk = createChunk('IDAT', compressed);
  const iendChunk = createChunk('IEND', Buffer.alloc(0));

  return Buffer.concat([signature, ihdrChunk, idatChunk, iendChunk]);
}

const publicDir = path.join(__dirname, 'public');

// Generate 192x192 PNG
fs.writeFileSync(path.join(publicDir, 'pwa-192x192.png'), generateParkingHubPNG(192, 192, false));
console.log('Created pwa-192x192.png');

// Generate 512x512 PNG
fs.writeFileSync(path.join(publicDir, 'pwa-512x512.png'), generateParkingHubPNG(512, 512, false));
console.log('Created pwa-512x512.png');

// Generate maskable 512x512 PNG
fs.writeFileSync(path.join(publicDir, 'maskable-icon-512x512.png'), generateParkingHubPNG(512, 512, true));
console.log('Created maskable-icon-512x512.png');

// Generate apple-touch-icon.png 180x180
fs.writeFileSync(path.join(publicDir, 'apple-touch-icon.png'), generateParkingHubPNG(180, 180, false));
console.log('Created apple-touch-icon.png');

// Generate screenshots for Richer PWA Install UI
fs.writeFileSync(path.join(publicDir, 'screenshot-desktop.png'), generateParkingHubPNG(1280, 720, true));
console.log('Created screenshot-desktop.png');

fs.writeFileSync(path.join(publicDir, 'screenshot-mobile.png'), generateParkingHubPNG(750, 1334, true));
console.log('Created screenshot-mobile.png');

