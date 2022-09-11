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
      <bk-popover v-if="username"
                  trigger="click"
                  theme="profile-popover light"
                  :on-show="() => isPopoverActive = true"
                  :on-hide="() => isPopoverActive = false">
        <div class="login-username" :class="isPopoverActive && 'active'">
          {{ username }}<span class="bk-icon icon-down-shape"></span>
        </div>
        <div slot="content" class="profile-popover-content">
          <ul class="bk-options">
            <li class="bk-option" @click="handleLogout">
              <div class="bk-option-content">
                <div class="bk-option-content-default">
                  <div class="bk-option-name">
                    <span class="gsekit-icon gsekit-icon-logout-fill"></span>
                    <span class="text">{{ $t('注销') }}</span>
                  </div>
                </div>
              </div>
            </li>
          </ul>
        </div>
      </bk-popover>
    </div>
  </header>
</template>

<script>
import { mapState, mapMutations, mapActions } from 'vuex';
import AuthSelect from '@/components/Auth/AuthSelect';

export default {
  components: {
    AuthSelect,
  },
  data() {
    return {
      isPopoverActive: false,
      bizId: '',
      bizList: [],
    };
  },
  computed: {
    ...mapState(['username', 'appName']),
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
      // location.assign('/console/accounts/logout/');
      location.href = `${window.PROJECT_CONFIG.LOGIN_URL}?&c_url=${window.location}`;
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

      .king-select {
        width: 240px;
        margin-right: 40px;
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
        margin-right: 40px;
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
