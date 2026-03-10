#!/usr/bin/env node
const puppeteer = require('puppeteer');
const path = require('path');

(async () => {
  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--ignore-certificate-errors'],
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 720 });

  const htmlPath = path.resolve(__dirname, 'thumbnail.html');
  await page.goto(`file://${htmlPath}`, { waitUntil: 'networkidle2', timeout: 15000 });

  // Wait for images to load
  await page.evaluate(() => {
    return Promise.all(
      Array.from(document.querySelectorAll('img')).map(img => {
        if (img.complete) return Promise.resolve();
        return new Promise((resolve, reject) => {
          img.onload = resolve;
          img.onerror = resolve; // don't block on failed loads
        });
      })
    );
  });

  await new Promise(r => setTimeout(r, 1000));

  const outPath = path.resolve(__dirname, 'thumbnail-giveaway.jpg');
  await page.screenshot({
    path: outPath,
    type: 'jpeg',
    quality: 95,
  });

  console.log(`Thumbnail saved: ${outPath}`);
  await browser.close();
})();
