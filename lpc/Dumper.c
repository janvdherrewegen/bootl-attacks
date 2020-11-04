        unsigned char *Addr;
        char cChar;

        //Dump Sector 0
        for(Addr=(unsigned char *)0x00000000;Addr<=(unsigned char *)0x00000FFF;Addr++)
             {
                 while ( !(LPC_UART->LSR & THRE) );
                 cChar = *Addr;
                 LPC_UART->THR = cChar;
             }

        //Dump Sector 2->7
        for(Addr=(unsigned char *)0x00002000;Addr<=(unsigned char *)0x00007FFF;Addr++)
             {
                 while ( !(LPC_UART->LSR & THRE) );
                 cChar = *Addr;
                 LPC_UART->THR = cChar;
             }