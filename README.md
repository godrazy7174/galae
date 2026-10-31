# 갈래 · 밸런스 게임

둘 중 하나만 고르는 밸런스 게임이에요. 9개 주제 540문제를 풀면 내 선택이 지하철 노선도로 그려져요.

바로 하기: https://godrazy7174.github.io/galae/

## 광고 켜기 (Google AdSense)

- 애드센스 사이트 주소: `godrazy7174.github.io` (뭐나와와 하나로 등록, ads.txt는 그 저장소에 있음)
- 켜기: `python3 tools/set_adsense.py ca-pub-… hub=광고단위ID result=광고단위ID xresult=광고단위ID`
  (또는 `index.html` 맨 위 `window.GALAE_ADS` 한 줄에 직접 입력, 끄기는 `off`)
- 광고 자리: 처음 화면 노선도 아래, 라운드 결과 아래, 급행 결과 아래. 문제 푸는 화면에는 넣지 않음
- 자동 광고는 문제 화면에도 끼어들 수 있으니 애드센스의 페이지 제외에 `/galae/` 아래 전체를 넣고 위 광고 단위만 쓰는 걸 권장
- 미리보기 이미지 다시 그리기: `python3 tools/make_og.py`
