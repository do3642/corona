document.addEventListener('DOMContentLoaded', () => {
  const sidebarLinks = document.querySelectorAll('.domestic_sidebar a');
  const sections = document.querySelectorAll('article');

  const observerOptions = {
    root: null, // 뷰포트 기준
    rootMargin: '0px',
    threshold: 0.9 // 섹션이 90% 이상 보일 때 활성화
  };

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      const id = entry.target.id;
      const sidebarLink = document.querySelector(`.domestic_sidebar a[href="#${id}"]`);

      if (entry.isIntersecting) {
        // 현재 보이는 섹션과 연결된 링크에 'active' 클래스 추가
        sidebarLinks.forEach(link => link.classList.remove('active'));
        if (sidebarLink) {
          sidebarLink.classList.add('active');
        }
      }
    });
  }, observerOptions);

  // 각 섹션을 observer에 등록
  sections.forEach(section => observer.observe(section));
});

document.addEventListener("DOMContentLoaded", () => {
  const buttons = document.querySelectorAll("button[data-graph]");
  buttons.forEach(button => {
    button.addEventListener("click", () => {
      buttons.forEach(btn => btn.classList.remove("active"));
      button.classList.add("active");
    });
  });
});