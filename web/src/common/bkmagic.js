/**
 * @file 引入 bk-magic-vue 组件
 * @author blueking
 */

import Vue from 'vue';

// 全量引入
// import './fully-import'

// 按需引入
import './demand-import';

const Message = Vue.prototype.$bkMessage;
const notify = Vue.prototype.$bkNotify;

let messageInstance = null;
let notifyInstance = null;

export const messageError = (message, delay = 3000) => {
  messageInstance && messageInstance.close();
  messageInstance = Message({
    message,
    delay,
    theme: 'error',
  });
};

export const messageSuccess = (message, delay = 3000) => {
  messageInstance && messageInstance.close();
  messageInstance = Message({
    message,
    delay,
    theme: 'success',
  });
};

export const messageInfo = (message, delay = 3000) => {
  messageInstance && messageInstance.close();
  messageInstance = Message({
    message,
    delay,
    theme: 'primary',
  });
};

export const messageWarn = (message, delay = 3000) => {
  messageInstance && messageInstance.close();
  messageInstance = Message({
    message,
    delay,
    theme: 'warning',
    hasCloseIcon: true,
  });
};

export const deployNotify = (message = window.i18n.t('静态文件加载失败请刷新页面重试'), delay = 0) => {
  notifyInstance && notifyInstance.close();
  notifyInstance = notify({
    theme: 'error',
    title: window.i18n.t('系统提示'),
    message,
    delay,
    position: 'top-right',
    offsetY: 60,
  });
};

Vue.prototype.messageError = messageError;
Vue.prototype.messageSuccess = messageSuccess;
Vue.prototype.messageInfo = messageInfo;
Vue.prototype.messageWarn = messageWarn;
global.showDeployTip = deployNotify;
