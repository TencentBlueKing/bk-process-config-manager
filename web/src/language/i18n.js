import Vue from 'vue';
import VueI18n from 'vue-i18n';
import cookie from 'cookie';
import { locale, lang } from 'bk-magic-vue';
import zh from '../language/lang/zh';
import en from '../language/lang/en';

Vue.use(VueI18n);

const localLanguage = cookie.parse(document.cookie).blueking_language || 'zh-cn';
// 等组件语言升级后删掉这代码
if (localLanguage === 'en') {
  locale.use(lang.enUS);
}
const i18n = new VueI18n({
  locale: localLanguage,
  fallbackLocale: 'zh-cn',
  messages: {
    'zh-cn': Object.assign(lang.zhCN, zh),
    en: Object.assign(lang.enUS, en),
  },
  silentTranslationWarn: false,
});
locale.i18n((key, value) => i18n.t(key, value));
window.language = localLanguage;

export default i18n;
