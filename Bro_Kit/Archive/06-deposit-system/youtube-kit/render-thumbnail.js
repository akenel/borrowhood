#!/usr/bin/env node
/**
 * Render YouTube thumbnail from thumbnail.html
 * Output: thumbnail-deposit.jpg (1280x720)
 */

const puppeteer = require('puppeteer');
const path = require('path');

(async () => {
  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--ignore-certificate-errors'],
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 720 });

  const htmlPath = path.join(__dirname, 'thumbnail.html');
  await page.goto(`file://${htmlPath}`, { waitUntil: 'networkidle2', timeout: 10000 });

  // Wait for background image to load
  await new Promise(r => setTimeout(r, 2000));

  const outPath = path.join(__dirname, 'thumbnail-deposit.jpg');
  await page.screenshot({ path: outPath, type: 'jpeg', quality: 92 });

  console.log(`Thumbnail saved: ${outPath}`);
  await browser.close();
})();
