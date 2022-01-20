"""Tool to make easy downloading multiple video lectures from Sharepoint
Needed to be able to study offline"""

import os
import re
import tkinter
import tkinter.filedialog
import webbrowser
from time import sleep

import tqdm

TIMEOUT = 60  # in seconds

# regexp for courses - found by experiment
LINK_REGEX_EXPERIMENTAL = re.compile(
    r'<video class="vjs-tech" playsinline="" preload="auto" src|data-savepage-src="(http|https:\/\/epam.*?)"'
)
LOAD_LIMIT = 2  # sharepoint downloading faces problems with loading more than 2 files at a time


def get_dir_path():
    """Use tkinter to let user choose a dir where he saved htmls"""
    tkinter.Tk().withdraw()
    # we don't want a full GUI, so keep the root window from appearing

    dirname = tkinter.filedialog.askdirectory()
    # show an "Open" dialog box and return the path to the selected file
    if dirname:
        print(f"Location chosen:\n{dirname}")
    return dirname


def parse_load_link_from_html(html_file, compiled_regexp=LINK_REGEX_EXPERIMENTAL):
    """Open html page file and use regexp to get video recording link from it"""
    matches = []
    if os.path.isfile(html_file):
        print('File found')
        with open(html_file, 'r', encoding='utf-8') as html:
            for line in html:
                for match in re.finditer(compiled_regexp, line):
                    print('Downloading link found!')
                    load_link = match.group(1)
                    matches.append(load_link)
            if matches:
                return matches
            print('Downloading link not found!\n')
            return None
    raise FileNotFoundError(f"{html_file} not found!")


def download_with_chrome(load_link, running_loads, timeout=TIMEOUT, load_limitation=LOAD_LIMIT):
    """Opening a download link once in a comfortable period not to be banned for ddos"""
    running_loads += 1
    webbrowser.open(load_link)
    if running_loads > load_limitation:
        print('Too many loads at time, need some chill...')
        sleep(1)
        for i in tqdm.tqdm(range(timeout)):
            sleep(1)
        running_loads -= 1
    return running_loads


def proceed_with_htmls(htmls_location):
    """Go through html files in folder passed as arg to get the loading link from them and open it in browser"""
    running_loads = 0
    if os.path.exists(htmls_location):
        for root, dirs, files in os.walk(htmls_location):
            if files:
                for file_inside_folder in files:
                    extension = os.path.splitext(file_inside_folder)[1][1:]
                    if extension not in ('html', 'htm'):
                        print('Not an html file, skip.')
                    else:
                        current = os.path.join(root, file_inside_folder).replace(os.sep, os.sep*2)
                        print(f'Getting link from file:\n{current}')
                        load_links = parse_load_link_from_html(current)
                        if load_links:
                            for item in load_links:
                                print(item)
                                download_with_chrome(item, running_loads)
                                print('Download started. Can pass to next.\n')
            break  # not to dig into subdirs
    print('\n --- FINISHED --- \n')


if __name__ == '__main__':
    proceed_with_htmls(get_dir_path())
