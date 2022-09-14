### gdb

```sh

```

看了很多参考说经过调试offset是20字节，笨办法get（我试出来的）。

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


### reference link

- https://hackmd.io/@duckie/start_pwnabletw
- https://v1ckydxp.github.io/2019/04/24/pwnable-tw-start-writeup/
- https://cool-y.github.io/2019/10/25/PWNtw-start/