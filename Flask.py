from flask import Flask, session
from flask import render_template
import os,json
from json import JSONDecoder
from flask import jsonify
from flask import request
from functools import partial
import string
import re
import types

app = Flask(__name__)

from collections import Mapping, Set, Sequence

# dual python 2/3 compatability, inspired by the "six" library
string_types = (str, unicode) if str is bytes else (str, bytes)
iteritems = lambda mapping: getattr(mapping, 'iteritems', mapping.items)()



import types

def walk(node):
	str=""
	if type(node) is types.UnicodeType:
		return node
	if type(node) is types.DictType:

		for key, item in node.items():
			if type(item) is types.DictType:
				str+=key+" : \n{}".format(walk(item))
			elif type(item) is types.ListType:
				str+=key+" : \n{}".format(walklist(item))

			else:
				str+=key+" : {}".format(item)

			str+='\n'


	if type(node) is types.ListType:

		for item in node:

			if type(item) is types.DictType:

				if str=="":

					str+="{}".format(walk(item))
				else:
					str="{}, {}".format(str,walk(item))
			else:
				if str=="":
					str+="{}".format(item)
				else:
					str="{}, {}".format(str,item)



	return str
def walklist(node):

	if type(node) is types.ListType:
		str=""
		flag=1
		for idx,item in enumerate(node):


			if type(item) is types.DictType or type(item) is types.ListType:

					str=str+"\n{}".format(walk(item))

			else:
				if str=="":
					str=str+"{}".format(item)
				else:
					str=str+",{}".format(item)



	return str

def objwalk(obj, path=(), memo=None):
    if memo is None:
        memo = set()
    iterator = None
    if isinstance(obj, Mapping):
        iterator = iteritems
    elif isinstance(obj, (Sequence, Set)) and not isinstance(obj, string_types):
        iterator = enumerate
    if iterator:
        if id(obj) not in memo:
            memo.add(id(obj))
            for path_component, value in iterator(obj):
                for result in objwalk(value, path + (path_component,), memo):
                    yield result
            memo.remove(id(obj))
    else:
        yield path, obj

@app.route('/apis')
def apis(name=None):
    return render_template('apis.html',name=name)




@app.route('/settings')
def settings(name=None):
    return render_template('settings.html',name=name)

@app.route('/index')
def index(name=None):
    sk=request.args.get('sk',"")
    return render_template('index.html',name=name,page=1,sk=sk)
    #return 'hello'

@app.route('/search',methods = ['POST','GET'])
def search(key=None):
    path=os.path.dirname(os.path.abspath(__file__))
    json_list={}
    for root, dirs, files in os.walk(os.path.join(path,'json')):
        for f in files:
           if f.lower().endswith((".json")):
              try:
                count=1
                with open(os.path.join(root,f)) as data_file:
                        for data in json_parse(data_file):
                            title=data['wiki']['article_title']
                            articles=[]
                            collection={}
                            found=False

                            for a in data['wiki']['article_sections']:

                                    str_section=re.sub(r'\n[\n]*', r'<br/><br/>', a['section_text'])
                                    section_number=a['section_number']
                                    str_section_name=a['section_name']
                                    str_find=request.args['sk']

                                    articles.insert(section_number,{str_section_name:str_section})
                                    res=string.find(str_section.lower() ,str_find.lower())

                                    if res!=-1:
                                        found=True


                                        if not collection:
                                            Summary=data.get('Summary', " ")

                                            Links="<table cellspacing='10'>"
                                            for k in data['triples']['link_subs']:
                                                Links+=("<tr><td>"+k[0]+"</td><td>"+k[1]+"</td><td>"+k[2]+"</td></tr>")
                                            Links+="</table>"

                                            Hierarchy=""
                                            for k in data['wm']['textReps']['reps']:
                                                level=k['level']
                                                if not k['children']:
                                                    Hierarchy+=('<p class="hierarchy-all" style="padding-left:' + str(level*50)+'px;">'+k['sentence']+'</p><br/><br/>')
                                                else:
                                                    Hierarchy+=('<p class="hierarchy-all hierarchy-child" style="padding-left:'+ str(level*50)+'px;">'+k['sentence']+'</p><br/><br/>')
                                            Inferences=walk(data.get('Inferences', ""))
                                            Reps=walk(data.get('Reps', ""))
                                            Stats=walk(data.get('Stats', ""))
                                            collection.update({'Summary':Summary})
                                            collection.update({'Links':Links})


                                            collection.update({'Hierarchy':Hierarchy})
                                            collection.update({'Inferences':Inferences})
                                            collection.update({'Reps':Reps})
                                            collection.update({'Stats':Stats})

                            if found:
                                json_list.update({title:{'articles_details':articles,'collection_details':collection}})



              except Exception as e:
                print e.message
    if not json_list:
        json_list.update({'error':'NO result found...'})
    #print json_list
    return jsonify(json_list)
    #return 'hello'


def json_parse(fileobj, decoder=JSONDecoder(), buffersize=2048):
    buffer = ''
    for chunk in iter(partial(fileobj.read, buffersize), ''):
         buffer += chunk
         while buffer:
             try:
                 result, index = decoder.raw_decode(buffer)
                 yield result
                 buffer = buffer[index:]
             except ValueError:
                 # Not enough data to decode, read more
                 break





if __name__ == '__main__':
    app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
    app.run(host='0.0.0.0',port=5001)
