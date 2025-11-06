<template>
  <section class="manage-layout">
    <header>
      <h1>模型管理中心</h1>
      <p>在此查看发布状态、审核进度以及模型性能数据。此页面可扩展为后台管理界面。</p>
    </header>

    <div class="manage-grid">
      <article class="card">
        <h2>待审核模型</h2>
        <p>提交的模型将在此展示审核状态，可与后端接口联动。</p>
        <button class="action">查看详情</button>
      </article>
      <article class="card">
        <h2>数据分析</h2>
        <p>展示下载量、点赞、收藏趋势，可整合图表组件。</p>
        <button class="action">生成报表</button>
      </article>
      <article class="card">
        <h2>创作者指南</h2>
        <p>统一的 MakerWorld 风格指南与上传规范。</p>
        <button class="action">查看指南</button>
      </article>
    </div>
  </section>
</template>

<style scoped>
.manage-layout {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

header h1 {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

header p {
  color: var(--text-secondary);
}

.manage-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1.5rem;
}

.card {
  background: rgba(12, 16, 32, 0.8);
  border-radius: 20px;
  padding: 1.75rem;
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: var(--shadow-lg);
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.card h2 {
  font-size: 1.25rem;
}

.card p {
  color: var(--text-secondary);
  flex: 1;
}

.action {
  align-self: flex-start;
  border-radius: 999px;
  border: none;
  padding: 0.6rem 1.4rem;
  background: rgba(0, 212, 255, 0.15);
  color: #6deaff;
  font-weight: 600;
  cursor: pointer;
}
</style>
