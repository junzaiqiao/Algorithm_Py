#coding=utf-8

'''
算法原理
kmeans的计算方法如下：
1 随机选取K个中心点
2 遍历所有数据，将每个数据划分到最近的中心点中
3 计算每个聚类的平均值，并作为新的中心点
4 重复2-3，直到这k个中线点不再变化（收敛了），或执行了足够多的迭代
时间复杂度：O(I*n*K*m)
空间复杂度：O(n*m)
其中m为每个元素字段个数，n为数据量，I为迭代次数。一般I,K,m均可认为是常量，所以时间和空间复杂度可以简化为O(n)，即线性的。
'''
from random import *
import linecache
import re
import math
import time


class Kmeans:
    K=0     #中心点个数
    I=0     #迭代次数
    W=0     #聚类数据维度个数
    check=None #判断是否拟合
    centerdict=dict()
    centercheck=dict()
    
    def __init__(self):
        self.K=3
        self.I=10
        self.W=14
        ret=self.selectCenter(self.K)
        if( ret['status'] == True ):
            self.check=False
    
    
    def selectCenter(self,K):
        p=re.compile('\s+')
        result=dict()
        filename="../data/kmdata.txt"
        f=open(filename,'r')
        num=0
        for line in f:
            num+=1
        #获取K个1到num的随机数
        klist=sample(range(1,num+1),K)
        print klist
        l=1
        n=1
        try:
            f.seek(0)
            for line in f:
                for j in klist:
                    if( l==j ):
                        line=re.sub(p,'',str(line.decode("utf-8-sig").encode("utf-8")))
                        line=str(line).split(',')
                        self.centerdict[str(line[0])+'_'+str(n)]=line[1:]
                        self.centercheck[str(line[0])+'_'+str(n)]=False
                        n+=1      
                l+=1

        except Exception as e :
            result={'status' : False,
                    'data':None,
                    'msg' : e}
            
            f.close()
            return result
        
        if( f ):
            f.close()
        result={'status':True,
                'data':None,
                'msg':'Success'}
        return result
        
    '''
    * 计算聚类的平均值
    * 处理输入条件 
    * @param cpudatadict:dict())
    * @return newcenter:dict()
    '''
    def computerKmeans(self,cpudatadict):
        center_dataplus_dict=dict()

        for i in range(1,int(self.K)+1):
            center_dataplus_dict[str(i)]=['0' for l in range(self.W)]
            center_dataplus_dict['num'+'_'+str(i)]=0
  
        for key in cpudatadict:
            id=str(key).split('_')[1]
            j=0
            for x1,x2 in zip(  cpudatadict[key], center_dataplus_dict[str(id)] ):
                center_dataplus_dict[str(id)][j] = float(x1) + float(x2)
                j+=1
            center_dataplus_dict['num'+'_'+id]+=1


        
        newcenterdict=dict()
        
        for idkey in range(1,int(self.K)+1):
            idkey=str(idkey)
            tmplist=[]
            for ld in center_dataplus_dict[idkey]:
                if(float(center_dataplus_dict['num_'+idkey]) <> 0 ):
                    tmplist.append( str(float(ld)/float(center_dataplus_dict['num_'+idkey])  ))
                else:
                    tmplist.append(str(ld))
                for ckey in self.centerdict:
                    ckeytmp=str(ckey).split('_')[0]+'_'+str(idkey)
                    if( ckeytmp in self.centerdict.keys() ):
                        newcenterdict[ckeytmp]=tmplist
                        break 
                    
            tmplist=[]


        return  newcenterdict     

    '''
    * 比较新的中心点和旧的中心位置是否一直不一致则替换
    * 处理输入条件 
    * @param newcenter:dict(), oldcenter:dict()
    * @return None
    '''
    def compareCenter(self,newcenter,oldcenter):

        for key in oldcenter:
            for newl ,oldl in zip(newcenter[key] , oldcenter[key]):
                if( str(newl) == str(oldl) ):
                    self.centercheck[key]=True
                else:
                    self.centercheck[key]=False
                    break
            if( self.centercheck[key] == False ):
                self.centerdict[key]=newcenter[key]
        
        for ckkey in self.centercheck:
            if( self.centercheck[ckkey] == True):
                self.check=True
            else:
                self.check=False
                break

    '''
    * 出来数据，将数据找到对应的离中心距离最近的中心打上对应的标签
    * 处理输入条件 
    * @param analine:list()
    * @return list() 打上标签的数据
    '''
    def analyseKmeans(self,analine):
        ab=0.0
        a=0.0
        b=0.0
        max_cos=0.0
        data_cos=list()
        analine=analine.split(',')
        maxdatadict={'max':0.0,'data':{}}
        
        for clist in self.centerdict.keys():       
            for al,bl in zip(analine[1:], self.centerdict[clist] ): 
                ab+=float(al)*float(bl)
                a+=pow(float(al),2)
                b+=pow(float(bl),2)
                
            tmpsqrt=math.sqrt(a*b)
            #判断分母是否为0
            if( tmpsqrt != 0  ):
                cos_res=ab/tmpsqrt
                #保留与K个中心距离最近的数据
                if( cos_res >= float(max_cos) ):
                    max_cos=cos_res
                    data_cos=analine[1:]
                    clisttmp=clist

        maxdatadict['max']=max_cos
        maxdatadict['data'][analine[0]+'_'+str(clisttmp).split('_')[1]]=data_cos

        return maxdatadict['data']

             

    
    def runKmeans(self):
        filename="../data/kmdata.txt"
        
        f = open( filename,'r' )
        p=re.compile('\s+')
        m=1
        
        while( self.check == False and  m <= self.I):
            cpudatadict=dict()
            for line in f:
                line=re.sub(p,'',str(line).decode("utf-8-sig").encode("utf-8"))
            
                tmpdict=self.analyseKmeans(line)

                for tmpdictkey in tmpdict:
                    cpudatadict[tmpdictkey]=tmpdict[tmpdictkey]
                tmpdict.clear()
            
            newcenter=self.computerKmeans(cpudatadict)
            print newcenter
            #新老中心比对，并将新的中心覆盖调旧的
            self.compareCenter(newcenter, self.centerdict)
                    
            m+=1
            f.seek(0)
            print cpudatadict
    


if __name__=='__main__':
    kmeans=Kmeans()
    
    kmeans.runKmeans()
    
    
    





