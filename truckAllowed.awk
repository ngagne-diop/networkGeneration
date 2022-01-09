BEGIN{
   inlink=0;
	 FS="\"";
	 s="\"";
   change = 0;
}

inlink==0 && /link id=/ {
   inlink+=1;
	 pers[1]=$0;
	 mds=$18 ",truck";
	 l1=$1 s $2 s $3 s $4 s $5 s $6 s $7 s $8 s $9 s $10 s $11 s $12 s $13 s $14 s $15 s $16 s $17 s $18 s $19 ;  
	 l2=$1 s $2 s $3 s $4 s $5 s $6 s $7 s $8 s $9 s $10 s $11 s $12 s $13 s $14 s $15 s $16 s $17 s mds s $19 ;  
$	 } 

inlink >= 1 && (/motorway/ || /primary/ || /trunk/ || /secondary/ || /tertiary/) && !/\/link/ && !/link id/ {
	  inlink += 1;
    change = 1;
$	  pers[inlink]=$0;} 

inlink>=1 && !/motorway/ && !/primary/ && !/trunk/ && !/secondary/ && !/tertiary/ && !/\/link/ && !/link id/{
   inlink+=1;
	 pers[inlink]=$0;
$	} 

	inlink>=1 && /\/link/{
	 inlink+=1;
	 pers[inlink]=$0;
   if (change==1) {
     pers[1] = l2;
   } else {
     pers[1] = l1;
   }
	 PrintLink();
   inlink=0;
   change = 0;
$	}
	 
inlink==0 && !/link id/ && !/\/link/ {
	  print $0;
$	}

/<\/links>/ {
  print $0;
$	}



function PrintLink (){
	 for (i=1; i<=inlink; i++) print  pers[i];
} 
