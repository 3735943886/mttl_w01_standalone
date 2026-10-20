#include "sdk_settings_flash.h"
#include "flash_api.h"
#include "device_lock.h"
#include "FreeRTOS.h"
#include "sdk_memory.h"
#include <string.h>
extern flash_t flash;
/* Worker-owned append journal, two 64KiB banks; no legacy import. */
#define RECORD 1024u
#define COMMIT 1020u
#define COUNT 128u
static int scanned,latest=-1;
static uint32_t sequence;
static uint32_t address(unsigned s){return s<64?0x70000u+s*RECORD:0xe0000u+(s-64)*RECORD;}
static uint32_t word(const uint8_t *p){return (uint32_t)p[0]|(uint32_t)p[1]<<8|(uint32_t)p[2]<<16|(uint32_t)p[3]<<24;}
static void put(uint8_t *p,uint32_t n){unsigned i;for(i=0;i<4;i++)p[i]=(uint8_t)(n>>(8*i));}
static uint32_t crc(uint32_t c,const uint8_t *p,size_t n){unsigned i;while(n--){c^=*p++;for(i=0;i<8;i++)c=(c>>1)^((0u-(c&1))&0xedb88320u);}return c;}
static uint32_t checksum(const uint8_t *b,size_t n){return ~crc(crc(0xffffffffu,b,12),b+16,n);}
static int valid(const uint8_t *b){uint32_t n=word(b+8);return !memcmp(b,"J210",4)&&n>0&&n<=COMMIT-16&&word(b+COMMIT)==0&&word(b+12)==checksum(b,n);}
static int geometry(void){
 uint8_t a[3],b[3];uint32_t first,second;int ok;
 device_mutex_lock(RT_DEV_LOCK_FLASH);
 ok=flash_read_id(&flash,a,3)==3&&flash_read_id(&flash,b,3)==3&&!memcmp(a,b,3)&&a[0]&&a[0]!=255&&a[2]==20&&
 flash_stream_read(&flash,0x18,4,(uint8_t *)&first)==1&&flash_stream_read(&flash,0x9000,4,(uint8_t *)&second)==1&&
 (first&0xffffu)==0x2c&&second==0x80000;
 device_mutex_unlock(RT_DEV_LOCK_FLASH);return ok;
}
static int read_record(unsigned s,uint8_t *b){unsigned i;int ok=1;if(s>=COUNT)return 0;
 device_mutex_lock(RT_DEV_LOCK_FLASH);
 for(i=0;i<RECORD;i+=256)if(flash_stream_read(&flash,address(s)+i,256,b+i)!=1){ok=0;break;}
 device_mutex_unlock(RT_DEV_LOCK_FLASH);mttl_sdk_memory_sample();return ok;
}
static int scan(uint8_t *b){unsigned i;int found=-1;uint32_t seq=0;
 if(scanned)return 1;
 for(i=0;i<COUNT;i++){uint32_t s,d;if(!read_record(i,b))return 0;if(!valid(b))continue;s=word(b+4);
  if(found<0){found=(int)i;seq=s;continue;}d=s-seq;if(!d||d==0x80000000u)return 0;if(d<0x80000000u){found=(int)i;seq=s;}}
 latest=found;sequence=seq;scanned=1;return 1;
}
static int blank(const uint8_t *b){unsigned i;for(i=0;i<RECORD;i++)if(b[i]!=255)return 0;return 1;}
static int erase(unsigned s,uint8_t *b){unsigned i;int ok=1;uint32_t a=address(s)&~4095u;
 if(latest>=0&&(address((unsigned)latest)&~4095u)==a)return 0;
 device_mutex_lock(RT_DEV_LOCK_FLASH);flash_erase_sector(&flash,a);
 for(i=0;i<4096;i+=256){unsigned j;if(flash_stream_read(&flash,a+i,256,b)!=1){ok=0;break;}for(j=0;j<256;j++)if(b[j]!=255){ok=0;break;}if(!ok)break;}
 device_mutex_unlock(RT_DEV_LOCK_FLASH);return ok;
}
static int program(unsigned s,unsigned off,const uint8_t *b,unsigned n){uint8_t check[256];int ok;uint32_t a;
 if(s>=COUNT||!n||n>256||off>=RECORD||n>RECORD-off)return 0;a=address(s)+off;
 device_mutex_lock(RT_DEV_LOCK_FLASH);
 ok=flash_stream_write(&flash,a,n,(uint8_t *)b)>=0&&flash_stream_read(&flash,a,n,check)==1&&!memcmp(check,b,n);
 device_mutex_unlock(RT_DEV_LOCK_FLASH);memset(check,0,sizeof(check));return ok;
}
int mttl_sdk_settings_load(mttl_settings *out){uint8_t *b;int result=-1;
 if(!out||!geometry())return -1;scanned=0;latest=-1;sequence=0;
 b=pvPortMalloc(RECORD);if(!b)return -1;
 if(scan(b)){if(latest<0){mttl_settings_default(out);result=0;}
  else if(read_record((unsigned)latest,b)&&valid(b)&&mttl_settings_storage_unpack(b+16,word(b+8),out))result=1;}
 memset(b,0,RECORD);vPortFree(b);return result;
}
int mttl_sdk_settings_save(const mttl_settings *in){uint8_t *b;unsigned target,i;size_t n;uint32_t seq;int result=-1;
 if(!in||!mttl_settings_valid(in)||!geometry())return -1;
 b=pvPortMalloc(RECORD);if(!b)return -1;if(!scan(b))goto done;
 if(latest>=0){uint8_t *body=pvPortMalloc(RECORD);int same=0;if(!body)goto done;
  n=mttl_settings_storage_pack(in,body,COMMIT-16);
  if(!n||!read_record((unsigned)latest,b)||!valid(b)){memset(body,0,RECORD);vPortFree(body);goto done;}
  same=n==word(b+8)&&!memcmp(body,b+16,n);memset(body,0,RECORD);vPortFree(body);
  if(same){result=1;goto done;}}
 target=latest<0?0:((unsigned)latest+1)%COUNT;
 if((target&3)!=0){if(!read_record(target,b))goto done;if(!blank(b))target=((target+3)&~3u)%COUNT;}
 if((target&3)==0&&!erase(target,b))goto done;
 memset(b,255,RECORD);n=mttl_settings_storage_pack(in,b+16,COMMIT-16);if(!n)goto done;
 memcpy(b,"J210",4);seq=latest<0?0:sequence+1;put(b+4,seq);put(b+8,(uint32_t)n);put(b+12,checksum(b,n));
 for(i=0;i<COMMIT;){unsigned take=COMMIT-i;if(take>256)take=256;if(!program(target,i,b+i,take))goto done;i+=take;}
 put(b+COMMIT,0);if(!program(target,COMMIT,b+COMMIT,4)||!read_record(target,b)||!valid(b)||word(b+4)!=seq)goto done;
 latest=(int)target;sequence=seq;result=1;
done:if(result<0)scanned=0;memset(b,0,RECORD);vPortFree(b);return result;
}
