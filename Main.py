from yelp.client import Client
from yelp.oauth1_authenticator import Oauth1Authenticator
import decimal
import OneStoreInfo
# import sys
# sys.setrecursionlimit(2500)

# params = {
#     'term': 'food',
#     'offset': offset
# }

# t = client.se
# arch('Portland').total
decimal.getcontext().prec = 10
BBox = (decimal.Decimal(46.273822), decimal.Decimal(-116.465874)
,decimal.Decimal(41.998673), decimal.Decimal(-124.613347))
a = [45.484367383117436384454503981049,-122.87118561565867375110833951792315118693370599862167182048100499969223164953291416168212890625]# la lo for Whole Oregon


exception = []
f = open('category.txt','r')
c = f.read()
f.close()
category = eval(c)
res = []
class Yelp:
    def __init__(self,la1,lo1,la2,lo2):
        self.YC = OneStoreInfo.YelpCrwaler()
        self.Bound = [la1,lo1,la2,lo2]
        f = open('category.txt','r')
        c = f.read()
        f.close()
        self.category = eval(c)
        Consumer_Key ='Qy__iwF-A9gHwkqOW4EydQ'
        Consumer_Secret = '256GVvv6EKufdvEPU62OLlhMmPo'
        Token = '24d5SNZuHvllp9qs4ULgL_x01_LBGKSw'
        Token_Secret = 'McvyemFVaWMJivLiMqwkdFDLGf0'
        auth = Oauth1Authenticator(
            consumer_key=Consumer_Key,
            consumer_secret=Consumer_Secret,
            token=Token,
            token_secret=Token_Secret
        )
        self.client = Client(auth)
    def Begin(self):
        self.do(self.Bound[0],self.Bound[1],self.Bound[2],self.Bound[3],)


    def usecategory(self,la1,lo1,la2,lo2):
        category = self.category
        for i in category.items():
            try:
                params = {'category_filter':i[0]}
                T = self.client.search_by_bounding_box( la1,lo1,la2,lo2,**params).total
                if T>1000:
                    for j in i[1]:
                        params = {'category_filter':i[0]}
                        T = self.client.search_by_bounding_box( la1,lo1,la2,lo2,**params).total
                        if T>1000:
                            # # exception.append([la1,lo1,la2,lo2,i[0]])
                            # return False
                            pass
                        else:
                            self.SearchForAll(la1,lo1,la2,lo2,i[1])
                            print(T)
                else:
                    # exception.append([la1,lo1,la2,lo2,i[0]])
                    self.SearchForAll(la1,lo1,la2,lo2,i[0])
                    print(T)
            except Exception as E:
                print(E)
        return True


    def do(self,la1,lo1,la2,lo2):
        if la2-la1<= 0.01 and lo2-lo1<= 0.01:
            return self.usecategory(la1,lo1,la2,lo2)
        else:
            try:
                T = self.client.search_by_bounding_box( la1,lo1,la2,lo2).total
                if T< 1000:
                    print(T)
                    self.SearchForAll(la1,lo1,la2,lo2)
                else:
                    print('too much')
                    mid_la = (la1+la2)/2
                    mid_lo = (lo1+lo2)/2
                    self.do(la1,lo1,mid_la,mid_lo)
                    self.do(mid_la,lo1,la2,mid_lo)
                    self.do(mid_la,mid_lo,la2,lo2)
                    self.do(la1,mid_lo,mid_la,lo2)
            except Exception as E:
                print (E)
                print(la1,la2,lo1,lo2)
                mid_la = (la1+la2)/2
                mid_lo = (lo1+lo2)/2
                self.do(la1,lo1,mid_la,mid_lo)
                self.do(mid_la,lo1,la2,mid_lo)
                self.do(mid_la,mid_lo,la2,lo2)
                self.do(la1,mid_lo,mid_la,lo2)
            return 0


    def SearchForAll(self,la1,lo1,la2,lo2,category = ''):
        offset = 0
        if category == '':
            T = self.client.search_by_bounding_box(la1,lo1,la2,lo2).total
        else:
            params = {
                # 'offset':offset,
                'category_filter':category
            }
            T = self.client.search_by_bounding_box(la1,lo1,la2,lo2,**params).total
        # f = open('coordinate.txt','a')
        # f.write(T+' '+str([la1,lo1,la2,lo2])+'\n')
        # f.close()
        while offset < T:
            params = {
            'offset':offset,
            'category_filter':category
        }
            c = self.client.search_by_bounding_box(la1,lo1,la2,lo2,**params).businesses
            for i in c:
                self.YC.Get_Major_Info(i.url,[i.id,i.name,[x.name for x in i.categories],i.location.coordinate.latitude,i.location.coordinate.longitude,i.location.city,i.location.state_code,i.rating])
            offset += 20




if __name__ == '__main__':
#     Yelp(decimal.Decimal(41.998673), decimal.Decimal(-124.613347),decimal.Decimal(46.273822), decimal.Decimal(-116.465874)   #for whole oregon
# ,).Begin()
    Yelp( decimal.Decimal(45.326197), decimal.Decimal(-122.913132)      ,   decimal.Decimal(45.931208), decimal.Decimal(-122.270432)       # for Portland
,).Begin()

# decimal.Decimal(45.326197), decimal.Decimal(-122.913132)         decimal.Decimal(45.931208), decimal.Decimal(-122.270432)

# la_dis = BBox[0]-BBox[2]
# lo_dis = BBox[1]-BBox[3]
# Init_Piece = 2
# for i in range(Init_Piece):
#     for j in range(Init_Piece):
#         print (i,j)
#         self.do(BBox[2]+decimal.Decimal(i)/Init_Piece*la_dis,BBox[3]+decimal.Decimal(j)/Init_Piece*lo_dis,BBox[2]+decimal.Decimal(i+1)/Init_Piece*la_dis,BBox[3]+decimal.Decimal(j+1)/Init_Piece*lo_dis)
#
# f= open('res.txt','w')
# f.write(str(res))
# f.close()
# f= open('exception','w')
# f.write(str(exception))
# f.close()








