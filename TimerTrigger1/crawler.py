import requests # pulling data
from bs4 import BeautifulSoup # xml parsing
import json # exporting to files
import pandas as pd
#from .preprocandindex import * 
import pickle
import datetime
import logging
import os
#import azure.functions as func
from azure.storage.blob import BlobServiceClient

from TimerTrigger1 import preprocandindex

def save_pickle_to_azure_blob(pickle_data, container_name, blob_name):
    # Connect to Azure Blob Storage
    connection_string = "DefaultEndpointsProtocol=https;AccountName=searchenginestrg;AccountKey=LB3Y3pG2mzMkxYzE6M8fBHuspzJTOTR+NZlm3Dv29jSsAszGmY111rLntxYAsZR82p/Wh3y/jGZ2+AStWWThUQ==;EndpointSuffix=core.windows.net"
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    # Get a reference to the container
    container_client = blob_service_client.get_container_client(container_name)

    # Save the pickle data to Azure Blob Storage
    blob_client = container_client.get_blob_client(blob_name)
    blob_client.upload_blob(pickle_data, overwrite=True)


def get_authors_list(publication_url):
    """Author List Scrapped from Publication Pages"""
    try:
        page = requests.get(publication_url)
        Soupobj2 = BeautifulSoup(page.text,"html.parser")
        authorlist=Soupobj2.find_all("p",{"class":'relations persons'})
        #print(authorlist)
#=============================================================================
        for authors in authorlist:
            print('--')
            #print(authors)
            print('--')
            authorlist=authors.text
            #print(authorlist)
            try:
                authorlink=authors.find('a',{"class":'link person'})['href'] 
                covuniauthor=authors.find('a',{"class":'link person'}).text
            except:
                authorlink=''
                covuniauthor=''
                
                
            return covuniauthor, authorlink, authorlist
#=============================================================================
    except Exception as e:
        print('The scraping job failed in Author List')
        print(e)    
        
 
# scraping function
def webcrawler():
    logging.info('Web crawler function triggered.')
  #  pub_list = []
    Datalist=[] 
    
    try:
        pgurl = "https://pureportal.coventry.ac.uk/en/organisations/school-of-economics-finance-and-accounting/publications/?page="
        #looping over the site
        
        for pagenum in range(0,1):
          url=pgurl +str(pagenum)
          print(url)
          page = requests.get(url)
          #print(page.text)
          soup = BeautifulSoup(page.text,"html.parser")
          publicationInfo= soup.find_all("a",{"rel":['ContributionToJournal','WorkingPaper','ContributionToBookAnthology','ContributionToConference','BookAnthology','OtherContribution','Thesis','ContributionToPeriodical']})

          date= soup.find_all(True,{"class":"date"})
#=============================================================================
          #Looping over each Publication
          for index in range(0, len (publicationInfo)):
            
            covuniauthor, authorlink, authorlist = get_authors_list(publicationInfo[index]['href'])  
            paper = {
              'Title':publicationInfo[index].string,
              'PublicationLink':publicationInfo[index]['href'],
              'AuthorName': covuniauthor,
              'AuthorProfile': authorlink,
              'DatePublished':date[index].string,
              'AuthorList': authorlist
              }
            print(json.dumps(paper,indent=2))
            Datalist.append(paper)
            #print(Datalist)
            #dumping data in json format for later use
            
        df=pd.DataFrame(Datalist)
       # save_function(Datalist)
        #print(json.dumps(paper,indent=2))
        data=df['Title']+df["AuthorList"]+df["DatePublished"]
        preprocessed_data = preprocandindex.preprocess_data(data.tolist())
        inverted_index = preprocandindex.InvertedIndex(preprocessed_data)
        idf_scores = preprocandindex.idfCalculator(preprocessed_data)
        scores = preprocandindex.tfidfCalculatorData(preprocessed_data,idf_scores)
        inverted_index_pickle = pickle.dumps(inverted_index)
        idf_scores_pickle = pickle.dumps(idf_scores)
        scores_pickle = pickle.dumps(scores)
    
        container_name = "searchenginepickle"
        # Save the inverted index pickle to Azure Blob Storage
        inverted_index_blob_name = "inverted_index.pkl"
        save_pickle_to_azure_blob(inverted_index_pickle, container_name, inverted_index_blob_name)
        # Save the IDF scores pickle to Azure Blob Storage
        idf_scores_blob_name = "idf_scores.pkl"
        save_pickle_to_azure_blob(idf_scores_pickle, container_name, idf_scores_blob_name)
        # Save the TF-IDF scores pickle to Azure Blob Storage
        scores_blob_name = "scores.pkl"
        save_pickle_to_azure_blob(scores_pickle, container_name, scores_blob_name) 
        return df,Datalist

    except Exception as e:
    
        print('The scraping job failed. See exception:')
        print(e)    
#webcrawler
#webcrawler()