from flask import Flask, render_template, request, jsonify
from playwright.sync_api import sync_playwright

app = Flask(__name__)

# 전 세계 국가 코드 딕셔너리 (기존과 동일)
country_codes = {
    # 🌏 아시아 / 태평양
    "+82": ("한국", "🇰🇷"), "+81": ("일본", "🇯🇵"), "+86": ("중국", "🇨🇳"),
    "+886": ("대만", "🇹🇼"), "+852": ("홍콩", "🇭🇰"), "+853": ("마카오", "🇲🇴"),
    "+84": ("베트남", "🇻🇳"), "+65": ("싱가포르", "🇸🇬"), "+66": ("태국", "🇹🇭"),
    "+62": ("인도네시아", "🇮🇩"), "+60": ("말레이시아", "🇲🇾"), "+63": ("필리핀", "🇵🇭"),
    "+91": ("인도", "🇮🇳"), "+92": ("파키스탄", "🇵🇰"), "+880": ("방글라데시", "🇧🇩"),
    "+94": ("스리랑카", "🇱🇰"), "+95": ("미얀마", "🇲🇲"), "+976": ("몽골", "🇲🇳"),
    "+977": ("네팔", "🇳🇵"), "+998": ("우즈베키스탄", "🇺🇿"), "+61": ("호주", "🇦🇺"),
    "+64": ("뉴질랜드", "🇳🇿"), "+679": ("피지", "🇫🇯"),

    # 🌎 북미 / 중남미
    "+1": ("미국/캐나다", "🇺🇸/🇨🇦"), "+1876": ("자메이카", "🇯🇲"), "+1787": ("푸에르토리코", "🇵🇷"),
    "+52": ("멕시코", "🇲🇽"), "+55": ("브라질", "🇧🇷"), "+54": ("아르헨티나", "🇦🇷"),
    "+56": ("칠레", "🇨🇱"), "+57": ("콜롬비아", "🇨🇴"), "+51": ("페루", "🇵🇪"),
    "+58": ("베네수엘라", "🇻🇪"), "+598": ("우루과이", "🇺🇾"), "+595": ("파라과이", "🇵🇾"),
    "+593": ("에콰도르", "🇪🇨"), "+591": ("볼리비아", "🇧🇴"), "+502": ("과테말라", "🇬🇹"),
    "+506": ("코스타리카", "🇨🇷"), "+507": ("파나마", "🇵🇦"), "+53": ("쿠바", "🇨🇺"),

    # 🌍 유럽
    "+44": ("영국", "🇬🇧"), "+33": ("프랑스", "🇫🇷"), "+49": ("독일", "🇩🇪"),
    "+39": ("이탈리아", "🇮🇹"), "+34": ("스페인", "🇪🇸"), "+7": ("러시아/카자흐스탄", "🇷🇺/🇰🇿"),
    "+31": ("네덜란드", "🇳🇱"), "+32": ("벨기에", "🇧🇪"), "+41": ("스위스", "🇨🇭"),
    "+43": ("오스트리아", "🇦🇹"), "+46": ("스웨덴", "🇸🇪"), "+47": ("노르웨이", "🇳🇴"),
    "+45": ("덴마크", "🇩🇰"), "+358": ("핀란드", "🇫🇮"), "+48": ("폴란드", "🇵🇱"),
    "+420": ("체코", "🇨🇿"), "+36": ("헝가리", "🇭🇺"), "+30": ("그리스", "🇬🇷"),
    "+351": ("포르투갈", "🇵🇹"), "+353": ("아일랜드", "🇮🇪"), "+380": ("우크라이나", "🇺🇦"),
    "+40": ("루마니아", "🇷🇴"), "+359": ("불가리아", "🇧🇬"),

    # 🐪 중동 / 아프리카
    "+971": ("아랍에미리트", "🇦🇪"), "+966": ("사우디아라비아", "🇸🇦"), "+90": ("튀르키예", "🇹🇷"),
    "+98": ("이란", "🇮🇷"), "+972": ("이스라엘", "🇮🇱"), "+962": ("요르단", "🇯🇴"),
    "+974": ("카타르", "🇶🇦"), "+965": ("쿠웨이트", "🇰🇼"), "+968": ("오만", "🇴🇲"),
    "+973": ("바레인", "🇧🇭"), "+20": ("이집트", "🇪🇬"), "+27": ("남아프리카공화국", "🇿🇦"),
    "+212": ("모로코", "🇲🇦"), "+213": ("알제리", "🇩🇿"), "+216": ("튀니지", "🇹🇳"),
    "+234": ("나이지리아", "🇳🇬"), "+254": ("케냐", "🇰🇪"), "+255": ("탄자니아", "🇹🇿"),
    "+233": ("가나", "🇬🇭"), "+251": ("에티오피아", "🇪🇹"), "+256": ("우간다", "🇺🇬")
}

@app.route('/')
def home():
    # 접속하면 UI가 담긴 HTML 파일을 보여줌
    return render_template('index.html')

@app.route('/check', methods=['POST'])
def check_region():
    # 프론트엔드(웹)에서 보낸 계정 이름을 받음
    data = request.get_json()
    account = data.get('account')
    
    if not account:
        return jsonify({"status": "error", "message": "사용자명을 입력해주세요.", "flag": "❓"})

    sorted_codes = sorted(country_codes.items(), key=lambda item: len(item[0]), reverse=True)
    result = {"status": "error", "message": "알 수 없는 오류", "flag": "❌"}

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
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

                if "Get link via SMS" in text_data:
                    number_founded = True
                    for code, (country, flag) in sorted_codes:
                        if code in text_data:
                            result = {"status": "success", "message": f"해당 계정은 {country} 번호로 가입되어 있습니다.", "flag": flag}
                            country_founded = True
                            break
                    break
            
            if not number_founded:
                result = {"status": "error", "message": "전화번호를 찾지 못했거나 존재하지 않는 계정입니다.", "flag": "📱"}
            elif not country_founded:
                result = {"status": "warning", "message": "국가코드를 찾지 못했거나 알 수 없는 국가입니다.", "flag": "🗺️"}

            browser.close()

    except Exception as e:
        result = {"status": "error", "message": f"오류 발생: {str(e)}", "flag": "🚨"}

    # 결과를 JSON 형태로 웹 브라우저에 응답
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, port=5000)