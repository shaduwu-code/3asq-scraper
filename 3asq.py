# 3asq Berserk Scraper
# ---------------
# Needed for scraping javascript's ajax
from turtle import title
from requests_html import HTMLSession
from socket import timeout
# Wait
import time
# For parsing arguments
import argparse
import sys
# progressbar
from progress.spinner import MoonSpinner
# parse chapter page
from bs4 import BeautifulSoup as bs
# import os to get current working directory
import os
# import progressbar
from alive_progress import alive_bar

# parse arguments from command line
parser = argparse.ArgumentParser(description="Download manga from 3asq.org")
parser.add_argument("-l", "--link", type=str, help='Link of manga')
args = parser.parse_args()
try:
    url = args.link
    manga_name = url.split('/', -1)[4]
except:
    argparse.ArgumentParser.print_help(parser)
    sys.exit()


class Asq():
    def __init__(self, url):
        self.url = url
        self.manga_name = manga_name
        # A dictionary for chapters names and links
        self.chapters_links = {}
        # sets of links (not strings but sets)
        self.links_sets = []
        # links without filtering
        self.links = []
        # only chapters links
        self.clinks = []
        # Initiate html session to load javascript
        self.session = HTMLSession()
        # Images links (chapter panels)
        self.imgs = []
        # chapters order
        self.chapters_order = {}
# get chapters links

    def get_links(self):
        # Initiate html session to load javascript
        r = self.session.get(url)
        # Wait until all elements are rendered
        r.html.render(sleep=1, keep_page=True, scrolldown=2, timeout=100)
        # elements that contain links
        links_containers = r.html.find('a')
        # loop for getting links from elements
        for link in links_containers:
            self.links_sets.append(link.absolute_links)
        # getting links strings from links sets
        for link_set in self.links_sets:
            for link in link_set:
                self.links.append(link)
        # getting only chapters links
        for link in self.links:
            if url.split("/")[-1] in link:
                self.clinks.append(link)
        # removing main manga link from chapters links
        if url == self.clinks[0]:
            self.clinks.remove(self.clinks[0])
        elif url == self.clinks[0]+'/':
            self.clinks.remove(self.clinks[0])
        elif url == self.clinks[0].split("/")[0] + "//" + "www."+self.clinks[0].split("/")[2]+"/"+self.clinks[0].split("/")[3]+"/"+self.clinks[0].split("/")[4] + "/":
            self.clinks.remove(self.clinks[0])
        elif url == self.clinks[0].split("/")[0] + "//" + "www."+self.clinks[0].split("/")[2]+"/"+self.clinks[0].split("/")[3]+"/"+self.clinks[0].split("/")[4]:
            self.clinks.remove(self.clinks[0])
        return self.clinks
# get chapters data

    def get_chapters(self, links):
        # while there is no links, try again
        while links == None:
            time.sleep(5)
            links = self.get.links()

        with MoonSpinner('Getting chapters… ') as bar:
            # Loop for getting final data (chapters names and links)
            for link in links:
                self.chapters_links[link.strip().rsplit(
                    '/', 2)[1]] = link.strip()
                time.sleep(0.03)
                bar.next()
        return self.chapters_links

# get chapters order from website
    def get_chapters_order(self, chapters_links):
        i = 1
        titles = list(chapters_links)
        # loop over chapter titles (official order) and sort them in website order
        for title in titles[::-1]:
            self.chapters_order[title] = i
            i += 1
        return self.chapters_order

    def get_panels(self, chapter_number):
        try:
            # get chapter official number from chapters order
            chapter_number = list(chapters_order.keys())[list(
                chapters_order.values()).index(chapter_number)]
            # get chapter link
            chapter_link = self.chapters_links[chapter_number]
            r = self.session.get(chapter_link)
            soup = bs(r.content, 'html.parser')
            # getting all images from chapter
            imgs = soup.find_all('img', {'class': 'wp-manga-chapter-img'})
            for img in imgs:
                self.imgs.append(img['src'])
            return self.imgs

        except(KeyError):
            print("please enter a valid chapter number")
            sys.exit()

    def download_chapter(self, chapter_number):
        panels = self.get_panels(chapter_number)
        chapter_title = list(chapters_order.keys())[list(
            chapters_order.values()).index(chapter_number)]
        # default setting
        with alive_bar(len(panels), stats=False, bar='bubbles', title=f'Downloading: {chapter_title}') as bar:
            for panel in panels:
                # get current directory to make the path
                cdir = os.getcwd()
                path = f'{cdir}/{manga_name}/{chapter_title}'
                # variable to verify if the path exists
                directory_Exist = os.path.exists(path)
                # if the path exists, check if the panel exists
                if directory_Exist:
                    # variable to verify if the panel exists
                    # panel_exists = os.path.exists(
                    #    f'{path}/{panel.split("/")[-1]}')
                    # # if panel exists, skip it
                    # if panel_exists:
                    #     time.sleep(0.03)
                    #     bar()
                    #     continue
                    # if panel doesn't exist, download it
                   # else:
                    r = self.session.get(panel)
                    with open(f'{path}/{panel.split("/")[-1]}', 'wb') as f:
                        f.write(r.content)
                    time.sleep(0.03)
                    bar()
                # if the path doesn't exist, create it and download the panel
                else:
                    os.makedirs(path)
                    r = self.session.get(panel)
                    with open(f'{path}/{panel.split("/")[-1]}', 'wb') as f:
                        f.write(r.content)

                    time.sleep(0.03)
                    bar()
        # resetting panels for next chapter (avoid duplicates)
        self.imgs = []


# -------------------------------------------------------
# Initialize Asq object
asq = Asq(url=url)
# get chapters links
links = asq.get_links()
# get chapters in official order
chapters = asq.get_chapters(links=links).keys()
# sort chapters in website order
chapters_order = asq.get_chapters_order(chapters_links=chapters)
# print all available chapters and their numbers (website order-official order)
print(
    ','.join(str(f'({chapters_order[chapter]}){chapter}') for chapter in chapters))
# get chapter number from user
chapter_number = input("Enter chapter number: ")
try:
    # check if chapter number is separated by comma (,) and split it to get all chapters numbers
    if ',' in chapter_number:
        chapter_numbers = chapter_number.split(',')
        for chapter_number in chapter_numbers:
            asq.download_chapter(chapter_number=chapter_number)
        sys.exit()
    # check if chapter number is separated by dash (-) and split it to get all chapters numbers
    elif '-' in chapter_number:
        chapters_range = chapter_number.split('-')
        chapter_numbers = []
        for chapter_number in range(int(chapters_range[0]), int(chapters_range[1])+1):
            chapter_numbers.append(chapter_number)
        for chapter_number in chapter_numbers:
            asq.download_chapter(chapter_number=chapter_number)
        sys.exit()
    # if chapter number is not separated by comma or dash, download the chapter
    else:
        asq.download_chapter(chapter_number=int(chapter_number))
        sys.exit()
# if chapter number is not a number, print error message
except(KeyError):
    print("please enter a valid chapter number")
    sys.exit()
# if chapter number is not in the list of available chapters, print error message
except(ValueError):
    print("Chapter number not in the list of available chapters")
    sys.exit()
# if script is closed, print notice message
except(KeyboardInterrupt):
    print("Script has been terminated by user")
    sys.exit()
