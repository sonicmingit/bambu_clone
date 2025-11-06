import { createRouter, createWebHistory } from 'vue-router';

const ModelList = () => import('../pages/ModelList.vue');
const ModelDetail = () => import('../pages/ModelDetail.vue');
const ModelManage = () => import('../pages/ModelManage.vue');

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/models'
    },
    {
      path: '/models',
      name: 'ModelList',
      component: ModelList
    },
    {
      path: '/models/:id',
      name: 'ModelDetail',
      component: ModelDetail
    },
    {
      path: '/manage',
      name: 'ModelManage',
      component: ModelManage
    }
  ],
  scrollBehavior() {
    return { top: 0 };
  }
});

export default router;
