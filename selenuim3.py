import time
import pandas
import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

def news_scraping(news_url, wd): #뉴스 본문,댓글 스크랩핑
    try:
        title = wd.find_element_by_id('articleTitle').text
        datetime = wd.find_element_by_class_name('t11').text
        article = wd.find_element_by_id('articleBodyContents').text
        article = article.replace("// flash 오류를 우회하기 위한 함수 추가","")
        article = article.replace("function _flash_removeCallback() {}","")
        article = article.replace("\n","")
        article = article.replace("\t","")

        
        print("뉴스:",[title,datetime,article,news_url])
        return [title,datetime,article,news_url]       
    except Exception:
        pass

        return ['','','','']
    
    


def comments_scarping(url,wd):#뉴스 댓글 스크래핑
    try:
        wd.find_element_by_css_selector('span.u_cbox_in_view_comment').click()
        print("[댓글 더보기]", end="")
        wd.implicitly_wait(10)
        

        while True:
                wd.find_element_by_class_name('u_cbox_btn_more').click()
                print("[더보기]", end="")
                wd.implicitly_wait(10)

            
    except:
        pass

    print("[댓글 스크래핑]")
    comments_idx = 0
    comments_df = pd.DataFrame(columns = ("Contents", "Name", "Datetime","Recommend","Unrecommend","URL"))
    comments = wd.find_elements_by_class_name('u_cbox_comment_box')
    for comment in comments:
        try:
            name = comment.find_element_by_class_name('u_cbox_name').text
            date = comment.find_element_by_class_name('u_cbox_date').text
            contents = comment.find_element_by_class_name('u_cbox_contents').text
            
                
            recomm = comment.find_element_by_class_name('u_cbox_cnt_recomm').text
            unrecomm = comment.find_element_by_class_name('u_cbox_cnt_unrecomm').text
            print(f"    댓글#{comments_idx+1}:", [contents, name, date, recomm, unrecomm,url])
            comments_df.loc[comments_idx] = [contents, name, date, recomm,unrecomm,url]
            comments_idx += 1
        except :
            print("부적절하거나 삭제된 댓글")
            continue
    return comments_df
    


        

def scraping(date): #main함수
    wd = webdriver.Chrome('chromedriver', options=chrome_options)
    wd.implicitly_wait(10)

    wd.execute_script('window.open("about:blank","_blank");')
    tabs = wd.window_handles

    #검색어 서치유알엘을 만들어줌 
    wd.switch_to.window(tabs[0])
    query = "도쿄올림픽"
    search_url = "https://search.naver.com/search.naver?where=news&ie=utf8&sm=nws_hty&query=" + query + "&nso=so%3Ar%2Cp%3Afrom"+date+"to"+date
    print(search_url)
    wd.get(search_url)

    news_idx = 0
    news_df = pd.DataFrame(columns = ("Title","DateTime","Article","URL"))
    comments_df = pd.DataFrame()

    while True:
        inLine_list = wd.find_elements_by_class_name('info_group')
        for inline in inLine_list:
            naver = inline.find_elements_by_css_selector('a.info')
            if len(naver) == 2:
                try:
                    news_url = naver[1].get_attribute('href')
                except:
                    continue
                
                wd.switch_to.window(tabs[1])
                wd.get(news_url)

                news_df.loc[news_idx] = news_scraping(news_url, wd) 
                

                if news_df.loc[news_idx][0] != '': 
                    df = comments_scarping(news_url,wd)
                    comments_df = pd.concat([comments_df, df])

                news_idx += 1
                
                
                wd.switch_to.window(tabs[0])
                
                
        #페이지 넘어가기 위해 다음버튼 클릭        
        nextButton = wd.find_element_by_class_name('btn_next')
        if nextButton.get_attribute("href")==None:
            break
        else:  nextButton.click()

    wd.close()
    return news_df, comments_df


dt_index = pandas.date_range(start = '20210808', end = '20210809')
dates = dt_index.strftime("%Y%m%d").tolist()
dic = {}



for date in dates:
    dic[date] = scraping(date)
    news_df,comments_df = dic[date]

    news_df.to_csv(f'csv/news/{date}.csv',encoding='utf-8-sig')
    comments_df.to_csv(f'csv/comments/{date}.csv',encoding='utf-8-sig')





