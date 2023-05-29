<template>
  <header class="header">
    <div class="header-left">
      <div class="logo-container" @click="jumpToHome">
        <img class="logo-image" src="../assets/images/favicon.png" alt="Logo">
        <span class="title">{{ appName }}</span>
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
      <MixinsControlDropdown>
        <div class="header-nav-btn header-nav-icon-btn">
          <i :class="`gsekit-icon gsekit-icon-lang-${lang}`" />
        </div>
        <template slot="content">
          <ul class="bk-dropdown-list">
            <li class="dropdown-list-item" v-for="item in langList" :key="item.id" @click="toggleLang(item)">
              <i :class="`gsekit-icon gsekit-icon-lang-${item.id}`" /> {{ item.name }}
            </li>
          </ul>
        </template>
      </MixinsControlDropdown>
      <MixinsControlDropdown>
        <div class="header-nav-btn header-nav-icon-btn">
          <i class="gsekit-icon gsekit-icon-help-document-fill"></i>
        </div>
        <template slot="content">
          <ul class="bk-dropdown-list">
            <li class="dropdown-list-item" v-for="item in helpList" :key="item.id" @click="handleGotoLink(item)">
              {{ item.name }}
            </li>
          </ul>
        </template>
      </MixinsControlDropdown>
      <MixinsControlDropdown>
        <div class="header-nav-btn login-username">
          {{ username }}<span class="bk-icon icon-down-shape"></span>
        </div>
        <template slot="content">
          <ul class="bk-dropdown-list">
            <li class="dropdown-list-item" @click="handleLogout">{{ $t('退出登录') }}</li>
          </ul>
        </template>
      </MixinsControlDropdown>
    </div>
    <bk-version-detail
      :current-version="currentVersion"
      :finished="finished"
      :show.sync="showVersionLog"
      :version-list="versionList"
      :version-detail="versionDetail"
      :get-version-detail="handleGetVersionDetail"
      :get-version-list="handleGetVersionList">
      <template slot-scope="content">
        <!-- eslint-disable-next-line vue/no-v-html -->
        <div class="detail-container" v-if="content" v-html="content.detail"></div>
      </template>
    </bk-version-detail>
  </header>
</template>

<script>
import { mapState, mapMutations, mapActions } from 'vuex';
import AuthSelect from '@/components/Auth/AuthSelect';
import MixinsControlDropdown from '@/components/MixinsControlDropdown';
import http from '@/api';

export default {
  components: {
    AuthSelect,
    MixinsControlDropdown,
  },
  data() {
    return {
      isPopoverActive: false,
      bizId: '',
      bizList: [],
      showVersionLog: false,
      helpList: [
        {
          id: 'DOC',
          name: this.$t('产品文档'),
          href: window.PROJECT_CONFIG.BK_DOCS_CENTER_URL,
        },
        {
          id: 'VERSION',
          name: this.$t('版本日志'),
        },
        {
          id: 'FAQ',
          name: this.$t('问题反馈'),
          href: 'https://bk.tencent.com/s-mart/community',
        },
        {
          id: 'OPEN',
          name: this.$t('开源社区'),
          href: window.PROJECT_CONFIG.BKAPP_NAV_OPEN_SOURCE_URL,
        },
      ],
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
      finished: false,
      currentVersion: '',
      versionDetail: '',
      versionList: [],
    };
  },
  computed: {
    ...mapState(['username', 'appName', 'lang']),
    showStaticRouter() {
      return this.$store.state.showStaticRouter;
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
      http.get(`${window.PROJECT_CONFIG.SITE_URL}logout/`);
      // location.href = `${window.PROJECT_CONFIG.LOGIN_URL}?&c_url=${window.location}`;
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
    toggleLang(item) {
      if (item.id !== this.lang) {
        const today = new Date();
        today.setTime(today.getTime() + 1000 * 60 * 60 * 24);
        const domainArr = document.domain.split('.');
        if (domainArr.length > 2) {
          domainArr.shift();
        }
        document.cookie = `blueking_language=0;path=/;domain=${domainArr.slice(-2).join('.')};expires=${new Date(0).toUTCString()}`;
        document.cookie = `blueking_language=${item.id};path=/;domain=${domainArr.join('.')};expires=${today.toUTCString()}`;
        document.cookie = `blueking_language=${item.id};path=/;domain=${domainArr.slice(-2).join('.')};expires=${today.toUTCString()}`;
        location.reload();
      }
    },
    handleGotoLink(item) {
      switch (item.id) {
        case 'DOC':
        case 'FAQ':
          item.href && window.open(item.href);
          break;
        case 'VERSION':
          this.showVersionLog = true;
          break;
      }
    },
    async handleGetVersionList() {
      const list = await http.get(`${window.PROJECT_CONFIG.SITE_URL}version_log/version_logs_list/`).catch(() => false);
      if (list) {
        this.finished = true;
        this.versionList = list.map(item => ({
          title: item[0],
          date: item[1],
        }));
      }
      const [firstVersion] = this.versionList;
      this.currentVersion = firstVersion?.title || '';
      return [...this.versionList];
    },
    async handleGetVersionDetail({ title }) {
      const detail = await http.get(`${window.PROJECT_CONFIG.SITE_URL}version_log/version_log_detail/?log_version=${title}`).catch(() => '');
      this.versionDetail = detail;
      return detail;
    },
  },
};
</script>

<style scoped lang="postcss">
  .header {
    display: flex;
    align-items: center;
    line-height: 52px;
    color: #eaebf0;
    background: #182132;
    font-size: 14px;

    .header-left {
      flex-shrink: 0;
      display: flex;
      width: 260px;

      .logo-container {
        display: flex;
        align-items: center;
        margin-left: 16px;
        transition: color .3s;

        .logo-image {
          height: 28px;
        }

        .title {
          margin-left: 10px;
          font-size: 16px;
          /* font-weight: 700; */
        }

        &:hover {
          color: #fff;
          transition: color .3s;
          cursor: pointer;
        }
      }
    }

    .header-nav {
      display: flex;
      width: 100%;
      padding: 0 16px;

      .nav-item {
        margin-right: 32px;
        color: #eaebf0;
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

      .header-nav-btn {
        display: flex;
        justify-content: center;
        align-items: center;
        min-width: 32px;
        min-height: 32px;
        margin-left: 12px;
        padding: 0 7px;
      }
      .header-nav-icon-btn {
        width: 32px;
        font-size: 18px;
      }
      /deep/ .dropdown-active {
        .header-nav-icon-btn {
          background: rgba(255, 255, 255, .1);
          border-radius: 16px;
          color: #fff;
        }
        .login-username {
          color: #fff;
          transition: color .2s;

          .icon-down-shape {
            transform: rotate(-180deg);
            transition: transform .2s;
          }
        }
      }

      .king-select {
        width: 240px;
        /* margin-right: 40px; */
        background: #252f43;
        border-color: #252f43;

        /deep/ .bk-select-name {
          color: #d3d9e4;
        }
      }

      .login-username {
        display: flex;
        align-items: center;
        line-height: 32px;
        cursor: pointer;
        transition: color .2s;
        user-select: none;

        .icon-down-shape {
          margin-left: 6px;
          transition: transform .2s;
        }
      }
    }
  }
</style>

<style lang="postcss">
  .tippy-tooltip.profile-popover-theme[data-size=small] {
    padding: 0;

    .profile-popover-content {
      color: #63656e;
      line-height: 32px;

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
