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
} dt0;

int neighbors0[4]={0,1,3,7};
/* students to write the following two routines, and maybe some others */
//初始化，将所有距离都设为999
int i,j;
void Initial0()
{

  for(i=0;i<4;i++)
  {
    for(j=0;j<4;j++)
    {
      dt0.costs[i][j]=999;
    }
  }
}
int min(int a,int b)
{
  return a<b?a:b;
}

void rtinit0() 
{
  // printf("hhhn\n");
  // printf("%d\n",min(1,2));
  Initial0();
  //更新0到其他节点的距离
  for(i=0;i<4;i++)
  {
    dt0.costs[0][i]=neighbors0[i];
  }
  //向各个邻居发送初始化内容
  for(i=0;i<4;i++)
  {
    if(neighbors0[i]!=999&&i!=0){
      struct rtpkt pkt;
      pkt.sourceid=0;
      pkt.destid=i;
      for(j=0;j<4;j++)
      {
        pkt.mincost[j]=dt0.costs[0][j];
      }
      tolayer2(pkt);
    }
  }
  printdt0(&dt0);
}


void rtupdate0(rcvdpkt)
  struct rtpkt *rcvdpkt;
{
  int sourceid=rcvdpkt->sourceid;
  //更新最短距离
  for(i=0;i<4;i++)
  {
    for(j=0;j<4;j++)
    {
      // printf("%d %d %d %d\n",i,j,dt0.costs[i][j],dt0.costs[i][sourceid]+rcvdpkt->mincost[j]);
      dt0.costs[i][j]=min(dt0.costs[i][j],dt0.costs[i][sourceid]+rcvdpkt->mincost[j]);
      // printf("%d\n",dt0.costs[i][j]);
    }
  }
  //将更新后的信息发送给各个邻居
  for(i=0;i<4;i++)
  {
    if(neighbors0[i]!=999&&i!=0){
      struct rtpkt pkt;
      pkt.sourceid=0;
      pkt.destid=i;
      for(j=0;j<4;j++)
      {
        pkt.mincost[j]=dt0.costs[0][j];
      }
      tolayer2(pkt);
    }
  }
  printdt0(&dt0);
}


printdt0(dtptr)
  struct distance_table *dtptr;
  
{
  
  
  printf("Node|  0       1        2       3 \n");
  printf("------------------------------------\n");
  printf("D%d  |  %d       %d        %d       %d         \n", 0,
  dtptr->costs[0][0], dtptr->costs[0][1], 
  dtptr->costs[0][2], dtptr->costs[0][3]);
  printf("\n\n");
}

linkhandler0(linkid, newcost)   
  int linkid, newcost;

/* called when cost from 0 to linkid changes from current value to newcost*/
/* You can leave this routine empty if you're an undergrad. If you want */
/* to use this routine, you'll need to change the value of the LINKCHANGE */
/* constant definition in prog3.c from 0 to 1 */
	
{
  neighbors0[linkid]=newcost;
  rtinit0();
  rtinit1();
  rtinit2();
  rtinit3();
}
