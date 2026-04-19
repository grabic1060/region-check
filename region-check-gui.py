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
            overflow: hidden;
        }
        .card {
            background: rgba(255, 255, 255, 0.85); backdrop-filter: blur(10px);
            border-radius: 20px; padding: 40px 30px;
            width: 90%; max-width: 450px; text-align: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.05);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        h2 { color: #333; font-size: 1.4rem; margin-bottom: 30px; word-break: keep-all; }
        input[type="text"] {
            width: 100%; padding: 15px; box-sizing: border-box;
            border: 2px solid #e1e1e1; border-radius: 12px;
            font-size: 1.1rem; text-align: center; outline: none;
            transition: border-color 0.3s ease; margin-bottom: 20px;
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
        
        #install-btn {
            background: linear-gradient(45deg, #ff9800, #f57c00);
            display: none; margin-top: 10px;
        }
        #install-btn:hover { background: linear-gradient(45deg, #f57c00, #e65100); }

        #flag-display { font-size: 6rem; margin: 20px 0; display: block; transition: transform 0.3s ease; }
        #status-text { font-size: 1.1rem; color: #666; margin-top: 10px; font-weight: 500; }
        #caution-text { font-size: 1.0rem; color: #555; margin-top: 10px; font-weight: 500; }
        
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
        <h2>Instagram 계정 국가 확인</h2>
        <input type="text" id="account-input" placeholder="사용자명을 입력하세요" autocomplete="off">
        <button id="check-btn" onclick="startCheck()">국가 확인하기</button>
        <button id="install-btn" onclick="installEngine()">🚀 전용 엔진 설치하기</button>
        
        <div id="loading-spinner" class="spinner"></div>
        <div id="flag-display">🌍</div>
        <div id="status-text">주의: 단시간 반복 시 차단될 수 있습니다.</div>
        <div id="caution-text">이 프로그램은 계정에 등록된 전화번호를 기준으로 분석하며, 계정 사용자의 국적을 보장하지 않습니다.</div>
    </div>

    <script>
        document.getElementById("account-input").addEventListener("keypress", function(event) {
            if (event.key === "Enter") { event.preventDefault(); startCheck(); }
        });

        async function startCheck(visible = false) {
            const account = document.getElementById("account-input").value.trim();
            if (!account) return updateUI("error", "⚠️ 사용자명을 입력해주세요.", "❓");

            if (!visible) {
                setLoading(true, `⏳ '${account}' 계정 정보 분석 중...`);
            } else {
                setLoading(true, `🤖 새로 뜬 창에서 캡차를 풀어주세요! (해결 시 자동 진행)`);
            }
            document.getElementById("install-btn").style.display = "none"; 

            try {
                const response = await fetch('/check', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ account: account, visible: visible }) 
                });
                const result = await response.json();
                
                if (result.status === "captcha_detected" && !visible) {
                    return startCheck(true);
                }

                setLoading(false);
                updateUI(result.status, result.message, result.flag);

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
            else if (status === "error" || status === "needs_install" || status === "captcha_detected" || status === "fake_account") statusText.style.color = "#d9534f";

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
    return render_template_string(HTML_TEMPLATE)

@app.route('/install', methods=['POST'])
def install_engine():
    try:
        subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/check', methods=['POST'])
def check_region():
    data = request.get_json()
    account = data.get('account')
    visible_mode = data.get('visible', False)
    
    is_headless = not visible_mode
    
    if not account:
        return jsonify({"status": "error", "message": "사용자명을 입력해주세요.", "flag": "❓"})

    sorted_codes = sorted(country_codes.items(), key=lambda item: len(item[0]), reverse=True)
    result = {"status": "error", "message": "알 수 없는 오류", "flag": "❌"}

    try:
        with sync_playwright() as p:
            current_os = platform.system()
            browser = None

            launch_options = {
                "headless": is_headless,
                "args": ["--disable-blink-features=AutomationControlled"]
            }

            try:
                if current_os == "Windows":
                    browser = p.chromium.launch(channel="msedge", **launch_options)
                elif current_os == "Darwin":
                    browser = p.chromium.launch(channel="chrome", **launch_options)
                else:
                    browser = p.firefox.launch(channel="firefox", **launch_options)
            except Exception:
                pass 

            if not browser:
                try:
                    browser = p.chromium.launch(**launch_options)
                except Exception:
                    return jsonify({
                        "status": "needs_install", 
                        "message": "사용 가능한 브라우저가 없습니다. 아래 버튼을 눌러 전용 엔진을 설치하세요.", 
                        "flag": "⚙️"
                    })

            # 사람처럼 보이기 위한 브라우저 컨텍스트(환경) 세팅
            context = browser.new_context(
                # User-Agent 위장 (Headless 글자 제거)
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                locale="ko-KR", # 무조건 한국어 페이지가 뜨도록 강제
                viewport={"width": 1280, "height": 720} # 모바일로 인식되지 않게 해상도 고정
            )

            # 위장된 context에서 페이지를 생성
            page = context.new_page()
            page.goto("https://www.instagram.com/accounts/password/reset/")
            
            # 사용자명 입력 필드 대기 및 입력
            try:
                page.wait_for_selector("#_r_4_", timeout=10000)
                page.fill("#_r_4_", account)
                page.press("#_r_4_", "Enter")
            except Exception:
                # 선택자가 변경되었을 경우를 대비한 보조 로직
                page.keyboard.type(account)
                page.keyboard.press("Enter")

            # 캡차 또는 결과 페이지 대기
            if visible_mode:
                try:
                    # 결과 페이지의 특징적인 텍스트가 나타날 때까지 대기
                    page.wait_for_function(
                        """() => {
                            const text = document.body.innerText;
                            const lowerText = text.toLowerCase();
                            
                            // 1. 성공 지표 (전송 옵션 또는 완료 메시지)
                            const isSuccess = lowerText.includes('sms') || lowerText.includes('email') || 
                                             text.includes('SMS') || text.includes('이메일') || text.includes('전송');
                            
                            // 2. 실제 데이터 패턴 (+82 또는 @ 가 포함되어야 함)
                            const hasData = text.includes('+') || text.includes('@');
                            
                            // 3. 오류 지표
                            const isError = lowerText.includes('no account found') || text.includes('찾을 수 없음');

                            return (isSuccess && hasData) || isError;
                        }""",
                        timeout=1800000 # 3분
                    )
                    # 데이터가 렌더링될 약간의 추가 시간
                    page.wait_for_timeout(1500)
                except Exception:
                    pass
            else:
                # 헤드리스 모드에서 네트워크 유휴 상태 대기
                try:
                    page.wait_for_load_state("networkidle", timeout=15000)
                except Exception:
                    pass

            # 화면 데이터 추출 (더 강력한 TreeWalker 방식 사용)
            extracted_texts = page.evaluate("""() => {
                const results = [];
                const walk = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, null, false);
                let node;
                while(node = walk.nextNode()) {
                    const text = node.textContent.trim();
                    if (text && text.length > 1) results.push(text);
                }
                // 입력 필드의 값(가려진 이메일 등)도 추가 추출
                document.querySelectorAll('input, label, button').forEach(el => {
                    if (el.innerText) results.push(el.innerText.trim());
                    if (el.value) results.push(el.value.trim());
                });
                return results;
            }""")
            page_text = " ".join(extracted_texts)
            
            # 브라우저 종료 전 주요 상태 확인
            is_no_account = any(kw in page_text.lower() for kw in ["no account found", "사용자를 찾을 수 없습니다", "계정을 찾을 수 없습니다", "no users found", "account not found", "사용자 이름을 확인하고"])
            is_captcha = "confirm it's you" in page_text.lower() or "본인 확인이 필요합니다" in page_text or "로봇이 아닙니다" in page_text or page.locator("iframe[title*='reCAPTCHA']").count() > 0 or page.locator("iframe[src*='captcha']").count() > 0

            browser.close()
            
            if is_no_account:
                return jsonify({"status": "error", "message": "존재하지 않는 사용자명입니다.", "flag": "❓"})

            if is_captcha and not visible_mode:
                return jsonify({
                    "status": "captcha_detected", 
                    "message": "캡차가 감지되었습니다. 잠시 후 창이 열리면 직접 해결해주세요.", 
                    "flag": "🤖"
                })

            number_founded = False
            Email_founded = False
            country_founded = False

            # 추출해둔 텍스트 데이터를 기반으로 분석 시작
            for text_data in extracted_texts:
                # 이메일 감지
                if "@" in text_data and ("." in text_data or "*" in text_data):
                    Email_founded = True

                # SMS 옵션 및 전송 완료 감지
                is_SMS_option = "Get link via SMS" in text_data or "SMS로 링크 받기" in text_data
                is_SMS_sent = any(kw in text_data for kw in ["SMS sent", "we sent an SMS", "SMS가 전송", "SMS 전송됨", "전송 완료"])

                if is_SMS_option or is_SMS_sent:
                    number_founded = True
                    for code, (country, flag) in sorted_codes:
                        if code in text_data:
                            result = {"status": "success", "message": f"해당 계정은 {country} 번호로 가입되어 있습니다.", "flag": flag}
                            country_founded = True
                            break
                    if country_founded: break
            
            # 최종 판별 로직
            if number_founded and country_founded:
                return jsonify(result)
            elif number_founded and not country_founded:
                return jsonify({"status": "warning", "message": "전화번호는 등록되어 있으나 국가 코드를 식별할 수 없습니다.", "flag": "🗺️"})
            elif Email_founded:
                # 이메일만 있는 경우: 국가 알 수 없음 + 가계정 경고
                return jsonify({
                    "status": "fake_account", 
                    "message": "⚠️ 이메일로만 가입된 계정입니다. 국가는 식별이 불가능하며, 가짜 계정일 확률이 매우 높습니다.", 
                    "flag": "🚫"
                })
            else:
                return jsonify({"status": "error", "message": "정보를 불러오는 데 실패했습니다. 잠시 후 다시 시도해주세요.", "flag": "📱"})

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