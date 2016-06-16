#from django.utils.encoding import smart_str, smart_unicode
from lxml import html
import couchdb
import json
import requests

#def listaDecodificada(list):
#	return [smart_str(w) for w in list]

page = requests.get('https://www.amazon.es/gp/bestsellers/books/ref=amb_link_167590607_5?pf_rd_m=A1AT7YVPFBWXBL&pf_rd_s=merchandised-search-leftnav&pf_rd_r=TQXPHBXPBCAKAZF5QJ71&pf_rd_t=101&pf_rd_p=912542407&pf_rd_i=599364031')
tree = html.fromstring(page.content)
#This will create a list of buyers:
book_title = tree.xpath('//div[@class="zg_title"]/a/text()')
list_price = tree.xpath('//span[@class="listprice"]/text()')
#This will create a list of prices
#prices = tree.xpath('//span[@class="item-price"]/text()')
print 'Titulos: ', book_title
print 'Precios: ', list_price

#Build the JSON Object
merge = []
for bt, lp in zip(book_title,list_price):
	merge.append(dict(titulo=bt,precio=lp))
jsonObj = json.dumps(merge)
print jsonObj