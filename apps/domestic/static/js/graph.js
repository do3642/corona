document.addEventListener("DOMContentLoaded", () => {
  const graphConfigs = [
    { id: 'chart-area-incidence', url: '/api/graph/area_incidence' },
  ];

  graphConfigs.forEach(config => {
    fetch(config.url)
      .then(response => response.json())
      .then(data => {
        if (data.error) {
          console.error(`Error loading graph: ${config.url}`, data.error);
          document.getElementById(config.id).innerHTML = `<p>데이터 처리 중에 오류가 발생했습니다.</p>`;
        } else {
          createChart(config.id, data);
        }
      })
      .catch(error => {
        console.error(`Fetch error for ${config.url}`, error);
        document.getElementById(config.id).innerHTML = `<p>서버에서 응답받을 받는데 실패했습니다.</p>`;
      });
  });
});

function createChart(canvasId, data) {
  const ctx = document.getElementById(canvasId).getContext("2d");
  new Chart(ctx, {
    type: data.type,
    data: {
      labels: data.labels,
      datasets: [{
        label: data.label,
        data: data.values,
        borderColor: data.borderColor,
        borderWidth: 1
      }]
    },
    options: {
      responsive: false,
      scales: {
        y: {
          beginAtzero:true
        }
      }
    }
  })
}
