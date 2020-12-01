CC=sdcc

enter_app: enter_app.c
	$(CC) -mstm8 --std-c99 --no-peep enter_app.c
	@mv enter_app.ihx enter_app.hex

chk_empty: check_empty.c
	$(CC) -mstm8 --std-c99 --no-peep check_empty.c
	@mv check_empty.ihx check_empty.hex
	
clean:
	@rm -f *.ihx *.o *.asm *.lst *.map *.cdb *.lk *.rel *.rst *.sym *.hex
	
	
