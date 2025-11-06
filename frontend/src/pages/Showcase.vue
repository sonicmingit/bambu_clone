<template>
  <section class="showcase">
    <header class="hero">
      <h1>模型资源展示</h1>
      <p class="lead">直接读取后端提供的演示数据，快速了解项目输出。</p>
    </header>

    <div v-if="loading" class="status">正在加载模型列表...</div>
    <div v-else-if="error" class="status error">{{ error }}</div>

    <ul v-else class="model-list">
      <li v-for="model in models" :key="model.id" class="model-card">
        <h2>{{ model.name }}</h2>
        <p class="description">{{ model.description }}</p>
        <dl class="meta">
          <div>
            <dt>分类</dt>
            <dd>{{ model.category || '未分类' }}</dd>
          </div>
          <div>
            <dt>负责人</dt>
            <dd>{{ model.owner || '未知' }}</dd>
          </div>
        </dl>
        <RouterLink class="detail-link" :to="`/models/${model.id}`">查看详情 →</RouterLink>
      </li>
    </ul>
  </section>
</template>

<script setup>
import { onMounted, ref } from 'vue';
import { fetchModels } from '../services/modelService';

const loading = ref(true);
const error = ref('');
const models = ref([]);

async function loadModels() {
  loading.value = true;
  error.value = '';
  try {
    const response = await fetchModels();
    models.value = Array.isArray(response) ? response : response?.data || [];
  } catch (err) {
    error.value = err?.response?.data?.message || '加载模型数据失败，请稍后再试。';
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  loadModels();
});
</script>

<style scoped>
.showcase {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.hero {
  padding: 2.5rem 2rem;
  border-radius: 20px;
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.15), rgba(122, 92, 255, 0.25));
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: 0 25px 40px rgba(8, 12, 24, 0.35);
}

.hero h1 {
  margin: 0;
  font-size: 2.25rem;
}

.hero .lead {
  margin-top: 0.75rem;
  color: rgba(255, 255, 255, 0.8);
}

.status {
  padding: 1rem 1.5rem;
  border-radius: 16px;
  background: rgba(12, 16, 32, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.status.error {
  color: #ffb3b3;
  border-color: rgba(255, 99, 132, 0.35);
}

.model-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 1.5rem;
}

.model-card {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding: 1.75rem;
  border-radius: 20px;
  background: rgba(12, 16, 32, 0.75);
  border: 1px solid rgba(255, 255, 255, 0.06);
  box-shadow: 0 18px 30px rgba(7, 11, 20, 0.3);
}

.model-card h2 {
  margin: 0;
  font-size: 1.3rem;
}

.description {
  color: rgba(255, 255, 255, 0.75);
  min-height: 3rem;
}

.meta {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.75rem;
  margin: 0;
}

.meta div {
  background: rgba(255, 255, 255, 0.04);
  border-radius: 14px;
  padding: 0.6rem 0.85rem;
}

.meta dt {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: rgba(255, 255, 255, 0.55);
}

.meta dd {
  margin: 0.35rem 0 0;
  font-weight: 600;
  color: #ffffff;
}

.detail-link {
  margin-top: auto;
  align-self: flex-start;
  text-decoration: none;
  font-weight: 600;
  color: #00d4ff;
}

.detail-link:hover {
  text-decoration: underline;
}

@media (max-width: 640px) {
  .hero {
    padding: 2rem 1.5rem;
  }

  .model-list {
    grid-template-columns: 1fr;
  }
}
</style>
