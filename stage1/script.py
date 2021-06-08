import gzip
import shutil
import os
import re
from datetime import datetime
from contextlib import redirect_stdout
currentDir = os.getcwd()
#onlyfiles = [f for f in listdir(os.getcwd()) if re.search(r'*.log.gz', f) join(os.getcwd(), f)

#listing the compressed log files in the directory
fileList=[]
for f in os.listdir(currentDir):
    if re.search (r"log.gz$", f):
        fileList.append(f)
#print(fileList)
with open('out.txt', 'a') as output:
    #defining a printing template
    with redirect_stdout(output):
        TEMPLATE = '{Date:^20} | {err4:^10} | {err5:^15}'
        row = TEMPLATE.format(Date="Date", err4="#4XX",err5="#5XX")
        print(row)
    totalErr4xx=0
    totalErr5xx=0
    for f in fileList:
        err4xx=0
        err5xx=0
        #decompressing log files
        
        with gzip.open(f, 'rb') as f_in:
        #remove .gz extension
            with open(f[:-3],'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
                with open(f[:-3]) as f_out:
                    fileDate=str(datetime.strptime(re.search(r"\d+",f).group(), '%Y%m%d'))
                    
                    err4xxPat=re.compile(r"\d 4\d\d \d")
                    err5xxPat=re.compile(r"\d 5\d\d \d")
                    for line in f_out:
                        if err4xxPat.search(line):
                            err4xx+=1
                        if err5xxPat.search(line):
                            err5xx+=1
                    
                    with redirect_stdout(output):
                        row = TEMPLATE.format(Date=fileDate, err4=err4xx,err5=err5xx)
                        print(row)
                    totalErr4xx+=err4xx
                    totalErr5xx+=err5xx
    #    print(fileDate)
        # with open(f[:-3]) as f_out:
            #searching 4xx & 5xx pattern
            # err4xxPat=re.compile(r"\d 4\d\d \d")
            # err5xxPat=re.compile(r"\d 5\d\d \d")
            # for line in f_out:
            #     if err4xxPat.search(line):
            #         err4xx+=1
            #     if err5xxPat.search(line):
            #         err5xx+=1

        
    with redirect_stdout(output):
        TEMPLATE = '{Total:^20}   {err4:^10}   {err5:^15}'
        row = TEMPLATE.format(Total="Total", err4=totalErr4xx,err5=totalErr5xx)
        print(row)

    
        
