#include <stdio.h>
#include <math.h>


extern struct rtpkt {
  int sourceid;       /* id of sending router sending this pkt */
  int destid;         /* id of router to which pkt being sent 
                         (must be an immediate neighbor) */
  int mincost[4];    /* min cost to node 0 ... 3 */
  };


extern int TRACE;
extern int YES;
extern int NO;

// int connectcosts1[4] = { 1,  0,  1, 999 };

struct distance_table 
{
  int costs[4][4];
} dt1;

int neighbors1[4]={ 1,  0,  1, 999 };
/* students to write the following two routines, and maybe some others */

int i,j;
int min(int a,int b);
void Initial1()
{

  for(i=0;i<4;i++)
  {
    for(j=0;j<4;j++)
    {
      dt1.costs[i][j]=999;
    }
  }
}

rtinit1() 
{
  Initial1();
  //更新1到其他节点的距离
  for(i=0;i<4;i++)
  {
    dt1.costs[1][i]=neighbors1[i];
  }
  //向各个邻居发送初始化内容
  for(i=0;i<4;i++)
  {
    if(neighbors1[i]!=999&&i!=1){
      struct rtpkt pkt;
      pkt.sourceid=1;
      pkt.destid=i;
      for(j=0;j<4;j++)
      {
        pkt.mincost[j]=dt1.costs[1][j];
      }
      tolayer2(pkt);
    }
  }
}


rtupdate1(rcvdpkt)
  struct rtpkt *rcvdpkt;
  
{
  int sourceid=rcvdpkt->sourceid;
  //更新最短距离
  for(i=0;i<4;i++)
  {
    for(j=0;j<4;j++)
    {
      dt1.costs[i][j]=min(dt1.costs[i][j],dt1.costs[i][sourceid]+rcvdpkt->mincost[j]);
    }
  }
  //将更新后的信息发送给各个邻居
  for(i=0;i<4;i++)
  {
    if(neighbors1[i]!=999&&i!=1){
      struct rtpkt pkt;
      pkt.sourceid=1;
      pkt.destid=i;
      for(j=0;j<4;j++)
      {
        pkt.mincost[j]=dt1.costs[1][j];
      }
      tolayer2(pkt);
    }
  }
  printdt1(&dt1);
}


printdt1(dtptr)
  struct distance_table *dtptr;
  
{

  printf("Node|  0       1        2       3 \n");
  printf("------------------------------------\n");
  printf("D%d  |  %d       %d        %d       %d         \n", 1,
  dtptr->costs[1][0], dtptr->costs[1][1], 
  dtptr->costs[1][2], dtptr->costs[1][3]);
  printf("\n\n");
}



linkhandler1(linkid, newcost)   
int linkid, newcost;   
/* called when cost from 1 to linkid changes from current value to newcost*/
/* You can leave this routine empty if you're an undergrad. If you want */
/* to use this routine, you'll need to change the value of the LINKCHANGE */
/* constant definition in prog3.c from 0 to 1 */
	
{
  neighbors1[linkid]=newcost;
  rtinit0();
  rtinit1();
  rtinit2();
  rtinit3();
}

