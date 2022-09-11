<template>
  <div class="empty-biz-container">
    <div class="flex-top"></div>
    <div class="empty-biz-content">
      <h2 class="empty-title">{{ $t('暂无业务权限提示') }}</h2>
      <div class="operate-list">
        <div class="operate-item">
          <h3 class="operate-title mt30">{{ $t('我有正在使用的业务') }}</h3>
          <div class="operate-center">
            <img src="../../assets/images/empty-has-biz.png" alt="">
          </div>
          <div class="operate-bottom">
            <bk-button
              class="operate-btn"
              theme="primary"
              :loading="btnLoading"
              @click="handleClick('apply')">
              {{ $t('申请业务权限') }}
            </bk-button>
          </div>
        </div>
        <div class="operate-item">
          <h3 class="operate-title mt30">{{ $t('我还没有创建过业务') }}</h3>
          <div class="operate-center">
            <img class="not-biz-image" src="../../assets/images/empty-not-biz.png" alt="">
          </div>
          <div class="operate-bottom">
            <bk-button class="operate-btn reset-icon-btn" theme="primary" @click="handleClick('newBiz')">
              <span class="flex-content">
                {{ $t('创建新业务') }}<span class="ml6 gsekit-icon gsekit-icon-jump-fill"></span>
              </span>
            </bk-button>
          </div>
        </div>
      </div>
      <p class="empty-footer">
        <i18n path="快速了解GSEkit">
          <span>{{ appName }}</span>
          <bk-button text theme="primary" class="reset-icon-btn" @click="handleClick('official')">
            <span class="flex-content">
              {{ $t('白皮书文档') }}<i class="ml6 gsekit-icon gsekit-icon-jump-fill"></i>
            </span>
          </bk-button>
        </i18n>
      </p>
    </div>
    <div class="flex-bottom"></div>
  </div>
</template>

<script>
import { mapActions, mapState } from 'vuex';

export default {
  name: 'AuthPage',
  data() {
    return {
      btnLoading: false,
    };
  },
  computed: {
    ...mapState(['bizId', 'appName']),
  },
  methods: {
    ...mapActions('iam', ['ajaxGetAuthApplyInfo']),
    async handleClick(type) {
      if (type === 'apply') {
        this.btnLoading = true;
        try {
          const params = {
            action_ids: ['view_business'],
            resources: this.bizId ? [{ type: 'biz', id: this.bizId }] : [],
          };
          const res = await this.ajaxGetAuthApplyInfo(params);
          const { apply_url: applyUrl = '' } = res.data;
          if (self === top) {
            window.open(applyUrl, '__blank');
          } else {
            try {
              window.top.BLUEKING.api.open_app_by_other('bk_iam', applyUrl);
            } catch (_) {
              window.open(applyUrl, '__blank');
            }
          }
        } catch (e) {
          console.warn(e);
        } finally {
          this.btnLoading = false;
        }
      } else if (type === 'newBiz') {
        window.open(`${window.PROJECT_CONFIG.CMDB_URL}/#/resource/business`, '_blank');
      } else {
        window.open(window.PROJECT_CONFIG.BKAPP_DOCS_URL, '_blank');
      }
    },
  },
};
</script>

<style lang="postcss" scoped>
  @import '../../css/variable.css';

  .empty-biz-container {
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    background: #f5f6fa;

    .flex-top {
      flex: 1;
      min-height: 88px;
    }

    .flex-bottom {
      flex: 2;
    }

    .empty-biz-content {
      display: flex;
      flex-direction: column;
      height: 500px;
      text-align: center;
    }

    .empty-title {
      line-height: 26px;
      font-size: 20px;
      font-weight: normal;
      color: $newBlackColor1;
    }

    .empty-footer {
      margin-top: 30px;
      line-height: 16px;
      font-size: 12px;
      color: $newBlackColor3;

      .bk-button-text {
        font-size: 12px;
      }
    }

    .operate-list {
      margin-top: 32px;
      display: flex;
      width: 670px;
      height: 360px;
    }

    .operate-item {
      flex: 1;
      border-radius: 4px;
      font-size: 16px;
      color: $newBlackColor1;
      background: #fff;
      box-shadow: 0px 1px 2px 0px rgba(0,0,0,.1);

      .operate-title {
        font-weight: normal;
        line-height: 19px;
      }

      .operate-center {
        margin-top: 18px;
        min-height: 194px;
        font-size: 0;

        img {
          width: 260px;
        }

        .not-biz-image {
          width: 250px;
        }
      }

      .operate-bottom {
        margin-top: 28px;
      }

      .operate-btn {
        min-width: 180px;
      }

      & + .operate-item {
        margin-left: 30px;
      }
    }
  }
</style>
