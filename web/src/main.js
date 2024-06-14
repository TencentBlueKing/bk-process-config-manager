import './public-path';
import Vue from 'vue';

import App from '@/App';
import router from '@/router';
import store from '@/store';
import i18n from '@/language/i18n';
import { bus } from '@/common/bus';
import '@/common/bkmagic';
import '@/common/directives';
import '@icon-cool/bk-icon-gsekit';
import '@/common/svg';
import '@/common/text-tool';
import { injectCSRFTokenToHeaders } from '@/api';
import '@/mixins/emptyMixin.js';
import StatusView from '@/components/StatusView';
import TableException from '@/components/Empty/TableException';
import VueCompositionAPI from '@vue/composition-api';

try {
  const id = window.PROJECT_CONFIG.TAM_AEGIS_KEY;
  if (id) {
    const aegis = new window.Aegis({
      id, // 项目key
      reportApiSpeed: true, // 接口测速
      reportAssetSpeed: true, // 静态资源测速
      spa: true,
    });
    window.__aegisInstance = aegis;
    Vue.config.errorHandler = function (err, vm, info) {
      aegis.error(`Error: ${err.toString()}\nInfo: ${info}`);
    };
  }
} catch (e) {
  console.warn('前端监控接入出错', e);
}

Vue.config.devtools = true;
Vue.component('StatusView', StatusView);
Vue.component('TableException', TableException);
Vue.use(VueCompositionAPI);

injectCSRFTokenToHeaders();
getUserInfo().then(() => {
  global.bus = bus;
  global.i18n = i18n;
  global.mainComponent = new Vue({
    el: '#app',
    router,
    store,
    i18n,
    components: { App },
    template: '<App/>',
  });
});

async function getUserInfo() {
  try {
    const res = await store.dispatch('meta/ajaxGetUserInfo');
    console.log("🚀 ~ getUserInfo ~ res:", res)
    this.username = res.data.username;
    store.commit('updateUsername', res.data.username);
    store.commit('updateToggleStaticRouter', !!res.data.is_superuser);
    if (window.__aegisInstance) {
      window.__aegisInstance.setConfig({
        uin: res.data.username,
      });
    }
  } catch (e) {
    console.log("🚀 ~ getUserInfo ~ e:", e)
    console.warn(e);
  }
}
