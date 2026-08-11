<template>
  <header class="header">
    <div class="header-left">
      <div class="logo-container" @click="jumpToHome">
        <img class="logo-image" :src="appLogo" alt="Logo">
        <span class="title">{{ name }}</span>
      </div>
    </div>
    <div class="header-nav" v-test.common="'headNav'">
      <!--<router-link class="nav-item" to="/home">{{ $t('首页') }}</router-link>-->
      <router-link class="nav-item" to="/process-manage">{{ $t('进程管理') }}</router-link>
      <router-link class="nav-item" to="/process-attr">{{ $t('进程属性') }}</router-link>
      <router-link class="nav-item" to="/config-file">{{ $t('配置文件') }}</router-link>
      <router-link class="nav-item" to="/task-history">{{ $t('任务历史') }}</router-link>
      <router-link v-if="showStaticRouter" class="nav-item" to="/statistics">{{ $t('运营统计') }}</router-link>
    </div>
    <div class="header-right">
      <AuthSelect
        class="king-select"
        id="bk_biz_id"
        name="bk_biz_name"
        v-test.common="'headBiz'"
        searchable
        :option-list="bizList"
        :clearable="false"
        v-model="bizId"
        @selected="handleSelect">
      </AuthSelect>
      <bk-dropdown-menu align="right" :trigger="triggerType" @show="dropdownShow" @hide="dropdownHide" ref="dropdown">
        <div @click="triggerType = 'click'" :class="['header-nav-btn', 'header-nav-icon-btn', { 'dropdown-active': isShow }]" slot="dropdown-trigger">
          <i :class="`gsekit-icon gsekit-icon-lang-${language}`"></i>
        </div>
        <ul class="bk-dropdown-list" slot="dropdown-content">
          <li class="dropdown-list-item" :class="{ 'active': item.id === language }" v-for="item in langList" :key="item.id"
            @click="toggleLang(item)">
            <span :class="`gsekit-icon gsekit-icon-lang-${item.id}`"></span>{{ item.name }}
          </li>
        </ul>
      </bk-dropdown-menu>
      <bk-dropdown-menu
        align="center"
        ext-cls="profile-popover"
        v-if="username"
        :trigger="popTriggerType"
        @show="isPopoverActive = true"
        @hide="popoverHide">
        <div class="login-username" @click="handleClick" :class="isPopoverActive && 'active'" slot="dropdown-trigger">
          {{ username }}<span class="bk-icon icon-down-shape"></span>
        </div>
        <ul class="bk-dropdown-list" slot="dropdown-content">
          <li class="dropdown-list-item" @click="handleLogout">
            <span class="gsekit-icon gsekit-icon-logout-fill"></span>
            <span class="text">{{ $t('退出登录') }}</span>
          </li>
        </ul>
      </bk-dropdown-menu>
    </div>
  </header>
</template>

<script>
import { mapState, mapMutations, mapActions } from 'vuex';
import AuthSelect from '@/components/Auth/AuthSelect';
import logoSrc from '@/assets/images/favicon.png';

export default {
  components: {
    AuthSelect,
  },
  data() {
    return {
      isPopoverActive: false,
      bizId: '',
      isShow: false,
      bizList: [],
      langList: [
        {
          id: 'zh-cn', // zhCN
          name: '中文',
        },
        {
          id: 'en', // enUS
          name: 'English',
        },
      ],
      triggerType: 'mouseover',
      popTriggerType: 'mouseover',
    };
  },
  computed: {
    ...mapState(['username', 'appName']),
    showStaticRouter() {
      return this.$store.state.showStaticRouter;
    },
    name() {
      return this.$store.state.platform.i18n.name || this.appName
    },
    appLogo() {
      return this.$store.state.platform.appLogo || logoSrc;
    },
    language() {
      return window.language;
    },
  },
  watch: {
    bizId(val) {
      this.updateBiz(this.bizList.find(biz => biz.bk_biz_id === val) || {});
      localStorage.setItem('bizId', val);
      this.ajaxGetUserVisit();
      this.resetAuthInfo();
    },
  },
  created() {
    // 等 router 初始化完成后执行
    setTimeout(() => {
      this.getBizList();
    });
  },
  methods: {
    ...mapMutations(['updateBizList', 'updateBiz', 'updateAuthPage', 'updateAuthMap']),
    ...mapActions('iam', ['ajaxGetActionsAuth']),
    ...mapActions('meta', ['ajaxGetUserVisit']),
    async getBizList() {
      try {
        this.$store.commit('setMainContentLoading', true);
        const { data: bizList } = await this.$store.dispatch('cmdb/ajaxGetBizList');
        if (bizList.length) {
          bizList.forEach((item) => {
            item.bk_biz_id += '';
            item.name = item.bk_biz_name;
            item.bk_biz_name = `[${item.bk_biz_id}] ${item.bk_biz_name}`;
            item.view_business = item.permission ? !!item.permission.view_business : false;
          });
          this.bizList = bizList.sort((current, next) => Number(next.view_business) - Number(current.view_business));
          this.updateBizList(bizList);
          const targetBiz = this.$route.query.biz || localStorage.getItem('bizId');
          if (targetBiz && bizList.some(item => item.bk_biz_id === targetBiz)) {
            this.updateBiz(targetBiz);
            this.bizId = targetBiz;
          } else {
            this.bizId = bizList[0].bk_biz_id;
            this.$router.replace({
              query: {
                ...this.$route.query,
                biz: this.bizId,
              },
            });
          }
          await this.$nextTick(); // 等 vuex 数据更新后渲染组件
        }
      } catch (e) {
        console.warn(e);
      } finally {
        this.$emit('showMain');
        this.$store.commit('setMainContentLoading', false);
      }
    },
    dropdownShow() {
      this.isShow = true;
    },
    dropdownHide() {
      this.isShow = false;
      this.triggerType = 'mouseover';
    },
    popoverHide() {
      this.isPopoverActive = false;
      this.popTriggerType = 'mouseover';
    },
    handleClick() {
      this.popTriggerType = 'click';
    },
    toggleLang(item) {
      if (item.id !== this.language) {
        const {
          BK_COMPONENT_API_URL: overwriteUrl = '',
          BK_DOMAIN: domain = '',
        } = window.PROJECT_CONFIG;

        const api = `${overwriteUrl}/api/c/compapi/v2/usermanage/fe_update_user_language/?language=${item.id}`;
        const scriptId = 'jsonp-script';
        const prevJsonpScript = document.getElementById(scriptId);
        if (prevJsonpScript) {
          document.body.removeChild(prevJsonpScript);
        }
        const scriptEl = document.createElement('script');
        scriptEl.type = 'text/javascript';
        scriptEl.src = api;
        scriptEl.id = scriptId;
        document.body.appendChild(scriptEl);

        const today = new Date();
        today.setTime(today.getTime() + 1000 * 60 * 60 * 24);
        document.cookie = `blueking_language=${item.id};path=/;domain=${domain};expires=${today.toUTCString()}`;
        location.reload();
      }
    },
    handleSelect(bizId) {
      this.$router.push({
        query: {
          ...this.$route.query,
          biz: bizId,
        },
      });
    },
    jumpToHome() {
      this.$router.push('/process-manage/status');
    },
    handleLogout() {
      
      // 加上协议头
      let loginUrl = window.PROJECT_CONFIG.LOGIN_URL;
      if (!/http(s)?:\/\//.test(loginUrl)) {
        loginUrl = `${window.location.protocol}//${loginUrl}`;
      }
      location.href = `${loginUrl}?is_from_logout=1&c_url=${encodeURIComponent(window.location)}`;
    },
    async resetAuthInfo() {
      const currentBiz = this.bizList.find(item => item.bk_biz_id === this.bizId);
      this.updateAuthPage(currentBiz && !!currentBiz.view_business);
      try {
        const { data = [] } = await this.ajaxGetActionsAuth();
        this.updateAuthMap(data);
      } catch (e) {
        console.warn(e);
      }
    },
  },
};
</script>

<style scoped lang="postcss">
.header {
  display: flex;
  align-items: center;
  line-height: 52px;
  color: #96a2b9;
  background: #182132;
  font-size: 14px;

  .header-left {
    flex-shrink: 0;
    display: flex;
    width: 260px;

    .logo-container {
      display: flex;
      align-items: center;
      margin-left: 8px;
      transition: color .3s;

      .logo-image {
        padding: 0 8px;
        height: 28px;
        background: v-bind(appLogo) no-repeat 0 center;
      }

      .title {
        padding: 0 8px;
        font-size: 18px;
        font-weight: 700;
      }

      &:hover {
        color: #fff;
        transition: color .3s;
        cursor: pointer;
      }
    }
  }

  .header-nav {
    width: 100%;
    padding-left: 25px;

    .nav-item {
      margin-right: 40px;
      color: #96a2b9;
      transition: color .3s;

      &:hover,
      &.router-link-active {
        color: #fff;
        transition: color .3s;
      }
    }
  }

  .header-right {
    flex-shrink: 0;
    display: flex;
    align-items: center;
    padding-right: 60px;

    .king-select {
      width: 240px;
      background: #252f43;
      border-color: #252f43;

      /deep/ .bk-select-name {
        color: #d3d9e4;
      }
    }

    .login-username {
      display: flex;
      align-items: center;
      line-height: 40px;
      margin-left: 10px;
      cursor: pointer;
      transition: color .2s;
      user-select: none;

      .icon-down-shape {
        margin-left: 6px;
        transition: transform .2s;
      }

      &:hover {
        color: #fff;
        transition: color .2s;
      }

      &.active {
        color: #fff;
        transition: color .2s;

        .icon-down-shape {
          transform: rotate(-180deg);
          transition: transform .2s;
        }
      }
    }
  }
  .profile-popover {
    /deep/.bk-dropdown-content {
      top: 39px !important;
    }
  }
  .bk-dropdown-menu {
    /deep/.bk-dropdown-content {
      margin: 14px 0 !important;
      min-width: 100px;
    }
  
    .header-nav-btn {
      display: flex;
      flex-flow: row nowrap;
      align-items: center;
      justify-content: center;
      min-width: 32px;
      min-height: 32px;
      margin: 0 17px;
      width: 32px;
      font-size: 18px;
      padding: 0 7px;
  
      &.dropdown-active {
        background: rgba(255, 255, 255, .1);
        border-radius: 16px;
        color: #fff;
      }
    }
  
    .bk-dropdown-list {
  
      min-width: 100px;
      margin: 0;
      z-index: 2500;
      border-radius: 2px;
      background: #fff;
  
      li {
        display: block !important;
        height: 32px;
        line-height: 32px;
        padding: 0 8px;
        color: #63656e;
        text-decoration: none;
        white-space: nowrap;
        cursor: pointer;
        font-size: 12px;
  
        &:hover {
          background: #f5f7fa;
        }
        &.active {
          background-color: #eaf3ff;
          color: #3a84ff
        }
  
        .gsekit-icon {
          margin-right: 8px;
          font-size: 18px;
        }
      }
    }
  }
}
</style>

<style lang="postcss">
.tippy-tooltip.profile-popover-theme[data-size=small] {
  padding: 0;
  margin-top: 4px;
  .profile-popover-content {
    color: #63656e;
    line-height: 32px;
    height: 42px;
    padding: 4px 0;

    .bk-option {
      margin: 0;
      min-width: 100px;

      .bk-option-name {
        .gsekit-icon-logout-fill {
          font-size: 14px;
          margin-right: 4px;
        }
      }
    }
  }
}
</style>
