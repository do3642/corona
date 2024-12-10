document.addEventListener('DOMContentLoaded', () => {
  // 기본적으로 '오늘' 상태로 설정
  let selectedDateType = 'today';

  // 날짜 선택 박스 이벤트 리스너 추가
  const dateSelect = document.querySelector('#date-select');
  dateSelect.addEventListener('change', async (event) => {
    selectedDateType = event.target.value;  // 선택한 날짜를 가져옵니다.
    // console.log(selectedDateType);
    document.querySelector('.new-cases').textContent = `로딩중`;
    document.querySelector('.new-cases-change').textContent = `로딩중`;
    
    document.querySelector('.new-recovered').textContent = `로딩중`;
    document.querySelector('.new-recovered-change').textContent = `로딩중`;
  
    document.querySelector('.new-deaths').textContent = `로딩중`;
    document.querySelector('.new-deaths-change').textContent = `로딩중`;
    await fetchCovidData(selectedDateType);
  });

  // 초기 데이터 로드 (오늘 상태로)
  fetchCovidData(selectedDateType);
});

// 서버에서 COVID-19 데이터를 가져오는 함수
async function fetchCovidData(dateType) {
  try {
    const response = await fetch(`/worldwide/covid-data/${dateType}`);

    if (!response.ok) {
      throw new Error(`Error fetching data: ${response.statusText}`);
    }
    const data = await response.json();
    
    // 데이터를 화면에 반영하는 함수 호출
    updateCovidData(data);
  } catch (error) {
    console.error("Error fetching data:", error);
  }
}

// 데이터를 화면에 업데이트하는 함수
function updateCovidData(data) {
  // 숫자형으로 변환하여 형식 적용
  document.querySelector('.new-cases').textContent = `${Number(data.new_cases).toLocaleString()} 명`;
  document.querySelector('.new-cases-change').textContent = Number(data.new_cases_change).toLocaleString();
  
  document.querySelector('.new-recovered').textContent = `${Number(data.new_deaths).toLocaleString()} 명`;
  document.querySelector('.new-recovered-change').textContent = Number(data.new_deaths_change).toLocaleString();

  document.querySelector('.new-deaths').textContent = `${Number(data.new_deaths).toLocaleString()} 명`;
  document.querySelector('.new-deaths-change').textContent = Number(data.new_deaths_change).toLocaleString();

  document.querySelector('.total-cases').textContent = `${Number(data.total_cases).toLocaleString()} 명`;
  document.querySelector('.total-cases-change').textContent = Number(data.total_cases_change).toLocaleString();

  document.querySelector('.total-recovered').textContent = `${Number(data.total_recovered).toLocaleString()} 명`;
  document.querySelector('.total-recovered-change').textContent = Number(data.total_recovered_change).toLocaleString();

  document.querySelector('.total-deaths').textContent = `${Number(data.total_deaths).toLocaleString()} 명`;
  document.querySelector('.total-deaths-change').textContent = Number(data.total_deaths_change).toLocaleString();
}


