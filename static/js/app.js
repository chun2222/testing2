function populateFilter() {
    // Let's populate the <option> elements in 
    // our <select> from the database. 
    const url = "api/values/region";
  
    d3.json(url).then(function(response) {
      
      var filerOptions = ["All"];
      filerOptions = filerOptions.concat(response);
      
      d3.select("#sel-filter-region")
        .selectAll("option")
        .data(filerOptions)
        .enter()
        .append("option")
        .text(d => d);
  
      // Bind an event to refresh the data
      // when an option is selected.
      d3.select("#sel-filter-region").on("change", refreshCharts);
    });
  }
  
  function refreshCharts(event) {
    // event.target will refer tp the selector
    // from which we will get the selected option
    var selectedValue = d3.select(event.target).property('value');
  
    // With the selectedValue we can refresh the charts
    // filtering if needed. 
    buildRegionPieChart(selectedValue);
    buildRegionByStateBarChart(selectedValue);
  }
  
  function buildRegionPieChart(selectedRegion) {
    // If we have race to filter by let's pass it
    // in as a querystring parameter
    var url = "api/count_by/region/state";
    if (selectedRegion != undefined) {
      url = `api/count_by/region/state?region=${selectedRegion}`;
    }
  
    d3.json(url).then(function(response) {
      // In order to render a pie chart we need to 
      // extract the labels and values from the 
      // json response. For an example see:
      // https://plotly.com/javascript/pie-charts/ 
      var data = [{
        labels: response.map(d => d.state),
        values: response.map(d => d.total),
        type: 'pie'
      }];
      
      var layout = {
        height: 400,
        width: 500
      };
      
      Plotly.newPlot('state-region-plot', data, layout);
  
    });
  }
  
  
  function buildRegionByStateBarChart(selectedRegion) {
    var url = "api/count_by/region/state";
    if (selectedRegion != undefined) {
      url = `api/count_by/region/state?region=${selectedRegion}`;
    }
  
    d3.json(url).then(function(response) {
  
      // Using the group method in d3 we can
      // do grouping of the received json
      // for the purposes of creating multiple traces.
      // https://github.com/d3/d3-array#group
      var grouped_data = d3.group(response, d => d.region)
  
      var traces = Array();
  
      // then iterating over each group by it's
      // key we can create a trace for each group
      // https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/forEach
      grouped_data.forEach(element => {      
        traces.push({
          x: element.map(d => d.state),
          y: element.map(d => d.total),
          name: element[0].region,
          type: 'bar'
        });
      });
      
      var layout = {
        barmode: 'stack',
        height: 400,
        width: 500
      };
      
      Plotly.newPlot('region-by-state-plot', traces, layout);
    });
  }
  
  // Upon intial load of the page setup
  // the visualisations and the select filter
  populateFilter();
  buildRegionPieChart();
  buildRegionByStateBarChart();
  