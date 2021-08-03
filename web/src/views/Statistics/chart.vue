<template>
  <div class="chart">
    <canvas ref="chartRef" class="chart-instance">
    </canvas>
  </div>
</template>

<script>
import Chart from '@blueking/bkcharts';

export default {
  props: {
    chartType: {
      type: String,
      required: true,
    },
    chartData: {
      type: Object,
      default: () => ({}),
    },
    chartOptions: {
      type: Object,
      default: () => ({}),
    },
  },
  data() {
    return {
      chart: null,
    };
  },
  watch: {
    chartData: {
      deep: true,
      handler(val) {
        if (this.chart) {
          // const { datasets = [], labels = [] } = val
          this.chart.data = val;
          this.update();
        }
      },
    },
    chartOptions: {
      deep: true,
      handler(val) {
        if (this.chart) {
          this.chart.options = val;
          this.update();
        }
      },
    },
  },
  mounted() {
    const el = this.$refs.chartRef;
    this.chart = new Chart(el, {
      type: this.chartType,
      data: this.chartData,
      options: this.chartOptions,
    });
  },
  methods: {
    onDataPickerPick() {
      this.getTaskHistoryList();
    },
    handleClearDate() {
      this.initDateTimeRange = ['', ''];
      this.getTaskHistoryList();
    },
    update() {
      this.chart && this.chart.update();
    },
  },
};
</script>

<style lang="postcss" scoped>
  .chart {
    position: relative;
    flex: 1;
    width: 100%;
    height: 100%;

    .chart-instance {
      width: 100%;
      height: 100%;
    }
  }
</style>
