#!/usr/bin/env python

from spider import *

class YoutubeSpider(Spider):

    def __init__(self):
        Spider.__init__(self)
        self.school = 'youtube'
        self.playlist = {}
        self.videos = {}
        
        self.playlist_urls = {\
                'mit': 'https://www.youtube.com/user/MIT/playlists',\
                'stanford': 'https://www.youtube.com/user/StanfordUniversity/playlists',\
                'stanfordonline' : 'https://www.youtube.com/user/stanfordonline/playlists',\
                'berkeley': 'https://www.youtube.com/user/UCBerkeley/playlists',\
                'cmu': 'https://www.youtube.com/user/CarnegieMellonU/playlists?view=1&sort=dd',\
                'harvard': 'https://www.youtube.com/user/harvard/playlists',\
                'caltech': 'https://www.youtube.com/user/caltech/playlists',\
                'udacity' : 'https://www.youtube.com/user/Udacity/playlists?view=1&sort=dd',\
                'cambridge' : 'https://www.youtube.com/user/CambridgeUniversity/playlists?sort=dd&view=1',\
                'oxford' : 'https://www.youtube.com/user/oxford/playlists?sort=dd&view=1',\
                'ucla' : 'https://www.youtube.com/user/UCLA/playlists',\
                'texas' : 'https://www.youtube.com/user/utaustintexas/playlists',\
                'imperialcollegelondon' : 'https://www.youtube.com/user/imperialcollegevideo/playlists',\
                'toronto' : 'https://www.youtube.com/user/universitytoronto/playlists',\
                'uns' : 'https://www.youtube.com/user/NUScast/playlists',\
                'unsw' : 'https://www.youtube.com/user/UNSWelearning/playlists?sort=dd&view=1',\
                'nptel' : 'https://www.youtube.com/user/nptelhrd/playlists'}
        self.videos_urls = { #'ucl' : 'https://www.youtube.com/user/Mikesev/videos?view=0&sort=dd&live_view=500&flow=grid',
                             'sciwrite' : 'https://www.youtube.com/channel/UC-wb-n89yM0lBiP2QltsDaA/videos'}
    def getPlaylist(self, html, user):
        soup = BeautifulSoup(html)
        for a in soup.find_all('a'):
            if a.attrs.get('href', '') != '' and a['href'].startswith('/playlist?list='):
                key = a.text.strip()
                if key.find('|') != -1:
                    key = key[key.find('|') + 1 :].strip()
                if user == 'berkeley' and key.startswith('Computer Science '):
                    key = key.replace('Computer Science ', 'CS')
                if user == 'berkeley' and key.startswith('Electrical Engineering '):
                    key = key.replace('Electrical Engineering ', 'EE')
                self.playlist[key] = 'https://www.youtube.com' + a['href']

    def getLoadMoreHref(self, html):
        if html.strip() == '':
            return ''
        soup = BeautifulSoup(html)
        button = soup.find('button', class_='yt-uix-button yt-uix-button-size-default yt-uix-button-default load-more-button yt-uix-load-more browse-items-load-more-button')
        if button != None:
            return button['data-uix-load-more-href']
        return ''

    def getVideo(self, html, user, contain, prefix):
        soup = BeautifulSoup(html)
        for a in soup.find_all('a'):
            if a.attrs.get('href', '') != '' and a['href'].startswith('/watch?v='):
                key = a.text.strip()
                if key == '':
                    continue
                if contain != '' and key.find(contain) == -1:
                    continue
                url = 'https://www.youtube.com' + a['href']
                print prefix + ' | ' + key + ' | ' + url + ' | '
                self.videos[key] = url

    def getVideos(self, user, url):
        self.videos = {}
        r = requests.get(url)
        contain = 'SciW'
        prefix = 'COMP3095'
        self.getVideo(r.text, user, contain, prefix)
        
        load_more_href = self.getLoadMoreHref(r.text)

        while (load_more_href != ''):

            r = requests.get('https://www.youtube.com' + load_more_href)
            jobj = json.loads(r.text)
            load_more_href = self.getLoadMoreHref(jobj['load_more_widget_html'].strip())

            self.getVideo(jobj['content_html'], user, contain, prefix) 


    def getPlaylists(self, user, url):
        self.playlist = {}
        r = requests.get(url)
        self.getPlaylist(r.text, user)

        load_more_href = self.getLoadMoreHref(r.text)

        while (load_more_href != ''):

            r = requests.get('https://www.youtube.com' + load_more_href)
            jobj = json.loads(r.text)
            load_more_href = self.getLoadMoreHref(jobj['load_more_widget_html'].strip())

            self.getPlaylist(jobj['content_html'], user)

        file_name = self.get_file_name(self.school + '/' + user, self.school)
        file_lines = self.countFileLineNum(file_name)
        f = self.open_db(file_name + ".tmp")
        self.count = 0
        for k, v in [(k,self.playlist[k]) for k in sorted(self.playlist.keys())]:
            self.count += 1
            video_id = user + '-' + str(self.count)
            if k.startswith('MIT'):
                k = k[4:]
                if k[0 : k.find(' ')].find('.') != -1:
                    video_id = user + '-' + k[0 : k.find(' ')]
                    k = k[k.find(' ') : ].strip()

            print k + ' ' + v
            #self.write_db(f, video_id, k, v, 'videourl:' + v)
        self.close_db(f)
        if file_lines != self.count and self.count > 0:
            self.do_upgrade_db(file_name)
            print "before lines: " + str(file_lines) + " after update: " + str(self.count) + " \n\n"
        else:
            self.cancel_upgrade(file_name)
            print "no need upgrade\n"

    def doWork(self):
        #for user, url in self.playlist_urls.items():
        #    self.getPlaylists(user, url)
        for user, url in self.videos_urls.items():
            self.getVideos(user, url)


def main(argv):
    start = YoutubeSpider()
    start.doWork()

if __name__ == '__main__':
    main(sys.argv)
