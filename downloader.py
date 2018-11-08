from bs4 import BeautifulSoup
import requests
import datetime
import os


lyrikline_url = 'https://www.lyrikline.org/de/gedichte?listitems=1000'

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0',
    'Referer': 'https://www.lyrikline.org/de/gedichte?nav=1&neu=1'
}


class LyriklineDownloader(object):

    def download_new_poems(self):
        links = self.get_new_poems_page()
        urls = self.build_urls(links)
        self.download(urls)

    def get_new_poems_page(self):
        s = requests.Session()

        poems_page = s.get('https://www.lyrikline.org/de/gedichte?nav=1&neu=1', headers=headers)
        all_poems = s.get('https://www.lyrikline.org/de/gedichte?listitems=1000', headers=headers)

        soup_poems_page = BeautifulSoup(all_poems.content, "lxml")
        ul = soup_poems_page.find("ul", class_="liste clearfix")
        links = ul.find_all('a')
        return links

    def build_urls(self, links):
        urls = []

        for link in links:
            href = link['href']
            author = link.find('p', class_='autor').text
            title = link.find('h3').text
            url = (href, author, title)
            urls.append(url)

        return urls

    def fetch_url(self, entry):
        href, author, title = entry
        path = f"{author} - {title}"
        if not os.path.exists(path):
            r = requests.get('https://www.lyrikline.org/' + href, stream=True, headers=headers)
            if r.status_code == 200:
                with open(path, 'wb') as f:
                    for chunk in r:
                        f.write(chunk)
        return path

    def download(self, urls):
        today = datetime.datetime.today()
        path = today.strftime("%d %B %Y")
        if not os.path.exists(path):
            os.makedirs(path)

        os.chdir(path)

        for entry in urls:
            href, author, title = entry
            title = title.replace("/", "-")
            poem =requests.get('https://www.lyrikline.org' + href, headers=headers)
            soap_poem = BeautifulSoup(poem.content, "lxml")
            text = soap_poem.find('section', class_="gedicht").find('div', class_="gedicht-originaltext")
            gedicht = f"{text}"
            if not os.path.exists(f"{author}"):
                os.makedirs(f"{author}")
            with open(f"{author}/{title}.html", "w") as f:
                f.write(gedicht)

downloader = LyriklineDownloader()
downloader.download_new_poems()
