import os
import sys
import threading
import webview
import platform
import subprocess
from flask import Flask, request, jsonify, render_template_string
from playwright.sync_api import sync_playwright

app = Flask(__name__)

# 전 세계 국가 코드 딕셔너리
country_codes = {
    "+82": ("한국", "🇰🇷"), "+81": ("일본", "🇯🇵"), "+86": ("중국", "🇨🇳"),
    "+886": ("대만", "🇹🇼"), "+852": ("홍콩", "🇭🇰"), "+853": ("마카오", "🇲🇴"),
    "+84": ("베트남", "🇻🇳"), "+65": ("싱가포르", "🇸🇬"), "+66": ("태국", "🇹🇭"),
    "+62": ("인도네시아", "🇮🇩"), "+60": ("말레이시아", "🇲🇾"), "+63": ("필리핀", "🇵🇭"),
    "+91": ("인도", "🇮🇳"), "+92": ("파키스탄", "🇵🇰"), "+880": ("방글라데시", "🇧🇩"),
    "+94": ("스리랑카", "🇱🇰"), "+95": ("미얀마", "🇲🇲"), "+976": ("몽골", "🇲🇳"),
    "+977": ("네팔", "🇳🇵"), "+998": ("우즈베키스탄", "🇺🇿"), "+61": ("호주", "🇦🇺"),
    "+64": ("뉴질랜드", "🇳🇿"), "+679": ("피지", "🇫🇯"),

    "+1": ("미국/캐나다", "🇺🇸/🇨🇦"), "+1876": ("자메이카", "🇯🇲"), "+1787": ("푸에르토리코", "🇵🇷"),
    "+52": ("멕시코", "🇲🇽"), "+55": ("브라질", "🇧🇷"), "+54": ("아르헨티나", "🇦🇷"),
    "+56": ("칠레", "🇨🇱"), "+57": ("콜롬비아", "🇨🇴"), "+51": ("페루", "🇵🇪"),
    "+58": ("베네수엘라", "🇻🇪"), "+598": ("우루과이", "🇺🇾"), "+595": ("파라과이", "🇵🇾"),
    "+593": ("에콰도르", "🇪🇨"), "+591": ("볼리비아", "🇧🇴"), "+502": ("과테말라", "🇬🇹"),
    "+506": ("코스타리카", "🇨🇷"), "+507": ("파나마", "🇵🇦"), "+53": ("쿠바", "🇨🇺"),

    "+44": ("영국", "🇬🇧"), "+33": ("프랑스", "🇫🇷"), "+49": ("독일", "🇩🇪"),
    "+39": ("이탈리아", "🇮🇹"), "+34": ("스페인", "🇪🇸"), "+7": ("러시아/카자흐스탄", "🇷🇺/🇰🇿"),
    "+31": ("네덜란드", "🇳🇱"), "+32": ("벨기에", "🇧🇪"), "+41": ("스위스", "🇨🇭"),
    "+43": ("오스트리아", "🇦🇹"), "+46": ("스웨덴", "🇸🇪"), "+47": ("노르웨이", "🇳🇴"),
    "+45": ("덴마크", "🇩🇰"), "+358": ("핀란드", "🇫🇮"), "+48": ("폴란드", "🇵🇱"),
    "+420": ("체코", "🇨🇿"), "+36": ("헝가리", "🇭🇺"), "+30": ("그리스", "🇬🇷"),
    "+351": ("포르투갈", "🇵🇹"), "+353": ("아일랜드", "🇮🇪"), "+380": ("우크라이나", "🇺🇦"),
    "+40": ("루마니아", "🇷🇴"), "+359": ("불가리아", "🇧🇬"),

    "+971": ("아랍에미리트", "🇦🇪"), "+966": ("사우디아라비아", "🇸🇦"), "+90": ("튀르키예", "🇹🇷"),
    "+98": ("이란", "🇮🇷"), "+972": ("이스라엘", "🇮🇱"), "+962": ("요르단", "🇯🇴"),
    "+974": ("카타르", "🇶🇦"), "+965": ("쿠웨이트", "🇰🇼"), "+968": ("오만", "🇴🇲"),
    "+973": ("바레인", "🇧🇭"), "+20": ("이집트", "🇪🇬"), "+27": ("남아프리카공화국", "🇿🇦"),
    "+212": ("모로코", "🇲🇦"), "+213": ("알제리", "🇩🇿"), "+216": ("튀니지", "🇹🇳"),
    "+234": ("나이지리아", "🇳🇬"), "+254": ("케냐", "🇰🇪"), "+255": ("탄자니아", "🇹🇿"),
    "+233": ("가나", "🇬🇭"), "+251": ("에티오피아", "🇪🇹"), "+256": ("우간다", "🇺🇬")
}

# 파이썬 코드 안에 UI(HTML/CSS/JS)를 통째로 내장
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>Instagram Region Checker</title>
    <style>
        body {
            margin: 0; padding: 0; min-height: 100vh;
            display: flex; justify-content: center; align-items: center;
            font-family: 'Pretendard', -apple-system, sans-serif;
            background: linear-gradient(135deg, #fdfbfb 0%, #ebedee 100%);
            overflow: hidden; /* 스크롤바 원천 차단 */
        }
        .card {
            background: rgba(255, 255, 255, 0.85); backdrop-filter: blur(10px);
            border-radius: 20px; padding: 40px 30px;
            width: 90%; max-width: 450px; text-align: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.05);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        input[type="text"]:focus { border-color: #0095f6; }
        button {
            width: 100%; padding: 15px; color: white; border: none;
            border-radius: 12px; font-size: 1.1rem; font-weight: bold;
            cursor: pointer; transition: background 0.3s ease, transform 0.1s ease;
        }
        button:active { transform: scale(0.98); }
        button:disabled { background: #cccccc !important; cursor: not-allowed; }
        
        #check-btn { background: linear-gradient(45deg, #0095f6, #0077c9); }
        #check-btn:hover { background: linear-gradient(45deg, #0077c9, #005a9e); }
        
        /* 엔진 설치 전용 버튼 디자인 */
        #install-btn {
            background: linear-gradient(45deg, #ff9800, #f57c00);
            display: none; /* 평소엔 숨김 */
            margin-top: 10px;
        }
        #install-btn:hover { background: linear-gradient(45deg, #f57c00, #e65100); }

        #flag-display { font-size: 6rem; margin: 20px 0; display: block; transition: transform 0.3s ease; }
        #status-text { font-size: 1.1rem; color: #666; margin-top: 10px; font-weight: 500; }
        
        .spinner {
            display: inline-block; width: 50px; height: 50px;
            border: 5px solid rgba(0, 149, 246, 0.2); border-radius: 50%;
            border-top-color: #0095f6; animation: spin 1s ease-in-out infinite;
            margin: 20px 0; display: none;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
    </style>
</head>
<body>
    <div class="card">
        <h2>Instagram 국가 확인/h2>
        <input type="text" id="account-input" placeholder="사용자명을 입력하세요" autocomplete="off">
        <button id="check-btn" onclick="startCheck()">국가 확인하기</button>
        <button id="install-btn" onclick="installEngine()">🚀 전용 엔진 설치하기</button>
        
        <div id="loading-spinner" class="spinner"></div>
        <div id="flag-display">🌍</div>
        <div id="status-text">주의: 단시간 반복 시 차단될 수 있습니다.</div>
    </div>

    <script>
        document.getElementById("account-input").addEventListener("keypress", function(event) {
            if (event.key === "Enter") { event.preventDefault(); startCheck(); }
        });

        async function startCheck() {
            const account = document.getElementById("account-input").value.trim();
            if (!account) return updateUI("error", "⚠️ 사용자명을 입력해주세요.", "❓");

            setLoading(true, `⏳ '${account}' 계정 정보 분석 중...`);
            document.getElementById("install-btn").style.display = "none"; // 검사 시작 시 설치버튼 숨김

            try {
                const response = await fetch('/check', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ account: account })
                });
                const result = await response.json();
                
                setLoading(false);
                updateUI(result.status, result.message, result.flag);

                // 파이썬 백엔드에서 엔진이 없다는 신호를 보내면 설치 버튼을 띄움
                if (result.status === "needs_install") {
                    document.getElementById("install-btn").style.display = "block";
                    document.getElementById("check-btn").style.display = "none";
                }

            } catch (error) {
                setLoading(false);
                updateUI("error", "서버 통신 중 오류가 발생했습니다.", "🚨");
            }
        }

        async function installEngine() {
            document.getElementById("install-btn").disabled = true;
            document.getElementById("install-btn").innerText = "설치 중입니다... (1~2분 소요)";
            setLoading(true, "⚙️ 필수 브라우저 엔진을 다운로드하고 있습니다...");

            try {
                const response = await fetch('/install', { method: 'POST' });
                const result = await response.json();
                
                setLoading(false);
                if (result.status === "success") {
                    updateUI("success", "✅ 설치가 완료되었습니다! 다시 확인해주세요.", "🎉");
                    document.getElementById("install-btn").style.display = "none";
                    document.getElementById("check-btn").style.display = "block";
                } else {
                    updateUI("error", "설치 실패: " + result.message, "❌");
                }
            } catch (error) {
                setLoading(false);
                updateUI("error", "설치 중 통신 오류가 발생했습니다.", "🚨");
            } finally {
                document.getElementById("install-btn").disabled = false;
                document.getElementById("install-btn").innerText = "🚀 전용 엔진 설치하기";
            }
        }

        function setLoading(isLoading, message = "") {
            const btn = document.getElementById("check-btn");
            const spinner = document.getElementById("loading-spinner");
            const flagDisplay = document.getElementById("flag-display");
            const statusText = document.getElementById("status-text");

            btn.disabled = isLoading;
            btn.innerText = isLoading ? "작업 중..." : "국가 확인하기";
            spinner.style.display = isLoading ? "inline-block" : "none";
            flagDisplay.style.display = isLoading ? "none" : "block";
            
            if (message) {
                statusText.style.color = "#0095f6";
                statusText.innerText = message;
            }
        }

        function updateUI(status, message, flag) {
            const statusText = document.getElementById("status-text");
            const flagDisplay = document.getElementById("flag-display");
            
            flagDisplay.innerText = flag;
            statusText.innerText = message;

            if (status === "success") statusText.style.color = "#28a745";
            else if (status === "warning") statusText.style.color = "#f0ad4e";
            else if (status === "error" || status === "needs_install") statusText.style.color = "#d9534f";

            if (status === "success") {
                flagDisplay.style.transform = "scale(1.2)";
                setTimeout(() => flagDisplay.style.transform = "scale(1)", 300);
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    # 이제 별도의 HTML 파일 없이 내장된 문자열을 랜더링함
    return render_template_string(HTML_TEMPLATE)

@app.route('/install', methods=['POST'])
def install_engine():
    # 서브프로세스를 이용해 터미널에 'playwright install chromium'을 입력한 것과 동일한 작업 수행
    try:
        subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/check', methods=['POST'])
def check_region():
    data = request.get_json()
    account = data.get('account')
    
    if not account:
        return jsonify({"status": "error", "message": "사용자명을 입력해주세요.", "flag": "❓"})

    sorted_codes = sorted(country_codes.items(), key=lambda item: len(item[0]), reverse=True)
    result = {"status": "error", "message": "알 수 없는 오류", "flag": "❌"}

    try:
        with sync_playwright() as p:
            current_os = platform.system()
            browser = None

            # [1단계] 사용자의 컴퓨터에 이미 깔려있는 상용 브라우저 시도
            try:
                if current_os == "Windows":
                    browser = p.chromium.launch(headless=True, channel="msedge")
                elif current_os == "Darwin":
                    browser = p.chromium.launch(headless=True, channel="chrome")
                else:
                    browser = p.firefox.launch(headless=True, channel="firefox")
            except Exception:
                pass # 시스템 브라우저가 없으면 무시하고 다음 단계로 넘어감

            # [2단계] Playwright 전용 Chromium 엔진 시도
            if not browser:
                try:
                    # 유저가 방금 [엔진 설치] 버튼을 눌러 설치했다면 여기서 성공하게 됨
                    browser = p.chromium.launch(headless=True)
                except Exception:
                    # [최종] 1, 2단계 모두 실패 시 UI로 '설치 필요' 신호 전송
                    return jsonify({
                        "status": "needs_install", 
                        "message": "사용 가능한 브라우저가 없습니다. 아래 버튼을 눌러 전용 엔진을 설치하세요.", 
                        "flag": "⚙️"
                    })

            # 브라우저가 정상적으로 실행되었다면 기존 스크래핑 로직 수행
            page = browser.new_page()
            page.goto("https://www.instagram.com/accounts/password/reset/")
            page.fill("#_r_4_", account)
            page.press("#_r_4_", "Enter")

            page.wait_for_load_state("networkidle")
            elements = page.locator("body *").all()
            
            number_founded = False
            country_founded = False

            for element in elements:
                text_data = element.text_content()
                if not text_data or not text_data.strip():
                    continue
                
                text_data = text_data.strip()

                if "Get link via SMS" in text_data or "SMS로 링크 받기" in text_data:
                    number_founded = True
                    for code, (country, flag) in sorted_codes:
                        if code in text_data:
                            result = {"status": "success", "message": f"해당 계정은 {country} 번호로 가입되어 있습니다.", "flag": flag}
                            country_founded = True
                            break
                    break
            
            if not number_founded:
                result = {"status": "error", "message": "전화번호를 찾지 못했습니다.", "flag": "📱"}
            elif not country_founded:
                result = {"status": "warning", "message": "국가코드를 찾지 못했거나 알 수 없는 국가입니다.", "flag": "🗺️"}

            browser.close()

    except Exception as e:
        result = {"status": "error", "message": f"오류 발생: {str(e)}", "flag": "🚨"}

    return jsonify(result)

def start_server():
    app.run(host='127.0.0.1', port=5000, debug=False)

if __name__ == '__main__':
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    webview.create_window(
        title='Instagram Region Checker', 
        url='http://127.0.0.1:5000', 
        width=1000, 
        height=750, 
        resizable=False
    )
    
    webview.start()