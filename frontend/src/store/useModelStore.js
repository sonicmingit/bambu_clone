import { defineStore } from 'pinia';

export const useModelStore = defineStore('modelStore', {
  state: () => ({
    categories: [],
    tags: [],
    lastFetchedAt: null
  }),
  actions: {
    setMeta(meta) {
      if (meta?.categories) {
        this.categories = meta.categories;
      }
      if (meta?.tags) {
        this.tags = meta.tags;
      }
      this.lastFetchedAt = Date.now();
    }
  }
});
