// =============================================
// ARTICLE PAGE JAVASCRIPT
// =============================================

document.addEventListener('DOMContentLoaded', async () => {
  const params = new URLSearchParams(window.location.search);
  const id = params.get('id');

  if (!id) {
    window.location.href = '/';
    return;
  }

  // Load article
  const article = await DB.getArticle(id);

  if (!article) {
    document.getElementById('article-container').innerHTML = `
      <div style="text-align:center;padding:60px 20px;">
        <h2>Article not found</h2>
        <a href="/" style="color:var(--accent);margin-top:16px;display:inline-block;">← Back to Home</a>
      </div>`;
    return;
  }

  // Update meta
  document.title = `${article.title} | CryptoSignals LK`;
  document.querySelector('meta[name="description"]').content = article.summary || '';

  // Track view
  DB.incrementViews(id);
  DB.trackEvent('article', id, 'view');

  // Render article
  renderArticle(article);

  // Load ads
  ADS.init();

  // Hamburger
  document.getElementById('hamburger').addEventListener('click', () => {
    document.getElementById('mobile-menu').classList.toggle('open');
  });
});

// =============================================
// RENDER ARTICLE
// =============================================

function renderArticle(article) {
  const container = document.getElementById('article-container');
  const tags = (article.coin_tags || []).map(t => `<span class="tag">${t}</span>`).join('');
  const date = new Date(article.published_at).toLocaleDateString('en-US', {
    year: 'numeric', month: 'long', day: 'numeric'
  });
  const img = article.image_url || 'https://images.unsplash.com/photo-1621761191319-c6fb62004040?w=800&q=80';

  container.innerHTML = `
    <div class="article-header">
      <div class="article-tags">${tags}</div>
      <h1 class="article-title">${escapeHtml(article.title)}</h1>
      <div class="article-meta">
        <span>📅 ${date}</span>
        <span>👁 ${article.views || 0} views</span>
        <span>AI Generated</span>
      </div>
    </div>

    <img src="${img}" alt="${escapeHtml(article.title)}" class="article-image"
         onerror="this.src='https://images.unsplash.com/photo-1621761191319-c6fb62004040?w=800&q=80'">
    ${article.image_credit ? `<p style="font-size:11px;color:var(--text-muted);margin:-16px 0 24px;text-align:right;">Photo: ${escapeHtml(article.image_credit)}</p>` : ''}

    <div id="ad-article-middle"></div>

    <div class="article-content">
      ${formatContent(article.content || article.summary || '')}
    </div>

    ${renderMarketAnalysis(article.market_analysis, article.coin_tags)}

    ${renderAffiliateCTA(article)}

    <div id="ad-article-bottom"></div>

    <div style="margin-top:32px;padding-top:24px;border-top:1px solid var(--border);">
      <a href="/" style="color:var(--accent);font-size:14px;">← Back to News</a>
    </div>`;
}

// =============================================
// MARKET ANALYSIS BOX
// =============================================

function renderMarketAnalysis(analysis, coinTags) {
  if (!analysis) return '';

  const sentiment = analysis.sentiment_score || 50;
  const coin = (coinTags || [])[0] || 'Crypto';

  const signalClass = sentiment >= 60 ? 'signal-bullish' :
                      sentiment <= 40 ? 'signal-bearish' : 'signal-neutral';
  const signalText = sentiment >= 60 ? '📈 Bullish Outlook' :
                     sentiment <= 40 ? '📉 Bearish Outlook' : '⚖️ Neutral — Wait & Watch';

  return `
    <div class="market-analysis">
      <div class="market-analysis-title">
        📊 Market Analysis — ${coin}
      </div>

      <div class="market-grid">
        <div class="market-item">
          <div class="market-item-label">Short Term</div>
          <div class="market-item-value" style="color:${getSentimentColor(analysis.short_term)}">${analysis.short_term || 'Neutral'}</div>
        </div>
        <div class="market-item">
          <div class="market-item-label">Long Term</div>
          <div class="market-item-value" style="color:${getSentimentColor(analysis.long_term)}">${analysis.long_term || 'Neutral'}</div>
        </div>
        <div class="market-item">
          <div class="market-item-label">Key Support</div>
          <div class="market-item-value">${analysis.support || 'N/A'}</div>
        </div>
        <div class="market-item">
          <div class="market-item-label">Key Resistance</div>
          <div class="market-item-value">${analysis.resistance || 'N/A'}</div>
        </div>
      </div>

      ${analysis.key_insight ? `
        <div style="font-size:13px;color:var(--text-secondary);margin:12px 0;padding:12px;background:var(--bg-secondary);border-radius:8px;line-height:1.6;">
          💡 ${escapeHtml(analysis.key_insight)}
        </div>` : ''}

      <div style="font-size:12px;color:var(--text-muted);margin-bottom:6px;">
        Market Sentiment: ${sentiment}% Bullish
      </div>
      <div class="market-sentiment-bar">
        <div class="market-sentiment-fill" style="width:${sentiment}%"></div>
      </div>

      <div class="market-signal-box ${signalClass}">
        ${signalText}
      </div>

      <p style="font-size:11px;color:var(--text-muted);margin-top:12px;text-align:center;">
        ⚠️ This is AI-generated analysis. Not financial advice. DYOR.
      </p>
    </div>`;
}

function getSentimentColor(sentiment) {
  if (!sentiment) return 'var(--text-primary)';
  const s = sentiment.toLowerCase();
  if (s.includes('bull') || s.includes('positive') || s.includes('strong')) return 'var(--accent-green)';
  if (s.includes('bear') || s.includes('negative') || s.includes('weak')) return 'var(--accent-red)';
  return 'var(--accent-yellow)';
}

// =============================================
// AFFILIATE CTA
// =============================================

async function renderAffiliateCTA(article) {
  const coinTags = article.coin_tags || [];
  const affiliates = await DB.getAffiliates(coinTags[0]);

  const container = document.querySelector('.article-content');
  if (!affiliates.length || !container) return;

  const ctaHtml = `
    <div class="article-affiliate">
      <h4>Start Trading ${coinTags[0] || 'Crypto'} Today</h4>
      <p>Trade on trusted exchanges with competitive fees</p>
      <div style="display:flex;flex-direction:column;gap:8px;">
        ${affiliates.slice(0, 2).map(a => `
          <a href="${a.url}" target="_blank" rel="noopener" class="affiliate-btn"
             onclick="DB.trackEvent('article', '${a.id}', 'affiliate_click')">
            Trade on ${a.name}${a.commission_rate ? ` — ${a.commission_rate} commission` : ''}
          </a>`).join('')}
      </div>
    </div>`;

  container.insertAdjacentHTML('beforeend', ctaHtml);
}

// =============================================
// FORMAT ARTICLE CONTENT
// =============================================

function formatContent(text) {
  if (!text) return '';

  return text
    .split('\n\n')
    .map(para => {
      para = para.trim();
      if (!para) return '';
      if (para.startsWith('## ')) return `<h2>${escapeHtml(para.slice(3))}</h2>`;
      if (para.startsWith('# ')) return `<h2>${escapeHtml(para.slice(2))}</h2>`;
      if (para.startsWith('### ')) return `<h3>${escapeHtml(para.slice(4))}</h3>`;
      if (para.startsWith('- ') || para.startsWith('* ')) {
        const items = para.split('\n').map(l => `<li>${escapeHtml(l.slice(2))}</li>`).join('');
        return `<ul>${items}</ul>`;
      }
      return `<p>${escapeHtml(para)}</p>`;
    })
    .join('');
}

function escapeHtml(text) {
  if (!text) return '';
  return text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}
