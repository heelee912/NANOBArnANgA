<img width="375" height="600" alt="image" src="https://github.com/user-attachments/assets/bf8e9cde-0e2f-4810-863a-e65897b2d5ef" /><img width="408" height="656" alt="image" src="https://github.com/user-attachments/assets/05ce5c58-47da-4796-bf48-2549de4ee10c" />

v3

<img width="375" height="600" alt="image" src = https://github.com/user-attachments/assets/1a323c7d-63d7-4450-8274-97b5c57254ca><img img width="408" height="656" alt="image" src = https://github.com/user-attachments/assets/f834a83c-eeb2-4bf5-843e-f394e982fda7>

v5

<img width="375" height="600" alt="image" src = https://github.com/user-attachments/assets/7689074c-a837-4ce8-a13c-53676189a1c0><img img width="408" height="656" alt="image" src = https://github.com/user-attachments/assets/87577fa4-f64a-476c-9469-e7fb19f6eb17>

v7

v7リリースから英語および中国語ユーザーサポートを開始する予定です。（現在プロトタイプが作成され、検討段階にあります）

https://y-y-y-y.tistory.com/ # 過去プロジェクトや AIS 使用量の確認など、注意事項が載っているページです。



以下の説明文は v3 を前提に書かれていますが、最新バージョンの更新内容は Releases にまとまっているので、そちらも参照してください。

https://github.com/heelee912/NANOBArnANgA/releases # Releases ページ


![Generated Image December 10, 2025 - 1_30PM](https://github.com/user-attachments/assets/ad7cb9d6-2255-4a56-8744-ebba7b52a2cc)
all loop 全体フローの概略図です。


1.



all loop v3 は、主な自動処理をほぼすべて担い、各種ファイルを生成するコードです。



select_best_outputs は、生成された画像を評価して、各ページごとに「一番良い」と判断した 1 枚を集めるスクリプトです。





2.



どちらのコードにも API キーを設定します。

Python ファイルの中に



API_KEY = " " 



という行があるので、このダブルクォーテーション "ここ" の中に API キーをそのまま書き込みます。



3.


<img width="564" height="139" alt="image" src="https://github.com/user-attachments/assets/66f8257d-7b27-4eaf-975e-d6c4c7f95ab0" />


manga フォルダの中に、元の日本語マンガ画像を入れます。



all loop（バージョンはどれでも可）.py を実行します。



4. 



最初の処理は、script フォルダ内にスクリプトを生成することです。  
3 Pro を使って manga フォルダ内の画像を読み込み、コード内のプロンプト規則に従って AI が判断するようになっています。

<img width="520" height="172" alt="image" src="https://github.com/user-attachments/assets/d1860bde-c432-4f6f-8a3e-ef37d89cbc3e" />

スクリプトは、画像生成時のガイドラインとして使われます。

<img width="827" height="148" alt="image" src="https://github.com/user-attachments/assets/b6ef7dde-be41-406e-bf46-ccae2039a01a" />

<img width="816" height="243" alt="image" src="https://github.com/user-attachments/assets/08c50bc0-0a54-4d36-ac18-d5dad420869e" />



内容としては、画像モデルに対して「どの文字を、どこに、どう書くか」を一つ一つ細かく指示する形になっており、ほぼ手取り足取り教えるイメージです。



いくつかの方法を試した中で、この方式が縦書きを防ぎ、横書きにさせる効果が最も高い結果になりました。



スクリプトが生成された直後に処理を止めてスクリプトを手動で修正し、  
（または、そのスクリプトから生成された画像を削除し）  
もう一度 Python を実行すれば、そのスクリプトに対する手動修正をすぐに反映させることができます。  
対応するスクリプトファイルが存在する場合はそれを読み込む仕様なので、この挙動を十分に活用できます。



5.



その後、上で作成したスクリプトを使って、画像生成モデルが実際の翻訳済み画像を出力します。

<img width="473" height="92" alt="image" src="https://github.com/user-attachments/assets/e06dff07-3e47-4ea5-8fe5-e2fb74b0d0a0" />



6. 



Eval モデルは、生成された画像と元画像の両方を読み込み、両者を比較します。

<img width="470" height="117" alt="image" src="https://github.com/user-attachments/assets/433e9800-e196-40ad-988b-8bab66bc7d57" />





- その結果として O / X 判定を行います。  
  O となった画像は、次の周回では新たに画像を生成せず、そのままコピーして次の out (n+1) フォルダに入れます。

- X となった画像については、どこが良くないのか、その理由を挙げて説明します。



<img width="851" height="103" alt="image" src="https://github.com/user-attachments/assets/76444a91-3fac-4dc2-b27f-268712c88cff" />


eval_log.tsv の結果も out フォルダ内に保存され、Python 側で読み込んで処理を継続できます。  
通常、このファイルの中身を手でいじる必要はありません。調整したい場合はスクリプトを触る方が楽だと思います。



7. 



スクリプト用モデルが、上記の eval_log を参照して新しいスクリプトを同じフォルダに生成します。  
最初に作られるスクリプトは _iter0.txt で、末尾の 0 が 1、2、3… と増えていきます。



8. 


修正されたスクリプトと Eval の O / X 結果、そして残りのプロンプトを見ながら、再度画像を生成します。

<img width="1120" height="163" alt="image" src="https://github.com/user-attachments/assets/3c11e27e-c24c-4ac9-91b3-906871772902" />


このとき、out2 など番号が増えた新しいフォルダに画像が保存されます。



9.



このプロセスは、MAX_ITERATIONS に設定した回数だけ繰り返されます。  
参考までに、パラメータは次の通りです。



IMAGE_RESOLUTION = "1K"      # "1K", "2K", "4K" から選択

MAX_ITERATIONS = 9           # 最大リファイン回数（out2..out{MAX+1}）

BATCH_SIZE = 2               # script / image / eval ジョブのバッチサイズ。1 回あたり最大およそ 100 ページまで送れるので、小さめの値でも問題ありません。

POLL_INTERVAL_SEC = 30       # バッチジョブのステータス確認のポーリング間隔（秒）

MAX_STAGE_RETRIES = 100      # 各ステージ（Stage 1 および各イテレーション）での最大リトライ回数。次のステージへ進む前に、確認して再生成するための上限です。

MAX_EVAL_RETRIES = 10        # Eval バッチの最大リトライ回数。1 回失敗した場合に、ここまで再試行します。

MAX_SCRIPT_RETRIES = 10      # スクリプトテキストが空で返ってきた場合の最大リトライ回数。同じく 1 回失敗したときに再試行します。

TARGET_LANG_EN = "Korean"    # 例: "Korean", "English", "Chinese"

TARGET_LANG_NATIVE = "한국어" # 例: "한국어", "English", "中文"





10.



select_best_outputs.py は、たとえば out1 から out10 まで生成されていることを想定しています  
（ルールがかなり厳しいため、最後まで回してもすべてが O になるとは限りません）。



もし最後の out10 フォルダ内の結果にも満足できない場合、  
select_best_outputs.py は元画像と 10 個の翻訳結果をすべて読み込み、  
各ページ番号ごとに「最も良い」と判断した 1 枚を選んで、manga_out フォルダに保存します。



これは、ランダムに生成されたおかしな画像  
（まったく違う絵柄の横長マンガを新しく創作してしまうケースなど）を弾く方法として、最も有効でした。



長時間かけて生成した結果にそれでも満足できない場合は、ほかの out フォルダを直接見てみたり  
（実際には、select_best_outputs の結果である manga_out の内容が完全というわけではなく、  
選ばれていない画像の方が人間の目から見ると良い場合もあります）、  
イテレーション回数を増やしたり、第 4 のステップでスクリプトを手動調整する頻度を増やす必要があります。

v2 以降のバージョンでは、ログが別途保存されるようになっています。



---



ある程度はステージごとに処理がはっきり分かれているので、途中でのチェックや修正作業もしやすい構造になっていると思います。



https://github.com/heelee912/NANOBArnANgA/issues # Issue を立てるページです。

このプロジェクトを気に入っていただけたら、  
[GitHub Sponsors](https://github.com/sponsors/heelee912) で少しだけ応援していただけると、とても励みになります 😊
