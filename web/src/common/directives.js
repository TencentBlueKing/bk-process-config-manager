import Vue from 'vue';
import cursor from './cursor';
import Test from './directives-test';
import AuthTag from '@/components/Auth/AuthTag';

Vue.use(cursor);
Vue.use(Test);
Vue.component('AuthTag', AuthTag);
