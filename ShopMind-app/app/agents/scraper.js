// scraper.js — Scrapes MercadoLibre Chile product listings using Puppeteer
// Called from Python via subprocess
// Usage: node scraper.js "auriculares cancelacion ruido" 10

const puppeteer = require('../../node_modules/puppeteer');

const query = process.argv[2] || "auriculares";
const limit = parseInt(process.argv[3] || "10", 10);

(async () => {
  let browser;
  try {
    browser = await puppeteer.launch({ headless: true });
    const page = await browser.newPage();
    await page.setUserAgent('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36');

    const searchUrl = `https://listado.mercadolibre.cl/${encodeURIComponent(query).replace(/%20/g, '-')}`;
    await page.goto(searchUrl, { waitUntil: 'networkidle2', timeout: 45000 });

    // Wait for product listings to load (after JS challenge)
    await page.waitForSelector('.andes-money-amount__fraction', { timeout: 25000 }).catch(() => {});

    const products = await page.evaluate((maxItems) => {
      const items = document.querySelectorAll('.ui-search-layout__item');
      const results = [];

      for (let i = 0; i < Math.min(items.length, maxItems); i++) {
        const el = items[i];
        const title = el.querySelector('.poly-component__title, .ui-search-item__title')?.textContent?.trim() || '';
        const priceEl = el.querySelector('.andes-money-amount__fraction');
        const price = priceEl ? priceEl.textContent.trim().replace(/\./g, '') : '0';
        const link = el.querySelector('a')?.href || '';
        const img = el.querySelector('img')?.src || '';
        const ratingEl = el.querySelector('.poly-reviews__rating');
        const rating = ratingEl ? ratingEl.textContent.trim() : '';
        const reviewsEl = el.querySelector('.poly-reviews__total');
        const reviews = reviewsEl ? reviewsEl.textContent.trim().replace(/[()]/g, '') : '';

        // Skip items with no data
        if (!title || !price || price === '0') continue;
        // Skip ad tracking URLs (click1.mercadolibre.cl)
        if (link.includes('click1.mercadolibre.cl') || link.includes('/mclics/')) continue;
        // Clean tracking params from URL
        const cleanUrl = link.split('#')[0];

        results.push({
          title,
          price_clp: parseInt(price, 10),
          price_usd: Math.round(parseInt(price, 10) / 950 * 100) / 100,
          url: cleanUrl,
          image: img,
          rating: rating ? parseFloat(rating) : null,
          review_count: reviews ? parseInt(reviews.replace(/\D/g, ''), 10) : null,
        });
      }
      return results;
    }, limit);

    console.log(JSON.stringify(products));

  } catch (err) {
    console.error(JSON.stringify({ error: err.message }));
    process.exit(1);
  } finally {
    if (browser) await browser.close();
  }
})();
