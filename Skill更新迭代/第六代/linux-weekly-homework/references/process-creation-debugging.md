# 进程创建与首次执行的调试要点

用于 `fork`／`clone`、`task_struct` 初始化和新任务首次切换实验。示例依据第七周实际使用的32位 x86 Linux 3.18.6；架构、版本或配置不同，应先对照对应源码，不套用本页字段和布局。仍按一步操作、截图核对后再继续，不一次交付整套调试命令。

## 调试触发器与源码范围

- 先阅读当前 MenuOS 的命令注册和构建规则。缺少可控调用时再添加处理函数，保留原文件，编译本周专用程序和镜像。若 `make rootfs` 会自动启动 QEMU，单独构建，再带 `-s -S` 启动本周镜像。
- 库函数 `fork()` 可以通过 `clone` 系统调用实现；以实际断点和参数确认，不预先断言一定进入 `sys_fork`。`SyS_clone`、`SYSC_clone` 等名称可能由系统调用宏生成，结合源码和调用链辨认。
- 不逐屏机械抄录长函数。围绕“任务结构与栈分配、资源关系、身份初始化、首次现场、唤醒”读取必要源码；筛选输出会省略 `else` 和括号，解释分支时补看上下文。
- 触发程序在 `fork()` 前刷新待输出缓冲，子进程退出前保证所需输出可见，父进程用 `waitpid()` 回收。父子输出顺序以实测为准，不作为成功条件。

## 优化内核：先确认实际帧，再决定如何前进

第七周 `tbreak dup_task_struct` 实际停在 `copy_process()` 的调用行；`orig` 在该上下文不可见，随后 `finish` 退出了整个 `copy_process()`。避免重复此问题：

1. 断点命中后先看 GDB 显示的当前函数和源码位置，必要时用 `bt`、`info frame`、`info args`、`x/i $pc` 核对；不能只看设置断点时打印的名字。
2. 参数显示 `<optimized out>`、`No symbol` 或命中位置不同于预期时，停止依赖该参数的后续命令。不要预先让用户连续执行“读取参数 → `finish` → 解释返回值”。
3. `finish` 退出当前实际选中的函数帧。确认它是哪个函数、退出后会跳过哪些观察点，才执行；优先在必要源码行设置临时断点，或按实际指令定向前进。
4. 在对应函数返回的第一时间保存返回值，按本次 ABI 解释。例如32位 x86 中，成功的 `copy_process()` 返回可从当时的 EAX 保存为 `task_struct *`；不能把任意时刻的 EAX 或 `do_fork()` 返回的 PID 转成任务指针。

若已经执行完 `copy_process()`、但仍停在 `do_fork()` 唤醒之前，可保留同一次调用继续验证。对已确认未设置 `CLONE_PARENT`、`CLONE_THREAD` 的普通 `fork()`，可在父子关系初始化完成后使用：

```gdb
set $parent = $child->real_parent
```

前提是 `$child` 已从真实、成功的任务指针返回值保存，并核对当前停点。不要把它用于尚未初始化的结构，也不要对所有 `clone` 调用都声称 `real_parent` 就是调用者。

## 把身份、资源准备和实际执行分开验证

| 阶段 | 适合记录的证据 | 不能据此直接声称 |
| --- | --- | --- |
| `copy_process()` 成功返回、唤醒之前 | 父子任务指针、PID/TGID、父子关系、内核栈、初始化后的架构现场 | 子进程已经运行 |
| 子进程首次内核入口 | 当前 PC、SP 与预先保存的入口、栈位置对应 | 已经回到用户态 |
| 最终返回指令前后 | 返回现场、实际寄存器、权限级、用户地址及返回值 | 中间所有条件工作分支都已逐项跟踪 |
| 用户程序执行完成 | 父子返回结果、父子身份、等待回收与菜单恢复 | 每次父子输出顺序都相同 |

任务结构复制不等于所有资源深复制。普通 `fork()` 的独立地址空间可通过写时复制暂时共享物理页；文件描述符表与底层打开文件对象也要区分。没有实际检查的资源结构写为源码分析，不包装成 GDB 观察结果。

## 32位 Linux 3.18.6：首次入口与栈的配对检查

先在 `arch/x86/kernel/process_32.c` 核对 `copy_thread()`。该版本普通用户任务路径将 `thread.sp` 设为子任务的 `pt_regs` 地址，将 `thread.ip` 设为 `ret_from_fork`，复制用户寄存器现场并把 `ax` 改为0。`PF_KTHREAD` 分支使用另一入口，不能混作用户进程路径。

在初始化完成、尚未首次运行时，可按上述已核对的赋值检查：

```gdb
set $childregs = (struct pt_regs *)$child->thread.sp
info symbol $child->thread.ip
p/x $child->thread.sp
p/x $child->thread.sp0
p $childregs->ax
p/x $childregs->ip
p/x $childregs->sp
p $child->thread.sp0 == (unsigned long)($childregs + 1)
set $user_pc = $childregs->ip
set $user_sp = $childregs->sp
```

这是首次运行前的布局，不能在后续任意时刻把 `thread.sp` 都强转成 `pt_regs *`。保留 `$childregs` 的值，并在子任务退出释放内存之前使用。

区分 `thread.sp`、`thread.sp0` 与 `childregs->sp`：它们分别服务于切换使用的内核栈、内核入口栈相关设置和恢复后的用户栈。`newsp=0` 在本版本普通用户路径中表示不覆盖复制的用户栈指针，不表示使用地址0的栈。

该版本32位切换代码加载新任务栈指针，并通过预置执行位置转入首次入口。若源码和反汇编确认入口第一条指令前 SP 应指向保存区，可用以下条件捕获：

```gdb
tbreak *ret_from_fork if $esp == (unsigned long)$childregs
```

实际命中后比较当前 EIP、ESP 与准备值。入口处实际 EAX 可能用于切换参数；子进程的系统调用返回值此时应从保存的 `childregs->ax` 检查，不能要求入口 EAX 已为0。

`ret_from_fork` 调用 `schedule_tail` 再进入返回路径；`schedule_tail` 是首次切换收尾，不是重新创建进程。只检查切换前后结果时，报告应说明没有逐条单步整个 `switch_to`。

## 限定同一子任务的用户态返回

确认本版本 `irq_return` 指向普通32位 `iret` 且 SP 指向 `pt_regs.ip` 对应现场后，可用：

```gdb
set $iret_sp = (unsigned long)&$childregs->ip
tbreak *irq_return if $esp == $iret_sp && *(unsigned int *)$esp == $user_pc
```

命中后核对当前指令、栈中五项返回现场及 EAX，再单步比较用户 PC、SP、权限级和返回值0。使用成员地址推导返回现场，不把本次栈地址或固定字节偏移复制到下一次实验。

`iret` 消费的是已经准备好的返回现场；返回值通常已由之前的恢复代码装入 EAX，不是 `iret` 自行生成。用户恢复地址可能位于系统调用辅助代码或库代码中，随后才完成库函数返回，不能直接说内核跳到了 C 语句的下一行。

子进程结束后再核对父进程获得子 PID、子进程进入0返回值分支以及成功回收。保存实际失败和修正截图；报告可选取足够支撑结论的图片，不要求把全部原图重复嵌入。原图数量与正文嵌图数量分开记录。

第七周具体 PID、地址和图像数量仅在 [课程上下文](course-context.md) 中作为已完成实验线索保留，不作为未来成功条件。一般系统调用返回工作和入口判断见 [系统调用调试要点](system-call-debugging.md)。
