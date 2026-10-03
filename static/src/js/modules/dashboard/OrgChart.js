import $ from "jquery";
require("orgchart");

class OrgChart {
  constructor() {
    this.events();
  }

  // Events
  events() {
    // OrgChart initialization is handled manually in templates
    // $(window).on("load", this.initOrgChart.bind(this));
  }

  // Methods

  /**
   * Initialize OrgChart
   */
  initOrgChart() {
    const chartDisplayEl = $("#chart-container");
    if (chartDisplayEl.length > 0) {
      $("#chart-container").orgchart({
        data: datascource,
        nodeContent: "title",
      });
    }
  }
}

export default OrgChart;
