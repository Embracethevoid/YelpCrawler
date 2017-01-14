import requests
from bs4 import BeautifulSoup
import ast
# import mysql.connector
import pymysql
import datetime

class YelpCrwaler:

    add_poster = ('INSERT INTO Poster''(Name,City,State,User_ID,Hovercard_ID)''VALUES(%s,%s,%s,%s,%s)')
    add_review = ('INSERT INTO Review''(Time,Content,Stars,Useful,Funny,Cool,Picture_Num,Store_Info_ID1,Poster_Hovercard_ID,IfRecommended)''VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)')
    add_store_info = ('INSERT INTO Store_Info''(Name,Latitude,Longitude,Price_Range,City,State,Start_Year,Store_Info_ID,Opentime,Closetime,Rate)''VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)')
    add_stars_month_year = ('INSERT INTO Stars_Month_Year''(Year,Month,Average_Star,Store_Info_ID)''VALUES(%s,%s,%s,%s)')
    add_Store_Category = ('INSERT INTO Store_Category''(Category,Store_Info_ID)''VALUES(%s,%s)')
    add_not_rec_review = ('INSERT INTO Review''(Time,Content,Stars,Picture_Num,Store_Info_ID1,Poster_Hovercard_Id,IfRecommended)''VALUES(%s,%s,%s,%s,%s,%s,%s)')
    BASE_URL = 'http://www.yelp.com'

    def __init__(self):
        self.cnx = self.connnect_mysql()
        self.cnx.autocommit(True)
        self.cursor = self.connnect_mysql().cursor()

    def InsertMysql(self,add,data):
        T = add.split('(')[0].split()[-1]
        try:
            self.cursor.execute(add, data)
            self.cnx.commit()
            print('sucessfully stored %s'%T)
        except Exception as e:
            if add == 'INSERT INTO Poster(Name,City,State,User_ID,Hovercard_ID)VALUES(%s,%s,%s,%s,%s)' and data[3] != None:
                try:
                    self.cursor.execute('UPDATE Poster SET User_ID = \'%s\' WHERE Hovercard_ID = \'%s\''%(data[3],data[4]))
                    print('Updated Poster Info')
                except Exception as e1:
                    print (e1,T)
            print (e,T)

    def Get_Major_Info(self,url,p):   # returns the the store: name, food type, price range, yelp since(year), location(latitude,longitude)
        soup = BeautifulSoup(requests.get(url).content)
        # [i.id,i.name,i.categories,i.location.coordinate.latitude,i.location.coordinate.longitude,i.location.city,i.location.state_code]
        biz_id = p[0]
        biz_name = p[1]
        category = p[2]
        la = p[3]
        lo = p[4]
        city = p[5]
        state = p[6]
        rating = p[7]
        # try:
        #     biz_name = soup.find_all('h1')[0].text.strip()
        # except:
        #     biz_name = ''
        # category = []
        # try:
        #     span = soup.find('span',class_ = 'category-str-list')
        #     for i in span.text.split(','): #this part contains the category of the store
        #         category.append(i.strip())
        # except:
        #     pass
        # try:
        #     whole_location = soup.find_all('address')[-1].find('br').next.strip()
        #     city = whole_location.split(',')[0]
        #     state = whole_location.split(',')[1].split()[0]
        # except:
        #     city = ''
        #     state = ''
        # try:
        #     temp = soup.find_all('div', class_ = 'lightbox-map hidden')[0]['data-map-state']
        #     p = temp.find('lati')
        #     q = temp[p:].find('}')
        #     loct = ast.literal_eval(temp[p-2:p+q+1])
        #     la = float(loct['latitude'])
        #     lo = float(loct['longitude'])
        # except:
        #     la = None
        #     lo = None
        try:
            runtimes = soup.find_all('li',class_ = 'biz-hours iconed-list-item')[0].find('strong').text.strip()

            j = runtimes.split('-')[0].strip()
            hour =  int(j.split()[0].split(':')[0]) + 12*(j.split()[1] == 'pm')
            minute = j.split()[0].split(':')[1]
            opentime = str(hour)+':'+minute

            j = runtimes.split('-')[1].strip()
            hour =  int(j.split()[0].split(':')[0]) + 12*(j.split()[1] == 'pm')
            minute = j.split()[0].split(':')[1]
            closetime = str(hour)+':'+str(minute)

        except:
            opentime = ''
            closetime = ''
        month_year_star = []
        try:
            # price_range = soup.find_all('div',class_ = 'icon-list-story').find_all('dl')[0].text.strip().split(' ')[-1]   #this part returns the price range of the store
            price_range = soup.find_all('dd',class_= 'nowrap price-description')[0].text.strip()
        except:
            price_range = ''
        try:
            all_review_pages = int(soup.find_all('div',class_= 'page-of-pages arrange_unit arrange_unit--fill').text.strip().split(' ')[-1])
        except:
            all_review_pages = 1
        try:
            for i in ast.literal_eval(soup.find('div',id= 'rating-details-modal-content')['data-monthly-ratings']).items():
                year = int(i[0])
                for e in i[1]:
                    month = e[0]+1
                    av_stars = e[1]
                    month_year_star.append([year,month,av_stars])
        except:
            pass
        try:
            not_rec_url = soup.find('a',class_ = 'subtle-text inline-block js-expander-link')['href']
        except:
            not_rec_url = ''

        try:
            start_year = int(soup.find('p',class_='rating-details-ratings-info').text.strip().split(' ')[2])
        except:
            start_year = None
        data_store = (biz_name,la,lo,price_range,city,state,start_year,biz_id,opentime,closetime,rating)
        self.InsertMysql(self.add_store_info,data_store)
        for c in category:
            data_category = (c,biz_id)
            self.InsertMysql(self.add_Store_Category,data_category)
        for n in month_year_star:
            year = n[0]
            month = n[1]
            av_stars = n[2]
            data_star_month_year = (year,month,av_stars,biz_id)
            self.InsertMysql(self.add_stars_month_year,data_star_month_year)
        for p in range(0,20*(all_review_pages+1),20):
            new_review_url = url+('?start=%d'% p)
            self.Get_Rec_Review_Info(BeautifulSoup(requests.get(new_review_url).content),biz_id)
        not_rec_pages = self.Get_Not_Rec_Pages(BeautifulSoup(requests.get(self.BASE_URL+not_rec_url).content))
        for p in range(0,10*(not_rec_pages+1),10):
            new_url = self.BASE_URL+not_rec_url+'?not_recommended_start=%d'%p
            self.Get_Not_Rec_Review_Info(BeautifulSoup(requests.get(new_url).content), biz_id)


    def Not_Rec_Major_Info(self,url,biz_id):
        content = BeautifulSoup(requests.get(url = url).content)
        page = self.Get_Not_Rec_Review_Info(self.Find_The_Not_Rec_Part(content))
        if page > 1 :
            for i in range(0,20*(page+ 1 ),20):
                new_url = url+'?start=%d'%i
                self.Get_Not_Rec_Review_Info(self.Find_The_Not_Rec_Part(BeautifulSoup(requests.get(url = new_url).content)),biz_id)


    def Find_The_Not_Rec_Part(self,content):
        for ele in content:
            try:
                if ele['class'] == ['ysection','not-recommended-reviews','review-list-wide']:
                    return ele
            except:
                return None

    def Get_Not_Rec_Pages(self,content):
        try:
            div = content.find('div',class_='ysection not-recommended-reviews review-list-wide').find_all('div',class_ = 'page-of-pages arrange_unit arrange_unit--fill')
            return int(div[0].text.strip().split(' ')[-1])
        except:
            return 0


    def Get_Rec_Review_Info(self,content,biz_id):                                                        #recommended review
        for ele in content.find_all('div',class_ = 'review review--with-sidebar'):
            try:
                poster_id = self.Get_Poster_Info(ele.find('div',class_ = 'review-sidebar-content'),1)             #give back the poster id
            except:
                poster_id = None
            pass
            self.Get_Review_Content(ele,biz_id,poster_id)

        # get the words
        # get if there is picture
        # get others attitude of this store(might not available in the not recommended review)
        # return content,img_count,stars,useful,funny,cool

    def Get_Review_Content(self,content,biz_name,poster_id):
        temp_time = content.find('span',class_= 'rating-qualifier').text.strip().split()
        if len(temp_time) == 1:
            review_content = content.find('p').text
            for x in content.find('div',class_ ='biz-rating biz-rating-large clearfix').find_all('div'):
                try:
                    stars =float(x['title'].split(' ')[0])
                    break
                except:
                    continue
            temp = temp_time[0].split('/')
            Time = temp[2]+'-'+temp[0]+'-'+temp[1]
            try:
                img_count = len(content.find_all('a',class_= 'biz-shim js-lightbox-media-link js-analytics-click'))[0]  #count of img
            except:
                img_count = 0
            useful,funny,cool = self.Get_Others_Attribute(content.find('div',class_='review-footer clearfix'))
            data_content = (Time,review_content,stars,useful,funny,cool,img_count,biz_name,poster_id,1)
            self.InsertMysql(self.add_review,data_content)

        else:
            Main_review_content = content.find('p').text
            for x in content.find('div',class_ ='biz-rating biz-rating-large clearfix').find_all('div'):
                try:
                    stars =float(x['title'].split(' ')[0])
                    break
                except:
                    continue
            temp = temp_time[0].split('/')
            Time = temp[2]+'-'+temp[0]+'-'+temp[1]
            useful,funny,cool = self.Get_Others_Attribute(content.find('div',class_='review-footer clearfix'))
            try:
                img_count = len(content.find_all('a',class_= 'biz-shim js-lightbox-media-link js-analytics-click'))[0]  #count of img
            except:
                img_count = 0
            data_content = (Time,Main_review_content,stars,useful,funny,cool,img_count,biz_name,poster_id,1)
            self.InsertMysql(self.add_review,data_content)
            for ele in content.find_all('div', class_ = 'previous-review clearfix'):
                try:
                    review_content = ele.find_all('span',class_= 'js-content-toggleable hidden')[0].text
                except:
                    review_content = None
                for x in ele.find('div',class_ ='biz-rating biz-rating-large clearfix').find_all('div'):
                    try:
                        stars =x['title'].split(' ')[0]
                        break
                    except:
                        continue
                temp_time = ele.find('span',class_= 'rating-qualifier').text.strip().split()
                temp = temp_time[0].split('/')
                Time = temp[2]+'-'+temp[0]+'-'+temp[1]
                useful,funny,cool = self.Get_Others_Attribute(ele.find('div',class_='rateReview voting-feedback'))
                try:
                    img_count = len(ele.find_all('a',class_= 'biz-shim js-lightbox-media-link js-analytics-click'))[0]  #count of img
                except:
                    img_count = 0
                data_content = (Time,review_content,stars,useful,funny,cool,img_count,biz_name,poster_id,1)
                self.InsertMysql(self.add_review,data_content)


    def Get_Others_Attribute(self,content):
        try:
            u = content.find_all('a',{'rel':'useful'})[0]
            useful = int(u.find('span',{'class':'count'}).text)
        except:
            useful = 0
        try:
            f = content.find_all('a',{'rel':'funny'})[0]
            funny = int(f.find('span',{'class':'count'}).text)
        except:
            funny = 0
        try:
            c = content.find_all('a',{'rel':'cool'})[0]
            cool = int(c.find('span',{'class':'count'}).text)
        except:
            cool = 0
        return useful,funny,cool



    def Get_Not_Rec_Review_Info(self,content,biz_id):
        for ele in content.find_all('div' ,class_ = 'review review--with-sidebar'):
            try:
                hovercard_id = self.Get_Poster_Info(ele.find('div',class_ = 'review-sidebar-content'),0)              #poster Info
            except:
                hovercard_id = None
            try:
                review_content = ele.find('div',class_= 'review-content').find('p').text
                for x in ele.find_all('div', class_= 'biz-rating biz-rating-large clearfix')[0].find_all('div'):
                    try:
                        stars = float(x['title'].split(' ')[0])          #stars of the review
                        break
                    except:
                        continue
                temp_time = content.find('span',class_= 'rating-qualifier').text.strip().split()
                temp = temp_time[0].split('/')
                Time = temp[2]+'-'+temp[0]+'-'+temp[1]
                try:
                    img_count = len(ele.find('div',class_= 'review-content').find_all('a',class_= 'biz-shim js-lightbox-media-link js-analytics-click'))
                except:
                    img_count = 0
            except:
                review_content = None
                stars = None
                img_count = None
                Time = None

            data_content = (Time,review_content,stars,img_count,biz_id,hovercard_id,0)
            self.InsertMysql(self.add_not_rec_review,data_content)






    def Get_Poster_Info(self,content,IfRec):
        if IfRec:
            try:
                user_id = content.find_all('li',class_= 'user-name')[0].find('a')['href'][21:]      #user-id
            except:
                user_id = None
            try:
                data_hovercard_id = content.find_all('li',class_= 'user-name')[0].find('a')['data-hovercard-id']
            except:
                data_hovercard_id = None
        else:
            try:
                data_hovercard_id = content.find_all('li',class_= 'user-name')[0].find('span')['data-hovercard-id']
            except:
                data_hovercard_id = None
            user_id = None
        try:
            user_name = content.find_all('li',class_= 'user-name')[0].text.strip() #user -name
        except:
            user_name = None
        try:
            loct = content.find_all('li',class_= 'user-location responsive-hidden-small')[0].text.strip().split(',')[-2:]
        except:
            loct = ['','']
        data_poster = (user_name,loct[0],loct[1],user_id,data_hovercard_id)
        self.InsertMysql(self.add_poster,data_poster)
        return data_hovercard_id


    def connnect_mysql(self):
        config = {
          'user': 'ashcrimson',
          'password': 'kaka1234',
          'host': 'ix.cs.uoregon.edu',
          'database': 'Yelp',
          # 'raise_on_warnings': True,
        'autocommit':True,
        'port':3808
        }
        cnx = pymysql.connect(**config)
        return cnx

# if __name__==  '__main__':
#     Yelp = YelpCrwaler()
#     location = 'Eugene, OR'
#     BASE_URL = 'http://www.yelp.com'
#     place = location.replace(",","%2C").replace(" ","+")
#     query = BASE_URL + "/search?find_loc="+place
#     content = requests.get(query).content
#     soup = BeautifulSoup(content)
#     # https://www.yelp.com/search?find_loc=Eugene,OR&start=0
#     for each in range(0,92): #do all the pages
#         query = BASE_URL + "/search?find_loc="+place+'&start=%d'%(10*each)
#         content = requests.get(query).content
#         soup = BeautifulSoup(content)
#         for ele in soup.find_all('a',class_ = 'biz-name js-analytics-click'):
#             back_url =  ele['href']
#             print back_url
#             store_content  = BeautifulSoup(requests.get(url = BASE_URL+back_url).content)  #one of the stores
#             Yelp.Get_Major_Info(BASE_URL+back_url,'Eugene','OR')