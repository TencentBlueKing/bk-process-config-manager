<template>
  <div class="detail-list">
    <ul class="row">
      <li class="couple">
        <label>{{ $t('模板ID') }}</label>
        <span>{{ configFileDetail.config_template_id || '--' }}</span>
      </li>
      <li class="couple">
        <label>{{ $t('模板名称') }}</label>
        <span v-bk-overflow-tips>{{ configFileDetail.template_name || '--' }}</span>
      </li>
      <li class="couple">
        <label>{{ $t('文件名称') }}</label>
        <span v-bk-overflow-tips>{{ configFileDetail.file_name || '--' }}</span>
      </li>
      <li class="couple">
        <label>{{ $t('文件所处路径') }}</label>
        <span v-bk-overflow-tips>{{ configFileDetail.abs_path || '--' }}</span>
      </li>
      <li class="couple">
        <label>{{ $t('文件拥有者') }}</label>
        <span>{{ configFileDetail.owner || '--' }}</span>
      </li>
      <li class="couple">
        <label>{{ $t('文件用户组') }}</label>
        <span>{{ configFileDetail.group || '--' }}</span>
      </li>
      <li class="couple">
        <label>{{ $t('文件权限') }}</label>
        <span>{{ configFileDetail.filemode || '--' }}</span>
      </li>
      <li class="couple">
        <label>{{ $t('输出格式') }}</label>
        <span>{{ fileFormatMap[configFileDetail.line_separator] || '--' }}</span>
      </li>
    </ul>
  </div>
</template>

<script>
export default {
  name: 'ConfigFileDetail',
  props: {
    configFileDetail: {
      type: Object,
      default: () => ({}),
    },
  },
  data() {
    return {
      fileFormatMap: {
        CRLF: 'CRLF - Windows（\\r\\n）',
        LF: 'LF - Unix and macOS（\\n）',
      },
    };
  },
};
</script>

<style lang="postcss" scoped>
  .detail-list {
    width: 100%;
    height: 134px;
    margin-bottom: 20px;
    background: #f5f7fa;
    padding: 20px 30px;

    .row {
      width: 100%;
      height: 30px;
      display: flex;
      align-items: center;
      flex-wrap: wrap;
      font-size: 12px;

      .couple {
        width: 50%;
        display: flex;
        align-items: center;
        margin-bottom: 10px;
        font-size: 12px;

        label {
          color: #b2b5bd;
          position: relative;
          flex-shrink: 0;

          &::after {
            content: ':';
            position: absolute;
            right: -5px;
            top: 0;
          }
        }

        span {
          color: #63656e;
          margin-left: 15px;
          display: inline-block;
          flex: 1;
          overflow: hidden;
          white-space: nowrap;
          text-overflow: ellipsis;
        }
      }

    }
  }

</style>
