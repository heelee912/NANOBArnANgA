<img width="375" height="600" alt="image" src="https://github.com/user-attachments/assets/bf8e9cde-0e2f-4810-863a-e65897b2d5ef" /><img width="408" height="656" alt="image" src="https://github.com/user-attachments/assets/05ce5c58-47da-4796-bf48-2549de4ee10c" />

<img width="375" height="600" alt="image" src = https://github.com/user-attachments/assets/1a323c7d-63d7-4450-8274-97b5c57254ca><img img width="408" height="656" alt="image" src = https://github.com/user-attachments/assets/f834a83c-eeb2-4bf5-843e-f394e982fda7>



https://y-y-y-y.tistory.com/ # 이전 프로젝트들과 AIS 사용량 확인 등 주의사항이 있는 곳


설명은 v3으로 되어 있지만 최신 버전 업데이트가 릴리즈에 있으니 참고하세요

https://github.com/heelee912/NANOBArnANgA/releases # 릴리즈 페이지


![Generated Image December 04, 2025 - 1_52AM](https://github.com/user-attachments/assets/bf2dd9da-9f21-4c75-80e5-85ca0b8432f5)
도식화된 all loop 에 대한 전체 플로우


1.



all loop v3 가 주요 모든 자동화로 파일을 만들어주는 코드입니다.



select_best_outputs 는 만들어진 이미지를 평가해서 나름 최고의 한장을 모아주는 녀석입니다.





2.



두 코드 모두 API 키를 넣습니다.

파이썬 파일 내에



API_KEY = " " 



라고 써진 큰따옴표 안 " 여기 " 에 API 키를 그대로 넣습니다.



3.


<img width="564" height="139" alt="image" src="https://github.com/user-attachments/assets/66f8257d-7b27-4eaf-975e-d6c4c7f95ab0" />


manga 폴더 안에 원본 일본어 만화를 넣습니다.



all loop(버전 무관).py 를 실행합니다.



4. 



가장 처음 동작은 script 폴더 안에 스크립트를 생성하는 것입니다. 3 pro 를 통해 manga 폴더 안의 이미지를 보고 AI가 판단하도록 되어 있습니다다. 다만 코드 내의 프롬프트 규칙에 따라서.

<img width="520" height="172" alt="image" src="https://github.com/user-attachments/assets/d1860bde-c432-4f6f-8a3e-ef37d89cbc3e" />

스크립트는 이미지 생성시에 가이드라인으로서 들어갑니다.

<img width="827" height="148" alt="image" src="https://github.com/user-attachments/assets/b6ef7dde-be41-406e-bf46-ccae2039a01a" />

<img width="816" height="243" alt="image" src="https://github.com/user-attachments/assets/08c50bc0-0a54-4d36-ac18-d5dad420869e" />



내용은 이렇게 이미지모델에게 하나하나 글자를 어떻게 써야 하는지 완전히 떠먹여주는 내용입니다.



이 방식이 여러 방법 중에 세로쓰기 방지 효과가 가장 좋았습니다.



스크립트가 만들어진 직후 작업을 종료하고 스크립트를 수동으로 수정하고 (혹은 해당 스크립트로 생성된 이미지를 제거하면) 파이썬을 다시 실행하면,
그 스크립트를 수동으로 수정한 부분을 바로 적용시킬 수 있습니다. 저장된 스크립트 파일이 존재하면, 이걸 불러온다는 것을 십분 활용해요.



5.



그 후 위 스크립트를 가지고 이미지 생성 모델이 실제 번역 결과 이미지를 출력합니다.

<img width="473" height="92" alt="image" src="https://github.com/user-attachments/assets/e06dff07-3e47-4ea5-8fe5-e2fb74b0d0a0" />



6. 



Eval 모델은 생성된 이미지와 원본 이미지를 둘 다 불러오고, 이를 비교하는 것을 통해

<img width="470" height="117" alt="image" src="https://github.com/user-attachments/assets/433e9800-e196-40ad-988b-8bab66bc7d57" />





- O X 판정을 합니다. O가 뜬 이미지는 다음 회차에 따로 이미지 생성 없이 복붙해서 다음 out (n+1) 폴더에 넣도록 합니다.

- X가 뜬 이미지는 뭐가 나쁜 부분인지 근거를 들어 설명해줍니다.


<img width="851" height="103" alt="image" src="https://github.com/user-attachments/assets/76444a91-3fac-4dc2-b27f-268712c88cff" />


eval_log.tsv 의 결과 또한 out 폴더 내에 저장되어서 파이썬이 불러와서 이어서 할 수 있습니다.
굳이 이 파일의 내용은 건드릴 필요는 없을 것 같습니다. 스크립트를 만지는 게 더 편할 테니까요.



7. 



스크립트 모델이 다시 위의 eval_log 를 보고 새로운 스크립트를 동일 폴더에 만듭니다. 처음 만들어진 스크립트는 _iter0.txt이고, 뒤의 0 숫자가 1 2 3 이런 식으로 증가합니다.



8. 


다시 수정된 스크립트와 eval 결과 의 O X 여부 및 나머지 프롬프트들을 보고 다시 이미지를 생성합니다.

<img width="1120" height="163" alt="image" src="https://github.com/user-attachments/assets/3c11e27e-c24c-4ac9-91b3-906871772902" />


이 때 out 2 등 폴더의 숫자가 증가한 새 폴더에 저장됩니다.



9.



이 과정이 MAX_ITERATIONS  숫자만큼 반복됩니다. 참고로 아래와 같은 파라미터들이 있습니다.



MAX_ITERATIONS = 5 # out1 이후 얼마나 더 반복할 것인지 (5면 out6까지 생성)

BATCH_SIZE = 1000  # 한번에 배치로 보낼 작업 페이지의 수량. 

POLL_INTERVAL_SEC = 30  # 배치로 보낸 후 결과물을 받으러 찾아가야 하는데 그 주기 (sec)

MAX_STAGE_RETRIES = 10  # 이미지생성 모델의 문제 등으로 인해 out 폴더 결과물 이미지 누락시 재시도 횟수

MAX_EVAL_RETRIES = 5  # 평가모델 실패시 재시도 횟수

MAX_SCRIPT_RETRIES = 10 # v4부터 추가된 스크립트모델 실패시 재시도 횟수 






10.



select_best_outputs.py 는 (out1 부터 out 10까지 예를 들어 만들었다고 가정. 아마 규칙이 빡빡해서 모두 O 처리가 되지 않았을 것입니다.)

마지막 out 10 폴더 내의 결과물도 마음에 들지 않을 경우, 기존 1~9 까지의 결과물을 포함하여
원본과 10개의 번역본을 모두 불러온 후, 
각 페이지당 가장 최고의 결과물이라고 판단된 페이지를 골라서 manga_out 폴더에 저장해줍니다.

랜덤하게 만들어진 엉뚱한 생성물 (전혀 그림체도 다른 가로 만화를 새로 창작하는 경우) 을 가장 잘 거르는 방법이었습니다.


오랜 시간이 걸려 만들어진 이것도 맘에 안든다면 다른 폴더를 뒤져보거나(사실 select를 실행해서 나온 manga out 선별이 완전한 게 아니라 선별되지 않은 다른 out 폴더 내 이미지가 사람이 판단하기에 더 나은 결과물일 수도 있습니다.)
횟수를 늘려보거나, 4번의 수동 스크립트 조작을 할 필요가 있습니다.


---


어느정도 단계가 명확하게 나뉘어 있으므로 중간 점검과 수정 작업 또한 용이할 것으로 생각됩니다.

https://github.com/heelee912/NANOBArnANgA/issues # 이슈 열기 페이지입니다.

이 작업이 마음에 드셨다면
[GitHub Sponsors](https://github.com/sponsors/heelee912)로 살짝 응원해 주셔도 정말 큰 힘이 됩니다 헤헤 😊
