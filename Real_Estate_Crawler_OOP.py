#-------------------------------------------
#Author: Brendon Lugo
#Purpose: Real Estate Website scrapper, crawler, and identifier of potentail good investments
#Date Written: 7/24/2019
#-------------------------------------------
class Crawler():
    import requests, re
    from bs4 import BeautifulSoup
    def __init__(self, base_url_front, base_url_end, locality, L_list, r, c, c_site,all,soup):
        self.base_url_front="https://www.zillow.com/"
        self.base_url_end="-fl"
        self.locality=''
        self.L_list=[]
        self.r=''
        self.c=''
        self.c_site=''
        self.all =''
        self.soup=''
        
    def get_locality(self):
        self.locality = str(input("What town from the following list would you like to search: Pace, Milton, Pensacola ?:"))
        while self.locality.lower() not in("milton","pace","pensacola"):
            self.locality = str(input("What town from the following list would you like to search: Pace, Milton, Pensacola ?:"))
        if self.locality in("Milton","Pace","Pensacola"):
            return True
    def get_Composite_url(self):
        self.c_site = self.base_url_front + self.locality + self.base_url_end
        
    def get_all(self):
        import requests, re
        from bs4 import BeautifulSoup
        self.r=requests.get(self.c_site)
        self.c=self.r.content
        print(self.c)
        self.soup=BeautifulSoup(self.c,"html.parser")
        self.all=self.soup.find_all("div",{"class":"grid-search-results"})
        for i in self.all:
            print(i)
    def Grab_Compile_Data(self):
        import requests, re
        from bs4 import BeautifulSoup
        print(self.c_site)
        page_nr=self.soup.find_all("div",{"class":"search-pagination"})
        print(self.all,"=====all")
        print("i am page_nr", page_nr)
        og_page = page_nr[0].text
        og_page = og_page.replace("Page","")
        og_page = og_page.replace("1","")
        og_page = int(og_page)
        for page in range(2,og_page,1):
            rr = requests.get(self.c_site+'/'+str(page) + '_p')
            cc = rr.content
            ssoup=BeautifulSoup(cc,"html.parser")
            aall=ssoup.find_all("article",{"class":"list-card list-card-short list-card_not-saved"})
            for item in aall:
                d={}
                try:
                    d["Price"]=item.find_all("list-card-price")[0].text
                except:
                    d["Price"]=None
                try:
                    if item.find_all("list-card-label")[1].text == "N/A":
                        d["Bed"]=None
                    else:
                        d["Bed"]=item.find_all("list-card-label")[1].text
                except:
                    d["Bed"]=None
                try:
                    if item.find_all("list-card-label")[2].text == "N/A":
                        d["Bath"]=None
                    else:
                        d["Bath"]=item.find_all("list-card-label")[2].text
                except:
                    d["Bath"]=None

                try:
                    d["Sqaure_Feet"]=item.find_all("list-card-label")[3].text
                except:
                    d["Sqaure_Feet"]=None
                try:
                    d["Address"]=item.find_all("h3",{"class":"list-card-addr"})[0].text
                except:
                    d["Address"]=None
                self.L_list.append(d)
                
    def Export_total_list_to_csv(self):
        import pandas as pd
        df = pd.DataFrame(self.L_list)
        df.to_csv("REOutputOOP_"+str(self.locality)+".csv")
        
    def Cal_ROI(self):
        GrossIncome = 12000
        Expenses = .6 
        NetCashFlow = 0
        GrossROI = 0
        NetROI = 0
        Potential_Investment_List=[]
        for house in self.L_list:
            if (house["Bath"] != None and float(house["Bath"]) >= 2) and (house["Bed"] != None and float(house["Bed"]) >= 3):
                house["Price"] = str(house["Price"])[1:]
                k0='000'
                m0='0000'
                if house["Price"][len(house["Price"])-1] == 'k':
                    house["Price"] = house["Price"][:-1]
                    house["Price"] = house["Price"] + k0
                    house["Price"] = float(house["Price"])
                elif house["Price"][len(house["Price"])-1] == 'm': #Yeah this was a pain in the ass to make work
                    house["Price"] = house["Price"].split('m')
                    house["Price"] = house["Price"][0]
                    bb=house["Price"].split('.')
                    aa=''
                    for i in range(0,len(bb)):
                        aa += str(bb[i])
                    house["Price"] = aa
                    house["Price"] = house["Price"] + m0
                    house["Price"] = float(house["Price"])


                GrossROI = 100*(GrossIncome / float(house["Price"]))
                NetCashFlow = GrossIncome * Expenses
                NetROI = 100*(NetCashFlow / float(house["Price"]))
                if NetROI >= 8.999:
                    house["ROI"]=NetROI
                    Potential_Investment_List.append(house)
                self.Export_ROI_list_to_csv(Potential_Investment_List)
    def Export_ROI_list_to_csv(self,obj):
        import pandas as pd
        Potential_Investment_List = obj
        PI_List = pd.DataFrame(Potential_Investment_List)
        #print(PI_List)
        PI_List.to_csv("RE_ROI_OutputOOP_"+str(self.locality)+".csv")

class database():
    #Setting up database consists of five steps
    #1. Connect to a database
    #2. Create a cursor object
    #3. Write an SQL query
    #4. Commit changes to database
    #5. Close connection
    def create_houses_table():
        conn=sqlite3.connect("lite.db")
        cur=conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS houses (address TEXT, beds INTEGER, baths INTEGER, price REAL, sqaure_feet REAL)")
        conn.commit()
        conn.close()

    def create_date_table():
        conn=sqlite3.connect("lite.db")
        cur=conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS date (date INTEGER, locality TEXT, mean INTEGER, median INTEGER, percent INTEGER)")
        conn.commit()
        conn.close()
        
    def insert_houses(address,beds,baths,price,sqaure_feet):
        conn=sqlite3.connect("lite.db")
        cur=conn.cursor()
        cur.execute("INSERT or IGNORE INTO houses VALUES (?,?,?,?,?)",(address,beds,baths,price,sqaure_feet))
        conn.commit()
        conn.close()

    def insert_date(date,locality,mean,median,percent):
        conn=sqlite3.connect("lite.db")
        cur=conn.cursor()
        cur.execute("INSERT or IGNORE INTO date VALUES (?,?,?,?,?)",(date,locality,mean,median,percent))
        conn.commit()
        conn.close()
        
    def view(table):
        table = str(table)
        conn=sqlite3.connect("lite.db")
        cur=conn.cursor()
        cur.execute("SELECT * FROM " + str(table))
        rows=cur.fetchall()
        conn.close()
        return rows

    def delete(item):
        conn=sqlite3.connect("lite.db")
        cur=conn.cursor()
        cur.execute("DELETE FROM houses WHERE address=?",(address,))
        conn.commit()
        conn.close()
        
    def update(address,beds,baths,price,sqaure_feet):
        conn=sqlite3.connect("lite.db")
        cur=conn.cursor()
        cur.execute("UPDATE houses SET address=?, beds=?, baths=?, price=?, square_feet=?, WHERE address=?",(address,beds,baths,price,sqaure_feet))
        conn.commit()
        conn.close()

    def add_homes_list(n_list):
        list = n_list
        for i in list:
            database.insert_houses(i["Address"],i["Bed"],i["Bath"],i["Price"],i["Sqaure_Feet"])

    def calc_stats(data_obj):
        from numpy import median
        db_data = data_obj
        p_list = []
        pp_list =[]
        for i in data_obj:
            p_list.append(i[3])
            
        total_nums = len(p_list)
        sum_total_nums = 0
        k0= '000'
        m1= '0000'
        m0= '00000'
        for p in p_list:
            if type(p) == str:
                if p[0] == '$':
                    p = p[1:]
                    if p[len(p)-1] == 'k':
                        p = str(p)
                        p = p[:-1]
                        p += k0
                        p = float(p)
                        pp_list.append(p)
                    elif p[len(p)-1] == 'm':
                        p = p[:-1]
                        ap = p.split('.')
                        bb =""
                        for i in ap:
                            bb += i
                        if len(bb) == 3:
                            bb += m1
                        if len(bb) == 2:
                            bb += m0
                        p = bb
                        p= float(p)
                        pp_list.append(p)
                
            sum_total_nums += int(p)
        mean = round(sum_total_nums / total_nums,3)
        p_median = median(pp_list)
        target_house_num = 0
        for p in pp_list:
            if p in range(60000,80000):
                target_house_num += 1
        percentage_target = round(target_house_num / total_nums,3)
        from datetime import date
        today = date.today()
        d = today.strftime("%m/%d/%y")
        database.insert_date(d,Run_Crawler.locality,mean,p_median,percentage_target)

    def Cool_Graphs(data):
        db_dates = data
        run = True
        from bokeh.plotting import figure
        from bokeh.io import output_file, show
        e_list = []
        for e in db_dates:
            e_list.append(e)
            print(e)
        while run == True:
            choice_town = str(input("What towns data would you like to view? :"))
            choice_data = str(input("What data you like to view? : (mean, median, percent)"))
            output_file = choice_town + "_" + choice_data + "_graph.html"
            x=[]
            y=['1','2','3','4']
            for e in e_list:
                if e[1] == choice_town.lower():
                    x.append(e[0])
                if choice_data =="mean":
                    if e[1] == choice_town.lower():
                        y.append(int(e[2]))
                elif choice_data =="median":
                    if e[1] == choice_town.lower():
                        y.append(int(e[3]))
                elif choice_data =="percent":
                    if e[1] == choice_town.lower():
                        y.append(int(e[4]))
            f=figure(x_axis_type='datetime')
            print("x=",x)
            print("y=",y)
            f.line(x,y)
            show(f)
            choice_run_again = str(input("Would you like to see another graph? y/n"))
            while choice_run_again not in("y,n"):
                choice_run_again = str(input("Would you like to see another graph? y/n"))
            if choice_run_again == 'y':
                continue
            else:
                break
                
###############GLOBAL CODE BELOW#########################################
Run_Crawler = Crawler("","","","","","","","","")
Run_Crawler.get_locality()
Run_Crawler.get_Composite_url()
Run_Crawler.get_all()
Run_Crawler.Grab_Compile_Data()
Run_Crawler.Export_total_list_to_csv()
Run_Crawler.Cal_ROI()

import sqlite3
database.create_houses_table()
database.add_homes_list(Run_Crawler.L_list)
db_data = database.view('houses')
database.create_date_table()
database.calc_stats(db_data)
db_dates = database.view('date')    #Use linux Cron Job to run all the commands up to this point than create a new class to trigger weekly analyzation of data and a monthly analyzation of data
                                    #then create a class to send an email with the monthly and weekly info with graphs to your email and dads email. 
database.Cool_Graphs(db_dates)
