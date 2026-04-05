import tkinter as tk
from tkinter import ttk
import threading
from playwright.sync_api import sync_playwright

# 전 세계 국가 코드 딕셔너리
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

class RegionCheckerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Instagram Region Checker")
        # 창 크기 약 2.5배 확대
        self.root.geometry("800x550")
        self.root.resizable(False, False)
        
        style = ttk.Style()
        if "clam" in style.theme_names():
            style.theme_use("clam")

        self.setup_ui()

    def setup_ui(self):
        # 모든 요소를 창의 정중앙에 배치하기 위한 메인 프레임 설정
        main_frame = ttk.Frame(self.root)
        main_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # 1. 메인 타이틀 (중앙 정렬)
        ttk.Label(main_frame, text="확인하려는 Instagram 계정의 사용자명을 입력하세요", 
                  font=("Helvetica", 16, "bold"), justify="center").pack(pady=(0, 25))

        # 2. 입력창 (텍스트 중앙 정렬 justify="center", 글씨 크기 확대)
        self.account_entry = ttk.Entry(main_frame, font=("Helvetica", 18), width=25, justify="center")
        self.account_entry.pack(pady=(0, 20), ipady=8)
        self.account_entry.bind("<Return>", lambda event: self.start_check())

        # 3. 실행 버튼 (가로 길이 맞춰서 확장)
        self.check_btn = ttk.Button(main_frame, text="국가 확인하기", command=self.start_check)
        self.check_btn.pack(fill=tk.X, ipady=10)

        # 4. 국기 표시 라벨 (초대형 폰트 사이즈)
        self.flag_var = tk.StringVar()
        self.flag_var.set("🌍") # 기본 대기 아이콘
        self.flag_label = ttk.Label(main_frame, textvariable=self.flag_var, font=("Helvetica", 90), justify="center")
        self.flag_label.pack(pady=(30, 15))

        # 5. 결과 및 상태 출력 라벨 (글씨 크기 확대 및 중앙 정렬)
        self.status_var = tk.StringVar()
        self.status_var.set("주의: 같은 IP로 단시간에 여러 번 시도 시 차단될 수 있습니다.")
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var, 
                                      font=("Helvetica", 14), foreground="#777777", justify="center")
        self.status_label.pack()

    def update_status(self, message, color="#333333", icon=None):
        # 상태 메시지, 색상, 그리고 국기(또는 상태 아이콘)를 한 번에 업데이트
        self.root.after(0, lambda: self.status_var.set(message))
        self.root.after(0, lambda: self.status_label.config(foreground=color))
        if icon:
            self.root.after(0, lambda: self.flag_var.set(icon))

    def reset_button(self):
        self.root.after(0, lambda: self.check_btn.config(state=tk.NORMAL, text="국가 확인하기"))

    def start_check(self):
        account = self.account_entry.get().strip()
        if not account:
            self.update_status("⚠️ 사용자명을 다시 확인해주세요.", "#d9534f", "❓")
            return

        self.check_btn.config(state=tk.DISABLED, text="확인 중...")
        self.update_status(f"⏳ '{account}' 계정 정보 확인 중...", "#0275d8", "🔍")

        sorted_codes = sorted(country_codes.items(), key=lambda item: len(item[0]), reverse=True)
        thread = threading.Thread(target=self.run_automation, args=(account, sorted_codes), daemon=True)
        thread.start()

    def run_automation(self, account, codes):
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()

                number_founded = False
                country_founded = False

                try:
                    page.goto("https://www.instagram.com/accounts/password/reset/")
                    page.fill("#_r_4_", account)
                    page.press("#_r_4_", "Enter")

                    page.wait_for_load_state("networkidle")

                    elements = page.locator("body *").all()
                    
                    for element in elements:
                        text_data = element.text_content()

                        if not text_data or not text_data.strip():
                            continue
                        
                        text_data = text_data.strip()

                        if "Get link via SMS" in text_data:
                            number_founded = True

                            for code, (country, flag) in codes:
                                if code in text_data:
                                    country_founded = True
                                    self.update_status(f"성공: {country} 번호로 가입되어 있습니다.", "#5cb85c", flag)
                                    break
                            break
                            
                except Exception as e:
                    self.update_status(f"과정 중 오류 발생: {e}", "#d9534f", "❌")

                finally:
                    if not number_founded: 
                        self.update_status("전화번호를 찾지 못했습니다.", "#d9534f", "📱")
                    elif not country_founded: 
                        self.update_status("국가코드를 찾지 못했거나 알 수 없는 국가입니다.", "#f0ad4e", "🗺️")
                    browser.close()

        except Exception as e:
            self.update_status(f"브라우저 실행 오류: {e}", "#d9534f", "🚨")
        
        finally:
            self.reset_button()

if __name__ == "__main__":
    root = tk.Tk()
    app = RegionCheckerApp(root)
    root.mainloop()