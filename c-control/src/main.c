#include <generated/csr.h>
#include <time.h>

void isr(void) {
    asm("nop");
}

int main(void) {
    seven_segment_ctrl_write(0x1);
    uint16_t value = 0x0;
    
    while (1) {
	seven_segment_value_write(value);

	uint32_t dip_state = dip_state_read();
	
	if (dip_state == 0)
	{
		seven_segment_ctrl_write(0x0);
		msleep(200);
	} else {
		seven_segment_ctrl_write(0x1);
		value++;
		msleep(10*dip_state);
	}
    }
}
