import serial
from exceptions import *
from gpiozero import DigitalOutputDevice, DigitalInputDevice
import argparse

from time import sleep

import logging

import sys

class stm8_bootloader:
    '''Interfaces with the STM8 bootloader through UART'''
    
    GPIO_RESET  =   23
    GPIO_RELAY  =   18 


    BYTE_SYNCH  =   0x7f
    BYTE_ACK    =   0x79
    BYTE_NACK   =   0x1f
    BYTE_BUSY   =   0xaa
    BYTE_UNK    =   0x22

    CMD_GET     =   0x00
    CMD_READ    =   0x11
    CMD_ERASE   =   0x43
    CMD_WRITE   =   0x31
    CMD_SPEED   =   0x03
    CMD_GO      =   0x21


    serial_opts = {"stm8l": (9600, serial.EIGHTBITS, serial.PARITY_EVEN, serial.STOPBITS_ONE, 0.1), "stm8a": (9600, serial.EIGHTBITS, serial.PARITY_NONE, serial.STOPBITS_TWO, 0.01)}

    def __init__(self, chip = "stm8l"):
        self.gpio_relay = DigitalOutputDevice(self.GPIO_RELAY, initial_value = 1)
        if chip not in self.serial_opts:
            chip = "stm8l"
        logging.info("[+] STM8 bootloader with {}".format(chip))
        self.serial_port = serial.Serial("/dev/ttyAMA0", *self.serial_opts[chip])
        self.reset = DigitalOutputDevice(self.GPIO_RESET, initial_value = 0)

    def send(self, data):
        '''Sends data on the output port'''
        self.serial_port.write(bytes(data))

    def recv(self, n_bytes):
        '''Receives data from the input port'''
        return self.serial_port.read(n_bytes)

    def recv_ack(self):
        '''Should receive an ACK byte'''
        data = self.recv(1)
        if not data or not (data[0] == self.BYTE_ACK):
            raise NoAckError("No ACK received: {}".format(data))


    def send_w_chk(self, cmd):
        '''Sends command according to the bootloader protocol'''
        self.send([cmd, cmd ^ 0xff])
        self.recv_ack()

    def recv_frame(self):
        '''Receives a frame back from the MCU'''
        data = self.recv(2)
        if not data:
            raise NoResponseError("Didn't receive a frame")
        if data[0] != self.BYTE_ACK:
            raise InvalidHeaderError("Start of frame is not ACK: {:02x}".format(data[0]))
        elif len(data) < 2:
            raise InvalidFrameError("Didn't receive frame length: {}".format(data))
        data_l = data[1]
        data = self.recv(data_l + 1)
        if data[-1] != self.BYTE_ACK:
            raise InvalidFooterError("End of frame is not ACK")
        return data[0:-1]

    def get_addr_data(self, addr):
        '''Returns address data (including checksum)'''
        addr_data = [(addr >> 0x18) & 0xff, (addr >> 0x10) & 0xff, (addr >>  0x8) & 0xff, addr & 0xff]
        chk = 0
        for b in addr_data:
            chk ^= b
        return addr_data + [chk]


    def synchr_bootl(self):
        self.serial_port.reset_input_buffer()
        logging.debug("Sending BYTE_SYNCH")
        self.send([self.BYTE_SYNCH])
        logging.debug("Receiving BYTE_ACK")
        self.recv_ack()

    def exit_bootl(self):
        self.reset.off()
        self.gpio_relay.on()


    def enter_bootloader(self):
        self.gpio_relay.off()
        sleep(0.05)
        self.reset.off()
        self.reset.on()
        sleep(0.01)
        self.synchr_bootl()
        sleep(0.1)

    def get_bootl(self):
        self.send_w_chk(self.CMD_GET)
        data = self.recv_frame()
        return data

    def read_mem(self, addr, n_bytes, dump_f = None):
        sleep(0.1)
        self.send_w_chk(self.CMD_READ)
        sleep(0.1)
        self.send(self.get_addr_data(addr))
        self.recv_ack() # TODO get this in the send method?
        self.send_w_chk(n_bytes)
        mem = self.recv(n_bytes)
        logging.info(" ".join(["{:02x}".format(b) for b in mem]))
        return mem

    def write_mem(self, addr, data_f):
        '''Writes the bytes in data_f (binary file) to the specified address'''
        raise NotImplementedError("Not yet implemented")



if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(filename)s:%(funcName)s: %(message)s")
    parser = argparse.ArgumentParser(description='STM8 bootloader interface')
    parser.add_argument('function', choices = {"get", "read", "write"},
            help='Function to be called: [get, read, write, ]')
    parser.add_argument('--addr', required='read' in sys.argv or 'write' in sys.argv, type=lambda x: int(x,0),
            help='Only for read/write: the address to be written to/read from')
    parser.add_argument('--n_bytes', required='read' in sys.argv, type=lambda x: int(x,0),
            help='Only for read: the amount of bytes to be read')
    parser.add_argument('--dump_file', required='write' in sys.argv,
            help='Only for read/write: the file the output/input is written to/read from')

    args = parser.parse_args()

    bootl_if = stm8_bootloader("stm8a") 
    bootl_if.enter_bootloader()

    logging.info("[+] Bootloader active")

    if args.function == 'get':
        bootl_if.get_bootl()
    elif args.function == 'read':
        bootl_if.read_mem(args.addr, args.n_bytes, args.dump_file)
    

