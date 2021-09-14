<template>
  <div class="empty-service-box">
    <div class="flex-top"></div>
    <div class="empty-service-content" :style="{ width: width ? `${width}px` : 'auto' }">
      <div class="empty-top">
        <img src="../../assets/images/empty-box.png" alt="">
      </div>
      <h3 class="empty-title">{{ displayTitle }}</h3>
      <p class="empty-desc">
        <section>{{ descPath }}</section>
        <i18n :path="displayDescSlot">
          <bk-button text theme="primary" class="reset-icon-btn" @click="handleClick">
            <span class="flex-content">
              {{ $t('配置平台') }}<i class="gsekit-icon gsekit-icon-jump-fill"></i>
            </span>
          </bk-button>
        </i18n>
      </p>
    </div>
    <div class="flex-bottom"></div>
  </div>
</template>

<script>
export default {
  name: 'EmptyServiceBox',
  props: {
    width: {
      type: [String, Number],
      default: '',
    },
    type: {
      type: String,
      default: 'instance',
    },
    info: {
      type: Object,
      default: () => ({ bk_obj_id: '', bk_inst_id: '' }),
    },
    title: {
      type: String,
      default: '',
    },
    desc: {
      type: String,
      default: '',
    },
    descSlot: {
      type: String,
      default: '',
    },
  },
  computed: {
    displayTitle() {
      return this.title || (this.type === 'instance' ? this.$t('当前模块暂无服务实例') : this.$t('当前业务暂无服务模版'));
    },
    descPath() {
      return this.desc || (this.type === 'instance' ? this.$t('模块暂无服务实例path') : this.$t('业务暂无服务模版path'));
    },
    displayDescSlot() {
      return this.descSlot || (this.type === 'instance' ? '模块暂无服务实例slot' : '业务暂无服务模版slot');
    },
  },
  methods: {
    handleClick() {
      if (this.info.bk_obj_id || this.info.bk_inst_id) {
        let queryStr = `${window.PROJECT_CONFIG.CMDB_URL}/#/business/${this.$store.state.bizId}/`;
        if (this.type === 'instance') {
          queryStr += `index?node=${this.info.bk_obj_id}-${this.info.bk_inst_id}&tab=serviceInstance`; // &view=instance
        } else {
          queryStr += 'service/template';
        }
        window.open(queryStr, '_blank');
      } else {
        this.$emit('click-link');
      }
    },
  },
};
</script>

<style lang="postcss" scoped>
  @import '../../css/variable.css';

  .empty-service-box {
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    height: 100%;

    .flex-top {
      flex: 2;
    }

    .flex-bottom {
      flex: 3;
    }

    .empty-service-content {
      display: flex;
      flex-direction: column;
      height: 230px;
      text-align: center;
    }

    .empty-title {
      margin: 20px 0 0 0;
      line-height: 26px;
      font-size: 20px;
      font-weight: normal;
      color: $newBlackColor2;
    }

    .empty-desc {
      margin: 16px 0 0 0;
      line-height: 24px;
      font-size: 14px;
      color: $newBlackColor3;
    }
  }
</style>
