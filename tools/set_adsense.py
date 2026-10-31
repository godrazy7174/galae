# -*- coding: utf-8 -*-
"""갈래 광고 켜기/끄기.

사용법
  python3 tools/set_adsense.py ca-pub-1234567890123456                       # 게시자 ID만 (광고 단위 없이)
  python3 tools/set_adsense.py ca-pub-1234567890123456 hub=111 result=222 xresult=333
  python3 tools/set_adsense.py off                                           # 광고 코드 모두 빼기

index.html 맨 위의 window.GALAE_ADS 한 줄만 바꾼다. ads.txt는 루트 사이트(godrazy7174.github.io 저장소)에 있다.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLACES = ("hub", "result", "xresult")
LINE = re.compile(r"window\.GALAE_ADS = \{.*?\};")


def main(argv):
    if not argv:
        print(__doc__)
        return 1
    client, slots = "", {k: "" for k in PLACES}
    if argv[0] != "off":
        client = argv[0].strip()
        if not re.fullmatch(r"ca-pub-\d{10,20}", client):
            print("게시자 ID는 ca-pub- 뒤에 숫자가 오는 형식이에요:", client)
            return 1
        for kv in argv[1:]:
            k, _, v = kv.partition("=")
            if k not in PLACES or not re.fullmatch(r"\d{6,20}", v):
                print("광고 단위는 hub=숫자, result=숫자, xresult=숫자 형식이에요:", kv)
                return 1
            slots[k] = v
    path = os.path.join(ROOT, "index.html")
    s = open(path, encoding="utf-8").read()
    if len(LINE.findall(s)) != 1:
        print("index.html에서 window.GALAE_ADS 줄을 찾지 못했어요.")
        return 1
    js_slots = ", ".join(f"{k}: {json.dumps(slots[k])}" for k in PLACES).replace('"', "'")
    s = LINE.sub(lambda m: f"window.GALAE_ADS = {{ client: '{client}', slots: {{ {js_slots} }} }};", s)
    open(path, "w", encoding="utf-8").write(s)
    print("광고 끔" if not client else f"광고 켬: {client} / 광고 단위: " + ", ".join(f"{k}={v or '-'}" for k, v in slots.items()))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
