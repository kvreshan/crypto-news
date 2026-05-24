// =============================================
// ADMIN AUTH - shared across all admin pages
// =============================================

const { createClient } = supabase;
const db = createClient(CONFIG.SUPABASE_URL, CONFIG.SUPABASE_ANON_KEY);

async function requireAuth() {
  const { data: { session } } = await db.auth.getSession();
  if (!session) {
    window.location.href = '/admin/login.html';
    return false;
  }
  return true;
}

async function logout() {
  await db.auth.signOut();
  window.location.href = '/admin/login.html';
}
