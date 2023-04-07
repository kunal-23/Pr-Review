// adding a comment
class FibonacciExample1{  
public static void main(String args[])  
{    
 int p1=0,p2=1,p3,i,count=10;    // changed the variables
 System.out.print(p1+" "+p2);//printing 0 and 1    
    
 for(i=2;i<count;++i)//loop starts from 2 because 0 and 1 are already printed    
 {    
  p3=p1+p2;    
  System.out.print(" "+p3);    
  p1=p2;    
  p2=p3;    
 }    
  
}}  
