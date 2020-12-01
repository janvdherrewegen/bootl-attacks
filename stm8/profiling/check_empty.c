#include <stdint.h>

#define CLK_CKDIVR	(*(volatile uint8_t *)0x50c6)
#define CLK_PCKENR1	(*(volatile uint8_t *)0x50c7)

// Port D since the UART_RX is on the same pin as PD6, UART_TX is on PD5
#define PD_ODR	(*(volatile uint8_t *)0x500f)
#define PD_DDR	(*(volatile uint8_t *)0x5011)
#define PD_CR1	(*(volatile uint8_t *)0x5012)




void main(void){
	CLK_PCKENR1 = 0xff;

	// set output
	PD_DDR = 0xf0;
	PD_CR1 = 0xf0;

	// Create trigger on PD5
	PD_ODR |= 0x20;
	

	// The first part of the bootloader: getting to rdp_check
__asm
	sim
	ld A, 0x8000
	cp A, #0x82
	jreq bootl_check
	cp A, #0xac
	jreq bootl_check
	jra rdp_check

bootl_check:
	ldw X, 0x487e  
	cpw X, #0x55aa 
	jreq rdp_check
	jra enter_app 

rdp_check:
	ld A, 0x500f
	or A, #0x80 // Using PD7 as the result GPIO since the UART_RX goes high sometimes after reset
	ld 0x500f, A

enter_app:
	nop
__endasm;

#ifdef ALWAYS_SUCCESS
	PD_ODR |= 0x80;
#endif
	
	for(;;);
}
