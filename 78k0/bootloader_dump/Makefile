CC=as78k0
LD=aslink
OBJCOPY=srec_cat

all: dump_bootl.asm
	$(CC) -o dump_bootl
	$(LD) -i dump_bootl.rel
	$(OBJCOPY) dump_bootl.ihx -intel -o dump_bootl.bin -binary

clean:
	@rm *.ihx *.bin *.rel
