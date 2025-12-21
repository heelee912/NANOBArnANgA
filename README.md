[English](./README.md) | [한국어](./README_ko.md) | [中文](./README_zh.md) | [日本語](./README_ja.md)



<img width="375" height="600" alt="image" src = https://github.com/user-attachments/assets/7689074c-a837-4ce8-a13c-53676189a1c0><img img width="408" height="656" alt="image" src = https://github.com/user-attachments/assets/87577fa4-f64a-476c-9469-e7fb19f6eb17>

v7
<img width="492" height="64" alt="image" src="https://github.com/user-attachments/assets/6a6621bd-22cf-4d9f-84d5-dde0c4ca4f5e" />

v7 (v7.2), which now supports multiple target languages for translation output, has been released.


https://y-y-y-y.tistory.com/ # Page with previous projects and notes such as checking AIS usage and other cautions



The explanation below assumes v3, but the latest updates are always listed on the Releases page, so please refer to it.

https://github.com/heelee912/NANOBArnANgA/releases # Releases page



![Generated Image December 10, 2025 - 1_19PM](https://github.com/user-attachments/assets/6479b662-6911-4553-b234-bc8a3613f0dc)

Diagram of the overall all loop flow


1.



all loop v3 is the code that performs most of the automation and generates all the files.



select_best_outputs evaluates the generated images and collects what it judges to be the best single page.





2.



Both scripts need an API key.

Inside the Python file,



API_KEY = " " 



you put your API key directly inside the double quotes here.



3.


<img width="564" height="139" alt="image" src="https://github.com/user-attachments/assets/66f8257d-7b27-4eaf-975e-d6c4c7f95ab0" />


Put the original Japanese manga inside the manga folder.



Run all loop (any version).py.



4. 



The very first step is to create scripts inside the script folder.  
Using 3 Pro, the model looks at the images in the manga folder and makes its own judgement, following the prompt rules written in the code.

<img width="520" height="172" alt="image" src="https://github.com/user-attachments/assets/d1860bde-c432-4f6f-8a3e-ef37d89cbc3e" />

The script is used as a guideline when generating images.

<img width="827" height="148" alt="image" src="https://github.com/user-attachments/assets/b6ef7dde-be41-406e-bf46-ccae2039a01a" />

<img width="816" height="243" alt="image" src="https://github.com/user-attachments/assets/08c50bc0-0a54-4d36-ac18-d5dad420869e" />



The content spoon-feeds the image model with detailed instructions on how to write each piece of text.



Among several methods that were tried, this approach worked best to prevent vertical writing and enforce horizontal text.



Right after the script is created, you can stop the process, edit the script manually  
(or delete the images that were generated from that script), then run the Python file again.  
Because the saved script file is loaded if it exists, you can fully take advantage of this to apply manual edits directly.



5.



After that, the image generation model uses the script above and outputs the actual translated images.

<img width="473" height="92" alt="image" src="https://github.com/user-attachments/assets/e06dff07-3e47-4ea5-8fe5-e2fb74b0d0a0" />



6. 



The Eval model loads both the generated image and the original image, and compares them.

<img width="470" height="117" alt="image" src="https://github.com/user-attachments/assets/433e9800-e196-40ad-988b-8bab66bc7d57" />





- It gives an O / X judgement.  
  Images with O will be copied as they are into the next out (n+1) folder in the next round, without generating a new image.

- For images with X, it explains what is wrong and gives reasons.



<img width="851" height="103" alt="image" src="https://github.com/user-attachments/assets/76444a91-3fac-4dc2-b27f-268712c88cff" />


The results in eval_log.tsv are also saved inside the out folder, so the Python script can load them and continue.  
In most cases you do not need to touch this file by hand. Editing the scripts is usually more convenient.



7. 



The script model then reads the eval_log again and creates a new script in the same folder.  
The first script is named _iter0.txt, and the 0 at the end increases to 1, 2, 3, and so on.



8. 


Using the updated script, the Eval O / X result, and the remaining prompts, the model generates images again.

<img width="1120" height="163" alt="image" src="https://github.com/user-attachments/assets/3c11e27e-c24c-4ac9-91b3-906871772902" />


This time the images are saved in a new folder with a higher number, such as out2, out3, and so on.



9.



This process repeats up to the value of MAX_ITERATIONS.  
For reference, here are the parameters:



IMAGE_RESOLUTION = "1K"      # choose from "1K", "2K", "4K"

MAX_ITERATIONS = 9           # Max refinement rounds (out2..out{MAX+1})

BATCH_SIZE = 2               # Batch size for script/image/eval jobs. You can send up to about 100 pages per batch, so a small value is also fine.

POLL_INTERVAL_SEC = 30       # Poll interval for batch jobs (sec)

MAX_STAGE_RETRIES = 100      # Max retries per stage (Stage 1 or each iteration). Used to regenerate after reviewing before moving on.

MAX_EVAL_RETRIES = 10        # Max retries for evaluation batches. If it fails once, it retries.

MAX_SCRIPT_RETRIES = 10      # Max retries when the script text is empty. If it fails once, it retries.

TARGET_LANG_EN = "Korean"    # Examples: "Korean", "English", "Chinese"

TARGET_LANG_NATIVE = "한국어" # Examples: "한국어", "English", "中文"





10.



select_best_outputs.py assumes, for example, that you have created out1 through out10.  
Because the rules are strict, not all images will be judged O.



If you are not satisfied even with the results in the final out10 folder,  
select_best_outputs.py loads the original and all ten translated versions,  
and for each page chooses the page that it judges to be the best, then saves it into the manga_out folder.



This was the most effective way to filter out random, off-target generations  
(for example, cases where it newly creates a completely different horizontal comic with a different art style).



If you still do not like the results that took a long time to produce,  
you can search through the other folders  
(in fact, the selection in manga_out is not perfect, and an image in another out folder that was not selected may look better to a human),  
increase the number of iterations, or use more manual script editing in step 4.

From v2, logs are saved separately.



---



Because the stages are fairly clearly separated, it should be easy to inspect and adjust things in the middle of the process.



https://github.com/heelee912/NANOBArnANgA/issues # Issues page



If you like this work,  
a small cheer through [GitHub Sponsors](https://github.com/sponsors/heelee912) will be a huge help 😊
