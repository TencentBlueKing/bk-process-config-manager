/**
 * @file main store
 * @author blueking
 */

import Vue from 'vue';
import Vuex from 'vuex';
// 一个一个引入，方便 IDE 解析
import iam from './modules/iam';
import cmdb from './modules/cmdb';
import configInstance from './modules/configInstance';
import configTemplate from './modules/configTemplate';
import configVersion from './modules/configVersion';
import job from './modules/job';
import meta from './modules/meta';
import process from './modules/process';
import home from './modules/home';
import { unifyObjectStyle } from '@/common/util';
import router from '@/router';

Vue.use(Vuex);

const store = new Vuex.Store({
  // 模块
  modules: {
    iam,
    cmdb,
    configInstance,
    configTemplate,
    configVersion,
    job,
    meta,
    process,
    home,
  },
  // 公共 store
  state: {
    appName: '',
    mainContentLoading: true,
    pageHeight: document.documentElement.clientHeight,
    bizList: [],
    bizId: '',
    bizName: '',
    authPage: false,
    authMap: {}, // 动作权限
    username: '',
    showStaticRouter: false,
    lang: '',
  },
  // 公共 getters
  getters: {
    enLang: state => state.lang === 'en',
  },
  // 公共 mutations
  mutations: {
    updateAppName(state, name) {
      state.appName = name;
    },
    setMainContentLoading(state, payload) {
      state.mainContentLoading = payload;
    },
    updatePageHeight(state, payload) {
      state.pageHeight = payload;
    },
    updateBizList(state, bizList) {
      state.bizList = bizList;
    },
    updateBiz(state, biz) {
      state.bizId = biz.bk_biz_id;
      state.bizName = biz.name;
    },
    updateAuthPage(state, hasAuth) {
      state.authPage = !!hasAuth;
    },
    updateAuthMap(state, authList = []) {
      authList.forEach((auth) => {
        if (auth.action_id) {
          Vue.set(state.authMap, auth.action_id, !!auth.is_allowed);
        }
      });
    },
    updateUsername(state, username) {
      state.username = username;
    },
    updateToggleStaticRouter(state, isShow) {
      state.showStaticRouter = isShow;
    },
    updateLang(state, lang) {
      state.lang = lang;
    },

    routeConfigTemplateList() { // 配置文件模板 ==> 列表
      router.push('/config-file/template');
    },
    routeConfigTemplateVersionList(state, { templateId }) { // 配置文件模板 ==> 版本列表
      router.push(`/config-file/template/${templateId}/version`);
    },
    routeConfigTemplateVersionDetail(state, { templateId, versionId, isPreview }) { // 配置文件模板 ==> 版本详情
      let url = `/config-file/template/${templateId}/version/${versionId}/detail`;
      if (isPreview) {
        url += '?preview=1';
      }
      router.push(url);
    },
    routeConfigTemplateDistribute(state, { templateId }) { // 配置文件模板 ==> 配置下发
      router.push(`/config-file/template/${templateId}/distribute`);
    },
    routeConfigTemplateGenerate(state, { templateId }) { // 配置文件模板 ==> 配置生成
      router.push(`/config-file/template/${templateId}/generate`);
    },
    routeConfigTemplateCheck(state, { templateId }) { // 配置文件模板 ==> 配置检查
      router.push(`/config-file/template/${templateId}/check`);
    },

    routeProcessManageStatus() { // 进程管理进程状态列表
      router.push('/process-manage/status');
    },
    routeProcessManageManage() { // 进程管理管理详情页
      router.push('/process-manage/manage');
    },
    routeProcessManageConfigInformationInstance(state, { type, serviceId, processId }) { // 进程管理配置进程实例
      if (processId) {
        router.push(`/process-manage/manage/${type}/service/${serviceId}/process/${processId}`);
      } else {
        router.push(`/process-manage/manage/${type}/service/${serviceId}/process`);
      }
    },
    routeProcessManageRelease() { // 进程管理配置下发页面
      router.push('/process-manage/release-config');
    },
    routeTaskHistoryList(state, highlightIds) { // 任务历史列表页
      if (highlightIds) {
        sessionStorage.setItem('taskHistoryHighlightIds', highlightIds);
      }
      router.push('/task-history/list');
    },
    routeTaskHistoryDetail(state, jobId) { // 任务历史列表页
      router.push(`/task-history/detail/${jobId}/`);
    },
    routeProcessAttr(state, { params, query }) {
      router.replace({ name: 'process-attr', params, query });
    },
  },
  actions: {},
});

/**
 * hack vuex dispatch, add third parameter `config` to the dispatch method
 *
 * @param {Object|string} _type vuex type
 * @param {Object} _payload vuex payload
 * @param {Object} config config 参数，主要指 http 的参数，详见 src/api/index initConfig
 *
 * @return {Promise} 执行请求的 promise
 */
store.dispatch = function (_type, _payload, config = {}) {
  const { type, payload } = unifyObjectStyle(_type, _payload);

  const action = { type, payload, config };
  const entry = store._actions[type];
  if (!entry) {
    if (NODE_ENV !== 'production') {
      console.error(`[vuex] unknown action type: ${type}`);
    }
    return;
  }

  store._actionSubscribers.forEach((sub) => {
    if (typeof sub === 'function') {
      sub(action, store.state);
    } else if (sub.after && typeof sub.after === 'function') {
      sub.after && sub.after(action, store.state);
    }
  });

  return entry.length > 1
    ? Promise.all(entry.map(handler => handler(payload, config)))
    : entry[0](payload, config);
};

export default store;
