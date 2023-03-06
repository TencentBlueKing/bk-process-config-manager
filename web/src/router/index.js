import Vue from 'vue';
import VueRouter from 'vue-router';

import http from '@/api';
import store from '@/store';

Vue.use(VueRouter);

const ProcessManage = () => import(/* webpackChunkName: 'ProcessManage' */'@/views/ProcessManage').catch(() => window.showDeployTip());
const ProcessManageStatus = () => import(/* webpackChunkName: 'ProcessManageStatus' */'@/views/ProcessManage/Status').catch(() => window.showDeployTip());
const ProcessManageReleaseConfig = () => import(/* webpackChunkName: 'ProcessManageReleaseConfig' */'@/views/ProcessManage/ReleaseConfig').catch(() => window.showDeployTip());

const ProcessAttribute = () => import(/* webpackChunkName: 'ProcessAttribute' */'@/views/ProcessAttribute').catch(() => window.showDeployTip());

const ConfigFile = () => import(/* webpackChunkName: 'ConfigFile' */'@/views/ConfigFile').catch(() => window.showDeployTip());
const ConfigFileTemplate = () => import(/* webpackChunkName: 'ConfigFileTemplate' */'@/views/ConfigFile/Template').catch(() => window.showDeployTip());
const ConfigFileTemplateList = () => import(/* webpackChunkName: 'ConfigFileTemplateList' */'@/views/ConfigFile/Template/List').catch(() => window.showDeployTip());
const ConfigFileTemplateVersion = () => import(/* webpackChunkName: 'ConfigFileTemplateVersion' */'@/views/ConfigFile/Template/Version').catch(() => window.showDeployTip());
const ConfigFileTemplateVersionList = () => import(/* webpackChunkName: 'ConfigFileTemplateVersion' */'@/views/ConfigFile/Template/Version/List').catch(() => window.showDeployTip());
const ConfigFileTemplateVersionDetail = () => import(/* webpackChunkName: 'ConfigFileTemplateVersion' */'@/views/ConfigFile/Template/Version/Detail').catch(() => window.showDeployTip());
const ConfigFileTemplateDistribute = () => import(/* webpackChunkName: 'ConfigFileTemplateDistribute' */'@/views/ConfigFile/Template/Distribute').catch(() => window.showDeployTip());
const ConfigFileTemplateGenerate = () => import(/* webpackChunkName: 'ConfigFileTemplateGenerate' */'@/views/ConfigFile/Template/Generate').catch(() => window.showDeployTip());
const ConfigFileTemplateCheck = () => import(/* webpackChunkName: 'ConfigFileTemplateCheck' */'@/views/ConfigFile/Template/Check').catch(() => window.showDeployTip());

const TaskHistory = () => import(/* webpackChunkName: 'TaskHistory' */'@/views/TaskHistory').catch(() => window.showDeployTip());
const TaskHistoryList = () => import(/* webpackChunkName: 'TaskHistoryList' */'@/views/TaskHistory/List').catch(() => window.showDeployTip());
const TaskHistoryDetail = () => import(/* webpackChunkName: 'TaskHistoryDetail' */'@/views/TaskHistory/Detail').catch(() => window.showDeployTip());

const Statistics = () => import(/* webpackChunkName: 'Statistics' */'@/views/Statistics').catch(() => window.showDeployTip());

const NotFound = () => import(/* webpackChunkName: 'none' */'@/views/NotFound').catch(() => window.showDeployTip());

const routes = [
  {
    path: '/',
    redirect: '/process-manage/status',
  },
  {
    path: '/process-manage',
    name: 'process-manage',
    redirect: '/process-manage/status',
    component: ProcessManage,
    children: [
      {
        path: '/process-manage/status',
        name: 'process-manage-status',
        component: ProcessManageStatus,
      },
      {
        path: '/process-manage/release-config',
        name: 'process-manage-release',
        component: ProcessManageReleaseConfig,
      },
    ],
  },
  {
    path: '/process-attr/:type?',
    name: 'process-attr',
    component: ProcessAttribute,
    props: true,
  },
  {
    path: '/config-file',
    name: 'config-file',
    redirect: '/config-file/template',
    component: ConfigFile,
    children: [
      {
        path: '/config-file/template',
        component: ConfigFileTemplate,
        children: [
          {
            path: '',
            name: 'config-file-template-list', // 配置文件模板列表
            component: ConfigFileTemplateList,
          },
          {
            path: '/config-file/template/:templateId/version',
            component: ConfigFileTemplateVersion,
            children: [
              {
                path: '',
                name: 'config-file-template-version-list', // 配置文件模板版本列表
                component: ConfigFileTemplateVersionList,
              },
              {
                path: '/config-file/template/:templateId/version/:versionId/detail',
                name: 'config-file-template-version-detail', // 配置文件模板版本详情
                component: ConfigFileTemplateVersionDetail,
              },
            ],
          },
          {
            path: '/config-file/template/:templateId/distribute', // 配置文件模板下发
            name: 'config-file-template-distribute',
            component: ConfigFileTemplateDistribute,
          },
          {
            path: '/config-file/template/:templateId/generate', // 配置文件模板生成
            name: 'config-file-template-generate',
            component: ConfigFileTemplateGenerate,
          },
          {
            path: '/config-file/template/:templateId/check', // 配置检查
            name: 'config-file-template-check',
            component: ConfigFileTemplateCheck,
          },
        ],
      },
    ],
  },
  {
    path: '/task-history',
    name: 'task-history',
    redirect: '/task-history/list',
    component: TaskHistory,
    children: [
      {
        path: '/task-history/list',
        name: 'task-history-list',
        component: TaskHistoryList,
      },
      {
        path: '/task-history/detail/:jobId?',
        name: 'task-history-detail',
        component: TaskHistoryDetail,
      },
    ],
  },
  {
    path: '/statistics',
    name: 'statistics',
    component: Statistics,
    beforeEnter(to, from, next) {
      if (store.state.showStaticRouter) {
        next();
      } else {
        next({
          name: 'process-manage',
          replace: true,
        });
      }
    },
  },
  {
    path: '*',
    name: '404',
    component: NotFound,
  },
];

const router = new VueRouter({
  base: window.PROJECT_CONFIG.SITE_URL,
  mode: 'history',
  routes,
});

const cancelRequest = async () => {
  const allRequest = http.queue.get();
  const requestQueue = allRequest.filter(request => request.cancelWhenRouteChange);
  await http.cancel(requestQueue.map(request => request.requestId));
};

router.beforeEach(async (to, from, next) => {
  router.__from_name = from.name;
  await cancelRequest();
  if (!to.query.biz && store.state.bizId) {
    // 是否 replace
    let replace = false;
    const replaceNames = ['config-file-template-version-detail', 'config-file-template-version-preview'];
    for (const name of replaceNames) {
      if (from.name === name && to.name === name) {
        replace = true;
        break;
      }
    }
    // 给路由统一带上业务ID
    next({
      name: to.name,
      params: to.params,
      replace,
      query: {
        ...to.query,
        biz: store.state.bizId,
      },
    });
  } else {
    next();
  }
});

export default router;
