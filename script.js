// Metric details in Korean
const metricDetails = {
    market: {
        title: '시장 규모',
        content: `
            <p><strong>점수: 8/10</strong></p>
            <h4>한국 시장 분석:</h4>
            <ul>
                <li>국내 홈서비스 시장: 연 15조원 규모 (2024년 기준)</li>
                <li>1인 가구 비중 33.4% (940만 가구) 달성</li>
                <li>고령 인구 증가로 생활 도우미 서비스 급성장</li>
                <li>맞벌이 부부 증가로 아웃소싱 문화 확산</li>
                <li>K-방역 이후 집 관리에 대한 프리미엄 의식 강화</li>
            </ul>
            <h4>성장 동력:</h4>
            <p>숨고 독점 시장에서 AI 차별화로 새로운 카테고리 창출 가능</p>
        `
    },
    competition: {
        title: '경쟁 강도',
        content: `
            <p><strong>점수: 6/10</strong></p>
            <h4>한국 경쟁 환경:</h4>
            <ul>
                <li><strong>숨고</strong> - 시장점유율 70%+, 연매출 500억원</li>
                <li><strong>핸디</strong> - 카카오 계열, 청소 특화</li>
                <li><strong>아이윌</strong> - 홈케어 서비스 전문</li>
                <li><strong>헬프미</strong> - 생활편의 서비스</li>
                <li>지역별 소상공인 네트워크 (전통적 방식)</li>
            </ul>
            <h4>차별화 포인트:</h4>
            <ul>
                <li>AI 성격 매칭 (한국 특유의 '눈치' 문화 고려)</li>
                <li>실시간 작업 모니터링 시스템</li>
                <li>구독형 정기 서비스 모델</li>
            </ul>
        `
    },
    execution: {
        title: '실행 난이도',
        content: `
            <p><strong>점수: 5/10</strong></p>
            <h4>한국 시장 진입 요건:</h4>
            <ul>
                <li><strong>초기 자본:</strong> 시드 5억원, 시리즈A 15억원</li>
                <li><strong>개발팀:</strong> 풀스택 3명, AI/ML 2명, 모바일 2명</li>
                <li><strong>사업자 등록:</strong> 직업정보제공사업 신고</li>
                <li><strong>보험:</strong> 서비스 제공자 배상책임보험</li>
            </ul>
            <h4>한국 특화 기술 요소:</h4>
            <ul>
                <li>카카오페이/네이버페이 결제 연동</li>
                <li>주민등록번호 기반 신원확인</li>
                <li>아파트 단지별 접근 권한 관리</li>
                <li>한국어 자연어처리 (욕설 필터링 등)</li>
            </ul>
        `
    },
    timing: {
        title: '진입 시기',
        content: `
            <p><strong>점수: 9/10</strong></p>
            <h4>2025년 한국 시장 환경:</h4>
            <ul>
                <li><strong>정부 정책:</strong> K-디지털 뉴딜 2.0으로 AI 스타트업 지원 확대</li>
                <li><strong>투자 환경:</strong> 카카오벤처스, 네이버 D2SF 등 적극적 투자</li>
                <li><strong>인구 구조:</strong> 1인 가구 1,000만 돌파 예정</li>
                <li><strong>기술 성숙도:</strong> 하이퍼클로바X 등 한국어 AI 모델 상용화</li>
            </ul>
            <h4>왜 지금이 골든타임인가:</h4>
            <ul>
                <li>숨고의 IPO 준비로 경쟁사 견제 여력 부족</li>
                <li>배달의민족 성공으로 O2O 플랫폼 수용성 극대화</li>
                <li>MZ세대의 구독경제 익숙함 + 시간 절약 니즈</li>
                <li>코로나 엔데믹으로 홈케어 서비스 일상화</li>
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