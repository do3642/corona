let chartInstances={};
document.addEventListener("DOMContentLoaded", () => {
  // 처음 들어갔을 때 화면에 뿌려줄 데이터들만 반복을 돌리면서 createChart 함수에 넣어줌.
  const graphConfigs = [
    {id: "chart-area", url: "/api/graph/area_incidence"},
    {id: "chart-age", url: "/api/graph/age_incidence"},
  ]

  graphConfigs.forEach(config => {
    fetch(config.url)
      .then(response => response.json())
      .then(data => {
        if (data.error) {
          console.error(`Error loading graph: ${config.url}`, data.error);
          document.getElementById(config.id).innerHTML = `<p>Error loading data</p>`;
        } else {
          createChart(config.id, data);
        }
      })
      .catch(error => {
        console.error(`Fetch error for ${config.url}:`, error);
        document.getElementById(config.id).innerHTML=`<p>Failed to load data</p>`;
      });
  });

  document.querySelector("#graph1 div").addEventListener("click", (event) => {
    const canvasId = "chart-area"
    const button = event.target;

    changeChart(canvasId, button);
  })

  document.querySelector("#graph3 div").addEventListener("click", (event) => {
    const canvasId = "chart-age";
    const button = event.target;

    changeChart(canvasId, button);
  })
  
});

// 버튼을 누르면 차트가 바뀌게 해주는 함수
function changeChart(canvasId, button) {
  const graphId = button.getAttribute("data-graph");

  if (graphId) {
    fetch(`/api/graph/${graphId}`)
      .then(response => response.json())
      .then(data => {
        if (chartInstances[canvasId]) {
          chartInstances[canvasId].destroy();
        }
        createChart(canvasId, data);
      })
      .catch(error => console.error(`Error loading graph: ${graphId}`, error));
  }
}

// 위에서 데이터를 받아 데이터마다 다른 그래프가 나올 수 있도록 함.
function createChart(canvasId, data) {
  const ctx = document.getElementById(canvasId).getContext("2d");

  chartInstances[canvasId] = new Chart(ctx, {
    type: data.type,
    data: {
      labels: data.labels,
      datasets: [{
        label: data.label,
        data: data.values,
        backgroundColor: data.backgroundColor,
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      scales: {
        y: {
          beginAtzero:true
        }
      },
      layout: {
        padding:{
          top: 90
        }
      }
    }
  })
}
