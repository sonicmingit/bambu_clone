<template>
  <div class="app-shell">
    <header class="app-header">
      <div class="logo">MakerWorld</div>
      <nav class="nav-links">
        <RouterLink
          :to="{ name: 'Showcase' }"
          class="nav-link"
          active-class=""
          exact-active-class="is-active"
        >展示页</RouterLink>
        <RouterLink to="/models" class="nav-link" active-class="is-active">模型库</RouterLink>
        <RouterLink to="/manage" class="nav-link" active-class="is-active">模型管理</RouterLink>
      </nav>
      <div class="user-actions">
        <button class="action-btn primary">上传模型</button>
        <button class="action-btn ghost">登录</button>
      </div>
    </header>

    <main class="app-main">
      <slot />
    </main>

    <footer class="app-footer">
      <div>© {{ currentYear }} MakerWorld Inspired Experience</div>
      <div class="footer-links">
        <a href="#">关于我们</a>
        <a href="#">社区规范</a>
        <a href="#">帮助中心</a>
      </div>
    </footer>
  </div>
</template>

<script setup>
const currentYear = new Date().getFullYear();
</script>

<style scoped>
.app-shell {
  min-height: 100vh;
  background: linear-gradient(180deg, #101322 0%, #04060c 100%);
  color: #f5f7fb;
  font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  display: flex;
  flex-direction: column;
}

.app-header {
  position: sticky;
  top: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.25rem 3rem;
  background: rgba(12, 16, 32, 0.75);
  backdrop-filter: blur(12px);
  z-index: 10;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.logo {
  font-size: 1.5rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #00d4ff;
}

.nav-links {
  display: flex;
  gap: 1rem;
}

.nav-link {
  padding: 0.5rem 1.25rem;
  border-radius: 999px;
  color: rgba(255, 255, 255, 0.75);
  transition: background 0.2s, color 0.2s, transform 0.2s;
  font-weight: 500;
}

.nav-link:hover {
  background: rgba(0, 212, 255, 0.1);
  color: #ffffff;
  transform: translateY(-1px);
}

.nav-link.is-active {
  background: linear-gradient(135deg, #00d4ff 0%, #7a5cff 100%);
  color: #0b0f1e;
  font-weight: 600;
}

.user-actions {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

.action-btn {
  border: none;
  border-radius: 999px;
  padding: 0.5rem 1.25rem;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s, opacity 0.2s;
}

.action-btn.primary {
  background: linear-gradient(135deg, #00d4ff 0%, #7a5cff 100%);
  color: #05070f;
  box-shadow: 0 12px 30px rgba(122, 92, 255, 0.35);
}

.action-btn.primary:hover {
  transform: translateY(-1px) scale(1.01);
}

.action-btn.ghost {
  background: transparent;
  color: rgba(255, 255, 255, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.18);
}

.action-btn.ghost:hover {
  opacity: 0.9;
}

.app-main {
  flex: 1;
  width: min(1200px, 92vw);
  margin: 0 auto;
  padding: 3rem 0 4rem;
}

.app-footer {
  padding: 2rem 3rem;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: rgba(255, 255, 255, 0.55);
  font-size: 0.875rem;
}

.app-footer a {
  color: inherit;
  text-decoration: none;
  margin-left: 1.25rem;
}

.app-footer a:hover {
  color: #00d4ff;
}

@media (max-width: 768px) {
  .app-header {
    flex-direction: column;
    gap: 1rem;
  }

  .app-main {
    width: 100%;
    padding: 2.5rem 1rem 3.5rem;
  }

  .app-footer {
    flex-direction: column;
    gap: 0.75rem;
  }
}
</style>
