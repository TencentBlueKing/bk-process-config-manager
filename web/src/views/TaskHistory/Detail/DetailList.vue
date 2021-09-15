<template>
  <div class="detail-list">
    <div class="row">
      <div class="couple">
        <label class="couple-label">{{ $t('任务ID') + $t('：') }}</label>
        <span>{{ taskDetail.id || '--' }}</span>
      </div>
      <div class="couple">
        <label class="couple-label">{{ $t('环境类型') + $t('：') }}</label>
        <span>{{ taskDetail.setEevName || '--' }}</span>
      </div>
      <div class="couple">
        <label class="couple-label">{{ $t('任务类型') + $t('：') }}</label>
        <span>{{ jobObject[taskDetail.job_object] + jobAction[taskDetail.job_action] || '--' }}</span>
      </div>
      <div class="couple">
        <label class="couple-label">{{ $t('操作范围') + $t('：') }}</label>
        <div
          class="button-text"
          v-test="'expressionFilter'"
          v-bk-overflow-tips
          @click="goProcessStatusPage(taskDetail.expression_scope)">
          {{ taskDetail.expression || '--' }}
        </div>
      </div>
    </div>
    <div class="row">
      <div class="couple">
        <label class="couple-label">{{ $t('执行账户') + $t('：') }}</label>
        <span>{{ taskDetail.created_by || '--' }}</span>
      </div>
      <div class="couple">
        <label class="couple-label">{{ $t('执行耗时') + $t('：') }}</label>
        <span>{{ taskDetail.timeout || '--' }}</span>
      </div>
      <div class="couple">
        <label class="couple-label">{{ $t('开始时间') + $t('：') }}</label>
        <span>{{ taskDetail.start_time || '--' }}</span>
      </div>
      <div class="couple">
        <label class="couple-label">{{ $t('结束时间') + $t('：') }}</label>
        <span>{{ taskDetail.end_time || '--' }}</span>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TaskHistoryDetail',
  props: {
    jobAction: {
      type: Object,
      default() {
        return {};
      },
    },
    jobObject: {
      type: Object,
      default() {
        return {};
      },
    },
    taskDetail: {
      type: Object,
      default: () => ({}),
    },
  },
  methods: {
    goProcessStatusPage(expression) {
      this.$router.push({
        path: '/process-manage/status',
        query: {
          expressionScope: JSON.stringify(expression),
        },
      });
    },
  },
};
</script>

<style lang="postcss" scoped>
  .detail-list {
    width: 100%;

    .row {
      width: 100%;
      height: 30px;
      display: flex;
      align-items: center;
      font-size: 12px;

      .couple {
        width: 260px;
        padding-right: 10px;
        display: flex;
        align-items: center;

        .couple-label {
          flex-shrink: 0;
          color: #b2b5bd;
          position: relative;
        }

        span {
          flex-shrink: 1;
          color: #63656e;
          margin-left: 2px;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
          cursor: default;
        }

        .button-text {
          flex-shrink: 1;
          margin-left: 2px;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }
      }

    }
  }

</style>
