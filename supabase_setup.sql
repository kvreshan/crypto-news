-- =============================================
-- CRYPTO NEWS SITE - SUPABASE SETUP SQL
-- Run this in Supabase SQL Editor
-- =============================================

-- 1. NEWS TABLE
create table if not exists news (
  id uuid default gen_random_uuid() primary key,
  title text not null,
  summary text,
  content text,
  coin_tags text[] default '{}',
  image_url text,
  image_credit text,
  affiliate_link_id uuid,
  market_analysis jsonb,
  views integer default 0,
  is_published boolean default true,
  ai_provider text default 'claude',
  published_at timestamptz default now(),
  created_at timestamptz default now()
);

-- 2. SIGNALS TABLE
create table if not exists signals (
  id uuid default gen_random_uuid() primary key,
  coin text not null,
  signal_type text check (signal_type in ('BUY','SELL','HOLD')),
  entry_price numeric,
  target_price numeric,
  stop_loss numeric,
  content text,
  confidence integer check (confidence between 1 and 100),
  is_active boolean default true,
  created_at timestamptz default now()
);

-- 3. AFFILIATE LINKS TABLE
create table if not exists affiliate_links (
  id uuid default gen_random_uuid() primary key,
  name text not null,
  url text not null,
  coin_tags text[] default '{}',
  commission_rate text,
  clicks integer default 0,
  is_active boolean default true,
  created_at timestamptz default now()
);

-- 4. AD CODES TABLE
create table if not exists ad_codes (
  id uuid default gen_random_uuid() primary key,
  name text not null,
  placement text check (placement in ('header','article_top','article_middle','article_bottom','sidebar','popup')),
  code text not null,
  is_active boolean default true,
  created_at timestamptz default now()
);

-- 5. ANALYTICS TABLE
create table if not exists analytics (
  id uuid default gen_random_uuid() primary key,
  page text,
  item_id uuid,
  event text check (event in ('view','click','affiliate_click')),
  ip_hash text,
  user_agent text,
  created_at timestamptz default now()
);

-- 6. ADMIN SETTINGS TABLE
create table if not exists settings (
  key text primary key,
  value text,
  updated_at timestamptz default now()
);

-- Default settings
insert into settings (key, value) values
  ('site_name', 'CryptoSignals LK'),
  ('site_description', 'Latest Crypto News, Signals & Market Analysis'),
  ('telegram_url', ''),
  ('auto_publish', 'true'),
  ('articles_per_day', '5')
on conflict (key) do nothing;

-- =============================================
-- ROW LEVEL SECURITY (RLS)
-- =============================================

alter table news enable row level security;
alter table signals enable row level security;
alter table affiliate_links enable row level security;
alter table ad_codes enable row level security;
alter table analytics enable row level security;
alter table settings enable row level security;

-- Public can read published news
create policy "Public read news" on news
  for select using (is_published = true);

-- Public can read active signals
create policy "Public read signals" on signals
  for select using (is_active = true);

-- Public can read active affiliate links
create policy "Public read affiliates" on affiliate_links
  for select using (is_active = true);

-- Public can read active ad codes
create policy "Public read ads" on ad_codes
  for select using (is_active = true);

-- Public can read settings
create policy "Public read settings" on settings
  for select using (true);

-- Public can insert analytics
create policy "Public insert analytics" on analytics
  for insert with check (true);

-- Authenticated (admin) can do everything
create policy "Admin all news" on news
  for all using (auth.role() = 'authenticated');

create policy "Admin all signals" on signals
  for all using (auth.role() = 'authenticated');

create policy "Admin all affiliates" on affiliate_links
  for all using (auth.role() = 'authenticated');

create policy "Admin all ads" on ad_codes
  for all using (auth.role() = 'authenticated');

create policy "Admin all settings" on settings
  for all using (auth.role() = 'authenticated');

create policy "Admin read analytics" on analytics
  for select using (auth.role() = 'authenticated');

-- =============================================
-- AUTO CLEANUP FUNCTION (30 days)
-- =============================================

create or replace function cleanup_old_data()
returns void as $$
begin
  delete from news where published_at < now() - interval '30 days';
  delete from analytics where created_at < now() - interval '30 days';
  delete from signals where created_at < now() - interval '30 days' and is_active = false;
end;
$$ language plpgsql;

-- =============================================
-- UPDATE VIEWS FUNCTION
-- =============================================

create or replace function increment_views(news_id uuid)
returns void as $$
begin
  update news set views = views + 1 where id = news_id;
end;
$$ language plpgsql;

-- =============================================
-- SAMPLE DATA (optional - delete if not needed)
-- =============================================

insert into affiliate_links (name, url, coin_tags, commission_rate) values
  ('Binance', 'https://www.binance.com/en/register?ref=YOUR_REF', '{BTC,ETH,BNB}', '20%'),
  ('Bybit', 'https://www.bybit.com/invite?ref=YOUR_REF', '{BTC,ETH}', '30%'),
  ('OKX', 'https://www.okx.com/join/YOUR_REF', '{BTC,ETH,OKB}', '50%')
on conflict do nothing;
