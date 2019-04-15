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
1、下载速度有点慢，只用requests单进程下载，后面使用多线程改进  
2、FFmpeg合成速度也有点慢，这个我解决不了  
3、目前只支持av格式的链接，番剧的话后面加  
4、我测试了很多链接都是可以下载的，如果有什么问题，可以在CSDN或者邮箱联系我  
5、这个会时时更新，失效请联系

# 联系方式
CSDN：https://blog.csdn.net/Qwertyuiop2016/article/details/89315288  
Email：kanade@blisst.cn  
GitHub：https://github.com/kanadeblisst/BDVideo