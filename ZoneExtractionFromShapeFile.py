#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun  9 12:47:30 2021
Reference : M. de Berg, O. Cheong, M. van Kreveld, M. Overmars,  Computational geometry,  (Springer, 2010)
	    [Geo_MYTNMAC] QGIS 46 – Sommet | Génèrer une couche de points représentant les sommets des entités https://www.youtube.com/watch?v=bpyfMjQe0Jo
@authors: ndiop, odiop

Aim: extraction of all links of a given zone represented by a shape file. 
   Inputs: a shape file containing the zone to extract and a matsim network from in which the zone is to be extracted (see End of Part 1)
   Output: a cvs file containing all links that cross the zone. That is to say all links that for which at least one extremity is in that the zone (see End of Part 2)

"""
import math
from matplotlib.pyplot import *
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
import numpy
import pandas as pd
import matsim
from collections import defaultdict

#-----------------------------------------------------------
#---------------------BEGIN PART 1-------------------------------
"""
Aim: Decomposition of a polygon into a set of triangles
"""
#----------------------------------------------------------
def voisin_sommet(n,i,di):
    return (i+di)%n

def equation_droite(P0,P1,M):
    return (P1[0]-P0[0])*(M[1]-P0[1])-(P1[1]-P0[1])*(M[0]-P0[0])

def point_dans_triangle(triangle,M):
    P0 = triangle[0]
    P1 = triangle[1]
    P2 = triangle[2]
    eq01=equation_droite(P0,P1,M) <=0 
    eq12=equation_droite(P1,P2,M) <=0
    eq20=equation_droite(P2,P0,M) <=0 
  #  print(eq01,eq12,eq20,M)
    return eq01 and eq12  and eq20 

def sommet_distance_maximale(polygone,P0,P1,P2,indices):
    n = len(polygone)
    distance = 0.0
    j = None
    for i in range(n):
        if not(i in indices):
            M = polygone[i]
            if point_dans_triangle([P0,P1,P2],M):
                d = abs(equation_droite(P1,P2,M))
                if d > distance:
                    distance = d
                    j = i
    return j

def sommet_gauche(polygone):
    n = len(polygone)
    x = polygone[0][0]
    j = 0
    for i in range(1,n):
        if polygone[i][0] < x:
            x = polygone[i][0]
            j = i
    return j
def nouveau_polygone(polygone,i_debut,i_fin):
    n = len(polygone)
    p = []
    i = i_debut
    while i!=i_fin:
        p.append(polygone[i])
        i = voisin_sommet(n,i,1)
    p.append(polygone[i_fin])
    return p 

def trianguler_polygone_recursif(polygone,liste_triangles):
    n = len(polygone)
  #  print(polygone)
    j0 = sommet_gauche(polygone)
    j1 = voisin_sommet(n,j0,1)
    j2 = voisin_sommet(n,j0,-1)
    P0 = polygone[j0]
    P1 = polygone[j1]
    P2 = polygone[j2]
    j = sommet_distance_maximale(polygone,P0,P1,P2,[j0,j1,j2])
    if j==None:
        liste_triangles.append([P0,P1,P2])
        polygone_1=nouveau_polygone(polygone,j1,j2)
        if len(polygone_1)==3:
            liste_triangles.append(polygone_1)
        else:
            trianguler_polygone_recursif(polygone_1,liste_triangles)
    else:
        polygone_1 = nouveau_polygone(polygone,j0,j)
        polygone_2 = nouveau_polygone(polygone,j,j0)
        if len(polygone_1)==3:
            liste_triangles.append(polygone_1)
        else:
            trianguler_polygone_recursif(polygone_1,liste_triangles)
        if len(polygone_2)==3:
            liste_triangles.append(polygone_2)
        else:
            trianguler_polygone_recursif(polygone_2,liste_triangles)
    return liste_triangles


def trianguler_polygone(polygone):
    liste_triangles = []
    trianguler_polygone_recursif(polygone,liste_triangles)
    return liste_triangles
                    

##################################### 
def FromCsv2Polygone(df):
    Xcol=df["X"]
    Ycol=df["Y"]
    n=len(df)
    Poly=[]
    
    for i in range(n):
        V=[Xcol.iloc[i],Ycol.iloc[i]]
        Poly.append(V)
    return Poly


######################################
""" Testing if a given point M=[xM,yM] belongs to the polygon or not.This is to say if the point belongs to one of the triangles 
  that constitued the polygon. """
   
def In_polygone(LT,M):
    n=len(LT)
    ok=0
    for i in range(n):
        if (point_dans_triangle(LT[i], M)):
            ok=1
            break
    return ok   

def In_polygone1(LT,M):
    n=len(LT)
    ok=False
    i=0
    while ((i<n) and (ok==False)):
          ok= (point_dans_triangle(LT[i], M))
          i=i+1      
    return ok   

####################################


#-----------------------------------------------------------
#---------------------End -------------------------------
#----------------------------------------------------------






#-----------------------------------------------------------
#---------------------BEGIN Optional PART--------------------------
"""
This is optional and its aim is only to plot the zone with all colored triangles 
"""
#----------------------------------------------------------
df1=pd.read_csv("XYsommetsLille.csv", ",")
polygone=FromCsv2Polygone(df1)
liste_triangles = trianguler_polygone(polygone)
def draw_liste_triangles(liste_triangles):
    fig,ax = subplots()
    patches = []
    for triangle in liste_triangles:
        patches.append(Polygon(triangle))
    p = PatchCollection(patches, cmap=matplotlib.cm.jet, alpha=1.0)
    colors = 100*numpy.random.rand(len(patches))
    p.set_array(numpy.array(colors))
    ax.add_collection(p)
    
draw_liste_triangles(liste_triangles)
minX = df1["X"].min()
maxX = df1["X"].max()
minY = df1["Y"].min()
maxY = df1["Y"].max()
axis([minX,maxX,minY,maxY])
matplotlib.pyplot.savefig("Polygone2Triangle.pdf")

#-----------------------------------------------------------
#---------------------End -------------------------------
#----------------------------------------------------------




#-----------------------------------------------------------
#---------------------BEGIN PART 2-------------------------------
"""
Aim: Links Extraction (internal, outgoing and ingoing)
"""
#----------------------------------------------------------
     

def ZoneExtration_FromShapeFile(FileZoneXYnodes,Filenetwork):
    # FileZoneXYnodes="XYsommetsLille.csv"
    #Filenetwork='melmultimodalnetwork.xml.gz'

    net = matsim.read_network(Filenetwork) 
    tabnode=net.nodes
    tablink=net.links
   
    df1=pd.read_csv(FileZoneXYnodes, ",") 
    inside=pd.DataFrame(columns=tablink.columns)# dataframe to return
    """ creation of a witness column, named "is", in both DataFrames inside and tablink : 
      is = 0 (if a & b inside), 1 (if a inside & b outside), -1 (if a outside & b inside)
      where a and b are respectively origin and destination of a given link"""
    inside["is"] = ""
    tablink["is"] = ""
    polygone=FromCsv2Polygone(df1)
    liste_triangles = trianguler_polygone(polygone)
   
    k=0;
    Nlink=len(tablink) ;
    for i in range(Nlink):
        a=tablink.iloc[i,7];
        b=tablink.iloc[i,8];
        taba=tabnode[tabnode["node_id"]==a]
        tabb=tabnode[tabnode["node_id"]==b]
        Ia=taba.index.values[0]
        Ib=tabb.index.values[0]
        if (len(taba)!=0):
            xa =tabnode.iloc[Ia,0] 
            ya = tabnode.iloc[Ia,1] 
            Va=[xa,ya]
            boola=In_polygone1(liste_triangles,Va)
        if (len(tabb)!=0):
           xb = tabnode.iloc[Ib,0] 
           yb = tabnode.iloc[Ib,1] 
           Vb=[xb,yb]
           boolb=In_polygone1(liste_triangles,Vb)
        if (boola and boolb) :
           # print("internal link")
            tablink.iloc[i,9]=0 ;
            inside.loc[k]=tablink.iloc[i,:];
            k=k+1;
        if (boola and not(boolb)) :
           # print("outgoing link")
            tablink.iloc[i,9]=1 ;
            inside.loc[k]=tablink.iloc[i,:];
            k=k+1;
        if (not(boola) and boolb) :
           # print("ingoing link")
            tablink.iloc[i,9]=-1 ;
            inside.loc[k]=tablink.iloc[i,:];
            k=k+1;
        print(i,"sur",Nlink)
    return inside   

    
dfinside=ZoneExtration_FromShapeFile("XYsommetsLille.csv",'npdc_multimodalnetwork.xml.gz')

dfinside.to_csv("insideTotal.csv", index=None, sep=";")
#######################

#-----------------------------------------------------------
#---------------------End -------------------------------
#----------------------------------------------------------




     
                 
       





