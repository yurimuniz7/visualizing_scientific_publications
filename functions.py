import requests
import time
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def get_metadata(api_key,query):
    """Return metadata from the Springer Nature API in JSON format."""
    url = "http://api.springer.com/metadata/json?api_key="+api_key+'&q='+query
    data = requests.get(url).json()
    return data

def top_countries(api_key,years,topics=[''],journals=['']):
    """Create a pandas dataframe with the countries with more publications by topic and by journal.

    The datarame columns are year, country, and the number of publications related to all topics in the
    topics list, all journals in the journals list, and all topics in each journal. The empty string can
    be used to get publications of all topics (and/or every journal in Springer Nature)
    """
    df = pd.DataFrame()

    cols = ['year','country']
    for topic in topics:
        cols = cols +["publications_"+topic]
        for journal in journals:
            cols = cols + ["publications_"+topic+"_on_"+journal]

    for year in years:
        df_year = pd.DataFrame(columns=['value'])

        for topic in topics:
            query = 'year:'+str(year)+'+'+topic+'+type:Journal&p=0'
            data = get_metadata(api_key,query)
            if data['facets'][-2]['values'] == []:
                df_topic = pd.DataFrame(columns=['value',"publications_"+topic])
            else:
                df_topic = pd.DataFrame(data['facets'][-2]['values']).rename(columns={"count": "publications_"+topic})
            df_year = pd.merge(df_year,df_topic,on='value',how='outer')
            time.sleep(1)
            for journal in journals:
                query = 'year:'+str(year)+'+'+topic+'+journal:'+journal+'+type:Journal&p=0'
                data = get_metadata(api_key,query)
                if data['facets'][-2]['values'] == []:
                    df_topic_journal = pd.DataFrame(columns=['value',"publications_"+topic+"_on_"+journal])
                else:
                    df_topic_journal = pd.DataFrame(data['facets'][-2]['values']).rename(columns={"count": "publications_"+topic+"_on_"+journal})
                df_year = pd.merge(df_year,df_topic_journal,on='value',how='outer')
                time.sleep(1)

        df_year['year'] = year
        df = pd.concat([df,df_year],ignore_index=True)

    df = df.rename(columns={"value": "country"})[cols]
    return df

def compare_publications(df,countries,topic,journal):
    """Generate a lineplot with years in the horizontal axis and publications on the vertical axis.

    The plot compares the total number of publications of different countries in a specific topic and journal
    """
    df_countries = df[df['country'].isin(countries)]

    fig,ax = plt.subplots(1,2,figsize=(15,5))
    for country in countries:
        ax[0].plot(df_countries[df_countries['country']==country]['year'],\
                   df_countries[df_countries['country']==country]['publications_'+topic], linewidth = 2)
        ax[1].plot(df_countries[df_countries['country']==country]['year'],\
                   df_countries[df_countries['country']==country]['publications_'+topic+'_on_'+journal],\
                   linewidth = 2,label = country)

    fig.suptitle(topic.capitalize(),fontsize=18)
    ax[1].legend(bbox_to_anchor=(1, 1))
    ax[0].set_xticks(list(range(2000,2021,2)))
    ax[0].set_xlim(2000,2020)
    ax[0].set_xlabel('Year')
    ax[0].set_ylabel('# of publications')
    ax[1].set_xticks(list(range(2000,2021,2)))
    ax[1].set_xlim(2000,2020)
    ax[1].set_xlabel('Year')
    ax[1].set_ylabel('# of publications on '+journal.capitalize())

    plt.show()
