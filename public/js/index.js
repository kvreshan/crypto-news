// =============================================
// INDEX PAGE - MAIN JAVASCRIPT
// =============================================

let currentFilter = 'all';
let currentOffset = 0;
let isLoading = false;

// =============================================
// INIT
// =============================================

document.addEventListener('DOMContentLoaded', async () => {
  // Load settings
  const settings = await DB.getSettings();
  document.title = settings.site_name || CONFIG.SITE_NAME;

  // Set telegram link
  const tgUrl = settings.telegram_url || CONFIG.TELEGRAM_URL;
  document.getElementById('telegram-link').href = tgUrl || '#';
  document.getElementById('telegram-link-mobile').href = tgUrl || '#';

  // Load everything
  await Promise.all([
    loadPriceTicker(),
    loadNews(),
    loadSignalsWidget(),
    loadTopCoins(),
    loadAffiliateWidget(),
    ADS.init(),
  ]);

  // Filter pills
  document.querySelectorAll('.pill').forEach(pill => {
    pill.addEventListener('click', () => {
      document.querySelectorAll('.pill').forEach(p => p.classList.remove('active'));
      pill.classList.add('active');
      currentFilter = pill.dataset.filter;
      currentOffset = 0;
      document.getElementById('news-grid').innerHTML = '';
      document.getElementById('featured-article').innerHTML = '';
      loadNews(true);
    });
  });

  // Load more
  document.getElementById('load-more').addEventListener('click', () => {
    currentOffset += CONFIG.ARTICLES_PER_PAGE;
    loadNews(false, true);
  });

  // Hamburger menu
  document.getElementById('hamburger').addEventListener('click', () => {
    document.getElementById('mobile-menu').classList.toggle('open');
  });
});

// =============================================
// PRICE TICKER (CoinGecko free API)
// =============================================

async function loadPriceTicker() {
  try {
    const res = await fetch(`${CONFIG.COINGECKO_API}/simple/price?ids=bitcoin,ethereum,binancecoin,solana,ripple&vs_currencies=usd&include_24hr_change=true`);
    const data = await res.json();

    const coins = {
      bitcoin: 'BTC',
      ethereum: 'ETH',
      binancecoin: 'BNB',
      solana: 'SOL',
      ripple: 'XRP',
    };

    const items = Object.entries(coins).map(([id, symbol]) => {
      const coin = data[id];
      if (!coin) return '';
      const change = coin.usd_24h_change?.toFixed(2) || 0;
      const isUp = change >= 0;
      return `<span class="ticker-item">
        <span class="ticker-name">${symbol}</span>
        <span class="ticker-price">$${coin.usd.toLocaleString()}</span>
        <span class="${isUp ? 'ticker-up' : 'ticker-down'}">${isUp ? '▲' : '▼'} ${Math.abs(change)}%</span>
      </span>`;
    }).join('');

    // Duplicate for seamless loop
    const ticker = document.getElementById('ticker-inner');
    ticker.innerHTML = items + items;
  } catch (e) {
    document.getElementById('ticker-inner').innerHTML = 'Crypto market data loading...';
  }
}

// =============================================
// LOAD NEWS
// =============================================

async function loadNews(reset = false, append = false) {
  if (isLoading) return;
  isLoading = true;

  const news = await DB.getNews(CONFIG.ARTICLES_PER_PAGE + 1, currentOffset, currentFilter === 'all' ? null : currentFilter);

  // Featured (first article on reset)
  if (reset || currentOffset === 0) {
    const featured = news[0];
    if (featured) renderFeatured(featured);
  }

  // Grid articles
  const gridArticles = currentOffset === 0 ? news.slice(1) : news;
  const grid = document.getElementById('news-grid');

  if (!append) grid.innerHTML = '';

  gridArticles.slice(0, CONFIG.ARTICLES_PER_PAGE).forEach(article => {
    grid.insertAdjacentHTML('beforeend', renderNewsCard(article));
  });

  // Hide load more if no more
  const loadMoreBtn = document.getElementById('load-more');
  loadMoreBtn.style.display = news.length <= CONFIG.ARTICLES_PER_PAGE ? 'none' : 'block';

  isLoading = false;
}

// =============================================
// RENDER FUNCTIONS
// =============================================

function renderFeatured(article) {
  const container = document.getElementById('featured-article');
  const tags = (article.coin_tags || []).map(t => `<span class="tag">${t}</span>`).join('');
  const date = formatDate(article.published_at);
  const img = article.image_url || 'https://images.unsplash.com/photo-1621761191319-c6fb62004040?w=800&q=80';

  container.innerHTML = `
    <img src="${img}" alt="${escapeHtml(article.title)}" class="featured-image" loading="lazy" onerror="this.src='https://images.unsplash.com/photo-1621761191319-c6fb62004040?w=800&q=80'">
    <div class="featured-body">
      <div class="featured-tags">${tags}</div>
      <h2 class="featured-title">${escapeHtml(article.title)}</h2>
      <p class="featured-summary">${escapeHtml(article.summary || '')}</p>
      <div class="featured-meta">
        <span>${date} · ${article.views || 0} views</span>
        <a href="/article/index.html?id=${article.id}" class="read-more-btn">Read More →</a>
      </div>
    </div>`;

  container.onclick = (e) => {
    if (!e.target.classList.contains('read-more-btn')) {
      window.location.href = `/article/index.html?id=${article.id}`;
    }
  };
  container.style.cursor = 'pointer';
}

function renderNewsCard(article) {
  const tags = (article.coin_tags || []).slice(0, 2).map(t => `<span class="tag">${t}</span>`).join('');
  const date = formatDate(article.published_at);
  const img = article.image_url || 'https://images.unsplash.com/photo-1621761191319-c6fb62004040?w=400&q=80';

  return `
    <div class="news-card" onclick="window.location.href='/article/index.html?id=${article.id}'">
      <img src="${img}" alt="${escapeHtml(article.title)}" class="news-card-image" loading="lazy" onerror="this.src='https://images.unsplash.com/photo-1621761191319-c6fb62004040?w=400&q=80'">
      <div class="news-card-body">
        <div class="news-card-tags">${tags}</div>
        <h3 class="news-card-title">${escapeHtml(article.title)}</h3>
        <div class="news-card-meta">
          <span>${date}</span>
          <span>${article.views || 0} views</span>
        </div>
      </div>
    </div>`;
}

// =============================================
// SIGNALS WIDGET
// =============================================

async function loadSignalsWidget() {
  const signals = await DB.getSignals(5);
  const container = document.getElementById('signals-widget');

  if (!signals.length) {
    container.innerHTML = '<p style="padding:16px;font-size:13px;color:var(--text-muted)">No active signals</p>';
    return;
  }

  container.innerHTML = signals.map(s => `
    <div class="signal-item" onclick="window.location.href='/signals.html'">
      <div>
        <div class="signal-coin">${s.coin}/USDT</div>
        <div class="signal-info">Entry: $${s.entry_price || 'TBA'}</div>
      </div>
      <span class="signal-badge badge-${s.signal_type?.toLowerCase()}">${s.signal_type}</span>
    </div>`).join('');
}

// =============================================
// TOP COINS WIDGET (CoinGecko)
// =============================================

async function loadTopCoins() {
  try {
    const res = await fetch(`${CONFIG.COINGECKO_API}/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=5&page=1`);
    const coins = await res.json();
    const container = document.getElementById('top-coins-widget');

    container.innerHTML = coins.map(c => {
      const change = c.price_change_percentage_24h?.toFixed(2) || 0;
      const isUp = change >= 0;
      return `<div class="coin-item">
        <span class="coin-name">${c.symbol.toUpperCase()}</span>
        <span class="coin-price">$${c.current_price.toLocaleString()}</span>
        <span class="coin-change ${isUp ? 'ticker-up' : 'ticker-down'}">${isUp ? '+' : ''}${change}%</span>
      </div>`;
    }).join('');
  } catch {
    document.getElementById('top-coins-widget').innerHTML = '<p style="padding:12px;font-size:12px;color:var(--text-muted)">Loading...</p>';
  }
}

// =============================================
// AFFILIATE WIDGET
// =============================================

async function loadAffiliateWidget() {
  const affiliates = await DB.getAffiliates();
  const container = document.getElementById('affiliate-widget');

  if (!affiliates.length) {
    container.style.display = 'none';
    return;
  }

  container.innerHTML = affiliates.map((a, i) => `
    <a href="${a.url}" target="_blank" rel="noopener" class="affiliate-btn ${i > 0 ? 'secondary' : ''}"
       onclick="DB.trackEvent('home', '${a.id}', 'affiliate_click')">
      Trade on ${a.name} ${a.commission_rate ? `· ${a.commission_rate} commission` : ''}
    </a>`).join('');
}

// =============================================
// UTILITIES
// =============================================

function formatDate(dateStr) {
  if (!dateStr) return '';
  const date = new Date(dateStr);
  const now = new Date();
  const diff = now - date;
  const hours = Math.floor(diff / 3600000);
  if (hours < 1) return 'Just now';
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  if (days < 7) return `${days}d ago`;
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

function escapeHtml(text) {
  if (!text) return '';
  return text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}
