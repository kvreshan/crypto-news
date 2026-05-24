// =============================================
// SUPABASE CLIENT
// =============================================

const { createClient } = supabase;
const db = createClient(CONFIG.SUPABASE_URL, CONFIG.SUPABASE_ANON_KEY);

// =============================================
// DATABASE HELPERS
// =============================================

const DB = {

  // Get latest news with optional coin filter
  async getNews(limit = 6, offset = 0, coinFilter = null) {
    let query = db
      .from('news')
      .select('id, title, summary, coin_tags, image_url, views, published_at')
      .eq('is_published', true)
      .order('published_at', { ascending: false })
      .range(offset, offset + limit - 1);

    if (coinFilter && coinFilter !== 'all') {
      query = query.contains('coin_tags', [coinFilter]);
    }

    const { data, error } = await query;
    if (error) console.error('getNews error:', error);
    return data || [];
  },

  // Get single article by ID
  async getArticle(id) {
    const { data, error } = await db
      .from('news')
      .select('*')
      .eq('id', id)
      .eq('is_published', true)
      .single();

    if (error) console.error('getArticle error:', error);
    return data;
  },

  // Get active signals
  async getSignals(limit = 10) {
    const { data, error } = await db
      .from('signals')
      .select('*')
      .eq('is_active', true)
      .order('created_at', { ascending: false })
      .limit(limit);

    if (error) console.error('getSignals error:', error);
    return data || [];
  },

  // Get affiliate links
  async getAffiliates(coinTag = null) {
    let query = db
      .from('affiliate_links')
      .select('*')
      .eq('is_active', true);

    if (coinTag) {
      query = query.contains('coin_tags', [coinTag]);
    }

    const { data, error } = await query.limit(3);
    if (error) console.error('getAffiliates error:', error);
    return data || [];
  },

  // Get active ad codes by placement
  async getAdCodes(placement) {
    const { data, error } = await db
      .from('ad_codes')
      .select('*')
      .eq('placement', placement)
      .eq('is_active', true);

    if (error) console.error('getAdCodes error:', error);
    return data || [];
  },

  // Get settings
  async getSettings() {
    const { data, error } = await db
      .from('settings')
      .select('*');

    if (error) console.error('getSettings error:', error);
    const settings = {};
    (data || []).forEach(s => settings[s.key] = s.value);
    return settings;
  },

  // Track analytics event
  async trackEvent(page, itemId, event) {
    await db.from('analytics').insert({
      page,
      item_id: itemId,
      event,
      ip_hash: await hashIP(),
    });
  },

  // Increment article views
  async incrementViews(newsId) {
    await db.rpc('increment_views', { news_id: newsId });
  },

  // Track affiliate click
  async trackAffiliateClick(affiliateId) {
    await db
      .from('affiliate_links')
      .update({ clicks: db.raw('clicks + 1') })
      .eq('id', affiliateId);
  },
};

// Simple IP hash for privacy
async function hashIP() {
  try {
    const res = await fetch('https://api.ipify.org?format=json');
    const { ip } = await res.json();
    const encoder = new TextEncoder();
    const data = encoder.encode(ip);
    const hash = await crypto.subtle.digest('SHA-256', data);
    return Array.from(new Uint8Array(hash)).map(b => b.toString(16).padStart(2, '0')).join('').slice(0, 16);
  } catch {
    return 'unknown';
  }
}
