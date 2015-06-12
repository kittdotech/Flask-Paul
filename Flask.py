from flask import Flask, session
from flask import render_template
import os,json
from json import JSONDecoder
from flask import jsonify
from flask import request
from functools import partial
import string
app = Flask(__name__)


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
@app.route('/details')
def page2(name=None):
    path=request.args['json_file']
    sk=request.args['sk']
    session['json_file']=path
    count=0
    section_text={}
    with open(path) as data_file:

        for data in json_parse(data_file):
            selected_info=data.get('article_title',"")
            Summary=data.get('Summary', "")
            Links=data.get('Links', "")
            Hierarchy=data.get('Hierarchy', "")
            Inferences=data.get('Inferences', "")
            Reps=data.get('Reps', "")
            Stats=data.get('Stats', "")


            for a in data['article_sections']:

                section_text.update({str(count):a['section_text']})

                count+=1



    return render_template('details.html',sk=sk,selected_info=selected_info,page=2,section_text=data['article_sections'],Stats=Stats,Reps=Reps,Summary=Summary,Links=Links,Inferences=Inferences,Hierarchy=Hierarchy )

@app.route('/search',methods = ['POST','GET'])
def search(key=None):
    path=os.path.dirname(os.path.abspath(__file__))+'/json'
    json_list={}
    for root, dirs, files in os.walk(os.path.dirname(path)):
        for f in files:
           if f.lower().endswith((".json")):
              try:
                with open(root+'/'+f) as data_file:
                        for data in json_parse(data_file):
                            title=data['article_title']
                            for a in data['article_sections']:
                                str_section=a['section_text']
                                str_find=request.args['sk']

                                res=string.find(str_section.lower() ,str_find.lower())
                                if res!=-1:
                                    json_list.update({root+'/'+f:title})


              except Exception as e:
                print e.message
    if not json_list:
        json_list.update({'error':'NO result found...'})
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
    app.run()
