<template>
  <section class="page-section">
    <header class="hero">
      <div>
        <p class="eyebrow">灵感库</p>
        <h1>探索全球创客的 3D 模型</h1>
        <p class="subtitle">搜索、筛选并发现最热门的打印模型，复刻 MakerWorld 的浏览体验。</p>
      </div>
      <div class="stats-pill">
        <div>
          <span class="metric">{{ formattedTotal }}</span>
          <span class="label">模型收录</span>
        </div>
        <div>
          <span class="metric">{{ filters.pageSize }}</span>
          <span class="label">每页显示</span>
        </div>
      </div>
    </header>

    <div class="toolbar-card">
      <form class="search-bar" @submit.prevent="applySearch">
        <span class="icon">🔍</span>
        <input v-model="searchInput" type="search" placeholder="搜索模型、作者或标签" />
        <button type="submit">搜索</button>
      </form>

      <div class="filter-group">
        <label>
          分类
          <select v-model="filters.category" @change="refresh">
            <option value="">全部</option>
            <option v-for="category in categories" :key="category" :value="category">{{ category }}</option>
          </select>
        </label>
        <label>
          标签
          <select v-model="filters.tag" @change="refresh">
            <option value="">全部</option>
            <option v-for="tag in tags" :key="tag" :value="tag">{{ tag }}</option>
          </select>
        </label>
        <label>
          排序
          <select v-model="filters.sort" @change="refresh">
            <option value="trending">趋势优先</option>
            <option value="latest">最新发布</option>
            <option value="popular">下载最多</option>
            <option value="rating">评分最高</option>
          </select>
        </label>
      </div>
    </div>

    <Transition name="fade" mode="out-in">
      <div v-if="state.loading" key="loading" class="feedback">加载中...</div>
      <div v-else-if="state.error" key="error" class="feedback error">{{ state.error }}</div>
      <div v-else key="list">
        <div v-if="state.models.length" class="model-grid">
          <article v-for="model in state.models" :key="model.id" class="model-card">
            <RouterLink :to="`/models/${model.id}`" class="preview">
              <img :src="model.thumbnail || fallbackImage" :alt="model.name" loading="lazy" />
              <span class="badge" v-if="model.badge">{{ model.badge }}</span>
            </RouterLink>
            <div class="card-body">
              <RouterLink :to="`/models/${model.id}`" class="title">{{ model.name }}</RouterLink>
              <p class="author">由 {{ model.author || '匿名创客' }} 发布</p>
              <ul class="meta">
                <li>
                  <span class="meta-label">下载</span>
                  <span>{{ formatNumber(model.downloads) }}</span>
                </li>
                <li>
                  <span class="meta-label">点赞</span>
                  <span>{{ formatNumber(model.likes) }}</span>
                </li>
                <li>
                  <span class="meta-label">更新时间</span>
                  <span>{{ formatDate(model.updated_at) }}</span>
                </li>
              </ul>
              <div class="tag-row">
                <span v-for="tag in model.tags?.slice(0, 3)" :key="tag" class="tag">#{{ tag }}</span>
              </div>
            </div>
          </article>
        </div>
        <div v-else class="feedback">未找到匹配的模型，试试调整筛选条件。</div>
      </div>
    </Transition>

    <footer class="pagination" v-if="totalPages > 1">
      <button :disabled="filters.page === 1" @click="goToPage(filters.page - 1)">上一页</button>
      <button
        v-for="page in pageNumbers"
        :key="page"
        :class="['page-btn', { active: page === filters.page }]"
        @click="goToPage(page)"
      >
        {{ page }}
      </button>
      <button :disabled="filters.page === totalPages" @click="goToPage(filters.page + 1)">下一页</button>
    </footer>
  </section>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue';
import { storeToRefs } from 'pinia';
import { useModelStore } from '../store/useModelStore';
import { fetchModels } from '../services/modelService';

const store = useModelStore();
const { categories, tags } = storeToRefs(store);

const state = reactive({
  loading: false,
  error: '',
  models: [],
  total: 0
});

const filters = reactive({
  page: 1,
  pageSize: 12,
  sort: 'trending',
  category: '',
  tag: '',
  search: ''
});

const searchInput = ref('');
const fallbackImage =
  'https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?auto=format&fit=crop&w=900&q=80';

const formattedTotal = computed(() => (state.total ? formatNumber(state.total) : '—'));
const totalPages = computed(() => (filters.pageSize ? Math.ceil(state.total / filters.pageSize) : 1));

const pageNumbers = computed(() => {
  const pages = [];
  const maxToShow = 5;
  const start = Math.max(1, filters.page - Math.floor(maxToShow / 2));
  const end = Math.min(totalPages.value, start + maxToShow - 1);
  for (let i = start; i <= end; i += 1) {
    pages.push(i);
  }
  return pages;
});

function formatNumber(value) {
  if (!value && value !== 0) return '—';
  if (value >= 10000) return `${(value / 1000).toFixed(0)}k`;
  return new Intl.NumberFormat('zh-CN').format(value);
}

function formatDate(value) {
  if (!value) return '—';
  return new Intl.DateTimeFormat('zh-CN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  }).format(new Date(value));
}

async function loadModels() {
  state.loading = true;
  state.error = '';
  try {
    const response = await fetchModels({
      page: filters.page,
      pageSize: filters.pageSize,
      sort: filters.sort,
      category: filters.category || undefined,
      tag: filters.tag || undefined,
      search: filters.search || undefined
    });
    const { data, meta } = normalizeResponse(response);
    state.models = data;
    state.total = meta.total ?? data.length;
    if (meta.categories || meta.tags) {
      store.setMeta(meta);
    }
  } catch (error) {
    state.error = error?.response?.data?.message || '加载模型列表失败，请稍后重试。';
  } finally {
    state.loading = false;
  }
}

function normalizeResponse(response) {
  if (Array.isArray(response)) {
    return {
      data: response,
      meta: {
        total: response.length
      }
    };
  }
  return {
    data: response?.data || [],
    meta: response?.meta || {}
  };
}

function applySearch() {
  filters.search = searchInput.value.trim();
  filters.page = 1;
  loadModels();
}

function refresh() {
  filters.page = 1;
  loadModels();
}

function goToPage(page) {
  if (page === filters.page || page < 1 || page > totalPages.value) return;
  filters.page = page;
  loadModels();
}

onMounted(() => {
  loadModels();
});
</script>

<style scoped>
.page-section {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.hero {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  background: radial-gradient(circle at top left, rgba(0, 212, 255, 0.12), transparent 55%);
  border-radius: 28px;
  padding: 2.75rem 3rem;
  border: 1px solid var(--border-soft);
  box-shadow: var(--shadow-lg);
}

.hero h1 {
  font-size: 2.75rem;
  line-height: 1.15;
  margin: 0.35rem 0 0.75rem;
}

.eyebrow {
  font-weight: 600;
  text-transform: uppercase;
  font-size: 0.875rem;
  letter-spacing: 0.24em;
  color: var(--accent);
}

.subtitle {
  color: var(--text-secondary);
  max-width: 42rem;
  font-size: 1rem;
}

.stats-pill {
  background: rgba(12, 16, 32, 0.6);
  border-radius: 20px;
  padding: 1.5rem 2rem;
  border: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  gap: 1.5rem;
}

.stats-pill > div {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.metric {
  font-size: 1.75rem;
  font-weight: 700;
  color: #ffffff;
}

.label {
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.toolbar-card {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  padding: 1.75rem;
  background: rgba(12, 16, 32, 0.72);
  border-radius: 22px;
  border: 1px solid var(--border-soft);
}

.search-bar {
  display: flex;
  align-items: center;
  gap: 1rem;
  background: rgba(12, 16, 32, 0.82);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 18px;
  padding: 0.75rem 1.25rem;
}

.search-bar input {
  flex: 1;
  background: transparent;
  border: none;
  color: var(--text-primary);
  font-size: 1rem;
}

.search-bar input:focus {
  outline: none;
}

.search-bar button {
  border-radius: 999px;
  border: none;
  padding: 0.6rem 1.5rem;
  background: linear-gradient(135deg, #00d4ff 0%, #7a5cff 100%);
  color: #05070f;
  font-weight: 600;
  cursor: pointer;
}

.icon {
  font-size: 1.1rem;
}

.filter-group {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1.25rem;
}

.filter-group label {
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.filter-group select {
  background: rgba(12, 16, 32, 0.92);
  border-radius: 14px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 0.65rem 0.85rem;
  color: var(--text-primary);
}

.model-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 1.75rem;
}

.model-card {
  background: var(--card-gradient);
  border-radius: 26px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.05);
  box-shadow: var(--shadow-lg);
  display: flex;
  flex-direction: column;
  transition: transform 0.2s ease, border-color 0.2s ease;
}

.model-card:hover {
  transform: translateY(-4px);
  border-color: rgba(0, 212, 255, 0.3);
}

.preview {
  position: relative;
  display: block;
}

.preview img {
  width: 100%;
  height: 180px;
  object-fit: cover;
  display: block;
}

.badge {
  position: absolute;
  top: 1rem;
  left: 1rem;
  padding: 0.4rem 0.75rem;
  border-radius: 999px;
  background: rgba(0, 212, 255, 0.9);
  color: #041425;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
}

.card-body {
  padding: 1.25rem 1.5rem 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.title {
  color: #ffffff;
  font-weight: 600;
  font-size: 1.05rem;
  text-decoration: none;
}

.title:hover {
  color: var(--accent);
}

.author {
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.meta {
  display: flex;
  justify-content: space-between;
  list-style: none;
  background: rgba(12, 16, 32, 0.66);
  padding: 0.75rem 1rem;
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.meta-label {
  display: block;
  font-size: 0.75rem;
  color: rgba(245, 247, 251, 0.5);
}

.tag-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.tag {
  background: rgba(0, 212, 255, 0.12);
  color: #6deaff;
  border-radius: 999px;
  padding: 0.25rem 0.75rem;
  font-size: 0.75rem;
}

.feedback {
  text-align: center;
  padding: 3rem;
  color: var(--text-secondary);
  border-radius: 20px;
  background: rgba(12, 16, 32, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.feedback.error {
  color: #ff8a8a;
}

.pagination {
  display: flex;
  justify-content: center;
  gap: 0.5rem;
  margin-top: 1.5rem;
}

.pagination button {
  border: 1px solid rgba(255, 255, 255, 0.12);
  background: rgba(12, 16, 32, 0.72);
  color: var(--text-primary);
  border-radius: 12px;
  padding: 0.5rem 1rem;
  cursor: pointer;
  transition: background 0.2s ease, transform 0.2s ease;
}

.pagination button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.page-btn.active {
  background: linear-gradient(135deg, #00d4ff 0%, #7a5cff 100%);
  color: #05070f;
}

@media (max-width: 960px) {
  .hero {
    flex-direction: column;
    gap: 1.5rem;
  }

  .stats-pill {
    align-self: flex-start;
  }
}

@media (max-width: 600px) {
  .toolbar-card {
    padding: 1.25rem;
  }

  .search-bar {
    flex-wrap: wrap;
  }

  .search-bar button {
    width: 100%;
  }
}
</style>
