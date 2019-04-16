# 功能
下载B站视频

# 版本
python3.x

# 依赖库
requests

# 示例
url = 'https://www.bilibili.com/video/av49382963'  
g = GetVideo(url, '720') # 720为视频清晰度，取值有：360,480,720,1080

# 其他
0、如果FFmpeg下载速度慢，可以直接百度官网下载，或者点这个链接https://www.lanzous.com/i3sjjla  
1、建议将ffmepg.exe的所在目录加入到Windows的环境变量里，或者直接放到系统环境变量的目录  
2、下载速度有点慢，只用requests单进程下载，后面使用多线程改进  
3、FFmpeg合成速度也有点慢，这个我解决不了  
4、目前只支持av格式的链接，番剧的话后面加  
5、我测试了很多链接都是可以下载的，如果有什么问题，可以在CSDN或者邮箱联系我  
6、这个会时时更新，失效请联系

# 联系方式
CSDN：https://blog.csdn.net/Qwertyuiop2016/article/details/89315288  
Email：kanade@blisst.cn  
GitHub：https://github.com/kanadeblisst/BDVideo