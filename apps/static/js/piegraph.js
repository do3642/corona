fetch('/api/covid-summary')
.then(response => response.json())
.then(data => {
    // 데이터 처리
    const labels = data.map(item => item["지역"]);
    const recoveryRates = data.map(item => item["완치율(%)"]);

    // Chart.js로 그래프 생성
    const ctx = document.getElementById('recoveryRateChart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels, // X축 레이블
            datasets: [{
                label: '완치율 (%)',
                data: recoveryRates, // Y축 데이터
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 5
            }]
        },
        options: {
            responsive: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 10,
                    title: {
                        display: true,
                        text: '완치율 (%)'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: '지역'
                    }
                }
            }
        }
    });
})
.catch(error => console.error('Error fetching data:', error));