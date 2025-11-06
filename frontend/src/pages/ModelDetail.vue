<template>
  <section class="detail-layout" v-if="!state.loading && !state.error">
    <header class="detail-header">
      <RouterLink to="/models" class="back-link">← 返回模型列表</RouterLink>
      <div class="header-content">
        <div>
          <p class="eyebrow">模型详情</p>
          <h1>{{ model?.name || '未命名模型' }}</h1>
          <p class="lead">由 {{ model?.author || '匿名创客' }} 发布 · 最近更新 {{ formatDate(model?.updated_at) }}</p>
        </div>
        <button class="primary" @click="downloadAll" :disabled="!attachments.length">下载全部</button>
      </div>
    </header>

    <section class="detail-body">
      <figure class="preview-card">
        <img :src="model?.preview || fallbackImage" :alt="model?.name" />
        <figcaption>
          <div class="stat">
            <span class="label">下载</span>
            <span class="value">{{ formatNumber(model?.downloads) }}</span>
          </div>
          <div class="stat">
            <span class="label">点赞</span>
            <span class="value">{{ formatNumber(model?.likes) }}</span>
          </div>
          <div class="stat">
            <span class="label">收藏</span>
            <span class="value">{{ formatNumber(model?.favorites) }}</span>
          </div>
        </figcaption>
      </figure>

      <article class="content-card">
        <h2>模型介绍</h2>
        <p>{{ model?.description || '暂无描述。' }}</p>

        <section class="meta-grid">
          <div>
            <h3>分类</h3>
            <p>{{ model?.category || '未分类' }}</p>
          </div>
          <div>
            <h3>标签</h3>
            <p>
              <span v-for="tag in model?.tags || []" :key="tag" class="tag">#{{ tag }}</span>
              <span v-if="!(model?.tags?.length)">暂无标签</span>
            </p>
          </div>
          <div>
            <h3>打印材料</h3>
            <p>{{ model?.material || '未指定' }}</p>
          </div>
          <div>
            <h3>模型尺寸</h3>
            <p>{{ model?.size || '未提供' }}</p>
          </div>
        </section>
      </article>

      <aside class="attachment-card">
        <header>
          <h2>附件下载</h2>
          <p class="hint">包含 STL、3MF 等格式，点击即可下载。</p>
        </header>
        <ul>
          <li v-for="attachment in attachments" :key="attachment.id" class="attachment-item">
            <div>
              <p class="file-name">{{ attachment.name }}</p>
              <p class="file-meta">{{ attachment.type?.toUpperCase() || '文件' }} · {{ formatFileSize(attachment.size) }}</p>
            </div>
            <a class="download" :href="attachment.url" target="_blank" rel="noopener" download>下载</a>
          </li>
          <li v-if="!attachments.length" class="empty">暂无可下载附件</li>
        </ul>
      </aside>
    </section>
  </section>

  <div v-else-if="state.loading" class="feedback">加载中...</div>
  <div v-else class="feedback error">{{ state.error }}</div>
</template>

<script setup>
import { computed, onMounted, reactive } from 'vue';
import { useRoute } from 'vue-router';
import { fetchModelDetail } from '../services/modelService';

const route = useRoute();
const state = reactive({
  loading: true,
  error: ''
});

const model = computed(() => state.model || null);
const attachments = computed(() => state.attachments || []);

const fallbackImage =
  'https://images.unsplash.com/photo-1545239351-ef35f43d514b?auto=format&fit=crop&w=1600&q=80';

function formatNumber(value) {
  if (!value && value !== 0) return '—';
  if (value >= 10000) return `${(value / 1000).toFixed(0)}k`;
  return new Intl.NumberFormat('zh-CN').format(value);
}

function formatFileSize(bytes) {
  if (!bytes) return '未知大小';
  const units = ['B', 'KB', 'MB', 'GB'];
  let size = bytes;
  let unitIndex = 0;
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024;
    unitIndex += 1;
  }
  return `${size.toFixed(size >= 10 || unitIndex === 0 ? 0 : 1)} ${units[unitIndex]}`;
}

function formatDate(value) {
  if (!value) return '未知时间';
  return new Intl.DateTimeFormat('zh-CN', {
    dateStyle: 'medium'
  }).format(new Date(value));
}

async function loadDetail() {
  state.loading = true;
  state.error = '';
  try {
    const response = await fetchModelDetail(route.params.id);
    const { data, attachments: files } = normalizeDetailResponse(response);
    state.model = data;
    state.attachments = files;
  } catch (error) {
    state.error = error?.response?.data?.message || '加载模型详情失败，请稍后重试。';
  } finally {
    state.loading = false;
  }
}

function normalizeDetailResponse(response) {
  if (!response) {
    return {
      data: {},
      attachments: []
    };
  }

  if (response.data) {
    return {
      data: response.data,
      attachments: response.attachments || response.data.attachments || []
    };
  }

  return {
    data: response,
    attachments: response.attachments || []
  };
}

function downloadAll() {
  attachments.value.forEach((file) => {
    if (!file?.url) return;
    const link = document.createElement('a');
    link.href = file.url;
    link.download = file.name || 'model-file';
    link.target = '_blank';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  });
}

onMounted(() => {
  loadDetail();
});
</script>

<style scoped>
.detail-layout {
  display: flex;
  flex-direction: column;
  gap: 2.5rem;
}

.detail-header {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  background: radial-gradient(circle at top left, rgba(122, 92, 255, 0.18), transparent 55%);
  border-radius: 28px;
  padding: 2.75rem 3rem;
  border: 1px solid var(--border-soft);
  box-shadow: var(--shadow-lg);
}

.back-link {
  color: var(--accent);
  text-decoration: none;
  font-weight: 500;
}

.header-content {
  display: flex;
  justify-content: space-between;
  gap: 2rem;
  align-items: center;
}

.header-content h1 {
  margin-top: 0.25rem;
  font-size: 2.5rem;
  line-height: 1.2;
}

.lead {
  color: var(--text-secondary);
  margin-top: 0.35rem;
}

.primary {
  border: none;
  padding: 0.75rem 1.75rem;
  border-radius: 999px;
  background: linear-gradient(135deg, #00d4ff 0%, #7a5cff 100%);
  color: #05070f;
  font-weight: 600;
  cursor: pointer;
}

.detail-body {
  display: grid;
  grid-template-columns: 2fr 3fr;
  gap: 1.75rem;
  align-items: start;
}

.preview-card {
  background: rgba(12, 16, 32, 0.75);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 26px;
  overflow: hidden;
  box-shadow: var(--shadow-lg);
}

.preview-card img {
  width: 100%;
  display: block;
  object-fit: cover;
  max-height: 420px;
}

.preview-card figcaption {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  background: rgba(4, 6, 12, 0.9);
}

.stat {
  padding: 1rem 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  align-items: flex-start;
}

.stat .label {
  color: rgba(255, 255, 255, 0.55);
  font-size: 0.85rem;
}

.stat .value {
  font-weight: 700;
  font-size: 1.3rem;
}

.content-card {
  background: rgba(12, 16, 32, 0.82);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 26px;
  padding: 2.25rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  box-shadow: var(--shadow-lg);
}

.content-card h2 {
  font-size: 1.5rem;
}

.content-card p {
  color: var(--text-secondary);
  line-height: 1.7;
}

.meta-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1.25rem;
}

.meta-grid h3 {
  font-size: 0.95rem;
  color: rgba(245, 247, 251, 0.7);
  margin-bottom: 0.4rem;
}

.tag {
  background: rgba(0, 212, 255, 0.12);
  color: #6deaff;
  border-radius: 999px;
  padding: 0.25rem 0.75rem;
  margin-right: 0.4rem;
}

.attachment-card {
  grid-column: span 2;
  background: rgba(12, 16, 32, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 24px;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  box-shadow: var(--shadow-lg);
}

.attachment-card header h2 {
  font-size: 1.4rem;
}

.hint {
  color: var(--text-secondary);
  margin-top: 0.3rem;
}

.attachment-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.25rem 1.5rem;
  border-radius: 18px;
  background: rgba(4, 6, 12, 0.75);
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.file-name {
  font-weight: 600;
  color: #ffffff;
}

.file-meta {
  color: rgba(255, 255, 255, 0.55);
  font-size: 0.85rem;
  margin-top: 0.35rem;
}

.download {
  border-radius: 999px;
  padding: 0.5rem 1.25rem;
  text-decoration: none;
  background: rgba(0, 212, 255, 0.15);
  color: #6deaff;
  font-weight: 600;
}

.empty {
  text-align: center;
  color: var(--text-secondary);
  padding: 2rem 0;
}

.feedback {
  text-align: center;
  padding: 4rem;
  background: rgba(12, 16, 32, 0.7);
  border-radius: 24px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: var(--text-secondary);
}

.feedback.error {
  color: #ff8a8a;
}

@media (max-width: 1024px) {
  .detail-body {
    grid-template-columns: 1fr;
  }

  .attachment-card {
    grid-column: span 1;
  }
}

@media (max-width: 720px) {
  .header-content {
    flex-direction: column;
    align-items: flex-start;
  }

  .primary {
    width: 100%;
  }
}
</style>
