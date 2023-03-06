<template>
  <div id="app" class="app">
    <Header @showMain="showMain = true" />
    <AuthModal ref="authModal"></AuthModal>
    <main class="main-content" v-bkloading="{ isLoading: mainContentLoading, opacity: 1 }">
      <template v-if="showMain">
        <router-view v-if="authPage" />
        <AuthPage v-else />
      </template>
    </main>
  </div>
</template>

<script>
import { mapState } from 'vuex';
import Header from './components/Header';
import AuthModal from '@/components/Auth/AuthModal';
import AuthPage from '@/components/Auth/AuthPage';

export default {
  name: 'App',
  components: {
    Header,
    AuthModal,
    AuthPage,
  },
  data() {
    return {
      showMain: false,
    };
  },
  computed: {
    ...mapState(['mainContentLoading', 'authPage']),
  },
  created() {
    this.$store.commit('updateAppName', window.PROJECT_CONFIG.APP_NAME);
    const platform = window.navigator.platform.toLowerCase();
    if (platform.indexOf('win') === 0) {
      document.body.style['font-family'] = 'Microsoft Yahei, PingFang SC, Helvetica, Aria';
    } else {
      document.body.style['font-family'] = 'PingFang SC, Microsoft Yahei, Helvetica, Aria';
    }
  },
  mounted() {
    let resizeTimer = null;
    this.resizeListener = () => {
      resizeTimer && clearTimeout(resizeTimer);
      resizeTimer = setTimeout(() => {
        this.$store.commit('updatePageHeight', document.documentElement.clientHeight);
      }, 300);
    };
    window.addEventListener('resize', this.resizeListener, { passive: true });
    window.bus.$on('show-permission-modal', (data) => {
      this.$refs.authModal.show(data);
    });
    this.$store.commit('updateLang', window.language);
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.resizeListener);
  },
};
</script>

<style lang="postcss">
  @import './css/reset.css';
  @import './css/variable.css';
  @import './css/animation.css';

  .app {
    height: 100%;
    min-width: 1366px;
    min-height: 708px;
    color: $newBlackColor1;

    .main-content {
      display: flex;
      flex-flow: column;
      height: calc(100% - 52px);
      overflow: auto;
    }
  }

  .button-text {
    color: $newMainColor;
    cursor: pointer;

    &:hover {
      color: $newMainColor1;
    }

    &:active {
      color: $newMainColor4;
    }

    &.is-disabled {
      color: #c4c6cc;
      cursor: not-allowed;
    }
  }

  .button-icon.dark {
    display: flex;
    justify-content: center;
    align-items: center;
    width: 32px;
    height: 32px;
    cursor: pointer;
    border-radius: 2px;
    border: 1px solid $blackThemeBorderColor;
    background: $blackThemeBackgroundColor;
    transition: border-color .2s;

    .icon {
      font-size: 16px;
      color: $newBlackColor3;
      transition: color .2s;
    }

    &:hover {
      border-color: $blackThemeHoverBorderColor;
      transition: border-color .2s;

      .icon {
        color: $blackThemeHoverColor;
        transition: color .2s;
      }
    }
  }

  .bk-button.king-button.dark {
    color: $blackThemeColor;
    border-color: $blackThemeBorderColor;
    background: $blackThemeBackgroundColor;
    transition: color .2s, border-color .2s;

    &:hover {
      color: $blackThemeHoverColor;
      border-color: $blackThemeHoverBorderColor;
      transition: color .2s, border-color .2s;
    }

    &.is-disabled {
      color: #595959;
      border-color: #484848;
      background: $blackThemeBackgroundColor;
    }

    &.primary-ghost {
      color: $blackThemeActiveColor;
      border-color: $newMainColor;
      background-color: #192845;
      transition: background-color .2s;

      &:hover {
        background-color: #233861;
        transition: background-color .2s;
      }
    }
  }

  .tippy-tooltip {
    &.bk-select-dropdown-theme {
      .auth-extension {
        .bk-select-extension {
          position: relative;
          padding: 0;
        }

        .auth-extension-content {
          padding: 0 16px;
        }
      }
    }
  }

  /* 新建配置文件模板弹窗全局样式 */
  .bk-dialog-wrapper.create-template-dialog {
    .bk-dialog-header.header-on-left {
      margin-top: -30px;
      padding: 0 24px;
      line-height: 64px;
      height: 65px;
      border-bottom: 1px solid #dcdee5;
    }

    .bk-dialog-body {
      padding: 0;
      height: 502px;
    }

    .bk-dialog-footer {
      padding: 9px 24px;
    }
  }

  /* 黑色主题下拉 */
  .king-select.dark {
    background: $blackThemeBackgroundColor;
    border: 1px solid $blackThemeBorderColor;
    transition: border-color .2s;

    .bk-select-name {
      color: $blackThemeColor;
      transition: color .2s;
    }

    &:hover {
      border-color: $blackThemeHoverBorderColor;
      transition: border-color .2s;

      .bk-select-name {
        color: $blackThemeHoverColor;
        transition: color .2s;
      }
    }

    &.is-focus {
      border-color: $newMainColor;
      transition: border-color .2s;
    }

    &.is-disabled {
      border-color: $newBlackColor2;

      .bk-select-name {
        color: #dcdee5;
      }
    }
  }

  /* 黑色主题下拉 tippy */
  .bk-select-dropdown-content.dark {
    color: $newBlackColor3 !important;
    background: #383838 !important;
    border-color: #474747 !important;

    .bk-option {
      &.is-selected {
        color: #e1ecff !important;
        background: #346 !important;
      }

      &:hover {
        color: #e1ecff !important;
        background: #415782 !important;
      }
    }
  }

  /* 单行文字溢出 */
  .text-overflow-row {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  /* hack bk-magic-vue global */

  /* 提示框 */
  .bk-info-box .bk-dialog-header-inner {
    white-space: normal !important;
  }

  /* 导航 */
  .hack-king-navigation.bk-navigation {
    width: 100% !important;
    height: 100% !important;

    .container-header {
      display: none !important;
    }

    .bk-navigation-wrapper {
      height: 100%;

      .navigation-container {
        max-width: calc(100% - 60px) !important;

        .container-content {
          height: 100% !important;
          max-height: 100% !important;
          padding: 0;

          .navigation-content {
            height: 100%;
          }
        }
      }
    }

    .nav-slider-list {
      height: calc(100% - 56px) !important;
    }
  }

  /* 表格 */
  .bk-table th .bk-table-column-filter-trigger.is-filtered {
    color: $newMainColor !important;
  }

  .bk-table .bk-table-body-wrapper .table-ceil-overflow {
    width: 100%;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  /* 表格...操作样式 */
  .bk-table .table-operation-container {
    display: flex;
    align-items: center;

    .bk-button-text + .bk-button-text {
      margin-left: 12px;
    }

    .dot-menu-trigger {
      display: flex;
      justify-content: center;
      align-items: center;
      width: 24px;
      height: 24px;
      margin-left: 12px;
      margin-top: 1px;
      border-radius: 50%;
      cursor: pointer;
      color: $newBlackColor3;
      transition: color .3s, background-color .3s;

      &:hover {
        color: $newMainColor;
        background-color: #dcdee5;
        transition: color .3s, background-color .3s;
      }

      .icon-more {
        font-weight: bold;
        font-size: 20px;
      }
    }
  }

  .tippy-tooltip.dot-menu-theme[data-size=small] {
    padding: 0;

    .dot-menu-list {
      margin: 0;
      padding: 5px 0;
      min-width: 50px;
      list-style: none;

      .dot-menu-item {
        padding: 0 16px;
        font-size: 12px;
        color: $newBlackColor2;
        line-height: 32px;
        cursor: pointer;
        &.cover {
          padding: 0;
        }

        &:hover {
          background-color: #e5efff;
          color: $newMainColor;
        }

        &.auth-box-disabled {
          color: #dcdee5;
        }
        &.disabled {
          color: #dcdee5;
          cursor: not-allowed;
        }
      }

      &>.auth-box {
        display: block;
      }
    }

    .tippy-content {
      background-color: #fff !important;
    }
  }

  .tippy-popper {
    .filter-header-theme {
      padding: 0 !important;
      border-radius: 2px !important;
      border: 1px solid #dcdee5;
      transform: translateY(2px) !important;
      background: #fff !important;
    }

    .bk-cascade-dropdown-theme {
      min-width: 109px !important;
      height: 234px;

      .tippy-content,
      .bk-tooltip-content {
        height: 100%;
      }

      .bk-cascade-dropdown-content {
        height: 100%;
        display: flex;
      }
    }

    .bk-table-setting-popover-content-theme {
      padding: 14px 0 0 !important;
    }

    .agent-operate-theme {
      padding: 0 !important;
    }

    .tippy-tooltip {
      border-radius: 2px !important;
    }

    .bk-select-dropdown-theme {
      .is-auth-disabled {
        color: #dcdee5;
        background-color: #fff;
        cursor: default;

        &:hover {
          color: #dcdee5;
        }
      }

      .auth-box {
        position: absolute;
        top: 0;
        left: 0;
        bottom: 0;
        right: 0;
        display: block;
      }

      .extension-container {
        display: flex;
        align-items: center;
        cursor: pointer;
      }
    }

    &.failed-tips {
      .tippy-tooltip {
        padding: 14px 16px;

        .failed-message,
        .resolve-message {
          line-height: 22px;
          color: #656770;

          .message-text {
            color: #979ba5;
          }
        }

        .resolve-message {
          margin-top: 6px;

          .solute-item {
            display: flex;
            /* align-items: center; */
          }
          .solute-item-order {
            display: inline-block;
            width: 16px;
          }
          .solute-item-content {
            flex: 1;
          }
        }
      }
    }
  }

  .reset-icon-btn {
    .flex-content {
      display: flex;
      align-items: center;
      justify-content: center;

      .ml6 {
        margin-left: 6px;
      }
    }
  }

  .v-cursor {
    background-repeat: no-repeat;
    background-position: center center;
    background-size: 12px 16px;
    background-image: url('./assets/images/lock.svg');
  }

  /* 侧栏标题样式 */
  .bk-sideslider-title {
    .config-contrast-header {
      .divide-line {
        font-weight: normal;
        margin: 0 2px;
      }

      .template-name {
        font-size: 14px;
      }
    }
  }

  /* 进程操作二次确认弹框 */
  .king-dialog {
    /deep/ .bk-dialog-header {
      padding: 18px 24px 16px !important;
    }

    .bk-dialog-body {
      text-align: center;
      padding-bottom: 0 !important;

      .body-prompt {
        margin-bottom: 16px;

        span {
          color: #313238;
          margin: 0 2px;
        }
      }
    }

    .bk-dialog-footer {
      border-top: 0 !important;
      background: #fff !important;
      text-align: center !important;
      padding: 10px 24px 42px !important;
    }
  }

  .text-has-tips {
    text-decoration: underline dashed #c4c6cc;
    text-underline-offset: 5px;
  }

  /* todo bug of monaco-editor */
  .monaco-aria-container {
    margin: -1px;
  }
  .exception-box {
    .bk-exception-img {
        overflow: hidden;
        .exception-image {
            width: 324px;
            height: 162px;
        }
    }
    .bk-exception-text  {
        margin-top: 14px;
    }
  }
</style>
