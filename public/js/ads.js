// =============================================
// ADS INJECTION SYSTEM
// Loads ad codes from Supabase and injects into page
// =============================================

const ADS = {

  async init() {
    const placements = ['header', 'article_top', 'article_middle', 'article_bottom', 'sidebar', 'popup'];
    for (const placement of placements) {
      await this.inject(placement);
    }
  },

  async inject(placement) {
    const elementId = `ad-${placement.replace('_', '-')}`;
    const container = document.getElementById(elementId);
    if (!container) return;

    const ads = await DB.getAdCodes(placement);
    if (!ads.length) return;

    ads.forEach(ad => {
      const wrapper = document.createElement('div');
      wrapper.className = 'ad-wrapper';
      wrapper.style.cssText = 'margin: 16px 0; text-align: center;';
      wrapper.innerHTML = ad.code;
      container.appendChild(wrapper);

      // Execute any scripts in ad code
      wrapper.querySelectorAll('script').forEach(oldScript => {
        const newScript = document.createElement('script');
        Array.from(oldScript.attributes).forEach(attr => newScript.setAttribute(attr.name, attr.value));
        newScript.textContent = oldScript.textContent;
        oldScript.parentNode.replaceChild(newScript, oldScript);
      });
    });
  },
};
