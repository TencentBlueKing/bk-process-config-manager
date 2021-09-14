<template>
  <div class="config-information">
    <template v-if="processInstance.length">
      <div class="tab-content">
        <bk-tab type="unborder-card" :active.sync="active" @tab-change="onChangeTab">
          <bk-tab-panel
            v-for="(panel, index) in panels"
            :name="panel.id.toString()"
            v-bind="panel"
            :key="index + Date.now()">
            <template slot="label">
              <div v-bk-tooltips="htmlConfig">
                <span class="panel-name">{{ panel.name }}</span>
                <span class="config-file-count">{{ '(' + panel.count + ')' }}</span>
                <i v-if="!panel.isFull" class="panel-icon gsekit-icon gsekit-icon-incomplete-line"></i>
                <i class="delete-icon bk-icon icon-delete" @click.stop="handleDeleteProcess(panel)"></i>
              </div>
              <div id="tooltips">
                <div>
                  <span>{{ $t('进程名称: ') }}</span>
                  {{ panel.name }}
                </div>
                <div>
                  <!-- eslint-disable-next-line vue/no-v-html -->
                  <span v-html="$t('配置文件: x个', { x: panel.count })"></span>
                </div>
                <div>
                  <span>{{ $t('进程管理: ') }}</span>
                  {{ panel.isFull ? $t('必填信息完整') : $t('必填信息不完整') }}
                </div>
              </div>
            </template>
          </bk-tab-panel>
        </bk-tab>
        <div class="add-process" @click="onAddProcess">
          <span class="divide-line"></span>
          <i class="bk-icon icon-plus-line"></i>
          {{ $t('新增进程') }}
        </div>
      </div>
      <div class="scroll-area">
        <!-- 配置文件 -->
        <div class="config-file">
          <div class="instance-title">
            <span class="instance-title-text">{{ isServiceInstance ? $t('配置文件') : $t('服务模版配置文件') }}</span>
            <div class="instance-title-content" @click="onConfigFile">
              <i class="title-icon gsekit-icon gsekit-icon-edit-fill"></i>
              <span>{{ $t('配置') }}</span>
            </div>
          </div>
          <div class="config-file-table">
            <bk-table v-if="tableData.length"
                      auto-scroll-to-top
                      header-row-class-name="header"
                      :data="tableData"
                      :outer-border="false"
                      :header-border="false"
                      :header-cell-style="{ background: '#fff' }">
              <bk-table-column label="ID" prop="config_template_id"></bk-table-column>
              <bk-table-column :label="$t('模板名称')" prop="template_name"></bk-table-column>
              <bk-table-column :label="$t('文件名称')" prop="file_name"></bk-table-column>
            </bk-table>
            <bk-exception v-else class="exception-wrap-item exception-part" type="empty" scene="part">
              <span class="no-config-file">{{ $t('没有配置文件') }}</span>
              <bk-button :theme="'primary'" @click="onConfigFile">{{ $t('配置') }}</bk-button>
            </bk-exception>
          </div>
        </div>
        <!-- 进程属性 -->
        <div class="process-attr">
          <div class="instance-title">
            <span class="instance-title-text">{{ isServiceInstance ? $t('进程属性') : $t('服务模版进程属性') }}</span>
            <div class="instance-title-content" @click="onEditor">
              <i class="title-icon gsekit-icon gsekit-icon-edit-fill"></i>
              <span>{{ $t('编辑') }}</span>
              <span v-if="!currentProcess.is_full" class="warn-prompt">
                <i class="gsekit-icon gsekit-icon-incomplete-line"></i>
                <span>{{ $t('进程管理的必填信息不完整') }}</span>
              </span>
            </div>
          </div>
          <div class="process-attr-content">
            <span class="attr-title">{{ $t('基础信息') }}</span>
            <div class="attr-content">
              <div class="content-item" v-for="item in baseInfo" :key="item.id">
                <label class="content-item-label">{{ item.name }}</label>
                <span class="content-item-span" v-bk-overflow-tips>
                  {{ processInfo[item.key] || '--' }}
                </span>
              </div>
            </div>
          </div>
          <div class="process-attr-content">
            <span class="attr-title">{{ $t('进程管理信息') }}</span>
            <div class="attr-content">
              <div class="content-item" v-for="item in processAttrInfo" :key="item.id">
                <span v-if="item.isrequired" class="warn-icon" v-bk-tooltips="$t('必填项')">*</span>
                <label class="content-item-label">{{ item.name }}</label>
                <span class="content-item-span" v-if="processInfo[item.key]" v-bk-overflow-tips>
                  {{ processInfo[item.key] }}
                </span>
                <span class="content-item-span" v-else>
                  <span v-if="item.isrequired" class="quire-empty" v-bk-tooltips="$t('进程管理必填项未填写')">{{ '--' }}</span>
                  <span v-else>{{ '--' }}</span>
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
      <!-- 侧滑绑定配置文件 -->
      <bk-sideslider :is-show.sync="isShowConfigFile" :width="680" :quick-close="false">
        <div slot="header">{{ $t('关联配置文件') }}</div>
        <div slot="content">
          <ConfigFileList
            :is-binding-data="tableData"
            :current-process="currentProcess"
            :is-service-instance="isServiceInstance"
            @onBindConfigFile="onBindConfigFile"
            @onCancel="onCancel">
          </ConfigFileList>
        </div>
      </bk-sideslider>
    </template>
    <div class="no-process" v-else-if="!processInstance.length">
      <bk-exception class="exception-wrap-item exception-part" type="empty" scene="page">
        <span class="no-process-text">{{ $t('暂无进程') }}</span>
        <div>
          <bk-button :theme="'primary'" @click="onAddProcess">{{ $t('新建进程') }}</bk-button>
        </div>
      </bk-exception>
    </div>
    <!-- 侧滑编辑模板 -->
    <bk-sideslider :is-show.sync="isShow" :width="800" :quick-close="false">
      <div slot="header">{{ sidesTitle }}</div>
      <div slot="content">
        <EditorAttribute
          :base-info="baseInfo"
          :process-attr-info="processAttrInfo"
          :process-info="processInfo"
          :is-service-instance="isServiceInstance"
          :template-name="templateName"
          :current-process="currentProcess"
          :is-add-process="isAddProcess"
          @onCreateProcess="onCreateProcess"
          @onCancel="onCancel"
          @onSaveEditor="onSaveEditor">
        </EditorAttribute>
      </div>
    </bk-sideslider>
    <!-- 操作二次确认弹框 -->
    <bk-dialog
      ext-cls="king-dialog"
      v-model="dialogInfo.visible"
      :render-directive="'if'"
      width="450"
      :mask-close="false"
      @confirm="handleDialogConFirm"
      @cancel="handleDialogCancel"
      :title="$t('删除进程')">
      <div class="body-prompt">
        {{ $t('确定要') }}
        <span>{{ $t('删除') }}</span>
        {{ $t('进程') }}：
        {{ dialogInfo.title }}
      </div>
    </bk-dialog>
  </div>
</template>

<script>
import EditorAttribute from './EditorAttribute';
import ConfigFileList from './ConfigFileList';
export default {
  components: {
    EditorAttribute,
    ConfigFileList,
  },
  props: {
    templateName: {
      type: String,
      default: '',
    },
    isServiceInstance: {
      type: Boolean,
      default: true,
    },
    panels: {
      type: Array,
      default: () => [],
    },
    tableData: {
      type: Array,
      default: () => [],
    },
    processInfo: {
      type: Object,
      default: () => ({}),
    },
    processInstance: {
      type: Array,
      default: () => [],
    },
    currentProcess: {
      type: Object,
      default: () => ({}),
    },
    processId: {
      type: Number,
    },
  },
  data() {
    const baseInfo = [
      {
        name: this.$t('进程名称'),
        key: 'bk_func_name',
        placeholder: this.$t('请输入进程名称'),
        isrequired: true,
      },
      {
        name: this.$t('进程别名'),
        key: 'bk_process_name',
        placeholder: this.$t('请输入进程别名'),
        isrequired: true,
      },
      {
        name: this.$t('进程启动参数'),
        key: 'bk_start_param_regex',
        placeholder: this.$t('请输入进程启动参数'),
      },
      {
        name: this.$t('备注'),
        key: 'description',
        placeholder: this.$t('请输入备注'),
      },
    ];
    const processAttrInfo = [
      {
        name: this.$t('工作路径'),
        key: 'work_path',
        placeholder: this.$t('请输入工作路径'),
        isrequired: true,
      },
      {
        name: this.$t('启动用户'),
        key: 'user',
        placeholder: this.$t('请输入启动用户'),
        isrequired: true,
      },
      {
        name: this.$t('PID 文件路径'),
        key: 'pid_file',
        placeholder: this.$t('请输入PID 文件路径'),
        isrequired: true,
      },
      {
        name: this.$t('启动命令'),
        key: 'start_cmd',
        placeholder: this.$t('请输入启动命令'),
        isrequired: true,
      },
      {
        name: this.$t('停止命令'),
        key: 'stop_cmd',
        placeholder: this.$t('请输入停止命令'),
        isrequired: true,
      },
      {
        name: this.$t('启动优先级'),
        key: 'priority',
        valueType: 'Number',
        placeholder: this.$t('请填写正整数，1表示最先启动'),
        isNumber: true,
        isrequired: true,
      },
      {
        name: this.$t('强制停止命令'),
        key: 'face_stop_cmd',
        placeholder: this.$t('请输入强制停止命令'),
      },
      {
        name: this.$t('启动数量'),
        key: 'proc_num',
        valueType: 'Number',
        placeholder: this.$t('请输入启动数量'),
        isNumber: true,
      },
      {
        name: this.$t('重启命令'),
        key: 'restart_cmd',
        placeholder: this.$t('请输入重启命令'),
      },
      {
        name: this.$t('操作超时时长'),
        key: 'timeout',
        valueType: 'Number',
        placeholder: this.$t('请输入操作超时时长'),
        isNumber: true,
        hasAppend: true,
      },
      {
        name: this.$t('重载命令'),
        key: 'reload_cmd',
        placeholder: this.$t('请输入重载命令'),
      },
      {
        name: this.$t('启动等待时长'),
        key: 'bk_start_check_secs',
        valueType: 'Number',
        placeholder: this.$t('请输入启动等待时长'),
        isNumber: true,
        hasAppend: true,
      },
    ];
    return {
      active: '',
      baseInfo,
      processAttrInfo,
      isAddProcess: false, // 是否为新增进程
      sidesTitle: '', // 侧滑标题
      isShow: false, // 展示编辑进程属性侧滑
      htmlConfig: {
        content: '#tooltips',
        placements: ['top-start'],
        allowHtml: true,
      }, // tooltips提示
      isShowConfigFile: false, // 展示绑定配置文件侧滑
      dialogInfo: { // 二次确认弹框信息
        visible: false, // 二次确认弹框是否可见
        rowId: null, // 当前点击行的id
        title: '', // dialog标题
      },
    };
  },
  watch: {
    processId(val) {
      this.active = String(val);
    },
  },
  mounted() {
    const { isConfigFile } = this.$route.query;
    if (isConfigFile) {
      this.isShowConfigFile = true;
    }
  },
  methods: {
    // tab栏切换
    async onChangeTab(id) {
      this.$emit('onChangeTab', id);
    },
    // 配置文件
    onConfigFile() {
      this.isShowConfigFile = true;
    },
    // 新建进程
    onAddProcess() {
      this.isAddProcess = true;
      this.isShow = true;
      this.sidesTitle = this.isServiceInstance ? this.$t('新增进程') : this.$t('新增模版进程');
    },
    // 编辑进程配置
    onEditor() {
      this.isAddProcess = false;
      this.isShow = true;
      this.sidesTitle = this.isServiceInstance ? this.$t('编辑进程属性') : this.$t('编辑模版进程属性');
    },
    // 保存事件
    async onSaveEditor() {
      this.isShow = false;
      this.$emit('onSaveEditor');
    },
    // 绑定配置文件成功
    async onBindConfigFile() {
      this.isShowConfigFile = false;
      this.$emit('onBindConfigFile');
    },
    onCancel() {
      this.isShow = false;
      this.isShowConfigFile = false;
    },
    // 创建进程or创建进程模板
    onCreateProcess() {
      this.isShow = false;
      this.$emit('onCreateProcess');
    },
    // 删除进程or删除进程模板
    handleDeleteProcess(panel) {
      this.dialogInfo = {
        visible: true,
        id: panel.id,
        title: panel.name,
      };
    },
    async handleDialogConFirm() {
      try {
        const { id } = this.dialogInfo;
        if (this.isServiceInstance) {
          const res = await this.$store.dispatch('process/ajaxDeleteProcessInstance', {
            data: {
              process_instance_ids: [Number(id)],
            },
          });
          if (res.result) {
            this.$bkMessage({
              message: this.$t('进程删除成功'),
              theme: 'success',
            });
          }
        } else {
          const res = await this.$store.dispatch('process/ajaxDeleteProcessTemplate', {
            data: {
              process_template_ids: [Number(id)],
            },
          });
          if (res.result) {
            const h = this.$createElement;
            this.$bkMessage({
              message: h('p', {
                style: {
                  margin: 0,
                },
              }, [
                this.$t('进程删除成功，请到'),
                h('span', {
                  style: {
                    color: '#3A84FF',
                    cursor: 'pointer',
                  },
                  on: {
                    click: () => {
                      const cmdbUrl = window.PROJECT_CONFIG.CMDB_URL;
                      const { bizId } = this.$store.state;
                      window.open(`${cmdbUrl}/#/business/${bizId}/service/operational/template/${this.currentProcess.service_template_id}?tab=instance`);
                    },
                  },
                }, this.$t('配置平台')),
                this.$t('进行同步'),
              ]),
              theme: 'success',
              ellipsisLine: 2,
            });
          }
        }
        this.$emit('handleDeleteProcess', this.active === String(id));
      } catch (error) {
        console.warn(error);
      }
    },
    handleDialogCancel() {
      this.dialogInfo = {};
    },
  },
};
</script>

<style lang="postcss" scoped>
  @import '../../../css/mixins/scroll.css';

  .config-information {
    height: 100%;
    width: 100%;
    padding-bottom: 20px;

    @media screen and (min-width: 960px) and (max-width: 1380px) {
      .attr-content {
        .content-item {
          width: 50% !important;
        }
      }
    }

    @media screen and (min-width: 1380px) and (max-width: 1680px) {
      .attr-content {
        .content-item {
          width: 33.33% !important;
        }
      }
    }

    @media screen and (min-width: 1680px) {
      .attr-content {
        .content-item {
          width: 33.33% !important;
        }
      }
    }

    .tab-content {
      height: 60px;
      margin: 0 22px 20px;
      display: flex;
      border-bottom: 1px solid #dfe0e5;
    }

    .add-process {
      display: flex;
      margin-top: 23px;
      text-align: right;
      font-size: 14px;
      color: #3a84ff;
      cursor: pointer;

      .divide-line {
        height: 18px;
        width: 1px;
        background: #d3d5db;
        margin: 0 20px;
      }

      .bk-icon {
        margin: 3px 4px 0 0;
      }
    }

    /deep/ .bk-tab {
      height: 60px;
      max-width: calc(100% - 118px);

      .bk-tab-header {
        height: 60px;
        background-image: none;

        .bk-tab-scroll-controller {
          background-color: #f5f6fa;
        }
      }

      .bk-tab-label-item {
        line-height: 65px;

        .panel-icon {
          font-size: 16px;
          color: #ff9c01;
        }

        .config-file-count {
          font-size: 12px;
          color: #9a9ea8;
        }

        .delete-icon {
          font-size: 16px;
          opacity: 0;
          color: #979ba5;
          cursor: pointer;

          &:hover {
            color: #3a84ff;
          }
        }

        &:hover {
          .config-file-count {
            color: #699df4;
          }

          .delete-icon {
            opacity: 1;
          }
        }

        &.active {
          .config-file-count {
            color: #699df4;
          }

          &::after {
            top: 57px !important;
            margin-left: 5px;
            width: calc(100% - 55px);
          }
        }
      }

      .bk-tab-scroll-controller {
        height: 60px;
        line-height: 65px;
      }
    }

    .scroll-area {
      height: calc(100% - 60px);
      padding: 0 22px 20px;
      overflow: auto;

      @mixin scroller;
    }

    .config-file {
      position: relative;
      width: 100%;
      background-color: #fff;
      box-shadow: 0px 1px 2px 0px rgba(0,0,0,.1);
      padding: 16px 20px;
      margin-bottom: 16px;

      /deep/ .header {
        .cell {
          background: #f5f6fa;
        }
      }

      /deep/ .exception-wrap-item {
        margin-bottom: 10px;
        font-size: 14px;
        color: #63656e;

        .no-config-file {
          display: block;
          margin-bottom: 10px;
        }
      }
    }

    .process-attr {
      position: relative;
      width: 100%;
      background-color: #fff;
      box-shadow: 0px 1px 2px 0px rgba(0,0,0,.1);
      padding: 16px 20px;
      font-size: 14px;

      .attr-title {
        color: #63656e;
        font-weight: 700;
      }

      .attr-content {
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        color: #979ba5;
        padding: 16px 0;

        .content-item {
          padding: 0 25px;
          width: 338px;
          height: 44px;
          position: relative;
          display: flex;
          align-items: center;
          cursor: default;

          .warn-icon {
            color: #ea3636;
            font-style: normal;
            position: absolute;
            top: 15px;
            left: 10px;
            font-weight: 700;
          }

          .content-item-label {
            min-width: 90px;
            display: inline-block;
            text-align: left;
            position: relative;
            margin-right: 10px;

            &::after {
              content: ':';
              position: absolute;
              right: -5px;
              top: 0;
              font-weight: 700;
              color: #63656e;
            }
          }

          .content-item-span {
            flex: 1;
            color: #63656e;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            display: inline-block;

            .quire-empty {
              color: #ff9c01;
            }
          }
        }
      }
    }

    .instance-title {
      display: flex;
      align-items: center;
      color: #3a84ff;
      font-size: 14px;
      margin-bottom: 19px;

      .instance-title-text {
        font-size: 16px;
        color: #313238;
        margin-right: 18px;

        &::before {
          content: '';
          position: absolute;
          left: 0;
          top: 20px;
          width: 4px;
          height: 15px;
          background: #dcdee5;
        }
      }

      .instance-title-content {
        display: flex;
        align-items: center;
        cursor: pointer;

        .title-icon {
          margin-right: 8px;
          font-size: 16px;
        }

        .warn-prompt {
          margin-left: 12px;
          color: #ff9c01;

          span {
            margin-left: 7px;
          }
        }
      }
    }

    .no-process {
      height: 100%;
      width: 100%;
      display: flex;
      align-items: center;

      /deep/ .bk-exception {
        margin-bottom: 150px;

        .no-process-text {
          font-size: 20px;
          color: #63656e;
          display: block;
          margin-bottom: 22px;
        }
      }
    }
  }

</style>
