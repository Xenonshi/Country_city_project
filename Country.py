import pandas as pd
import numpy as np

# import nltk
# nltk.download('words') if needed
# reference to here https://www.nltk.org/data.html

from nltk.corpus import words as english

COUNTRY_LIST = [line.rstrip('\n').lower() for line in open('Country_list.txt')]
US_STATES_LIST =  [line.rstrip('\n').lower() for line in open('US_states_list.txt')]

WORLD_CITIES = pd.read_excel("worldcities.xlsx")
CITY_LIST = [x.lower() for x in WORLD_CITIES['city_ascii'].tolist()]
CITY_TO_COUNTRY = pd.concat([WORLD_CITIES['city_ascii'].str.lower(), WORLD_CITIES['country'].str.lower()], axis=1).\
    reindex(WORLD_CITIES['city_ascii'].str.lower().index).\
    set_index('city_ascii')

NATIONALITIES = pd.read_excel("nationality_to_nation.xlsx")
NATIONALITY_LIST = [x.lower() for x in NATIONALITIES['Adjectivals'].tolist()]
NATIONALITY_TO_COUNTRY = pd.concat([NATIONALITIES['Adjectivals'].str.lower(), NATIONALITIES['Country/entity name'].str.lower()], axis=1).\
    reindex(NATIONALITIES['Adjectivals'].str.lower().index).\
    set_index('Adjectivals')

# VOCAB = set(w.lower() for w in english.words())


def find_names_for_google(df_birth_names):
    """

    :param df_birth_names: 所有的birth data from the data given by Lu
    :return 1: df_country_found,
    返回一个dataframe 里面有国家了

    先通过country list过滤，有些国家可能有问题（如有好几个名字的（e.g. 荷兰），有些含有特殊符号，如刚果布，刚果金，朝鲜，南朝鲜北朝鲜是三个“国家”，
    再比如说南奥塞梯，一些太平洋岛国归属有问题，还就是香港台湾这样的。。。。暂时算是国家）
    而后看看是不是美国的一个州。
    而后看城市，city在city list里面，citylist 参考 worldcities 数据库。 城市重名了就取人口多的那个城市。如Valencia

    :return 2: df_need_google_search,
    返回一个dataframe 里面都是不在“国家列表”里面的，也不是美国的州，并且“worldcities database”里面找不到的

    """
    whitelist = set('abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    # teststr = "   happy t00o go 129.129$%^&*("
    # answer = ''.join(filter(whitelist.__contains__, teststr))

    dirty_list = []
    need_searching_list = []


    for index, row in df_birth_names.head(30).iterrows():

        item = ''.join(filter(whitelist.__contains__, row['birth'])).strip()

        # item = row['birth'].replace("'","").strip()

        if item is "":# null
            dirty_list.append(np.nan)
            print(item, " is null")
            continue

        if item in COUNTRY_LIST:    # known countries
            dirty_list.append(item)
            print(item, " is a country")
            continue

        if item in US_STATES_LIST: # add us states as United States
            dirty_list.append("United States")
            print(item, " is a state in the US")
            continue

        if item in NATIONALITY_LIST: # add national from nationality information e.g. Chinese -> China
            nation_from_nationality = NATIONALITY_TO_COUNTRY.loc[item]["Country/entity name"]
            dirty_list.append(nation_from_nationality)
            print(item, " is a national of a certain country")
            continue

        if item in CITY_LIST: # known city to country e.g. London -> UK
            country_from_city = CITY_TO_COUNTRY.loc[item]["country"]
            dirty_list.append(country_from_city)
            print(item, " is a city and it has been transformed")
            continue


        flag1=0 # known city to country e.g. London -> UK
        for i in COUNTRY_LIST:
            if i in item:
                dirty_list.append(i)
                print(i, " maybe a country")
                flag1 = 1
                break
        if flag1 == 1:
            continue

        flag2 = 0
        for i in US_STATES_LIST:
            if i in item:
                dirty_list.append("United States")
                print(i, "maybe a state in the US")
                flag2 = 1
                break
        if flag2 == 1:
            continue

        flag3 = 0
        for i in CITY_LIST:
            if i in item:
                country_from_city = CITY_TO_COUNTRY.loc[i]["country"]
                dirty_list.append(country_from_city)
                print(i, " maybe a city, and we are attempting to transform it")
                flag3 = 1
                break
        if flag3 == 1:
            continue


        need_searching_list.append(item)
        print("this item: ", item, " is not added")

    need_searching_list = list(dict.fromkeys(need_searching_list))#     remove duplicates

    df_country_found = pd.DataFrame(dirty_list)
    df_need_google_search = pd.DataFrame(need_searching_list)


    return df_country_found, df_need_google_search

def read(fpath):
    """
    :rtype: a dataframe read
    """
    df = pd.read_stata(fpath)
    return df

if __name__ == "__main__":
    fpath = "list.dta"

    df = read(fpath)
    df_country_found, df_need_google_search = find_names_for_google(df)

    print('df_need_google_search的长度 ', len(df_need_google_search))
    print('df_country_found 长度: ', len(df_country_found))

    # df_temp = clean_names(read(fpath))
    # print(df_temp)