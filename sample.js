const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({args: ['--no-sandbox', '--disable-setuid-sandbox','--lang=en-GB']});
  const page = await browser.newPage();
  await page.goto('https://google.com');
  await page.screenshot({path: 'buddy-screenshot.png'});

  await browser.close();
})();
