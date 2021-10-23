"""
Real simple stuff

1. Scrapes the wiki for the current items Baro is selling on PC, and how many Ducats they cost.
2. Scrapes warframe.market to get an approximate value of how much they're worth.
    -> This is done fast and loose. It should catch all Mods, but might miss some other items.
3. For the items you can sell, prints out a quick ratio of plat per 100 ducats the item costs.

This is a console application, so run it from a command line or from an IDE.
"""


import requests

res = requests.get('https://warframe.fandom.com/wiki/Baro_Ki%27Teer/Current_PC_Items')
text = res.text

def backtrack(string, stopAt):
    pos=len(string)-1
    ret=""
    while pos >= 0 and pos < len(string) and string[pos] != stopAt:
        ret = string[pos]+ret
        pos -= 1
    return ret

#just get the important stuff\
pos = text.find("gallery-0")
text = text[pos : text.find("mw-empty-elt", pos)]

sales={}

#repeat until you can't find another
pos = text.find("lightbox-caption", 1)
while pos != -1:
    """
        structure is:
        <div id="gallery-0"
            <div class="wikia-gallery-item"
                <div class="lightbox-caption"
                    <span OR a>Name</span or /a>
                    ...
                    <span class="mobile-hidden"><a></a>&#160;DUCATS</span>
                    ...
                    <span class="mobile-hidden"><a></a>&#160;CASH</span>
                    ...
                </div>
            </div>
        </div>
        basic idea:
        find gallery-0
        repeat until you hit the end
        find the first /span or /a, backtrack to find the name
        find the next /span, backtrack to find the ducats
        find the next /span, backtrack to find the cash
    """

    #--get name--

    end = min(text.find("</a>",pos),text.find("</span>",pos))
    name = backtrack(text[pos:end], ">")

    #--get Ducats--

    end = text.find("</span>",text.find("</span>",end+1)+1)
    ducs = backtrack(text[pos:end], ">")
    ducs = ducs[6:] #get rid of starting &#160;

    #--get Credits--

    end = text.find("</span>",text.find("</span>",end+1)+1)
    creds = backtrack(text[pos:end], ">")
    creds = creds[6:] #get rid of starting &#160;

    pos = text.find("lightbox-caption", pos+1)

    sales[name] = (int(ducs), creds)

"""
We have all of the current sales: check plat values, calculate ratio
"""

for key in sales.keys():
    res = requests.get("https://warframe.market/items/" + key.lower().replace(" ","_")).text

    if len(res) < 100:
        #print(key + " didn't work")
        continue

    #attempting to get the price really quickly
    priceLoc = res.find("\"order_type\": \"sell\", \"platinum\": ") + 34
    minPrice = 100000
    while priceLoc != 33: #adding 34 to it, so a result of -1 (miss) will turn into 33
        price = res[priceLoc : res.find(",", priceLoc)]
        minPrice = min(int(price), minPrice)
        priceLoc = res.find("\"order_type\": \"sell\", \"platinum\": ", priceLoc+1) + 34

    print(key, ": Plat:", minPrice,"  => Plat/100 Ducats =", round(100*minPrice/sales[key][0],2))
