'''
# @ author: Takfarinas Saber
# @ about: this code searches information on Wikipedia about a given term and prints the result
# @ usage: python3 wiki.py term 
#       e.g., python3 wiki.py "Barack Obama"
'''

import wikipedia
import sys

def searchWikipedia(term):
    pageIds = wikipedia.search(term)
    pages = []
    for pageId in pageIds:
        try:
            page = wikipedia.page(pageId)
            pages.append(page)
        except:
            print("Oups: could not parse the page:", pageId)
            pass
    if len(pages) >= 0:
        for page in pages:
            print("title: " + page.title + " URL: " + page.url + " Content: " + page.content)
    else:
        return "No results!"

arguments = "".join(sys.argv[1:]) ## read the arguments (i.e., the search term)
searchWikipedia(arguments)

