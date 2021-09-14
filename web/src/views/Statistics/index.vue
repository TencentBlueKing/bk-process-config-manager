<template>
  <div class="operational-statistics" v-bkloading="{ isLoading: loading }">
    <div class="page-head">
      <div>{{ $t('运营统计') }}</div>
      <div class="search-head">
        <div></div>
        <bk-date-picker
          ref="datePickerRef"
          :clearable="false"
          :shortcuts="picker.shortcuts"
          :type="'daterange'"
          :shortcut-close="true"
          :use-shortcut-text="true"
          :shortcut-selected-index="0"
          :value="formData.timeRange"
          :placeholder="$t('选择日期范围')"
          :options="picker.options"
          @change="onPickerChange"
          @shortcut-change="handleShortcutChange">
        </bk-date-picker>
      </div>
    </div>
    <section class="page-content">
      <div class="chart-list">
        <section class="chart-item">
          <div class="chart-item-top">
            <div class="chart-item-title">{{ $t('活跃排行') }}</div>
            <div class="chart-item-filter">
              <div class="select-job">
                <bk-select :clearable="false" v-model="formData.ranking" @change="getStaticByRanking">
                  <bk-option v-for="item in rankingFilters" :key="item.id" :id="item.id" :name="item.name"></bk-option>
                </bk-select>
              </div>
            </div>
          </div>
          <div class="chart-item-bottom" :style="{ height: `${chartHeight}px` }">
            <div class="chart-item-content">
              <Chart
                ref="chartTrendRef"
                chart-type="bar"
                :chart-data="chartData.ranking"
                :chart-options="{
                  ...chartOption,
                  plugins: rankingPlugins
                }">
              </Chart>
            </div>
          </div>
        </section>
        <section class="chart-item">
          <div class="chart-item-top">
            <div class="chart-item-title">{{ $t('统计频次') }}</div>
            <div class="chart-item-filter">
              <bk-radio-group v-model="formData.frequency" @change="getStaticByFrequency">
                <bk-radio class="mr20" :value="item.value" v-for="item in frequencyFilters" :key="item.value">
                  {{ item.label }}
                </bk-radio>
              </bk-radio-group>
            </div>
          </div>
          <div class="chart-item-bottom" :style="{ height: `${chartHeight}px` }">
            <div class="chart-item-content">
              <Chart
                ref="chartFrequencyRef"
                chart-type="bar"
                :chart-data="chartData.frequency"
                :chart-options="{
                  ...chartOption,
                  plugins: frequencyPlugins
                }">
              </Chart>
            </div>
          </div>
        </section>
        <section class="chart-item">
          <div class="chart-item-top">
            <div class="chart-item-title">{{ $t('趋势统计') }}</div>
            <div class="chart-item-filter">
              <div class="select-job">
                <bk-select :clearable="false" v-model="formData.job_object" @change="getStaticByTrend">
                  <bk-option v-for="item in objectFilters" :key="item.id" :id="item.id" :name="item.name"></bk-option>
                </bk-select>
              </div>
              <div class="select-job ml10">
                <bk-select :clearable="false" v-model="formData.job_action" @change="getStaticByTrend">
                  <bk-option v-for="item in actionFilters" :key="item.id" :id="item.id" :name="item.name"></bk-option>
                </bk-select>
              </div>
            </div>
          </div>
          <div class="chart-item-bottom" :style="{ height: `${chartHeight}px` }">
            <div class="chart-item-content">
              <Chart
                ref="chartTrendRef"
                chart-type="line"
                :chart-data="chartData.trend"
                :chart-options="chartOption">
              </Chart>
            </div>
          </div>
        </section>
      </div>
    </section>
  </div>
</template>

<script>
import Chart from './chart';
import { mapState, mapActions } from 'vuex';
import { formatDate } from '@/common/util';

export default {
  name: 'OperationalStatistics',
  components: {
    Chart,
  },
  data() {
    return {
      loading: false,
      formData: {
        shortcutIndex: 0,
        timeRange: [],
        frequency: 'bk_biz_id',
        job_object: 'all',
        job_action: 'all',
        ranking: 'bk_biz_id',
      },
      chartData: {
        frequency: {},
        trend: {},
        ranking: {},
      },
      chartOption: {
        maintainAspectRatio: false,
        layout: {
          padding: {
            left: 0,
            right: 0,
            top: 30,
            bottom: 0,
          },
        },
        parsing: {
          xAxisKey: 'date',
          yAxisKey: 'count',
        },
        scales: {
          x: { stacked: true },
          y: { stacked: true },
        },
        plugins: {
          legend: { display: false },
          datalabels: {
            anchor: 'end',
            align: 'center',
            color: '#63656e',
            font: { weight: 'bold', size: '10px' },
            formatter: Math.round,
            display: ({ dataIndex, dataset }) => dataset.data[dataIndex],
          },
        },
      },
      frequencyPlugins: {},
      rankingPlugins: {},
      color: [
        'rgb(75, 192, 192)',
        'rgb(255, 99, 132)',
        'rgb(255, 159, 64)',
        'rgb(255, 205, 86)',
        'rgb(75, 192, 192)',
        'rgb(54, 162, 235)',
        'rgb(153, 102, 255)',
        'rgb(201, 203, 207)',
      ],
      frequencyFilters: [
        { label: this.$t('按业务'), value: 'bk_biz_id' },
        { label: this.$t('按执行人'), value: 'created_by' },
        { label: this.$t('按执行命令'), value: 'job_action' },
      ],
      objectFilters: [
        { name: this.$t('全部任务对象'), id: 'all' },
        { name: this.$t('配置文件'), id: 'configfile' },
        { name: this.$t('进程'), id: 'process' },
      ],
      actionFilters: [
        { name: this.$t('全部动作'), id: 'all' },
        { name: this.$t('生成'), id: 'generate' },
        { name: this.$t('下发'), id: 'release' },
        { name: this.$t('启动'), id: 'start' },
        { name: this.$t('停止'), id: 'stop' },
        { name: this.$t('重启'), id: 'restart' },
        { name: this.$t('重载'), id: 'reload' },
        { name: this.$t('强制停止'), id: 'force_stop' },
        { name: this.$t('托管'), id: 'set_auto' },
        { name: this.$t('取消托管'), id: 'unset_auto' },
      ],
      rankingFilters: [
        { name: this.$t('按业务'), id: 'bk_biz_id' },
        { name: this.$t('按执行人'), id: 'created_by' },
        { name: this.$t('按执行命令'), id: 'job_action' },
        { name: this.$t('按任务状态'), id: 'status' },
        { name: this.$t('按任务来源'), id: 'bk_app_code' },
      ],
      statusMap: {
        pending: this.$t('等待执行'),
        running: this.$t('正在执行'),
        succeeded: this.$t('执行成功'),
        failed: this.$t('执行失败'),
        ignored: this.$t('已忽略'),
      },
      picker: {
        format: 'YYYY-mm-dd',
        options: {
          disabledDate(time) {
            return time.getTime() > Date.now();
          },
        },
        shortcuts: [
          {
            text: window.i18n.t('近7天'),
            value() {
              const end = new Date();
              const start = new Date();
              start.setTime(start.getTime() - (3600 * 1000 * 24 * 6));
              return [start, end];
            },
          }, {
            text: window.i18n.t('近15天'),
            value() {
              const end = new Date();
              const start = new Date();
              start.setTime(start.getTime() - (3600 * 1000 * 24 * 14));
              return [start, end];
            },
          }, {
            text: window.i18n.t('近30天'),
            value() {
              const end = new Date();
              const start = new Date();
              start.setTime(start.getTime() - (3600 * 1000 * 24 * 29));
              return [start, end];
            },
          },
          {
            text: window.i18n.t('近1年'),
            value() {
              const end = new Date();
              const start = new Date();
              start.setTime(start.getTime() - (3600 * 1000 * 24 * 364));
              return [start, end];
            },
          },
        ],
      },
    };
  },
  computed: {
    ...mapState(['bizList', 'pageHeight']),
    chartHeight() {
      return (Math.max(this.pageHeight, 708) - 220) / 2 - 52;
    },
  },
  created() {
    this.frequencyPlugins = this.getChartPlugin('frequency');
    this.rankingPlugins = this.getChartPlugin('ranking');
    const end = new Date();
    const start = new Date();
    start.setTime(start.getTime() - (3600 * 1000 * 24 * 7));
    this.formData.timeRange = [start, end];
    this.getStaticPageData();
  },
  methods: {
    ...mapActions('meta', ['ajaxFrequencyStatistics', 'ajaxTrendStatistics', 'ajaxJobCountStatistics']),
    // 按频率
    getStaticPageData() {
      this.getStaticByFrequency();
      this.getStaticByTrend();
      this.getStaticByRanking();
    },
    async getStaticByFrequency() {
      const { frequency } = this.formData;
      try {
        const params = this.getDateParams();
        params.group_by = frequency;
        let { data = [] } = await this.ajaxFrequencyStatistics(params);
        if (data.length) {
          if (['bk_biz_id', 'job_action'].includes(frequency)) {
            const i18nMap = this.getI18nMap(frequency);
            data = data.map(item => ({
              ...item,
              [frequency]: i18nMap[item[frequency]],
            }));
          }
          const dateMap = {};
          data.reduce((obj, item) => {
            obj[item.date] = item;
            return obj;
          }, dateMap);
          // 补齐缺失的日期
          const dateArr = this.getContinuityDate(params.start_time.slice(0, 10), params.end_time.slice(0, 10));
          data = dateArr.map(date => ({
            date,
            count: dateMap[date] ? dateMap[date].count : 0,
            [frequency]: dateMap[date] ? dateMap[date][frequency] : '',
          }));
          const { color } = this;
          this.$set(this.chartData, 'frequency', {
            labels: data.map(item => item.date),
            datasets: [
              { data, backgroundColor: color, borderColor: color },
            ],
          });
        } else {
          this.chartData.frequency = {
            labels: [],
            datasets: [],
          };
        }
      } catch (e) {
        console.warn(e);
      }
    },
    // 按趋势
    async getStaticByTrend() {
      try {
        const params = this.getDateParams();
        if (this.formData.job_object !== 'all') {
          params.job_object = this.formData.job_object;
        }
        if (this.formData.job_action !== 'all') {
          params.job_action = this.formData.job_action;
        }
        let { data = [] } = await this.ajaxTrendStatistics(params);
        if (data.length) {
          const dateMap = {};
          data.reduce((obj, item) => {
            obj[item.date] = item;
            return obj;
          }, dateMap);
          // 补齐缺失的日期
          const dateArr = this.getContinuityDate(params.start_time.slice(0, 10), params.end_time.slice(0, 10));
          data = dateArr.map(date => ({
            date,
            count: dateMap[date] ? dateMap[date].count : 0,
          }));
          const [borderColor] = this.color;
          this.chartData.trend = {
            labels: data.map(item => item.date),
            datasets: [
              { data: data.map(item => item.count), borderColor },
            ],
          };
        } else {
          this.chartData.trend = {
            labels: [],
            datasets: [],
          };
        }
      } catch (e) {
        console.warn(e);
      }
    },
    async getStaticByRanking() {
      try {
        const { ranking } = this.formData;
        const { color } = this;
        const { start_time: startTime, end_time: endTime } = this.getDateParams();
        const params = {
          exclude_conditions: {},
          filter_conditions: {
            start_time__gte: startTime,
            start_time__lte: endTime,
          },
          group_by: [ranking],
        };
        let { data = [] } = await this.ajaxJobCountStatistics(params);
        if (data.length) {
          if (['bk_biz_id', 'job_action', 'status'].includes(ranking)) {
            const i18nMap = this.getI18nMap(ranking);
            data = data.map(item => ({
              ...item,
              [ranking]: i18nMap[item[ranking]] || item[ranking],
            }));
          }
          this.chartData.ranking = {
            labels: data.map(item => item[ranking]),
            datasets: [
              { data, backgroundColor: color, borderColor: color },
            ],
          };
        } else {
          this.chartData.trend = {
            labels: [],
            datasets: [],
          };
        }
      } catch (e) {
        console.warn(e);
      }
    },
    handleShortcutChange(value, index) {
      this.formData.shortcutIndex = index;
    },
    onPickerChange(date) {
      this.formData.timeRange = date;
      this.getStaticPageData();
    },
    getDateParams() {
      let startTime = '';
      let endTime = '';
      if (this.formData.shortcutIndex > -1) {
        const currentShortcut = this.picker.shortcuts[this.formData.shortcutIndex];
        if (currentShortcut) {
          const [start, end] = currentShortcut.value();
          startTime = formatDate(start, this.picker.format);
          endTime = formatDate(end, this.picker.format);
        }
      } else {
        const [start, end] = this.formData.timeRange;
        startTime = formatDate(start, this.picker.format);
        endTime = formatDate(end, this.picker.format);
      }
      return {
        start_time: `${startTime} 00:00:00`,
        end_time: `${endTime} 23:59:59`,
      };
    },
    getDateTimes(date) {
      return Date.parse(date.split('-'));
    },
    // 拿到完整的时间段日期
    getContinuityDate(beginDate, endDate) {
      const continuityDateArr = [];
      let beginTime = this.getDateTimes(beginDate);
      const endTime = this.getDateTimes(endDate);
      const dayTimes = 60 * 60 * 24 * 1000;
      const dayNum = (endTime - beginTime) / dayTimes;
      for (let i = 0; i <= dayNum; i++) {
        if (beginTime >= endTime) {
          beginTime = formatDate(endTime, this.picker.format);
          continuityDateArr.push(beginTime);
        } else {
          continuityDateArr.push(formatDate(beginTime, this.picker.format));
        }
        beginTime += dayTimes;
      }
      return continuityDateArr;
    },
    getI18nMap(type) {
      let i18nMap = {};
      switch (type) {
        case 'bk_biz_id':
          this.bizList.reduce((obj, item) => {
            i18nMap[item.bk_biz_id] = item.name;
            return obj;
          }, i18nMap);
          break;
        case 'job_action':
          this.actionFilters.reduce((obj, item) => {
            i18nMap[item.id] = item.name;
            return obj;
          }, i18nMap);
          break;
        case 'status':
          i18nMap = this.statusMap;
          break;
        default:
          i18nMap = {};
      }
      return i18nMap;
    },
    getChartPlugin(type) {
      let formatter = data => data[this.formData[type]] || '';
      let display = ({ dataset }) => dataset.data.length <= 31;
      const tooltip = {
        callbacks: {
          label: ({ formattedValue }) => this.$t('执行次数', [formattedValue]),
        },
      };
      let rotation = '-70';
      if (type === 'ranking') {
        formatter = data => data.count || '';
        display = ({ dataIndex, dataset }) => dataset.data[dataIndex];
        rotation = 0;
      } else {
        tooltip.callbacks.label = ({ dataset, dataIndex }) => {
          const data = dataset.data[dataIndex] || {};
          return this.$t('不定项次数', [data[this.formData.frequency], data.count]);
        };
      }
      const datalabels = {
        anchor: 'end',
        clamping: true,
        align: 'top',
        offset: 1,
        color: '#63656e',
        font: {
          weight: 'bold',
          size: '10px',
        },
        rotation,
        formatter,
        display,
      };
      const plugin = {
        legend: { display: false },
        tooltip,
        datalabels,
      };
      return plugin;
    },
  },
};
</script>

<style lang="postcss" scoped>
  .operational-statistics {
    flex: 1;
    display: flex;
    flex-direction: column;
    padding: 18px 60px 20px;
    background-color: #f5f7fa;
    overflow: hidden;

    .search-head {
      display: flex;
      justify-content: space-between;
      margin: 20px 0 16px;
    }

    .page-content {
      flex: 1;
      display: flex;
      flex-direction: column;
      overflow: auto;
    }

    .chart-list {
      display: flex;
      flex-direction: column;
      height: 100%;

      .chart-item {
        padding: 10px 20px;
        flex: 1;
        display: flex;
        flex-direction: column;
        background: #fff;

        & + .chart-item {
          margin-top: 10px;
        }

        .chart-item-top {
          display: flex;
          align-items: center;
          margin-bottom: 15px;
          height: 32px;

          .chart-item-filter {
            display: flex;
            flex: 1;
            margin-left: 25px;
          }
        }

        .chart-item-bottom {
          overflow: hidden;
        }

        .chart-item-content {
          width: 100%;
          height: 100%;
          overflow: hidden;
        }

        .select-job {
          width: 200px;
          display: inline-flex;

          .bk-select {
            width: 100%;
          }
        }
      }
    }
  }
</style>
