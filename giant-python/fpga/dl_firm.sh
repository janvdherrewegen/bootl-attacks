#!/bin/sh

cd $(dirname $0)
./FWLoader -c -f -uu uc.ihx -uf main.bit
