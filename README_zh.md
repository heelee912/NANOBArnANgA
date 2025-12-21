<img width="375" height="600" alt="image" src="https://github.com/user-attachments/assets/bf8e9cde-0e2f-4810-863a-e65897b2d5ef" /><img width="408" height="656" alt="image" src="https://github.com/user-attachments/assets/05ce5c58-47da-4796-bf48-2549de4ee10c" />

v3

<img width="375" height="600" alt="image" src = https://github.com/user-attachments/assets/1a323c7d-63d7-4450-8274-97b5c57254ca><img img width="408" height="656" alt="image" src = https://github.com/user-attachments/assets/f834a83c-eeb2-4bf5-843e-f394e982fda7>

v5

<img width="375" height="600" alt="image" src = https://github.com/user-attachments/assets/7689074c-a837-4ce8-a13c-53676189a1c0><img img width="408" height="656" alt="image" src = https://github.com/user-attachments/assets/87577fa4-f64a-476c-9469-e7fb19f6eb17>

v7

<img width="492" height="64" alt="image" src="https://github.com/user-attachments/assets/91b23351-cc77-44bc-81b7-5b3ea98de291" />


现已发布 v7（v7.2），支持将翻译输出目标语言扩展为多种语言。


https://y-y-y-y.tistory.com/ # 这里可以查看以往项目，以及 AIS 使用量检查等注意事项



下面的说明是基于 v3 写的，不过最新版的更新内容都发布在 Releases 页面，请一并参考。

https://github.com/heelee912/NANOBArnANgA/releases # Releases 页面



![Generated Image December 10, 2025 - 12_43AM](https://github.com/user-attachments/assets/4dc0ce6d-ad6f-499a-93d9-bf6a08e0f505)

all loop 的整体流程示意图


1.



all loop v3 是负责主要自动化流程、生成各种文件的核心代码。



select_best_outputs 会对生成的图片进行评价，并为每一页挑选它认为最好的那一张。





2.



这两个脚本都需要填写 API Key。

在 Python 文件中



API_KEY = " " 



把 API Key 直接写在这个双引号 “这里” 里面即可。



3.


<img width="564" height="139" alt="image" src="https://github.com/user-attachments/assets/66f8257d-7b27-4eaf-975e-d6c4c7f95ab0" />


把原始的日文漫画图片放到 manga 文件夹里。



执行 all loop（版本不限）.py。



4. 



最开始的步骤，是在 script 文件夹中生成脚本文件。  
通过 3 Pro 模型读取 manga 文件夹里的图片，让 AI 按照代码中写好的提示词规则进行判断并生成脚本。

<img width="520" height="172" alt="image" src="https://github.com/user-attachments/assets/d1860bde-c432-4f6f-8a3e-ef37d89cbc3e" />

脚本会在图片生成时作为“指南”使用。

<img width="827" height="148" alt="image" src="https://github.com/user-attachments/assets/b6ef7dde-be41-406e-bf46-ccae2039a01a" />

<img width="816" height="243" alt="image" src="https://github.com/user-attachments/assets/08c50bc0-0a54-4d36-ac18-d5dad420869e" />



脚本内容会非常细致地告诉图像模型：每一个字该怎么写、写在哪个位置，几乎是“喂到嘴边”的程度。



在尝试过的多种方法中，这种方式在防止竖排文字、强制横排方面效果最好。



脚本生成完成后，可以直接终止程序，手动修改脚本  
（或者删除由该脚本生成的图片），然后重新运行 Python。  
如果对应页面的脚本文件已经存在，程序会优先读取这个脚本文件，所以可以充分利用这一点，把手动修改内容直接应用到后续流程中。



5.



之后，图像生成模型会根据上面生成的脚本，输出真正的翻译结果图片。

<img width="473" height="92" alt="image" src="https://github.com/user-attachments/assets/e06dff07-3e47-4ea5-8fe5-e2fb74b0d0a0" />



6. 



Eval 模型会同时读取生成的图片和原始图片，并将两者进行比较。

<img width="470" height="117" alt="image" src="https://github.com/user-attachments/assets/433e9800-e196-40ad-988b-8bab66bc7d57" />





- 对每张生成图片给出 O / X 判定。  
  判定为 O 的图片，在下一轮会直接复制到下一个 out (n+1) 文件夹，而不再重新生成。

- 判定为 X 的图片，会说明哪些地方存在问题，并给出理由。



<img width="851" height="103" alt="image" src="https://github.com/user-attachments/assets/76444a91-3fac-4dc2-b27f-268712c88cff" />


eval_log.tsv 的结果同样保存在对应的 out 文件夹中，Python 会读取这份文件继续后续流程。  
通常不用手动修改这个文件。实际调参时，直接改脚本会更方便。



7. 



脚本模型会再次读取上面的 eval_log，并在同一文件夹中生成新的脚本。  
最初生成的脚本名为 _iter0.txt，后面的数字会变成 1、2、3…… 这样递增。



8. 


然后根据更新后的脚本、eval 的 O / X 结果，以及其他提示词，再次生成图片。

<img width="1120" height="163" alt="image" src="https://github.com/user-attachments/assets/3c11e27e-c24c-4ac9-91b3-906871772902" />


此时会把图片保存到新的文件夹中，例如 out2、out3 等，文件夹编号递增。



9.



这一整套流程会根据 MAX_ITERATIONS 的数值重复执行多次。  
相关参数如下：



IMAGE_RESOLUTION = "1K"      # 可选 "1K", "2K", "4K"

MAX_ITERATIONS = 9           # 最大细化轮数（out2..out{MAX+1}）

BATCH_SIZE = 2               # 脚本/图像/Eval 任务的批次大小。一次最多可以发送约 100 页，所以这个值设小一点也没问题。

POLL_INTERVAL_SEC = 30       # 轮询批处理任务状态的时间间隔（秒）

MAX_STAGE_RETRIES = 100      # 每个阶段（第 1 阶段或每轮迭代）的最大重试次数。用于在进入下一阶段前，根据检查结果重新生成。

MAX_EVAL_RETRIES = 10        # Eval 批处理的最大重试次数。失败一次会重试。

MAX_SCRIPT_RETRIES = 10      # 当脚本文本为空时的最大重试次数。失败一次会重试。

TARGET_LANG_EN = "Korean"    # 例："Korean", "English", "Chinese"

TARGET_LANG_NATIVE = "한국어" # 例："한국어", "English", "中文"





10.



假设已经生成了 out1 到 out10（规则比较严格，所以最后一轮也不一定所有页面都拿到 O 判定）。



如果你对 out10 文件夹里的结果仍然不满意，  
select_best_outputs.py 会把原始图片和 10 份翻译结果全部读进来，  
然后对每一个页面编号，从这些候选结果中挑选出它认为最好的那一张，并保存到 manga_out 文件夹中。



这种做法对于过滤“随机乱画”的结果非常有效，  
例如模型新创作了一整页完全不同画风的横向漫画，这类情况往往会在这一步被筛掉。



如果你对这些花了很长时间生成的结果还是不满意，  
可以自己翻一翻其他 out 文件夹  
（实际上，manga_out 的自动筛选并不是绝对完美，没有被选中的某些图片可能在人眼看起来更好），  
也可以增加迭代次数，或者像第 4 步那样更积极地手动调整脚本。

从 v2 版本开始，日志会单独保存，方便调试。



---



整个流程的各个阶段都分得比较清楚，所以在中途检查结果和修改设置会相对容易。



https://github.com/heelee912/NANOBArnANgA/issues # 提交 Issue 的页面

如果你觉得这个项目对你有帮助，  
也欢迎通过 [GitHub Sponsors](https://github.com/sponsors/heelee912) 轻轻支持一下，这对作者会是很大的鼓励 😊
