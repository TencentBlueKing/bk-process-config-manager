import { moduleMap, testAnchorMap } from '@/config/test-anchor-key';
import { camelize } from './util';

const modulesMap = {};
const all = [];
const moduleNames = Object.keys(testAnchorMap);
moduleNames.forEach((moduleName) => {
  modulesMap[moduleName] = Array.from(Object.values(testAnchorMap[moduleName])).map(item => `${moduleName}_${item}`);
  all.push(...modulesMap[moduleName]);
});

window.testAnchor = {
  moduleMap: testAnchorMap,
  moduleSet: modulesMap,
  moduleUnknown: [],
  all,
};

export default class TestAnchorDirective {
  static install(Vue) {
    Vue.directive('test', {
      bind(el, { value, modifiers }, { context }) {
        let moduleName = moduleNames.find(key => modifiers[key]) || camelize(context.$route.name);
        moduleName = moduleMap[moduleName] || moduleName;
        const anchorModule = testAnchorMap[moduleName];
        if (anchorModule?.[value]) {
          el.setAttribute('data-test-id', `${moduleName}_${anchorModule[value]}`);
        } else {
          window.testAnchor.moduleUnknown.push({ module: moduleName, key: value });
          console.warn(`not find test anchor: data-test-id="{{${moduleName}.${value}}}"`);
        }
      },
    });
  }
}
