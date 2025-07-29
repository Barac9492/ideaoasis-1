// Metric details in Korean
const metricDetails = {
    market: {
        title: '시장 규모',
        content: `
            <p><strong>점수: 8/10</strong></p>
            <h4>분석:</h4>
            <ul>
                <li>전 세계 홈서비스 시장은 연간 4000억 달러 규모</li>
                <li>한국 홈서비스 시장은 지속적으로 성장하는 추세</li>
                <li>1인 가구 증가와 고령화로 수요 급증</li>
                <li>코로나19 이후 집 관리에 대한 관심 증대</li>
            </ul>
            <h4>기회:</h4>
            <p>대형 시장이지만 여전히 분산되어 있어 통합 솔루션의 기회가 큼</p>
        `
    },
    competition: {
        title: '경쟁 강도',
        content: `
            <p><strong>점수: 6/10</strong></p>
            <h4>현재 경쟁사:</h4>
            <ul>
                <li>숨고 - 국내 최대 홈서비스 플랫폼</li>
                <li>TaskRabbit (해외) - 글로벌 선도기업</li>
                <li>지역별 소규모 업체들</li>
            </ul>
            <h4>경쟁 우위 기회:</h4>
            <ul>
                <li>AI 기반 매칭 시스템으로 차별화</li>
                <li>실시간 가격 비교 및 투명성</li>
                <li>품질 보증 시스템</li>
            </ul>
        `
    },
    execution: {
        title: '실행 난이도',
        content: `
            <p><strong>점수: 5/10</strong></p>
            <h4>필요한 자원:</h4>
            <ul>
                <li>초기 자본: 5억-10억원</li>
                <li>개발팀: 풀스택 개발자 3-5명</li>
                <li>AI/ML 엔지니어 1-2명</li>
                <li>마케팅 및 영업팀</li>
            </ul>
            <h4>기술적 과제:</h4>
            <ul>
                <li>실시간 매칭 알고리즘 개발</li>
                <li>결제 시스템 통합</li>
                <li>리뷰 및 평가 시스템</li>
                <li>모바일 앱 개발</li>
            </ul>
        `
    },
    timing: {
        title: '시기',
        content: `
            <p><strong>점수: 9/10</strong></p>
            <h4>시장 타이밍:</h4>
            <ul>
                <li>AI 기술의 대중화와 접근성 향상</li>
                <li>디지털 트랜스포메이션 가속화</li>
                <li>온디맨드 서비스에 대한 소비자 기대 증가</li>
                <li>코로나19 이후 비대면 서비스 선호</li>
            </ul>
            <h4>지금이 최적인 이유:</h4>
            <ul>
                <li>AI 기술이 충분히 성숙했지만 아직 완전히 도입되지 않음</li>
                <li>투자자들의 AI 스타트업에 대한 관심 고조</li>
                <li>정부의 디지털 뉴딜 정책 지원</li>
            </ul>
        `
    }
};

// Modal functionality
const modal = document.getElementById('metric-modal');
const modalTitle = document.getElementById('modal-title');
const modalBody = document.getElementById('modal-body');
const closeBtn = document.getElementsByClassName('close')[0];

// Function to get today's date in KST format
function getTodayKST() {
    const now = new Date();
    const kstOffset = 9 * 60; // KST is UTC+9
    const kst = new Date(now.getTime() + (kstOffset * 60 * 1000));
    
    const year = kst.getFullYear();
    const month = kst.getMonth() + 1;
    const day = kst.getDate();
    
    return `${year}년 ${month}월 ${day}일`;
}

// Add click event listeners to metrics
document.addEventListener('DOMContentLoaded', function() {
    // Update date to today's KST
    const dateElement = document.querySelector('.date');
    if (dateElement) {
        dateElement.textContent = getTodayKST();
    }
    
    const metrics = document.querySelectorAll('.metric');
    
    metrics.forEach(metric => {
        metric.addEventListener('click', function() {
            const metricType = this.getAttribute('data-metric');
            const detail = metricDetails[metricType];
            
            if (detail) {
                modalTitle.textContent = detail.title;
                modalBody.innerHTML = detail.content;
                modal.style.display = 'block';
            }
        });
    });
});

// Close modal when clicking X
closeBtn.onclick = function() {
    modal.style.display = 'none';
}

// Close modal when clicking outside of it
window.onclick = function(event) {
    if (event.target === modal) {
        modal.style.display = 'none';
    }
}