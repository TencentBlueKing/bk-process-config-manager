<template>
  <div class="empty-process-container">
    <div class="flex-top"></div>
    <div class="empty-process-content" v-if="isEmptyPage">
      <p class="empty-title">{{ $t('接入GSEKit进程管理', [appName]) }}</p>
      <p class="empty-sub-title">
        <i18n tag="p" path="欢迎使用GSEKit">
          <span>{{ appName }}</span>
          <bk-button text theme="primary" class="reset-icon-btn" @click="handleClick('document')">
            <span class="flex-content">
              {{ $t('帮助文档') }}<i class="gsekit-icon gsekit-icon-jump-fill"></i>
            </span>
          </bk-button>
        </i18n>
      </p>
      <section class="empty-box-list">
        <EmptyBox
          class="empty-box-item"
          desc-path="无拓扑提示"
          :completed="completed"
          :index="1"
          :link-btn="$t('配置平台')"
          :image-src="emptyTopoSrc"
          @click="handleClick('cmdb')">
        </EmptyBox>
        <EmptyBox
          class="empty-box-item"
          desc-path="完善进程信息提示"
          :index="2"
          :link-btn="$t('进程属性')"
          :image-src="emptyProcessSrc"
          @click="handleClick('attributes')">
        </EmptyBox>
      </section>
    </div>
    <EmptyBox
      v-else
      class="empty-topo-box"
      desc-path="无拓扑提示"
      :link-btn="$t('配置平台')"
      :image-src="emptyTopoSrc"
      @click="handleClick('cmdb')">
    </EmptyBox>
    <div class="flex-bottom"></div>
  </div>
</template>

<script>
import EmptyBox from './EmptyBox';
import emptyTopoSrc from '@/assets/images/empty-topo.png';
import emptyProcessSrc from '@/assets/images/empty-process.png';
import { mapState } from 'vuex';

export default {
  name: 'EmptyProcess',
  components: {
    EmptyBox,
  },
  props: {
    emptyType: {
      type: String,
      default: 'page',
    },
    completed: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      emptyTopoSrc,
      emptyProcessSrc,
    };
  },
  computed: {
    ...mapState(['appName']),
    isEmptyPage() {
      return this.emptyType === 'page';
    },
  },
  methods: {
    handleClick(type) {
      if (type === 'cmdb') {
        const { bizId } = this.$store.state;
        window.open(`${window.PROJECT_CONFIG.CMDB_URL}/#/business/${bizId}/index?node=biz-${bizId}`, '_blank');
      } else if (type === 'attributes') {
        this.$router.push({
          name: 'process-attr',
        });
      } else if (type === 'document') {
        window.open(window.PROJECT_CONFIG.BKAPP_DOCS_URL, '_blank');
      }
    },
  },
};
</script>

<style lang="postcss" scoped>
  @import '../../css/variable.css';

  .empty-process-container {
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

    .empty-process-content {
      display: flex;
      flex-direction: column;
      text-align: center;
    }

    .empty-title {
      margin: 0;
      line-height: 26px;
      font-size: 20px;
      color: $newBlackColor1;
    }

    .empty-sub-title {
      max-width: 670px;
      margin: 20px 0 0 0;
      line-height: 19px;
      font-size: 14px;
    }

    .empty-box-list {
      display: flex;
      margin-top: 30px;
    }

    .empty-box-item {
      >>> .empty-desc {
        text-align: left;
      }

      & + .empty-box-item {
        margin-left: 30px;
      }
    }
  }
</style>
