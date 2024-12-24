document.addEventListener('DOMContentLoaded', () => {
    const countryList = document.querySelector(".country-list");
    const selectedCountryDiv = document.getElementById("selected-country");
    const searchResultsDiv = document.getElementById("search-results");

    // 초기값 설정
    const initialCountry = "South Korea"; // 초기값으로 한국 설정

    // 페이지 로드 시 초기값 데이터 요청
    selectedCountryDiv.textContent = `선택된 국가: ${initialCountry}`;
    searchCountryData(initialCountry);

    // 국가 리스트 클릭 이벤트
    countryList.addEventListener("click", (event) => {
        const li = event.target.closest('li');
        
        if (li) {
            // `li` 태그의 데이터 속성 가져오기
            const country = li.getAttribute('data-country');

            if (country) {
                // 선택된 국가 표시
                selectedCountryDiv.textContent = `선택된 국가: ${country}`;

                // AJAX 요청으로 데이터 검색
                searchCountryData(country);
            } else {
                console.error("국가 정보가 없습니다.");
            }
        }
    });

    // AJAX 요청 함수
    function searchCountryData(country) {
        // 기존 결과 초기화
        searchResultsDiv.innerHTML = "검색 중...";

        // Fetch API로 서버 요청
        fetch(`/crw/crawl?country=${encodeURIComponent(country)}`)
            .then(response => response.json())  // 응답을 JSON으로 받기
            .then(data => {
                // 서버에서 받은 데이터 처리
                if (data.status === "success") {
                    // 메타데이터와 크롤링 결과 표시
                    displaySearchResults(data);
                } else {
                    searchResultsDiv.innerHTML = "<p style='color: red;'>크롤링 실패: 데이터를 가져올 수 없습니다.</p>";
                }
            })
            .catch((error) => {
                console.error("Error fetching data:", error);
                searchResultsDiv.innerHTML = `<p style="color: red;">데이터를 가져오는 중 오류가 발생했습니다.</p>`;
            });
    }

    // 검색 결과 화면에 출력
    function displaySearchResults(data) {
        console.log(data); // 크롤링한 데이터 확인

        // 기존 결과 초기화
        searchResultsDiv.innerHTML = "";

        // 메타데이터 출력 (예: 총 결과 개수, 검색한 국가 등)
        const metaDataDiv = document.createElement('div');
        metaDataDiv.style.marginBottom = '16px';
        metaDataDiv.innerHTML = `
            <p><strong>결과 개수:</strong> ${data.result.length}</p>
        `;
        searchResultsDiv.appendChild(metaDataDiv);

        if (!data.result || data.result.length === 0) {
            searchResultsDiv.innerHTML += "<p>데이터가 없습니다.</p>";
            return;
        }

        // 결과 영역에 뉴스 기사 카드 표시
        data.result.forEach((item) => {
            const articleCard = document.createElement('div');
            articleCard.classList.add('article-card');

            // 카드 내용
            articleCard.innerHTML = `
                <h3 style="font-size: 18px; font-weight: bold;"><a href="${item.url}" target="_blank" style="color: #333;">${item.title}</a></h3>
                <p style="font-size: 14px; color: #777;">${item.metadata}</p>
                <a href="${item.url}" target="_blank" style="font-size: 14px; color: #007bff;">자세히 보기</a>
            `;
        
            searchResultsDiv.appendChild(articleCard);
        });
    }
});