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

struct distance_table 
{
  int costs[4][4];
} dt3;

int neighbors3[4]={7,999,2,0};
/* students to write the following two routines, and maybe some others */

int i,j;
int min(int a,int b);
void Initial3()
{

  for(i=0;i<4;i++)
  {
    for(j=0;j<4;j++)
    {
      dt3.costs[i][j]=999;
    }
  }
}

void rtinit3() 
{
  Initial3();
  //更新3到其他节点的距离
  for(i=0;i<4;i++)
  {
    dt3.costs[3][i]=neighbors3[i];
  }
  //向各个邻居发送初始化内容
  for(i=0;i<4;i++)
  {
    if(neighbors3[i]!=999&&i!=3){
      struct rtpkt pkt;
      pkt.sourceid=3;
      pkt.destid=i;
      for(j=0;j<4;j++)
      {
        pkt.mincost[j]=dt3.costs[3][j];
      }
      tolayer2(pkt);
    }
  }
}


void rtupdate3(rcvdpkt)
  struct rtpkt *rcvdpkt;
  
{
  int sourceid=rcvdpkt->sourceid;
  //更新最短距离
  for(i=0;i<4;i++)
  {
    for(j=0;j<4;j++)
    {
      dt3.costs[i][j]=min(dt3.costs[i][j],dt3.costs[i][sourceid]+rcvdpkt->mincost[j]);
    }
  }
  //将更新后的信息发送给各个邻居
  for(i=0;i<4;i++)
  {
    if(neighbors3[i]!=999&&i!=3){
      struct rtpkt pkt;
      pkt.sourceid=3;
      pkt.destid=i;
      for(j=0;j<4;j++)
      {
        pkt.mincost[j]=dt3.costs[3][j];
      }
      tolayer2(pkt);
    }
  }
  printdt3(&dt3);
}


printdt3(dtptr)
  struct distance_table *dtptr;
  
{

  printf("Node|  0       1        2       3 \n");
  printf("------------------------------------\n");
  printf("D%d  |  %d       %d        %d       %d         \n", 3,
  dtptr->costs[3][0], dtptr->costs[3][1], 
  dtptr->costs[3][2], dtptr->costs[3][3]);
  printf("\n\n");

}






