// data.py에 불러온 데이터들을 반복을 돌리면서 createChart 함수에 넣어줌.
let chartInstance=null;
document.addEventListener("DOMContentLoaded", () => {

  document.querySelector("#graph1 div").addEventListener("click", (event) => {
    const canvasId = "chart-area"
    const button = event.target;

    changeChart(canvasId, button);
  })


  
});

function changeChart(canvasId, button) {
  const graphId = button.getAttribute("data-graph");

  if (graphId) {
    fetch(`/api/graph/${graphId}`)
      .then(response => response.json())
      .then(data => {
        if (chartInstance) {
          chartInstance.destroy();
        }
        createChart(canvasId, data);
      })
      .catch(error => console.error(`Error loading graph: ${graphId}`, error));
  }
}

// 위에서 받은 데이터를 받아 데이터마다 다른 그래프가 나올 수 있도록 함.
function createChart(canvasId, data) {
  const ctx = document.getElementById(canvasId).getContext("2d");
  chartInstance = new Chart(ctx, {
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
