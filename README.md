# 논문읽기 도우미

딥러닝 필독 논문 10편을 하루 한 단락씩 원문으로 읽는 앱입니다.
`index.html` 하나만 브라우저로 열면 서버 없이 동작하고, 진행률은 브라우저에 저장됩니다.

## 쓰는 법

`index.html`을 더블클릭하면 끝입니다. 폰에서 보려면 이 파일 하나만 옮기면 됩니다.

각 단락은 **구조 → 핵심 개념 → 요약 → 원문** 순서로 놓여 있습니다.
앞의 셋을 먼저 읽고 원문에 들어가면, 모르는 문장을 만나도 맥락으로 버틸 수 있습니다.
원문의 **문장을 누르면 한국어 해석과 구문 포인트**가 열립니다. 먼저 스스로 읽고 나서 확인하세요.

- **오늘** — 오늘 읽을 단락 하나. 다 읽으면 목표 달성으로 표시되고, 더 읽고 싶으면 이어서 갈 수 있습니다.
- **용어** — RNN, CNN, 파라미터, 기울기 같은 기초 AI 용어 28개를 중학생도 이해할 수 있게 비유로 설명한 사전입니다. 핵심 개념 카드에 뜬 **📘 왕초보** 버튼을 누르면 그 자리에서 바로 펼쳐볼 수도 있습니다.
- **논문** — 10편의 목록과 논문별 진행률. 누르면 그 논문의 다음 단락으로 갑니다.
- **기록** — 연속 일수, 최근 20주 히트맵, 최근 읽은 단락.
- **설정** — 우측 상단 ⚙️ 아이콘. 테마·글자 크기, 해석 자동 펼치기, 백업·복원, 초기화(논문 하나만 / 읽기 기록 전체 / 단어장만 / 완전 초기화)를 관리합니다.
- **단어장** — 읽은 단락의 핵심 개념이 자동으로 쌓입니다. 플래시카드로 복습하며, 아는 카드는 1일 → 3일 → 7일 → 14일로 간격이 늘어납니다.

진행률과 단어장은 그 브라우저에만 저장됩니다. 다른 기기로 옮기려면 기록 탭에서 내보내기 한 JSON을 붙여넣고 가져오기를 누르세요.

## 수록 논문 — 읽는 순서

시간순이되, 관련 있는 논문끼리는 붙여 두었습니다. Bahdanau는 Transformer 바로 앞에,
Batch Norm은 Dropout·Adam 옆에, ViT·Diffusion·InstructGPT는 GPT-3 뒤에 이어집니다.

| # | 논문 | 연도 | 단락 | 왜 이 순서인가 |
|---|------|------|------|----------------|
| 1 | Long Short-Term Memory | 1997 | 10 | 시퀀스를 다루는 가장 오래된 발상부터 |
| 2 | ImageNet Classification (AlexNet) | 2012 | 10 | 딥러닝 시대의 시작점 |
| 3 | Playing Atari with Deep RL (DQN) | 2013 | 11 | 강화학습에 신경망을 붙인 사례 |
| 4 | Neural MT by Jointly Learning to Align and Translate (Bahdanau) | 2014 | 10 | attention의 원조. Transformer가 답하는 질문을 먼저 던진 논문 |
| 5 | Generative Adversarial Nets | 2014 | 8 | 생성 모델의 첫 계보 |
| 6 | Dropout | 2014 | 11 | 과적합을 막는 첫 번째 정규화 기법 |
| 7 | Adam | 2015 | 11 | 지금도 쓰는 표준 옵티마이저 |
| 8 | Batch Normalization | 2015 | 10 | Dropout과 짝을 이루는 또 다른 정규화 기법 |
| 9 | Deep Residual Learning (ResNet) | 2016 | 11 | 100층 넘게 쌓을 수 있게 만든 전환점 |
| 10 | Attention Is All You Need | 2017 | 14 | RNN·CNN을 걷어내고 attention만 남긴 전환점 |
| 11 | BERT | 2019 | 13 | 사전학습·미세조정 표준을 확립 |
| 12 | Language Models are Few-Shot Learners (GPT-3) | 2020 | 11 | 규모를 극단까지 키운 결과 |
| 13 | An Image is Worth 16x16 Words (ViT) | 2020 | 10 | Transformer가 컴퓨터 비전까지 정복 |
| 14 | Denoising Diffusion Probabilistic Models | 2020 | 10 | GAN을 잇는 지금의 이미지 생성 주류 |
| 15 | Training LMs to Follow Instructions (InstructGPT) | 2022 | 10 | GPT-3가 ChatGPT로 바뀌는 지점 |

원문은 각 논문의 공개 PDF에서 그대로 추출한 것이며, 초록·서론·핵심 방법론·결론을 골랐습니다.
실험 세부와 부록은 제외했습니다. 총 160단락 839문장입니다.
1997년 LSTM 논문은 비트맵 폰트 PDF라 OCR로 복구했습니다 (아래 "옛날 PDF" 항목 참고).

## 고칠 때

`index.html`은 빌드 산출물이라 직접 고치지 마세요. 다음 두 곳을 고치고 다시 빌드합니다.

- `template.html` — 화면과 동작
- `data/<논문id>.json` — 해석, 구조, 핵심 개념, 요약

```bash
python3 build.py
```

빌드는 `data/*.json`과 `data/raw/*.json`을 합쳐 `index.html`과 `papers.json`을 만듭니다.
필드가 빠졌거나 영어 문장 수와 해석 개수가 어긋나면 어디가 잘못됐는지 알려주고 멈춥니다.

검증만 하려면:

```bash
python3 build.py --check
```

## 논문 추가하기

1. PDF를 `data/pdf/<id>.pdf`에 넣습니다.
2. 원문을 단락 단위로 뽑습니다.

```bash
.venv/bin/python extract_pdf.py --all
```

`data/raw/<id>.txt`에 단락 번호(`p001`, `p002` …)가 매겨진 원문이 나옵니다. 여기서 읽힐 단락을 고릅니다.

3. 고른 단락이 어떻게 문장으로 쪼개지는지 확인합니다.

```bash
python3 build.py --split <id> p008 p009
```

4. `data/<id>.json`을 만들고 문장마다 해석을 답니다. 형식은 기존 파일을 그대로 따르면 됩니다.

각 단락(section)은 원문을 두 방식 중 하나로 지정합니다.

- `"src": "p008"` + `"sentences_ko"` — 원문 영어는 `data/raw`에서 가져오고 해석만 순서대로 붙입니다. 문장 수가 맞지 않으면 빌드가 분리 결과를 보여주며 멈춥니다.
- `"sentences"` — 영어까지 직접 적습니다. 원문 추출이 어려운 곳에 씁니다.

PDF 추출이 지저분한 곳을 다듬는 보조 필드도 있습니다.

- `"from"` / `"to"` — 문장 앞부분 문자열로 앞뒤를 잘라냅니다.
- `"drop": [3, 5]` — 수식이나 각주만 남은 문장을 뺍니다.
- `"fix": {"2": "올바른 문장"}` — 깨진 문장을 교체합니다. 값에 배열을 주면 한 문장을 여러 개로 쪼갭니다.

`"order"`가 논문 목록의 순서를 정합니다.

### 옛날 PDF라 글자가 깨질 때

1997년 LSTM 논문처럼 비트맵 폰트로 만들어진 PDF는 글자가 통째로 깨져 나옵니다.
그럴 때는 macOS 내장 OCR로 읽습니다.

```bash
.venv/bin/python ocr_pdf.py data/pdf/lstm.pdf --id lstm --pages 1-12
```

산출물은 `extract_pdf.py`와 같은 형식이라 이후 과정은 동일합니다. 다만 수식은 여전히 깨지므로,
수식이 많은 문장은 `drop`으로 빼거나 `sentences`로 직접 적는 편이 낫습니다.

## 개발 환경

PDF 처리에만 파이썬 패키지가 필요합니다. 빌드 자체는 표준 라이브러리만 씁니다.

```bash
python3 -m venv .venv
.venv/bin/pip install pymupdf pyobjc-framework-Vision pyobjc-framework-Quartz
```

## 파일

```
index.html        완성본. 이것만 열면 됩니다 (빌드 산출물)
template.html     화면과 동작
data/<id>.json    논문별 해석·구조·개념·요약
data/raw/<id>.*   PDF에서 뽑은 원문 (빌드 입력)
data/pdf/<id>.pdf 원본 논문
build.py          빌드와 검증
extract_pdf.py    PDF → 단락 추출
ocr_pdf.py        옛 PDF용 OCR 추출
papers.json       병합된 전체 데이터 (참고용)
archive/          이전 Streamlit 버전
IDEA.md           최초 기획 메모
```
