<template>
  <div class="bk-custom-table">
    <bk-table
      ref="statusTable"
      :data="tableData"
      :size="setting.size"
      :max-height="$store.state.pageHeight - (isSelectedAllPages ? 271 : 235)"
      row-key="bk_process_id"
      :expand-row-keys="expandRow"
      :pagination="pagination"
      @sort-change="handleSortChange"
      @row-click="toggleExpansion"
      @page-change="handlePageChange"
      @page-limit-change="handlePageLimitChange">
      <bk-table-column type="expand" width="30" :before-expand-change="onBeforeExpandChange">
        <template slot-scope="{ row }">
          <div class="process-status" v-if="row.proc_inst_infos.length">
            <div class="col-status-item" v-for="(instInfo, index) in row.proc_inst_infos" :key="instInfo.id">
              <div class="item-instance-text">{{ $t('实例') + (index + 1) }}</div>
              <div class="item-template-name">
                <bk-popover :content="$t('主机下唯一标识')">
                  <span>{{ 'LocalInstID：' }}</span>
                </bk-popover>
                <div v-bk-overflow-tips>{{ instInfo.local_inst_id }}</div>
              </div>
              <div class="item-file-name">
                <bk-popover :content="$t('模块下唯一标识')">
                  <span>{{ 'InstID：' }}</span>
                </bk-popover>
                <div v-bk-overflow-tips>{{ instInfo.inst_id }}</div>
              </div>
              <div class="item-status">
                {{ $t('状态') + '：' }}
                <StatusView v-if="instInfo.process_status === 0" type="origin" :is-solid="true" :text="$t('未运行')" />
                <StatusView
                  v-else-if="instInfo.process_status === 1"
                  type="success"
                  :is-solid="true"
                  :text="$t('运行中')" />
                <StatusView
                  v-else-if="instInfo.process_status === 2"
                  type="failed"
                  :is-solid="true"
                  :text="$t('未运行')" />
              </div>
            </div>
          </div>
          <div class="process-status" v-else>
            <span class="no-other-instance">{{ $t('暂无其他实例') }}</span>
          </div>
        </template>
      </bk-table-column>
      <bk-table-column
        key="selection"
        width="65"
        :resizable="false"
        :render-header="renderSelectionHeader">
        <div slot-scope="props" @click.stop>
          <bk-checkbox
            v-test.common="'rowSelect'"
            :value="props.row.isSelect"
            :disabled="props.row.disable"
            @change="handleRowCheck(props.row)">
          </bk-checkbox>
        </div>
      </bk-table-column>
      <template v-for="item in setting.selectedFields">
        <bk-table-column
          v-if="!['process_status', 'is_auto', 'bk_process_id'].includes(item.id)"
          :key="item.id"
          :label="item.label"
          :prop="item.id"
          :min-width="columnMinWidth[item.id]"
          :sortable="item.sortable ? 'custom' : ''">
          <div slot-scope="{ row }" v-bk-overflow-tips>
            <!-- 配置文件数 -->
            <!-- <div v-if="item.id === 'config_templates'" @click.stop>
              <template v-if="row.templateCount">
                <bk-popover placement="right">
                  <span class="file-num" @click="onCheckProcessConfig(row, 'configFile')">{{ row.templateCount }}</span>
                  <div slot="content">
                    <div v-for="file in row.config_templates" :key="file.config_template_id">
                      <span>{{ file.template_name }}</span>
                      {{ $t('（') }}<span>{{ file.file_name }}</span>{{ $t('）') }}
                    </div>
                  </div>
                </bk-popover>
              </template>
              <span class="file-num" v-else @click="onCheckProcessConfig(row, 'configFile')">{{ '0' }}</span>
            </div>
            其他
            <template v-else> -->
            <span :title="row[item.id]">{{ row[item.id] || '--' }}</span>
            <!-- </template> -->
          </div>
        </bk-table-column>
        <!-- process_id -->
        <bk-table-column
          v-if="item.id === 'bk_process_id'"
          :label="item.label"
          :prop="item.id"
          :key="item.id"
          :min-width="columnMinWidth[item.id]"
          sortable="custom"
          :render-header="renderProcessHeader">
          <template slot-scope="{ row }">
            <span :title="row[item.id]">{{ row[item.id] || '--' }}</span>
          </template>
        </bk-table-column>
        <!-- 进程状态 -->
        <bk-table-column
          v-if="item.id === 'process_status'"
          :label="item.label"
          :prop="item.id"
          :key="item.id"
          :min-width="columnMinWidth[item.id]"
          :render-header="renderFilterHeader">
          <template slot-scope="{ row }">
            <StatusView v-if="row.process_status === 0" type="origin" :is-solid="true" :text="$t('未运行')" />
            <StatusView v-else-if="row.process_status === 1" type="success" :is-solid="true" :text="$t('运行中')" />
            <StatusView v-else-if="row.process_status === 2" type="failed" :is-solid="true" :text="$t('未运行')" />
          </template>
        </bk-table-column>
        <!-- 托管状态 -->
        <bk-table-column
          v-if="item.id === 'is_auto'"
          :label="item.label"
          :prop="item.id"
          :key="item.id"
          :min-width="columnMinWidth[item.id]"
          :render-header="renderFilterHeader">
          <template slot-scope="{ row }">
            <span
              :class="['hosting-status', row.process_status === 1 ? (row.is_auto ? 'hosting' : 'fail') : 'unmanaged']"
              v-bk-tooltips="{
                content: $t('进程处于未托管状态如遇异常退出不会被自动拉起'),
                disabled: row.process_status !== 1 || !!row.is_auto
              }">
              {{ row.is_auto ? $t('托管中') : $t('未托管') }}
            </span>
          </template>
        </bk-table-column>
      </template>
      <bk-table-column :label="$t('操作')" width="170" class="operat-headr">
        <div class="table-operation-container" slot-scope="{ row }" @click.stop>
          <AuthTag action="manage_process" :authorized="authMap.manage_process">
            <template slot-scope="{ disabled }">
              <bk-popover :disabled="row.process_status !== 1"
                          :content="$t('进程运行中，无需启动')">
                <bk-button
                  style="margin-right: 12px;"
                  v-test="'start'"
                  :disabled="disabled || row.process_status === 1"
                  theme="primary"
                  text
                  @click="operateProcess('start', row.bk_process_id)">
                  {{ $t('启动') }}
                </bk-button>
              </bk-popover>
              <bk-popover :disabled="row.process_status !== 2"
                          :content="$t('进程未运行')">
                <bk-button
                  style="margin-right: 12px;"
                  v-test="'stop'"
                  :disabled="disabled || row.process_status === 2"
                  theme="primary"
                  text
                  @click="operateProcess('stop', row.bk_process_id)">
                  {{ $t('停止') }}
                </bk-button>
              </bk-popover>
            </template>
          </AuthTag>
          <AuthTag action="operate_config" :authorized="authMap.operate_config">
            <template slot-scope="{ disabled }">
              <bk-popover :disabled="Boolean(row.templateCount)"
                          :content="$t('没有绑定配置文件，无法进行配置下发')">
                <bk-button
                  v-test="'release'"
                  :disabled="disabled || !Boolean(row.templateCount)"
                  theme="primary"
                  text
                  @click="operateConfigDistribute(row)">
                  {{ $t('配置下发') }}
                </bk-button>
              </bk-popover>
            </template>
          </AuthTag>
          <bk-popover placement="bottom-start" theme="dot-menu light" trigger="click" :arrow="false" :distance="0">
            <div class="dot-menu-trigger">
              <span class="bk-icon icon-more" v-test.common="'more'"></span>
            </div>
            <ul class="dot-menu-list" slot="content">
              <AuthTag
                tag="li"
                class="dot-menu-item"
                v-test.common="'moreItem'"
                v-for="item in jobAction.slice(2)"
                :test-key="item.type"
                :key="item.type"
                action="manage_process"
                :authorized="authMap.manage_process"
                @click="operateProcess(item.type, row.bk_process_id)">
                {{ item.actionName }}
              </AuthTag>
              <li class="dot-menu-item" @click="onCheckProcessConfig(row)">{{ $t('查看进程配置') }}</li>
            </ul>
          </bk-popover>
        </div>
      </bk-table-column>
      <bk-table-column type="setting">
        <bk-table-setting-content
          :size="setting.size"
          :fields="setting.fields"
          :selected="setting.selectedFields"
          @setting-change="handleSettingChange">
        </bk-table-setting-content>
      </bk-table-column>
      <TableException
        slot="empty"
        :delay="loading"
        :type="tableEmptyType"
        @empty-clear="emptySearchClear" />
    </bk-table>
  </div>
</template>

<script>
import { mapState } from 'vuex';
import ColumnCheck from '@/components/ColumnCheck';
import FilterHeader from '@/components/FilterHeader';
import ProcessHeader from '@/components/ProcessHeader';
export default {
  props: {
    pagination: {
      type: Object,
      default: () => ({}),
    },
    tableData: {
      type: Array,
      default: () => [],
    },
    jobAction: {
      type: Array,
      default() {
        return [];
      },
    },
    filterData: {
      type: Array,
      default() {
        return [];
      },
    },
    searchSelectData: {
      type: Array,
      default() {
        return [];
      },
    },
    searchSelectValue: {
      type: Array,
      default() {
        return [];
      },
    },
    ordering: {
      type: String,
      default: '',
    },
    tableEmptyType: {
      type: String,
      default: 'empty',
    },
    loading: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    const fields = [
      {
        id: 'bk_set_name',
        label: this.$t('集群'),
        sortable: true,
      }, {
        id: 'bk_module_name',
        label: this.$t('模块'),
        sortable: true,
      }, {
        id: 'bk_service_name',
        label: this.$t('服务实例'),
        sortable: true,
      }, {
        id: 'bk_process_name',
        label: this.$t('进程别名'),
        disabled: true,
        sortable: true,
      },
      {
        id: 'bk_process_id',
        label: 'process_id',
        sortable: true,
      }, {
        id: 'bk_host_innerip',
        label: this.$t('内网IP'),
        sortable: true,
      }, {
        id: 'process_status',
        label: this.$t('进程状态'),
        disabled: true,
        sortable: true,
      }, {
        id: 'is_auto',
        label: this.$t('托管状态'),
        sortable: true,
      }, {
        id: 'bk_cloud_name',
        label: this.$t('云区域'),
        sortable: true,
        // }, {
        //     id: 'config_templates',
        //     label: this.$t('配置文件数'),
        //     sortable: true
      },
    ];
    return {
      isDataLoading: false,
      fields,
      setting: {
        fields,
        selectedFields: fields.slice(0, 7),
        size: 'small',
      },
      // 是否全选
      isSelectedAllPages: false,
      checkLoading: false,
      expandRow: [], // 展开行
      columnMinWidth: {},
    };
  },
  computed: {
    ...mapState(['authMap']),
    indeterminate() {
      if (this.isSelectedAllPages) {
        this.tableData.forEach((item) => {
          item.isSelect = true;
          item.disable = true;
        });
        return false;
      }
      // 当前页选中的数量
      let isSelectedNum = 0;
      this.tableData.forEach((item) => {
        if (item.isSelect) {
          isSelectedNum += 1;
        }
      });
      if (isSelectedNum) {
        return !(isSelectedNum === this.tableData.length);
      }
      return false;
    },
    isAllChecked() {
      if (this.isSelectedAllPages) {
        return true;
      }
      // 当前页选中的数量
      let isSelectedNum = 0;
      this.tableData.forEach((item) => {
        if (item.isSelect) {
          isSelectedNum += 1;
        }
      });
      if (isSelectedNum) {
        return isSelectedNum === this.tableData.length;
      }
      return false;
    },
    headerData() { // 表头筛选列表数据源
      return this.filterData.reduce((obj, item) => {
        if (item.children && item.children.length) {
          obj[item.id] = item.children;
        }
        return obj;
      }, {});
    },
  },
  mounted() {
    this.getFields();
  },
  methods: {
    // 获取当前视图表格头显示字段
    getFields() {
      const settingCache = window.localStorage.getItem('settingCache');
      if (settingCache) {
        const { fields, size } = JSON.parse(settingCache);
        const defaultColumn = fields;
        this.setting.size = size;
        this.setting.selectedFields = this.fields.slice(0).filter(m => defaultColumn.includes(m.id));
        this.computedColumnWidth()
      }
    },
    handleSortChange({ prop, order }) {
      this.$emit('handleSortChange', { prop, order });
    },
    // 自定筛选表头
    renderFilterHeader(h, data) {
      const filterList = this.headerData[data.column.property] || [];
      this.setChecked(filterList);
      const title = data.column.label || '';
      const property = data.column.property || '';
      return <FilterHeader
        name={ title } property={ property } filterList={ filterList }
        onConfirm={ (prop, list) => this.handleFilterHeaderConfirm(prop, list) }
        onReset={ prop => this.handleFilterHeaderReset(prop) }>
      </FilterHeader>;
    },
    // 自定义进程表头
    renderProcessHeader(h, data) {
      const title = data.column.label || '';
      const tips = this.$t('配置平台统一为每一个进程实例单独分配了全局唯一的ID，此ID非旧版“实例ID”且不可更改');
      return <ProcessHeader
        name={ title } tips={ tips }>
      </ProcessHeader>;
    },
    setChecked(data) {
      data.forEach((item) => {
        if (!item.checked) {
          item.checked = false;
        }
        if (item.child && item.child.length) {
          this.setChecked(item.child);
        }
      });
    },
    handleFilterHeaderReset(prop) {
      this.$emit('handleFilterHeaderReset', prop);
    },
    // 表头筛选变更
    handleFilterHeaderConfirm(prop, list) {
      this.$emit('handleFilterHeaderConfirm', prop, list);
    },
    /**
     * 自定义selection表头
     */
    renderSelectionHeader() {
      return <ColumnCheck
        ref="customSelectionHeader"
        indeterminate={this.indeterminate}
        isAllChecked={this.isAllChecked}
        loading={this.checkLoading}
        disabled={Boolean(this.tableData.length)}
        onChange={value => this.handleCheckAll(value)}>
      </ColumnCheck>;
    },
    /**
     * 表头勾选事件
     * @param {Boolean} value 全选 or 取消全选
     */
    async handleCheckAll(value) {
      this.tableData.forEach((item) => {
        item.isSelect = value;
        item.disable = value;
      });
      this.isSelectedAllPages = value;
      this.$emit('selectedAllPages', value);
    },
    // 清除选中的所有数据
    onClearSelectedData() {
      this.tableData.forEach((item) => {
        item.isSelect = false;
        item.disable = false;
      });
      this.isSelectedAllPages = false;
      this.$refs.customSelectionHeader.handleCheckChange();
    },
    // 选择表格某一行
    handleRowCheck(row) {
      row.isSelect = !row.isSelect;
      this.$emit('handleRowCheck', row);
    },
    // 表格功能选项
    handleSettingChange({ fields, size }) {
      this.setting.size = size;
      this.setting.selectedFields = fields;
      const fieldIds = fields.map(m => m.id);
      window.localStorage.setItem('settingCache', JSON.stringify({
        fields: fieldIds,
        size,
      }));
      this.computedColumnWidth()
    },
    // 切换页
    handlePageChange(page) {
      this.$emit('handlePageChange', page);
    },
    handlePageLimitChange(limit) {
      this.$emit('handlePageLimitChange', limit);
    },
    // 操作
    operateProcess(type, id) {
      this.$emit('operateProcess', type, id);
    },
    // 配置下发
    operateConfigDistribute(row) {
      this.$emit('showSideSlider', row);
    },
    // 查看进程配置
    onCheckProcessConfig(row) { // , isConfigFile) {
      const templateId = row.service_template_id;
      // const type = templateId ? 'service-template' : 'service-instance'
      // const serviceId = templateId || row.service_instance_id
      // const processId = templateId ? row.process_template_id : row.bk_process_id
      // if (isConfigFile) {
      //     if (!row.proc_inst_infos.length) {
      //         this.$bkMessage({
      //             message: '该进程暂无相关实例',
      //             theme: 'error'
      //         })
      //         return
      //     }
      //     const siteUrl = window.PROJECT_CONFIG.SITE_URL
      //     const bizId = this.$store.state.bizId
      // eslint-disable-next-line max-len
      //     window.open(`${window.origin}${siteUrl}/process-manage/manage/${type}/service/${serviceId}/process/${processId}?biz=${bizId}&isConfigFile=true`, '_self')
      // } else {
      //     this.$store.commit('routeProcessManageConfigInformationInstance', {
      //         type,
      //         serviceId
      //     })
      // }
      const query = {};
      const type = templateId ? 'template' : 'node';
      if (templateId) {
        query.template = templateId;
      } else {
        query.node = `module-${row.bk_module_id}`;
      }
      this.$router.push({
        name: 'process-attr',
        params: { type },
        query,
      });
    },
    toggleExpansion(row) {
      if (this.expandRow.includes(row.bk_process_id)) {
        this.expandRow = [];
      } else {
        this.expandRow = [row.bk_process_id];
      }
    },
    onBeforeExpandChange({ row }) {
      this.toggleExpansion(row);
    },
    computedColumnWidth() {
      const widthMap = {};
      this.setting.selectedFields.reduce((obj, item) => {
        obj[item.id] = this.$textTool.getHeadWidth(item.label, item);
        return obj;
      }, widthMap);
      this.columnMinWidth = widthMap;
    }
  },
};
</script>

<style lang="postcss" scoped>
  @import '../../../css/variable.css';

  .bk-custom-table {
    /deep/ .bk-table {
      background-color: #fff;

      .bk-table-fixed-right-patch {
        &::before {
          content: '';
          position: absolute;
          top: 0;
          left: 0;
          height: 42px;
          width: 1px;
          background: #dcdee5;
        }
      }

      &.bk-table-outer-border:after {
        z-index: 8;
      }

      .bk-table-row {
        &:hover {
          cursor: pointer;
        }

        &.expanded {
          .bk-table-expand-icon {
            color: #979ba5;
          }
        }
      }

      /* 状态 */
      .bk-table-expanded-cell {
        background: #fafbfd;
        padding: 0;
        padding-left: 110px;

        .process-status {
          display: flex;
          align-items: center;
          flex-wrap: wrap;
        }

        &:hover {
          background: #f0f1f5;
        }
      }
    }

    .file-num {
      color: $newMainColor;
    }

    .hosting-status {
      padding: 2px 4px;
      font-size: 12px;
    }

    .hosting {
      background: rgba(63, 192, 109, .2);
      color: #3fc06d;
    }

    .fail {
      background: rgba(239, 149, 153, .2);
      color: #ea3636;
    }

    .unmanaged {
      background: rgba(151, 155, 165, .2);
      color: #979ba5;
    }

    /deep/ .bk-table-body-wrapper {
      height: 100%;
      background-color: #fff;
    }

    /deep/ .operat-headr {
      .bk-button {
        margin-right: 5px;
      }
    }

    .no-other-instance {
      width: 100%;
      display: flex;
      justify-content: center;
    }

    .col-status-item {
      width: 100%;
      height: 44px;
      display: flex;
      align-items: center;
      border-bottom: 1px solid #dcdee5;
      color: #8c9099;

      &:last-child {
        border-bottom: 0;
      }

      /deep/ .loading-text {
        margin-left: 0;
      }

      .item-template-name,
      .item-file-name,
      .item-status {
        display: flex;
        align-items: center;
        width: 230px;
        padding-right: 10px;

        div {
          flex-shrink: 1;
          overflow: hidden;
          white-space: nowrap;
          text-overflow: ellipsis;
        }
      }

      .item-template-name,
      .item-file-name {
        /deep/ .bk-tooltip-ref {
          line-height: 24px;
        }

        span {
          border-bottom: 1px dashed #c4c6cc;
          padding-bottom: 3px;
        }
      }

      .item-instance-text {
        width: 140px;
      }
    }
  }
</style>
