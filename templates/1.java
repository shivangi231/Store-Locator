      import java.util.*;
        class Solution{
            public static void main(String argsp[]){
               Scanner s=new Scanner(System.in);
               int t=s.nextInt();
               for(int i=0;i<t;i++){
               long n=s.nextLong();
               long[] array=new long[n];
                array[0]=s.nextLong();
                 long count=0;
                 int var=0;
               for(int x=1;x<n;x++){
                  array[x]=s.nextlong();
                  if(array[x-1]!=array[x]){
                  count+=1;
                  var=1;
                  }
                  else if(var==1){
                  count+=1;
                  var=0;
                  
                  }
                  
                }
               
               System.out.print(count);
               
               }
           
            }
          
        }  
     
    