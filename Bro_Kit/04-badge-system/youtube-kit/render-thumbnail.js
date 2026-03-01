#!/usr/bin/env node
const puppeteer = require('puppeteer');
const path = require('path');

(async () => {
  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox'],
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 720 });

  const htmlPath = path.resolve(__dirname, 'thumbnail.html');
  await page.goto(`file://${htmlPath}`, { waitUntil: 'networkidle2', timeout: 15000 });
  await new Promise(r => setTimeout(r, 1000));

  const outPath = path.resolve(__dirname, 'badge-system-THUMB.png');
  await page.screenshot({ path: outPath, type: 'png' });

  console.log(`Thumbnail saved: ${outPath}`);
  await browser.close();
})();
