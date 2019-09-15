"""
A web crawler that automatically plays the Getting to Philosophy game on Wikipedia.

By navigating to a Wikipedia article and clicking the first link in the body of the article that is not parenthesized,
and repeating this for each new page you visit, you are almost guaranteed to eventually reach the page on Philosophy.
This program asks the user for the title of a Wikipedia article and follows this path of links automatically.
"""

import requests
from bs4 import BeautifulSoup as bs

while True:
    start = input("What page will you start on? ")
    url = "https://en.wikipedia.org/wiki/" + "_".join(start.split())
    titles = []

    while True:
        # Downloads the page
        res = requests.get(url)
        try:
            res.raise_for_status()
            res_soup = bs(res.text, features="html.parser")

            title = res_soup.select("#firstHeading")[0].getText()
            print(title)

            # Ends the search if we get to philosophy or to a page we've already seen (which signals a loop)
            if title in titles:
                print("Loop found! Wow!")
                break
            elif title == "Philosophy":
                print(f"\nFinished in {len(titles)} steps.")
                break

            # Continues the search if neither of these are true
            else:
                titles.append(title)
                paragraphs = res_soup.select(".mw-parser-output > p")  # Gets a list of paragraphs on the page
                for p in paragraphs:
                    found_url = False

                    anchors = p.select("a")  # Gets a list of links in the current paragraph

                    # Finds the first link that isn't in parentheses by checking if all text before the link has the same
                    # number of opening and closing parentheses
                    for a in anchors:
                        link = a.get("href")
                        before_link = str(p).split(link)[0]
                        if link.startswith("/wiki") and (before_link.count("(") == before_link.count(")")):
                            url = "https://en.wikipedia.org" + link
                            found_url = True
                            break
                    if found_url:
                        break

                else:
                    print("There were no valid links on this page!")
                    break
        except requests.exceptions.HTTPError:
            print("Invalid Wikipedia link.\n")
            break

    play_again = input("Play again? (y/n) ").lower() == "y"
    if play_again:
        print()
    else:
        break
