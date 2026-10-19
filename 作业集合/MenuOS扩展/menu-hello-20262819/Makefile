#
# Makefile for Menu Program
#

CC_PTHREAD_FLAGS			 = -lpthread
CC_FLAGS                     = -c 
CC_OUTPUT_FLAGS				 = -o
CC                           = gcc
RM                           = rm
RM_FLAGS                     = -f

TARGET  =   test
OBJS    =   linktable.o  menu.o test.o

all:	$(OBJS)
	$(CC) $(CC_OUTPUT_FLAGS) $(TARGET) $(OBJS) 
rootfs:
	gcc -std=gnu11 -m32 -static -fno-pie -no-pie -o init linktable.c menu.c test.c -lpthread
	gcc -std=gnu11 -m32 -static -fno-pie -no-pie -o hello hello.c
	mkdir -p rootfs/dev
	cp init hello rootfs/
	test -c rootfs/dev/console || sudo mknod -m 600 rootfs/dev/console c 5 1
	test -c rootfs/dev/null || sudo mknod -m 666 rootfs/dev/null c 1 3
	bash -o pipefail -c 'cd rootfs && find . -print0 | cpio --null -o -H newc --owner=0:0 | gzip -9 > ../../rootfs.img'
qemu: rootfs
	qemu -kernel ../linux-3.18.6/arch/x86/boot/bzImage -initrd ../rootfs.img
qemu-gdb: rootfs
	qemu -kernel ../linux-3.18.6/arch/x86/boot/bzImage -initrd ../rootfs.img -s -S
.c.o:
	$(CC) $(CC_FLAGS) $<

clean:
	$(RM) $(RM_FLAGS)  $(OBJS) $(TARGET) *.bak
