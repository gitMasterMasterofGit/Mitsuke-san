# Description
Mitsuke-san is a language-learning tool that automates sentence mining for Anki card creation.

It can automatically make cards for new words that contain pictures (if video content is being mined), audio, and sentences (regardless of whether or not the content has subtitles).

# DEPENDENCIES:
### These external programs are requried for Mistuke-san to function  
[Anki](https://apps.ankiweb.net/)  
ffmpeg 
>ffmpeg installation methods:
>>[chocolately](https://chocolatey.org/install) (preferred)  
>>[ffmpeg direct download](https://ffmpeg.org/download.html) (not recommended)

# Installing ffmpeg with chocolatey

This method is recommended since it requires fewer steps and automatically adds ffmpeg to your system's PATH variable, which is neccessary for Mitsuke-san to function

Once chocolatey is intalled according to the directions on the [download page](https://chocolatey.org/install), run the following command in powershell with administrative access:

choco install ffmpeg

When prompted to confirm the installation, type a to confirm all requests and proceed with the install

In order to check if ffmpeg installed properly, enter the following command in powershell:

ffmpeg -version

If information about the ffmpeg install is displayed, then ffmpeg has been installed correctly