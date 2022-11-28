# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
import PyPDF2

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from owlready2 import *
import numpy as np
from autocorrect import Speller

spell = Speller(lang='en')

def change(w):
    w=str(w).replace('Ontology_PMBOKV2.0.','').replace('_',' ')
    return w

def RechercheOntology(concepet):
    for element in list(onto.classes()):
        if concepet.lower().replace(' ','_') in str(element):
            return element
    return ""

processes=['plan risk management','identify risks','perform qualitative  risk analysis','perform quantitative  risk analysis','plan risk responses','control risks']

dict_processes={'plan risk management':'&P1',
 'identify risks':'&P2',
 'perform qualitative  risk analysis':'&P3',
 'perform quantitative  risk analysis':'&P4',
 'plan risk responses':'&P5',
 'control risks':'&P6'}

onto_path.append("/home/ayadi/Documents/ProjectAi/")
onto = get_ontology("Ontology_PMBOKV2.0.owl").load()

list_classes=list(onto.classes())
    
list_classes_new=[change(classe) for classe in list_classes]
docs = [(classe) for classe in list_classes_new ]
    
tfidf_vectorizer = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf_vectorizer.fit_transform(docs)

def isSubOfProcess(classe):
    if ('inputs' in classe or ('outputs' in classe) or ('tools' in classe )):
        return True
    else :
        return False
def isProcess(classe):
    if classe in processes:
        return True
    else : 
        return False
def get_process_name(classe):
    return classe.replace('tools and techniques','').replace('inputs','').replace('outputs','').strip()

def get_annotation(process,list_annotation):
    for annotation in list_annotation:
        if (dict_processes.get(process) in  annotation):
            return annotation
    return ""
def get_list_annotation(process,process_sub):
    list_annotations=[]
    for element in process_sub.subclasses():
        list_annotations.append(get_annotation(process,element.comment))
    return list_annotations  
def get_subclasses(Type,classe):
    list_subclasses=[]
    for element in classe.subclasses():
        if Type in change(str(element)):
            for value in element.subclasses():
                list_subclasses.append(change(str(value)))
    return list_subclasses    

def list_Instance(instance):
    list_ancestors=instance.ancestors()
    list_ancestors=[change(value) for value in list_ancestors]
    list_ancestors =[ classe for classe in list_ancestors if ('inputs' in classe or ('outputs' in classe) or ('tools' in classe ) )]
    return list_ancestors
    

def Recommande(query):
    isSubProcess,isaProcess,is_instance,is_found=False,False,False,True
    concept=np.nan        
    query_vector = tfidf_vectorizer.transform([query])
    list_sim=cosine_similarity(query_vector, tfidf_matrix)[0].tolist()
    max_sim_term=max(list_sim)
    if(max_sim_term<0.2):
        is_found=False
    index=list_sim.index(max_sim_term)
    keyword=list_classes_new[index]
    #print(keyword)
    #concept=RechercheOntology(keyword)
    concept=list_classes[index]
    if len(list_Instance(concept))>0 :
        is_instance=True
    if (concept!=np.nan):
        keyword=change(concept)
    if (isSubOfProcess(keyword)):
        isSubProcess=True
        is_instance=False
    if (isProcess(keyword)):
        isaProcess=True     
    return keyword,concept,[isaProcess,isSubProcess,is_instance],list_Instance(concept),is_found
pdfFileObj = open('PMBOK5th.pdf', 'rb')
pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
table_figures=""
for i in range(15,26):
    my_page = pdfReader.getPage(i)
    table_figures=table_figures+my_page.extractText()
table_figures=table_figures.replace("\n"," ").replace("..","")
def extract_text(text,startT,endT):
    start = text.find(startT) + len(startT)
    end = text.find(endT)
    substring = text[start:end]
    return substring
def to_int(text):
    page=""
    i=0
    for s in text:
        if(s.isdigit()):
            page=page+s
            i=i+1
            if(i==3):
                break;
    page=int(page)
    return page
def extracy_figure_page(annotation,table_figures):
    dict_Figure={}
    listF=re.findall(r'Figure +.[0-9]+-[0-9].', annotation)
    for figure in listF:
        figure=figure.replace('.','').strip()
        last_number=int(figure[-1])
        page=extract_text(table_figures,figure,figure[:-1]+str(last_number+ 1))
        dict_Figure[figure]=to_int(page)+26
    return dict_Figure
def get_section_page(comment):
    if "Section" in comment:
        section=extract_text(comment,"Section",". ").strip()+" "
        index=0
        n=int((section).split('.')[0])
        l=[]
        if n in range(1,5):
            l=[27,130]
        elif n in range(5,8):
            l=[130,252]
        elif n in range(8,12):
            l=[253,380]
        else :
            l=[381,500]
        for i in range(l[0],l[1]):        
            page=pdfReader.getPage(i)
            if (section in page.extractText()):
                index=i
                return index+1

    return 
    


def index(request):
    search=""
    context = {'segment': 'index'}
    if request.method == 'POST':
        send=search=request.POST["send"]
        print(send)
    if "search" in request.GET:
        search=request.GET["search"]
        search=spell(search)
        
        

        recommendation=Recommande(search.replace('TT','tools and techniques').replace('tt','tools and techniques'))
        list_change=[change(classe) for classe in list(recommendation[1].subclasses())]
        
        is_process=recommendation[2][0]
        is_sub_process=recommendation[2][1]
        is_instance=recommendation[2][2]
        is_found=recommendation[-1]
        #context={'concepts':list_change}
        #context={'comments':comments}
        #print(list(recommendation))
        if (is_process):
            comment=recommendation[1].comment[0]
            links=extracy_figure_page(comment,table_figures)
            for key in links.keys():
                comment=comment.replace(key,'')
            


            comments=get_list_annotation(get_process_name(recommendation[0]),recommendation[1])
            mylist = zip(list_change, comments)
            context={ 'inputs' :get_subclasses("inputs",recommendation[1]),
            'outputs' :get_subclasses("outputs",recommendation[1]),
            'tools' :get_subclasses("tools and techniques",recommendation[1]),
            'process_annotation':comment,
            'mylist':mylist,
            'is_process':is_process,
            'is_sub_process':is_sub_process,
            'is_instance':is_instance,
            'links':links}
        if (is_sub_process):
            comments=get_list_annotation(get_process_name(recommendation[0]),recommendation[1])
            
            mylist = zip(list_change, comments)
            context={ 
            'mylist':mylist,
            'is_process':is_process,
            'is_sub_process':is_sub_process,
            'is_instance':is_instance
            }
        if (is_instance):
            comments=get_list_annotation(get_process_name(recommendation[0]),recommendation[1])
            mylist = zip(list_change, comments)
            context={ 
            'mylist':mylist,
            'is_process':is_process,
            'is_sub_process':is_sub_process,
            'is_instance':is_instance,
            'annotation':recommendation[1].comment[0],
            'ancestors':recommendation[3]
            }

        if(is_found):
            if ( True not in list(recommendation[2])):
                context={
                    'key_word': recommendation[0],
                    'comment': recommendation[1].comment,
                    'sub_class': list_change
                }
        else:
            context={'is_found':is_found}
    else:
        print("nnnnnnnnnnn")
        context = {'is_vide': True}

 


        
  


    html_template = loader.get_template('index.html')
    return HttpResponse(html_template.render(context, request))


def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:

        load_template = request.path.split('/')[-1]

        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        context['segment'] = load_template

        html_template = loader.get_template(load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('page-404.html')
        return HttpResponse(html_template.render(context, request))

    except:
        html_template = loader.get_template('page-500.html')
        return HttpResponse(html_template.render(context, request))
