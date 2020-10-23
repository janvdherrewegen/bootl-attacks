CC=sdcc

all: test.c
	$(CC) -mstm8 --std-c99 --no-peep test.c
	@mv test.ihx test.hex

clean:
	@rm -f *.ihx *.o *.asm *.lst *.map *.cdb *.lk *.rel *.rst *.sym *.hex
