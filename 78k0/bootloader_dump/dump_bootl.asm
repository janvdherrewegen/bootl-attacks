; This assembly code is for the 78K0/Kx2 MCU - change registers if needed	
	.area CODE1 (ABS)
	.org 0x0000

	SP = 0xfeb8      		; Initial stack pointer 
	P1 = 0xff01       
	RXB6 = 0xff0a          	;Receive buffer register 6
	TXB6 = 0xff0b      		; Transmit buffer register 6 
	PM1 = 0xff21      		; Port mode register 1 
	ASIM6 = 0xff50      	;Asynchronous serial interface mode register 0
	ASIS6 = 0xff53       ;Asynchronous serial interface status register 0
	ASIF6 = 0xff55       
	CKSR6 = 0xff56      	; Clock selection register 6 
	BRGC6 = 0xff57      	; Baud rate generator control register 6 
	ASICL6 = 0xff58      	; Asynchronous serial interface control register 6 
	OSCCTL = 0xff9f      	; Clock operation mode select register 
	RCM = 0xffa0           ; Internal oscillation mode register
	MCM = 0xffa1          ;Main clock mode register
	MOC = 0xffa2          ;Main OSC control register
	RESF = 0xffac       ; Reset flag
	PFCMD = 0xffc0		; Flash protect command reg - Not sure if the same on 78K0/Kx2
	PFS = 0xffc2		; Flash status register - again not sure	
	FLPMC = 0xffc4		; Flash programming mode control register
	IF0H = 0xffe1           ;Interrupt request flag register 0H
	MK0H = 0xffe5           ;Interrupt mask flag register 0H
	PR0H = 0xffe9           ;Priority level specification flag register 0H
	IMS = 0xfff0            ;Memory size switching register
	PCC = 0xfffb            ;Processor clock control register


rst_vect:
	.word _start	    ;VECTOR RST

unused0_vect:
	.word 0xffff            ;VECTOR (unused)

intwdt_vect:
	.word 0xffff            ;VECTOR INTWDT

intp0_vect:
	.word 0xffff            ;VECTOR INTP0

intp1_vect:
	.word 0xffff            ;VECTOR INTP1

intp2_vect:
	.word 0xffff            ;VECTOR INTP2

intp3_vect:
	.word 0xffff            ;VECTOR INTP3

intp4_vect:
	.word 0xffff            ;VECTOR INTP4

intp5_vect:
	.word 0xffff            ;VECTOR INTP5

intp6_vect:
	.word 0xffff            ;VECTOR INTP6

intp7_vect:
	.word 0xffff           ; VECTOR INTP7

intser0_vect:
	.word 0xffff           ;VECTOR INTSER0

intsr0_vect:
	.word 0xffff            ;VECTOR INTSR0

intst0_vect:
	.word 0xffff            ;VECTOR INTST0

intcsi30_vect:
	.word 0xffff            ;VECTOR INTCSI30

intcsi31_vect:
	.word 0xffff          ;00CTOR INTCSI31

intiic0_vect:
	.word 0xffff            ;VECTOR INTIIC0

intc2_vect:
	.word 0xffff            ;VECTOR INTC2

intwtni0_vect:
	.word 0xffff            ;VECTOR INTWTNI0

inttm000_vect:
	.word 0xffff            ;VECTOR INTTM000

inttm010_vect:
	.word 0xffff            ;VECTOR INTTM010

inttm001_vect:
	.word 0xffff            ;VECTOR INTTM001

inttm011_vect:
	.word 0xffff            ;VECTOR INTTM011

intad00_vect:
	.word 0xffff            ;VECTOR INTAD00

intad01_vect:
	.word 0xffff            ;VECTOR INTAD01

unused1_vect:
	.word 0xffff            ;VECTOR (unused)

intwtn0_vect:
	.word 0xffff            ;VECTOR INTWTN0

intkr_vect:
	.word 0xffff            ;VECTOR INTKR

unused2_vect:
	.word 0xffff            ;VECTOR (unused)

unused3_vect:
	.word 0xffff            ;VECTOR (unused)

unused4_vect:
	.word 0xffff            ;VECTOR (unused)

brk_i_vect:
	.word 0xffff            ;VECTOR BRK_I

callt_0_vect:
	.word 0xffff            ;VECTOR CALLT #0

callt_1_vect:
	.word 0xffff            ;VECTOR CALLT #1

callt_2_vect:
	.word 0xffff            ;VECTOR CALLT #2

callt_3_vect:
	.word 0xffff            ;VECTOR CALLT #3

callt_4_vect:
	.word 0xffff            ;VECTOR CALLT #4

callt_5_vect:
	.word 0xffff            ;VECTOR CALLT #5

callt_6_vect:
	.word 0xffff            ;VECTOR CALLT #6

callt_7_vect:
	.word 0xffff            ;VECTOR CALLT #7

callt_8_vect:
	.word 0xffff            ;VECTOR CALLT #8

callt_9_vect:
	.word 0xffff            ;VECTOR CALLT #9

callt_10_vect:
	.word 0xffff            ;VECTOR CALLT #10

callt_11_vect:
	.word 0xffff            ;VECTOR CALLT #11

callt_12_vect:
	.word 0xffff            ;VECTOR CALLT #12

callt_13_vect:
	.word 0xffff            ;VECTOR CALLT #13

callt_14_vect:
	.word 0xffff            ;VECTOR CALLT #14

callt_15_vect:
	.word 0xffff            ;VECTOR CALLT #15

callt_16_vect:
	.word 0xffff            ;VECTOR CALLT #16

callt_17_vect:
	.word 0xffff            ;VECTOR CALLT #17

callt_18_vect:
	.word 0xffff            ;VECTOR CALLT #18

callt_19_vect:
	.word 0xffff            ;VECTOR CALLT #19

callt_20_vect:
	.word 0xffff            ;VECTOR CALLT #20

callt_21_vect:
	.word 0xffff            ;VECTOR CALLT #21

callt_22_vect:
	.word 0xffff            ;VECTOR CALLT #22

callt_23_vect:
	.word 0xffff            ;VECTOR CALLT #23

callt_24_vect:
	.word 0xffff            ;VECTOR CALLT #24

callt_25_vect:
	.word 0xffff            ;VECTOR CALLT #25

callt_26_vect:
	.word 0xffff            ;VECTOR CALLT #26

callt_27_vect:
	.word 0xffff            ;VECTOR CALLT #27

callt_28_vect:
	.word 0xffff            ;VECTOR CALLT #28

callt_29_vect:
	.word 0xffff            ;VECTOR CALLT #29

callt_30_vect:
	.word 0xffff            ;VECTOR CALLT #30

callt_31_vect:
	.word 0xffff            ;VECTOR CALLT #31

	.byte 0x7f              ; Option byte area
	.byte 0x00              ;DATA 0x00 
	.byte 0x00              ;DATA 0x00 
	.byte 0x00              ;DATA 0x00 
	.byte 0x00              ;DATA 0x00 

_start:
	sel rb0
	movw sp,#SP
	call !_sysinit
	call !_main



_sysinit:
	call !_CLK_Init		; Initialise clock
	call !_UART6_Init	; Initialise UART init
	call !_UART6_Start
	ret

_main:
	movw ax, #0x0
.wait:	
	incw ax
	cmpw ax, #0xffff
	bc .wait
	call !_FlashStart
	movw ax, #0x8000	; Start dumping on address 0x8000 - where bootloader starts
.tx_loop:
	cmpw ax, #0xc000	; Max address
	bnc .inf_loop		; If finished, just loop infinitely
	movw hl, ax
	call !_UART6_SendByte
	incw ax
	br .tx_loop	

.inf_loop:
	br .inf_loop	

_FlashStart:
	mov PFCMD,#0xa5	
	mov FLPMC,#0x01
	mov FLPMC,#0xfe
	mov FLPMC,#0x01
	ret

_CLK_Init:			; Select internal high speed osc of 8MHz
	clr1 RCM.0		; Make sure internal oscillator is running
	mov OSCCTL, #0x0	; Select internal oscillator mode
	set1 MOC.7		; Stop X1/X2 oscillator
	clr1 RCM.1		;Internal low-speed oscillator oscillating
	clr1 MCM.2		; main sys clock = internal high speed osc clock            
	clr1 MCM.0		; peripheral HW clock = same 
	mov PCC, #0x0		; select fXP as main sys clock freq
	ret

_UART6_Init:
	clr1 ASIM6.6		; Disable transmission    
	clr1 ASIM6.5		; Disable reception 
	clr1 ASIM6.7   		; Resets the internal circuit 
	mov CKSR6,#0x00		; Set base clock as peripheral HW clock 
	mov BRGC6,#0x3c		; Set baud rate to 115200 - based on a weird frequency of 69000000
	mov ASIM6,#0x04		; Set mode to 8n1 
	mov ASICL6,#0x2		; LSB first
	or P1,#0x08     
	mov a,PM1       
	and a,#0xf7       
	mov PM1,a       
	mov a,PM1       
	or a,#0x10        
	mov PM1,a       
	ret               

_UART6_Start:			; Sets UART to transmit only
        set1 ASIM6.7		; Enable operation of internal clock
        set1 ASIM6.6		; Enable transmission
        ret         

_UART6_SendByte:		; Sends byte on the UART - byte pointer given in register hl. Blocks until transmit buffer empty!
	push ax
.wait_to_clear:			; Wait until ready to transmit
	mov a, ASIF6
	bt a.1, .wait_to_clear
	mov a, [hl]
	mov TXB6, a		; Move the byte into the transmit buffer
	pop ax
	ret




