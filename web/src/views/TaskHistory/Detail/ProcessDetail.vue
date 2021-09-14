<template>
  <div class="detail-list">
    <div class="row">
      <div class="couple">
        <label class="couple-label">{{ $t('任务ID') + $t('：') }}</label>
        <span>{{ taskDetail.id || '--' }}</span>
      </div>
      <div class="couple">
        <label class="couple-label">{{ $t('操作范围') + $t('：') }}</label>
        <span v-bk-overflow-tips>{{ taskDetail.expression || '--' }}</span>
      </div>
      <div class="couple">
        <label class="couple-label">{{ $t('开始时间') + $t('：') }}</label>
        <span>{{ taskDetail.start_time || '--' }}</span>
      </div>
      <div class="couple">
        <label class="couple-label">{{ $t('执行耗时') + $t('：') }}</label>
        <span>{{ taskDetail.timeout || '--' }}</span>
      </div>
    </div>
    <div class="row">
      <div class="couple">
        <label class="couple-label">{{ $t('任务类型') + $t('：') }}</label>
        <span>{{ taskDetail.type || '--' }}</span>
      </div>
      <div class="couple">
        <label class="couple-label">{{ $t('执行账户') + $t('：') }}</label>
        <span>{{ taskDetail.created_by || '--' }}</span>
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
    taskDetail: {
      type: Object,
      default: () => ({}),
    },
  },
};
</script>

<style lang="postcss" scoped>
  .detail-list {
    width: 100%;
    padding-left: 23px;

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
        }
      }

    }
  }

</style>
