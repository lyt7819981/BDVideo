# -*- coding: utf-8 -*-
import re
import json
import sys
import time
import os
import requests


class GetVideo:
    def __init__(self, url, clarity='720'):
        '''
            url:视频的URL地址
            clarity:视频清晰度，取值：360(流畅) 480(清晰) 720(高清) 1080(更高清)
        '''
        self.url = url
        self.slice = 1024*1024*2 # 一次下载的分片长度
        self.clarity = clarity
        data = self.get_home_page(url)
        if isinstance(data, dict):
            urls = self.extract(data)
            self.download(urls)
            self.merge()
        elif isinstance(data, list):
            for i in data:
                cid = i.get('cid')
                name = i.get('part')
                playinfo = self.get_playinfo(cid).get('data')
                urls = self.extract(playinfo)
                self.download(urls)
                self.merge(name)
              
    def __call__(self):
        pass
    
    def get_home_page(self, url):
        '''
            请求主页面，获取相应数据
        '''
        headers = {
            'Host': 'www.bilibili.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'
        }
        resp = requests.get(url, headers=headers)
        status = resp.status_code
        if status == 200:
            html = resp.text
            playinfo = re.search(r'window.__playinfo__=(.*?)</script>', html)
            
            initinfo = re.search(r'window.__INITIAL_STATE__=(\{.*?\});', html).group(1)
            initinfo = json.loads(initinfo)
            
            name = initinfo.get('videoData').get('title') + '.mp4'
            self.pic = initinfo.get('videoData').get('pic') # 封面图
            self.aid = initinfo.get('videoData').get('aid')
            self.duration = initinfo.get('videoData').get('duration')   # 视频时长
            # 去掉特殊字符
            trantab = str.maketrans('\/:*?"<>|', ' '*9)
            self.name = name.translate(trantab) # 视频名称
            # playinfo存在则只有一个视频，否则为空则说明该链接含有多个视频
            if playinfo:
                return json.loads(playinfo.group(1)).get('data') # 字典格式的数据
            else:
                pages = initinfo.get('videoData').get('pages')
                return [{'cid': x.get('cid'), 'part': x.get('part'), 'duration': x.get('duration')} for x in pages]
        else:
            print('访问视频页出错!，状态码为 %s  ' % status)
            print('程序即将退出！')
            sys.exit()
            
    def extract(self, data):
        '''
            从数据中提取视频和音频的实际下载地址
        '''
        d1 = {'360': 4, '480':5, '720':6, '1080':7}
        videos = data['dash']['video']
        audios = data['dash']['audio']
        video_url = videos[d1[self.clarity]]['baseUrl']
        audio_url = audios[1]['baseUrl']
        
        return video_url, audio_url
    
    def get_playinfo(self, cid):
        '''   
            请求接口得到下载视频数据
        '''
        url = 'https://api.bilibili.com/x/player/playurl?avid=%s&cid=%s&qn=64&type=&otype=json&fnver=0&fnval=16' % (self.aid, cid)
        headers = {
            'Host': 'api.bilibili.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'
        }
        
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200:
            return json.loads(resp.text)
    
    
    def get_size(self, url):
        '''
            通过URL获取文件大小
        '''
        headers = {
            'Origin': 'https://www.bilibili.com',
            'Range': 'bytes=0-',
            'Referer': self.url,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'
        }
        resp = requests.head(url, headers=headers)
        if resp.status_code < 300:
            length = resp.headers.get('Content-Length')
            total_bytes = int(length)
            return total_bytes
        else:
            print('获取头信息失败，状态码为%d' % resp.status_code)
            sys.exit()
    
        
    def http_get(self, url, start, end):
        '''
            下载视频分片
        '''
        headers = {
            'Origin': 'https://www.bilibili.com',
            'Range': 'bytes=%d-%d' % (start, end),
            'Referer': self.url,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'
        }
        resp = requests.get(url, headers=headers)
        if resp.status_code < 300:
            slice_name = str(start//self.slice)
            with open(slice_name, 'wb') as f:
                length = resp.headers.get('Content-Length')
                length = int(length.strip()) if length else None
                crange = resp.headers.get('Content-Range')
                total_bytes = int(crange.split('/')[-1]) if crange else None
                if total_bytes == end:
                    f.write(resp.content)
                else:
                    f.write(resp.content)
                    slice_size = os.path.getsize(slice_name)
                    if length == slice_size and slice_size == (self.slice+1):
                        pass
                    else:
                        self.http_get(url, start, end)
        else:
            print('下载视频失败，状态码为%d' % resp.status_code)
            sys.exit()
            
    def download(self, urls):
        '''
            下载视频
        '''
        print('---开始下载视频分片---')
        video_url, audio_url = urls
        if not os.path.exists('video'):
            os.mkdir('video')
        os.chdir('video')
        
        total_bytes = self.get_size(video_url)
        self.video_n = total_bytes//self.slice + 1 
        start = 0
        end = start + self.slice
        while start < total_bytes:
            if total_bytes - start < self.slice:
                self.http_get(video_url, start, total_bytes)
                break
            else:
                self.http_get(video_url, start, end)
            start = end + 1
            end = start + self.slice
            print(f'\r当前进度：{int(start/total_bytes*100)}%({round(start/1024/1024)}M/{round(total_bytes/1024/1024,2)}M)', end='')
            time.sleep(0.01)
        print(f'\r当前进度：100%({round(total_bytes/1024/1024,2)}M/{round(total_bytes/1024/1024,2)}M)')
        os.chdir('../')
        print('---开始下载音频分片---')
        if not os.path.exists('audio'):
            os.mkdir('audio')
        os.chdir('audio')
        total_bytes = self.get_size(audio_url)
        self.audio_n = total_bytes//self.slice + 1
        start = 0
        end = start + self.slice
        while start < total_bytes:
            if total_bytes - start < self.slice:
                self.http_get(audio_url, start, total_bytes)
                break
            else:
                self.http_get(audio_url, start, end)
            start = end + 1
            end = start + self.slice
            print(f'\r当前进度：{int(start/total_bytes*100)}%({round(start/1024/1024)}M/{round(total_bytes/1024/1024,2)}M)', end='')
            time.sleep(0.01)
        print(f'\r当前进度：100%({round(total_bytes/1024/1024,2)}M/{round(total_bytes/1024/1024,2)}M)')
        os.chdir('../')
                     
    
    def merge(self, vname=None):
        '''
            合并视频
        '''
        print('----开始合并视频分片----')
        if not os.path.exists('video'):
            print('不存在video目录！')
            return
        with open('temp.mp4', 'wb') as fw:
            for i in range(self.video_n):
                with open('video/' + str(i), 'rb') as fr:
                    fw.write(fr.read())
                    
        print('----开始合并音频分片----')
        if not os.path.exists('audio'):
            print('不存在audio目录！')
            return
        with open('temp.mp3', 'wb') as fw:
            for i in range(self.audio_n):
                with open('audio/' + str(i), 'rb') as fr:
                    fw.write(fr.read())
                    
        print('----开始合并视频和音频----\n(大概需要几分钟，进度请看弹出的命令窗口！)')
        name = str(self.aid) + '.mp4'
        cmd = 'ffmpeg -i temp.mp4 -i temp.mp3 %s' % name
        if not os.system(cmd):
            print('----合并音视频成功----')
            # 如果想以av号命名请注释这个
            try:
#                os.remove('temp.mp3')
#                os.remove('temp.mp4')
                if vname:
                    os.rename(name, vname+'.mp4')
                else:
                    os.rename(name, self.name)
            except FileExistsError:
                pass
        else:
            print('----合并音视频失败----')
            
        curdir = os.getcwd()
        video_dir = curdir + '\\video'
        audio_dir = curdir + '\\audio'
        if os.system('rd /s /q %s %s'%(video_dir, audio_dir)):
            print('---删除临时文件失败---')
            
        
        


if __name__ == '__main__':
    url = 'https://www.bilibili.com/video/av49382963'
    g = GetVideo(url, '720')
    
    
    
