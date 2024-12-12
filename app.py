import requests
import re
import random
import string
import base64
import urllib.parse
import json
import time
import os
import sys
from requests_toolbelt import MultipartEncoder
from rich import print as printf
from PIL import Image
import pytesseract
from rich.panel import Panel
from rich.console import Console
from requests.exceptions import RequestException

try:
    import requests, re, random, string, base64, urllib.parse, json, time, os, sys
    from requests_toolbelt import MultipartEncoder
    from rich import print as printf
    from PIL import Image
    import pytesseract
    from rich.panel import Panel
    from rich.console import Console
    from requests.exceptions import RequestException
except (ModuleNotFoundError) as e:
    __import__('sys').exit(f"Error: {str(e).capitalize()}!")

COOKIES, SUCCESS, LOGOUT, FAILED = {
    "Cookie": None
}, [], [], []

class REQUIRED:

    def __init__(self) -> None:
        pass

    def LOGIN(self):
        with requests.Session() as session:
            session.headers.update(
                {
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Host': 'zefoy.com',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                    'Sec-Fetch-User': '?1',
                    'Sec-Fetch-Dest': 'document'
                }
            )
            response = session.get('https://zefoy.com/').text
            if 'Sorry, you have been blocked' in str(response) or 'Just a moment...' in str(response):
                printf(Panel(f"[bold red]Zefoy server is currently affected by cloudflare, you can try again until cloudflare\nis gone, please visit[bold green] zefoy.com[bold red] to check it!", width=56, style="bold bright_white", title="[bold bright_white][ Cloudflare ]"))
                sys.exit()
            else:
                self.captcha_image = re.search(r'src="(.*?)" onerror="errimg$$$$"', str(response)).group(1).replace('amp;', '')
                self.form = re.search(r'type="text" name="(.*?)"', str(response)).group(1)
                session.headers.update(
                    {
                        'Cookie': "; ".join([str(x) + "=" + str(y) for x, y in session.cookies.get_dict().items()]),
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7'
                    }
                )
                response2 = session.get('https://zefoy.com{}'.format(self.captcha_image))

                with open('Storage/Image.png', 'wb') as w:
                    w.write(response2.content)
                w.close()
                session.headers.update(
                    {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'Connection': 'keep-alive',
                        'Origin': 'null',
                        'Cache-Control': 'max-age=0',
                        'Cookie': "; ".join([str(x) + "=" + str(y) for x, y in session.cookies.get_dict().items()])
                    }
                )
                data = {
                    self.form: self.BYPASS_CAPTCHA(),
                }
                response3 = session.post('https://zefoy.com/', data = data).text

                if 'placeholder="Enter Video URL"' in str(response3):
                    COOKIES.update(
                        {
                            "Cookie": "; ".join([str(x)+"="+str(y) for x,y in session.cookies.get_dict().items()])
                        }
                    )
                    printf(f"[bold bright_white]   ──>[bold green] LOGIN SUCCESSFUL!                ", end='\r')
                    time.sleep(2.5)
                    return (COOKIES['Cookie'])
                else:
                    printf(f"[bold bright_white]   ──>[bold red] LOGIN FAILED!                     ", end='\r')
                    time.sleep(2.5)
                    return (False)

    def BYPASS_CAPTCHA(self):
        self.image_file = ('Storage/Image.png')
        self.image = Image.open(self.image_file)
        self.image_string = pytesseract.image_to_string(self.image)
        return (self.image_string.replace('\n', ''))
    
    def GET_FORM(self, video_url):
        with requests.Session() as session:
            session.headers.update(
                {
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                    'Host': 'zefoy.com',
                    'Cookie': f'{COOKIES["Cookie"]}; window_size=1280x551; user_agent=Mozilla%2F5.0%20(Windows%20NT%2010.0%3B%20Win64%3B%20x64)%20AppleWebKit%2F537.36%20(KHTML%2C%20like%20Gecko)%20Chrome%2F131.0.0.0%20Safari%2F537.36; language=en-US; languages=en-US; cf-locale=en-US;',
                    'Sec-Fetch-Site': 'none',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-User': '?1',
                    'Sec-Fetch-Dest': 'document',
                }
            )
            try:
                response = session.get('https://zefoy.com/')
                response.raise_for_status()  # Raise an exception for bad status codes
                response_text = response.text

                if 'placeholder="Enter Video URL"' in response_text:
                    video_form_match = re.search(r'name="(.*?)" placeholder="Enter Video URL"', response_text)
                    post_actions = re.findall(r'action="(.*?)">', response_text)

                    if video_form_match and len(post_actions) > 3:
                        self.video_form = video_form_match.group(1)
                        self.post_action = post_actions[3]
                        printf(f"[bold bright_white]   ──>[bold green] SUCCESSFULLY FOUND VIDEO FORM!   ", end='\r')
                        time.sleep(1.5)
                        return self.SEND_VIEWS(self.video_form, self.post_action, video_url)
                    else:
                        raise ValueError("Failed to extract video form or post action")
                else:
                    raise ValueError("Video form placeholder not found in response")

            except requests.RequestException as e:
                printf(f"[bold bright_white]   ──>[bold red] NETWORK ERROR: {str(e)}        ", end='\r')
            except ValueError as e:
                printf(f"[bold bright_white]   ──>[bold red] PARSING ERROR: {str(e)}        ", end='\r')
            except Exception as e:
                printf(f"[bold bright_white]   ──>[bold red] UNEXPECTED ERROR: {str(e)}        ", end='\r')

            time.sleep(3.5)
            COOKIES.update({"Cookie": None})
            return False
    
    def SEND_VIEWS(self, video_form, post_action, video_url):
        global SUCCESS, FAILED
        with requests.Session() as session:
            boundary = '----WebKitFormBoundary' \
                + ''.join(random.sample(string.ascii_letters + string.digits, 16))
            session.headers.update(
                {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                    'Cookie': f'{COOKIES["Cookie"]}; {self.BYPASS_GOOGLE_ADS()}; window_size=1280x551; user_agent=Mozilla%2F5.0%20(Windows%20NT%2010.0%3B%20Win64%3B%20x64)%20AppleWebKit%2F537.36%20(KHTML%2C%20like%20Gecko)%20Chrome%2F131.0.0.0%20Safari%2F537.36; language=en-US; languages=en-US; time_zone=Asia/Jakarta; cf-locale=en-US;',
                    'Sec-Fetch-Mode': 'cors',
                    'Sec-Fetch-Site': 'same-origin',
                    'Connection': 'keep-alive',
                    'Origin': 'https://zefoy.com',
                    'Sec-Fetch-Dest': 'empty',
                    'Content-Type': 'multipart/form-data; boundary={}'.format(boundary),
                    'Accept': '*/*'
                }
            )

            data = MultipartEncoder(
                {
                    video_form: (None, video_url)
                }, boundary=boundary
            )

            response = session.post('https://zefoy.com/{}'.format(post_action), data = data).text
            self.base64_string = self.DECRYPTION_BASE64(response)

            if 'type="submit"' in str(self.base64_string):
                boundary = '----WebKitFormBoundary' \
                    + ''.join(random.sample(string.ascii_letters + string.digits, 16))
                session.headers.update(
                    {
                        'Content-Type': 'multipart/form-data; boundary={}'.format(boundary),
                    }
                )
                self.find_form_video = re.findall(r'type="hidden" name="(.*?)" value="(.*?)"', str(self.base64_string))
                if len(self.find_form_video) >= 2:
                    self.form_videolink, self.videolink = self.find_form_video[1][0], self.find_form_video[1][1]
                    self.form_videoid, self.videoid = self.find_form_video[0][0], self.find_form_video[0][1]
                else:
                    printf(f"[bold bright_white]   ──>[bold red] UNABLE TO FIND REQUIRED FORM FIELDS!     ", end='\r')
                    time.sleep(3.5)
                    return (False)
                self.next_post_action = re.search(r'action="(.*?)"', str(self.base64_string)).group(1)
                data = MultipartEncoder(
                    {
                        self.form_videoid: (None, self.videoid),
                        self.form_videolink: (None, self.videolink)
                    }, boundary=boundary
                )

                response2 = session.post('https://zefoy.com/{}'.format(self.next_post_action), data = data).text
                self.base64_string2 = self.DECRYPTION_BASE64(response2)

                if 'Successfully 1000 views sent.' in str(self.base64_string2):
                    SUCCESS.append(f"{self.base64_string2}")
                    printf(Panel(f"""[bold white]Status :[bold green] Successfully...
[bold white]Link :[bold red] {video_url}
[bold white]Views :[bold yellow] +1000""", width=56, style="bold bright_white", title="[bold bright_white][ Success ]"))
                    printf(f"[bold bright_white]   ──>[bold green] TRY SENDING VIEWS AGAIN!           ", end='\r')
                    time.sleep(2.5)
                    self.SEND_VIEWS(video_form, post_action, video_url)
                elif 'Successfully ' in str(self.base64_string2) and ' views sent.' in str(self.base64_string2):
                    self.views_sent = re.search(r'Successfully (.*?) views sent.', str(self.base64_string2)).group(1)
                    SUCCESS.append(f"{self.base64_string2}")
                    printf(Panel(f"""[bold white]Status :[bold yellow] Successfully...
[bold white]Link :[bold red] {video_url}
[bold white]Views :[bold green] +{self.views_sent}""", width=56, style="bold bright_white", title="[bold bright_white][ Success ]"))
                    printf(f"[bold bright_white]   ──>[bold green] TRY SENDING VIEWS AGAIN!           ", end='\r')
                    time.sleep(2.5)
                    self.SEND_VIEWS(video_form, post_action, video_url)
                else:
                    FAILED.append(f"{self.base64_string2}")
                    printf(f"[bold bright_white]   ──>[bold red] FAILED TO SEND VIEWS!           ", end='\r')
                    time.sleep(3.5)
                    COOKIES.update(
                        {
                            "Cookie": None
                        }
                    )
                    return (False)
            elif 'Checking Timer...' in str(self.base64_string):
                printf(f"[bold bright_white]   ──>[bold green] WAIT FOR 4 MINUTES!          ", end='\r')
                time.sleep(2.5)

                list(map(lambda _: (self.DELAY(0, 30), self.ANTI_LOGOUT()), range(8)))

                printf(f"[bold bright_white]   ──>[bold green] TRY SENDING VIEWS AGAIN!           ", end='\r')
                time.sleep(2.5)
                self.SEND_VIEWS(video_form, post_action, video_url)
            elif 'Please try again later or' in str(self.base64_string):
                printf(f"[bold bright_white]   ──>[bold red] PLEASE TRY AGAIN IN A FEW MOMENTS!     ", end='\r')
                time.sleep(2.5)
                self.DELAY(0, 300)
                return (False)
            elif 'Please try again later. Server too busy.' in str(self.base64_string):
                printf(Panel(f"[bold red]Zefoy server is busy, you can try again in a few days, please check regularly on zefoy.com!", width=56, style="bold bright_white", title="[bold bright_white][ Server Busy ]"))
                sys.exit()
            elif 'An error occurred. Please try again.' in str(self.base64_string):
                printf(f"[bold bright_white]   ──>[bold red] AN ERROR OCCURRED, PLEASE TRY AGAIN IN A FEW MOMENTS!", end='\r')
                time.sleep(2.5)
                self.DELAY(0, 120)
                return (False)
            elif 'Too many requests. Please slow down.' in str(self.base64_string):
                printf(f"[bold bright_white]   ──>[bold red] SUBJECT TO SPAM OR LIMIT!           ", end='\r')
                time.sleep(2.5)
                self.DELAY(0,500)
                return (False)
            elif 'Please wait ' in str(self.base64_string) and ' seconds before trying again.' in str(self.base64_string):
                self.wait_time = re.search(r'Please wait (.*?) seconds before trying again.', str(self.base64_string)).group(1)
                printf(f"[bold bright_white]   ──>[bold red] PLEASE WAIT {self.wait_time} SECONDS BEFORE TRYING AGAIN!     ", end='\r')
                time.sleep(2.5)

                self.DELAY(0, int(self.wait_time))

                printf(f"[bold bright_white]   ──>[bold green] TRY SENDING VIEWS AGAIN!           ", end='\r')
                time.sleep(2.5)
                self.SEND_VIEWS(video_form, post_action, video_url)
            else: # YOU CAN DEBUGGING IF THIS ERROR HAPPENS!
                printf(f"[bold bright_white]   ──>[bold red] FAILED TO GET VIEWS FORM!     ", end='\r')
                time.sleep(3.5)
                COOKIES.update(
                    {
                        "Cookie": None
                    }
                )
                return (False)

    def ANTI_LOGOUT(self):
        with requests.Session() as session:
            session.headers.update(
                {
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Cookie': COOKIES["Cookie"],
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                    'Host': 'zefoy.com',
                    'Sec-Fetch-Site': 'none',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-User': '?1',
                    'Sec-Fetch-Dest': 'document',
                }
            )
            response = session.get('https://zefoy.com/').text
            return (True)

    def DECRYPTION_BASE64(self, base64_code):
        return base64.b64decode(urllib.parse.unquote(base64_code[::-1])).decode()
    
    def DELAY(self, minutes, seconds):
        self.total = (minutes * 60 + seconds)
        while (self.total):
            minutes, seconds = divmod(self.total, 60)
            printf(f"[bold bright_white]   ──>[bold white] WAIT[bold green] {minutes:02d}:{seconds:02d}[bold white] SUCCESS:-[bold green]{len(SUCCESS)}[bold white] FAILED:-[bold red]{len(FAILED)}              ", end='\r')
            time.sleep(1)
            self.total -= 1
        return ("0_0")

    def BYPASS_GOOGLE_ADS(self):
        with requests.Session() as session:
            session.headers.update(
                {
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Cookie': COOKIES["Cookie"],
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                    'Host': 'zefoy.com',
                    'Sec-Fetch-Site': 'none',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-User': '?1',
                    'Sec-Fetch-Dest': 'document',
                }
            )
            params = {
                'domain': 'zefoy.com',
                'callback': '_gfp_s_',
                'client': 'ca-pub-3192305768699763',
            }
            response = session.get('https://partner.googleadservices.com/gampad/cookie.js', params=params).text
            if '_gfp_s_' in str(response):
                self.json_cookies = json.loads(re.search(r'_gfp_s_$$(.*?)$$;', str(response)).group(1))
                return (f"_gads={self.json_cookies['_cookies_'][0]['_value_']}; __gpi={self.json_cookies['_cookies_'][1]['_value_']}")
            else:
                return ('_gads=; __gpi=;')

class MAIN:

    def __init__(self):
        try:
            self.DISPLAY_LOGO()
            printf(Panel(f"[bold white]Please enter your TikTok video link. Make sure the account is not private and the\nlink is correct. Get the video link via browser!", width=56, style="bold bright_white", title="[bold bright_white][ Video Link ]", subtitle="[bold bright_white]╭─────", subtitle_align="left"))
            video_url = Console().input("[bold bright_white]   ╰─> ")
            if 'tiktok.com' in str(video_url) or '/video/' in str(video_url):
                printf(Panel(f"[bold white]You can use[bold green] CTRL + C[bold white] if stuck and use[bold red] CTRL + Z[bold white] if you want to stop. If views do not come\nin, try running manually and run this program again!", width=56, style="bold bright_white", title="[bold bright_white][ Note ]"))
                while True:
                    try:
                        if COOKIES['Cookie'] is None or len(COOKIES['Cookie']) == 0:
                            if not REQUIRED().LOGIN():
                                raise Exception("Login failed")
                        else:
                            printf(f"[bold bright_white]   ──>[bold green] SENDING VIEWS!     ", end='\r')
                            time.sleep(2.5)
                            if not REQUIRED().GET_FORM(video_url):
                                raise Exception("Failed to get or process video form")
                    except Exception as e:
                        printf(f"[bold bright_white]   ──>[bold red] ERROR: {str(e)}            ", end='\r')
                        time.sleep(7.5)
                        COOKIES['Cookie'] = None  # Reset cookie on error
                        continue
                    except KeyboardInterrupt:
                        printf(f"\r                                 ", end='\r')
                        time.sleep(2.5)
                        break
            else:
                printf(Panel(f"[bold red]Please enter the TikTok video link correctly. Make sure you get the video link from the browser!", width=56, style="bold bright_white", title="[bold bright_white][ Invalid Link ]"))
                sys.exit()
        except Exception as e:
            printf(Panel(f"[bold red]{str(e).capitalize()}!", width=56, style="bold bright_white", title="[bold bright_white][ Error ]"))
            sys.exit()

    def DISPLAY_LOGO(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        printf(
            Panel(r"""[bold red]● [bold yellow]● [bold green]●[bold white]
[bold red] ______     ______     ______   ______     __  __    
[bold red]/\___  \   /\  ___\   /\  ___\ /\  __ \   /\ \_\ \   
[bold red]\/_/  /__  \ \  __\   \ \  __\ \ \ \/\ \  \ \____ \  
[bold white]  /\_____\  \ \_____\  \ \_\    \ \_____\  \/\_____\ 
[bold white]  \/_____/   \/_____/   \/_/     \/_____/   \/_____/
        [underline green]Free TikTok Views - Coded by RYOEVISU""", width=56, style="bold bright_white")
        )
        return True

if __name__ == '__main__':
    try:
        os.system('git pull')
        MAIN()
    except Exception as e:
        printf(Panel(f"[bold red]{str(e).capitalize()}!", width=56, style="bold bright_white", title="[bold bright_white][ Error ]"))
        sys.exit()
    except KeyboardInterrupt:
        sys.exit()

