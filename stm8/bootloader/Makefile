CC=sdcc

all: bl_dump.c
	$(CC) -mstm8 --std-c99 --no-peep bl_dump.c
	@mv bl_dump.ihx bl_dump.hex

clean:
	@rm -f *.ihx *.o *.asm *.lst *.map *.cdb *.lk *.rel *.rst *.sym *.hex
