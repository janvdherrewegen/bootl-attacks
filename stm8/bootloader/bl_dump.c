// Source: http://www.colecovision.eu
// compile sdcc -lstm8 -mstm8 --out-fmt-ihx --std-sdcc11

#include <stdint.h>

// Peripherals for the init code

#define PC_DDR		(*(volatile uint8_t *)0x500c)
#define PC_CR1		(*(volatile uint8_t *)0x500d)

#define UART2_SR	(*(volatile uint8_t *)0x5240)
#define UART2_DR	(*(volatile uint8_t *)0x5241)
#define UART2_BRR1	(*(volatile uint8_t *)0x5242)
#define UART2_BRR2	(*(volatile uint8_t *)0x5243)
#define UART2_CR2	(*(volatile uint8_t *)0x5245)
#define UART2_CR3	(*(volatile uint8_t *)0x5246)

#define UART_CR2_TEN (1 << 3)
#define UART_CR3_STOP2 (1 << 5)
#define UART_CR3_STOP1 (1 << 4)
#define UART_SR_TXE (1 << 7)


#define CLK_CKDIVR	(*(volatile uint8_t *)0x50c6)
#define CLK_PCKENR1	(*(volatile uint8_t *)0x50c7)

static char putchar(char c)
{
	while(!(UART2_SR & UART_SR_TXE ));
	UART2_DR = c;
	return UART2_DR;

}


void main(void)
{
	unsigned char* addr;

	CLK_PCKENR1 = 0xff;
	CLK_CKDIVR = 0x00;


	PC_DDR = 0x08;
	PC_CR1 = 0x08;

	UART2_CR2 = UART_CR2_TEN; // Allow TX and RX
	UART2_CR3 &= ~(UART_CR3_STOP1 | UART_CR3_STOP2); // 1 stop bit
	UART2_BRR2 = 0x03; UART2_BRR1 = 0x68; // 9600 baud

	for(addr=(unsigned char *)0x006000;addr<(unsigned char *)0x008000;addr++)
	{
		putchar(*addr);	
	}

	for(;;);
}
