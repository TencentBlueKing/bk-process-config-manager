<template>
  <div class="instance-table-container">
    <div class="header">
      <div class="header-left">
        <b>{{ $t('选择实例') }}</b>
        {{ $t('（') + $t('已选') }}
        <span class="blue">{{ instanceList.length }}</span>
        {{ $t('个_实例') + $t('）') }}
      </div>
      <div v-if="curStep === 2" class="header-right">
        <span class="success">{{ statusCounter.succeeded }}</span>
        {{ $t('已生成') + $t('，') }}
        <span class="failed">{{ statusCounter.failed }}</span>
        {{ $t('生成失败') + $t('，') }}
        <span class="loading">{{ statusCounter.pending + statusCounter.running }}</span>
        {{ $t('生成中') }}
      </div>
    </div>
    <bk-table
      v-bkloading="{ isLoading: tableLoading, zIndex: 0 }"
      class="king-table"
      :max-height="maxHeight"
      :empty-text="emptyText"
      :data="tableLoadedList">
      <bk-table-column :label="$t('集群')">
        <div v-bk-overflow-tips class="table-ceil-overflow" slot-scope="{ row }">
          <span>{{ row.bk_set_name }}</span>
        </div>
      </bk-table-column>
      <bk-table-column :label="$t('模块')">
        <div v-bk-overflow-tips class="table-ceil-overflow" slot-scope="{ row }">
          <span>{{ row.bk_module_name }}</span>
        </div>
      </bk-table-column>
      <bk-table-column :label="$t('服务实例')">
        <div v-bk-overflow-tips class="table-ceil-overflow" slot-scope="{ row }">
          <span>{{ row.bk_service_name }}</span>
        </div>
      </bk-table-column>
      <bk-table-column :label="$t('进程别名')">
        <div v-bk-overflow-tips class="table-ceil-overflow" slot-scope="{ row }">
          <span>{{ row.bk_process_name }}</span>
        </div>
      </bk-table-column>
      <bk-table-column label="process_id">
        <div v-bk-overflow-tips class="table-ceil-overflow" slot-scope="{ row }">
          <span>{{ row.bk_process_id }}</span>
        </div>
      </bk-table-column>
      <bk-table-column label="inst_id">
        <div v-bk-overflow-tips class="table-ceil-overflow" slot-scope="{ row }">
          <span>{{ row.inst_id }}</span>
        </div>
      </bk-table-column>
      <bk-table-column :label="$t('内网IP')">
        <div v-bk-overflow-tips class="table-ceil-overflow" slot-scope="{ row }">
          <span>{{ row.bk_host_innerip }}</span>
        </div>
      </bk-table-column>
      <template v-if="curStep === 2">
        <bk-table-column :label="$t('状态')" prop="taskStatus">
          <template slot-scope="{ row }">
            <StatusView
              v-if="row.taskStatus === 'pending' || row.taskStatus === 'running'"
              type="loading"
              :text="$t('生成中')" />
            <StatusView v-if="row.taskStatus === 'succeeded'" type="success" :text="$t('已生成')" />
            <GenerateFailed
              v-else-if="row.taskStatus === 'failed'"
              :failed-reason="row.failed_reason"
              :solutions="row.solutions">
            </GenerateFailed>
          </template>
        </bk-table-column>
        <bk-table-column :label="$t('操作')" width="170px">
          <template slot-scope="{ row }">
            <bk-button
              theme="primary"
              text
              style="margin-right: 6px;"
              :disabled="hasPollingTask || isDistributing || ['pending', 'running'].includes(row.taskStatus)"
              @click="regenerate(row)"
            >{{ $t('重新生成') }}
            </bk-button>
            <bk-button
              theme="primary" text
              :disabled="row.taskStatus !== 'succeeded' || isDistributing"
              @click="compareConfiguration(row)"
            >{{ $t('配置对比') }}
            </bk-button>
          </template>
        </bk-table-column>
      </template>
    </bk-table>
    <!-- 配置对比 -->
    <bk-sideslider
      :is-show.sync="sliderData.isShow"
      :quick-close="true"
      :width="1200"
      @hidden="handleCloseSlider">
      <div class="config-contrast-header" slot="header">
        <span>{{ $t('配置对比') }}</span>
        <span class="divide-line">{{ '-' }}</span>
        <span class="template-name">{{ selectedConfig.template_name + '(' + selectedConfig.file_name + ')' }}</span>
      </div>
      <div v-bkloading="{ isLoading: sliderData.isLoading }" style="height: calc(100vh - 60px);" slot="content">
        <SidesliderDiff v-if="sliderData.oldData" :old-data="sliderData.oldData" :new-data="sliderData.newData">
          <template slot="leftTitle">
            <div class="status-flag">{{ $t('实时') }}</div>
            <div class="create-time">{{ $t('更新时间') + $t('：') + (formatDate(sliderData.oldData.time) || '--') }}</div>
          </template>
          <template slot="rightTitle">
            <div class="status-flag">{{ $t('预生成') }}</div>
            <div class="create-time">{{ $t('生成时间') + $t('：') + (formatDate(sliderData.newData.time) || '--') }}</div>
          </template>
        </SidesliderDiff>
      </div>
    </bk-sideslider>
  </div>
</template>

<script>
import { formatDate } from '@/common/util';
import SidesliderDiff from '@/components/SidesliderDiff';
import GenerateFailed from '@/components/GenerateFailed';

export default {
  components: {
    SidesliderDiff,
    GenerateFailed,
  },
  props: {
    curStep: {
      type: Number,
      required: true,
    },
    selectedConfig: {
      type: Object,
      required: true,
    },
    hasPollingTask: {
      type: Boolean,
      required: true,
    },
    statusCounter: {
      type: Object,
      required: true,
    },
    isDistributing: {
      type: Boolean,
      required: true,
    },
    isGeneratePage: {
      type: Boolean,
      required: true,
    },
    instanceList: {
      type: Array,
      required: true,
    },
    tableLoading: {
      type: Boolean,
      required: true,
    },
  },
  data() {
    return {
      formatDate,
      emptyText: this.$t('暂未选择实例'),

      isThrottled: false, // 滚动节流 是否进入cd
      isPageOver: false, // 前端分页加载是否结束
      tableScroller: null, // 滚动容器
      tableLoadedList: [], // 展示的列表数据
      tablePagedList: [], // 将列表数据按 pageSize 分页
      pageSize: 50, // 每页展示多少数据
      totalCount: null, // 数据总条数
      totalPage: null, // 计算出总共多少页
      currentPage: null, // 当前加载了多少页

      sliderData: {
        isShow: false,
        isLoading: false,
        oldData: null, // 配置对比数据
        newData: null, // 配置对比数据
      },
    };
  },
  computed: {
    maxHeight() { // 表格最大高度
      const { pageHeight } = this.$store.state;
      if (this.isGeneratePage) { // 配置生成
        return pageHeight - 257;
      }  // 配置下发 header 52 标题 60 步骤 40 选择实例 72 下边留余 53
      return pageHeight - 317;
    },
  },
  watch: {
    instanceList(val) {
      this.emptyText = this.$t('当前指定范围未能匹配到实例，请确认所选范围是否有误，或对应范围是否存在主机');
      this.tableLoadedList.splice(0);
      if (val.length) {
        this.initPagination(val);
      } else {
        this.isPageOver = true;
      }
    },
  },
  mounted() {
    this.tableScroller = this.$el.querySelector('.bk-table-body-wrapper');
    this.tableScroller.addEventListener('scroll', this.handleTableScroll, { passive: true });
  },
  beforeDestroy() {
    this.tableScroller.removeEventListener('scroll', this.handleTableScroll);
  },
  methods: {
    initPagination(list) {
      this.isPageOver = false;
      this.totalCount = list.length;
      this.totalPage = Math.ceil(this.totalCount / this.pageSize);
      this.currentPage = 0;
      this.tablePagedList.splice(0);
      for (let i = 0; i < this.totalCount; i += this.pageSize) {
        this.tablePagedList.push(list.slice(i, i + this.pageSize));
      }
      this.loadPage();
      this.tableScroller.scrollTop = 0;
    },
    loadPage() {
      this.currentPage += 1;
      this.isPageOver = this.currentPage === this.totalPage;
      this.tableLoadedList.splice(this.tableLoadedList.length, 0, ...this.tablePagedList[this.currentPage - 1]);
      this.$emit('pageAdd', this.tableLoadedList.length);
    },
    handleTableScroll() {
      if (!this.isPageOver && !this.isThrottled) {
        this.isThrottled = true;
        setTimeout(() => {
          this.isThrottled = false;
          const el = this.tableScroller;
          if (el.scrollHeight - el.offsetHeight - el.scrollTop < 10) {
            this.loadPage();
          }
        }, 200);
      }
    },

    async regenerate(row) { // 重新生成
      const generateList = this.instanceList.filter(item => item.bk_process_id === row.bk_process_id);
      generateList.forEach((item) => {
        this.updateStatus('running', this.statusCounter.running + 1);
        if (item.taskStatus === 'succeeded') {
          this.updateStatus('succeeded', this.statusCounter.succeeded - 1);
        } else if (item.taskStatus === 'failed') {
          this.updateStatus('failed', this.statusCounter.failed - 1);
        }
        item.taskStatus = 'running';
      });
      try {
        const res = await this.$store.dispatch('configTemplate/ajaxSyncGenerateConfig', {
          data: {
            bk_process_id: row.bk_process_id,
          },
          templateId: this.$route.params.templateId,
        });
        generateList.forEach((item) => {
          const matchTaskItem = res.data.find(taskItem => item.inst_id === taskItem.extra_data.inst_id) || {};
          if (matchTaskItem.status === 'succeeded') {
            item.taskStatus = 'succeeded';
            this.updateStatus('running', this.statusCounter.running - 1);
            this.updateStatus('succeeded', this.statusCounter.succeeded + 1);
          } else if (matchTaskItem.status === 'failed') {
            item.taskStatus = 'failed';
            item.failed_reason = matchTaskItem.extra_data.failed_reason;
            item.solutions = matchTaskItem.extra_data.solutions;
            this.updateStatus('running', this.statusCounter.running - 1);
            this.updateStatus('failed', this.statusCounter.failed + 1);
          } else {
            console.warn('同步生成接口出错，没有 matchTaskItem 或者状态不对');
            item.taskStatus = 'failed';
            this.updateStatus('running', this.statusCounter.running - 1);
            this.updateStatus('failed', this.statusCounter.failed + 1);
          }
        });
      } catch (e) {
        console.warn(e);
        generateList.forEach((item) => {
          item.taskStatus = 'failed';
          this.updateStatus('running', this.statusCounter.running - 1);
          this.updateStatus('failed', this.statusCounter.failed + 1);
        });
      }
    },
    async compareConfiguration(row) { // 配置对比
      try {
        this.sliderData.isShow = true;
        this.sliderData.isLoading = true;
        const res = await this.$store.dispatch('configInstance/ajaxGetLatestConfigInstance', {
          instId: row.inst_id,
          processId: row.bk_process_id,
          templateId: Number(this.$route.params.templateId),
        });
        res.data.released_config = res.data.released_config || {}; // 第一次生成时还没有下发内容
        this.sliderData.oldData = {
          content: res.data.released_config.content,
          language: res.data.released_config.file_format,
          time: res.data.released_config.created_at,
        };
        this.sliderData.newData = {
          content: res.data.generated_config.content,
          language: res.data.generated_config.file_format,
          time: res.data.generated_config.created_at,
        };
      } catch (e) {
        console.warn(e);
      } finally {
        this.sliderData.isLoading = false;
      }
    },
    handleCloseSlider() { // 关闭配置对比后清除数据
      this.sliderData.oldData = null;
      this.sliderData.newData = null;
    },
    updateStatus(key, value) {
      this.$emit('updateStatus', { key, value });
    },
  },
};
</script>

<style scoped lang="postcss">
  @import '../../../../css/variable.css';

  .instance-table-container {
    padding: 0 60px;

    .header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      height: 42px;
      padding: 0 16px;
      background: #f0f1f5;
      border: 1px solid #dcdee5;
      border-bottom: 0;
      border-radius: 2px 2px 0 0;
      font-size: 12px;

      .header-left {
        display: flex;

        .blue {
          color: $newMainColor;
          font-weight: bold;
          margin: 0 4px;
        }
      }

      .header-right {
        display: flex;
        align-items: center;

        > span {
          font-weight: bold;
          padding-right: 4px;
        }

        .success {
          color: #3fc06d;
        }

        .failed {
          color: #ea3636;
        }

        .loading {
          color: $newMainColor;
        }
      }
    }

    .king-table {
      border-radius: 0;
      background-color: #fff;
    }

    .status-flag {
      padding: 0 10px;
      text-align: center;
      min-width: 60px;
      line-height: 52px;
      color: #dcdee5;
      background: #424242;
      font-size: 14px;
    }

    .create-time {
      padding-left: 20px;
      line-height: 52px;
      color: #c4c6cc;
      font-size: 14px;
    }
  }
</style>
