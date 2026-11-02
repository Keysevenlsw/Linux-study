# 课程上下文与资料索引

## 已确认的信息

- 姓名：刘顺文；学号：20262819。
- 课程工作区：`D:/Study/研一课程/Linux原理与实践`；作业放在其 `Linux作业/` 下。
- 教材：根目录 `庖丁解牛Linux操作系统分析.pdf`，414 页扫描版。当前目录有 ARM64、openEuler、KVM、容器相关章节，不能假定与旧博客使用的版次相同。
- 每周任务检索入口：根目录 `《Linux内核原理与分析》CSDN博客.mhtml`。用户于2026-10-21指定以后按周到此文件查找作业，用户同时发送的当次说明优先。文件虽被称为 HTML，实际是 MHTML 归档；先解析 MIME 并解码正文，再按 HTML 声明的字符集读取。本文件的 MIME HTML 部分没有 charset，但 HTML meta 声明 UTF-8，不能用 email 默认 ASCII 解码后再做检索。只提取对应周作业，不使用考核方案、旧学期进程、截止日期、推荐、评论等其他部分。
- 实验平台：蓝桥云课，`https://www.lanqiao.cn/`。
- 云班课视频由学生本人观看，按2026-10-18用户要求默认已完成，不追问观看状态；有最新明确进度时以该说明为准。
- 章节总结由助手检索网上对应章节的总结、笔记和技术资料后归纳；默认不打开或渲染本地教材 PDF。提交正文不加来源行、页码串、豆列说明或文末参考资料章节，个人总结与心得直接写好。
- 默认跳过“基于树莓派或其他平台完成 ARM 相关内容”、关注豆列“Linux内核及安全”等拓展关注任务，不列为未完成项。教材中与指定主题有关的架构概念仍可按需解释，不由此新增 ARM 实践。
- 2026-10-21确认的流程：一步命令／代码 → 用户截图 → 核对和必要修复 → 下一步；用户直接说明已完成及路径时可据此继续。实验完成后先交 Markdown，等待审核；用户后续明确要求才导出 PDF 或迭代 skill，不能从博客的提交格式推断可以提前做这两项。
- 2026-10-31确认的环境偏好：蓝桥云课每次进入都是全新环境，用户要求不做例行环境验证。开始实验时不先索取 `uname`、版本、旧周目录的整批输出，直接准备当前任务；不假设上周的源码修改、程序或镜像仍存在。实际报错后的必要定向排查仍可进行，报告中未采集的版本不补写。
- 2026-10-11 建立 skill 时，用户说已经做到第三周；文件中能明确识别的材料为安装与基础报告、第二周预习、课堂命令测试。不要将课堂测试擅自归为第三周，也不要因此否定用户的进度。

## 已有风格样本

相对课程根目录：

- `Linux作业/第二周预习作业/20262819《Linux内核原理与分析》第二周预习作业.md`：常规周作业的主要版式依据。
- `Linux作业/Linux安装与基础/Linux安装与基础学习报告.md`：安装类任务的短报告样本。
- `Linux作业/课上测试：Linux命令实践（AI）/20262819-刘顺文-Linux命令实践.md`：命令实践、错误说明与材料纠错样本。

旧样本图片多引用 `C:/Users/sevenlsw7/AppData/Roaming/Typora/typora-user-images/`，新作业改用 `assets/`。已有样本只作风格证据，不自动修改旧作业。

## 本地博客的作业检索索引

下表只作本地归档的周次检索索引，不代替每次读取原文件。用户已指定其中的每周作业段落为检索入口，其他旧信息不使用；用户当次发送的要求和删减优先。表中章节序号按归档原文，章节主题按当前教材确认，不能用视频主题替换教材章节。

| 归档周次 | 归档阅读章节 | 视频／实验线索 |
| --- | --- | --- |
| 第一周 | 未列具体章节 | Ubuntu 安装、Linux 核心命令、Linux 基础入门 |
| 第二周 | 第1、2章 | 计算机是如何工作的；实验一 |
| 第三周 | 第3章 | 操作系统是如何工作的；实验二 |
| 第四周 | 第4章 | 构造一个简单的 Linux 系统 MenuOS；实验三 |
| 第五周 | 第5章 | 扒开系统调用的三层皮（上）；实验四 |
| 第六周 | 第6章 | 扒开系统调用的三层皮（下）；实验五 |
| 第七周 | 第7章 | 进程的执行和进程的切换；实验六 |
| 第八周 | 第8章 | Linux 内核的实质和 Linux 系统的一般执行过程；实验七 |
| 第九周 | 第9章 | Linux 系统架构和执行过程概览；实验八 |
| 第十周 | 第10、11章 | 原作业段未指定视频和编号实验 |
| 第十一周 | 第12章 | 原作业段未指定视频和编号实验 |
| 第十二、十三周 | 未列具体章节 | Linux 安全类实验；旧版提到两人一组、题目不能重复，今年另行核对 |

第二周起作业原文要求标题采用“学号《Linux内核原理与分析》第X周作业”，记录教材、视频、问题和解决方案，提交 Markdown 及 PDF。实际生成顺序遵从用户偏好：先实验和 MD 审核，之后收到导出指令再生成 PDF。

本次核对发现：当前教材第3章是“Linux 内核源代码及调试环境”，而旧版第三周视频主题为“操作系统是如何工作的”；当前第4章是系统调用，而旧第四周主题是 MenuOS。两者不可强行合并成同一教学范围。

## 当前教材章节定位（识别主题用，原文核对按需进行）

下表保留先前核对的章节名和页码映射，用于识别老师所说章节的主题、区分版次；不是要求每周逐页读取扫描 PDF。只有用户明确要求核对原文或页码时，才使用以下 PDF 定位和渲染工具。

目录位于 PDF 第12–19页。正文书内第1页位于 PDF 第20页；**当前文件正文 PDF 页码 = 书内页码 + 19**。页码从1开始，Python 索引另减1。该映射已对照正文开头确认；未来换文件或跨扫描缺页时需再核验。

| 章 | 实际章名 | 书内页码范围 | PDF 页码范围 |
| --- | --- | --- | --- |
| 1 | Linux 操作系统概览 | 1–26 | 20–45 |
| 2 | 计算机系统的基本工作原理 | 27–89 | 46–108 |
| 3 | Linux 内核源代码及调试环境 | 90–111 | 109–130 |
| 4 | 深入理解系统调用 | 112–153 | 131–172 |
| 5 | 进程的描述和创建 | 154–197 | 173–216 |
| 6 | 可执行程序工作原理 | 198–233 | 217–252 |
| 7 | 中断处理、内核线程和设备驱动 | 234–254 | 253–273 |
| 8 | 进程调度与进程切换 | 255–282 | 274–301 |
| 9 | Linux 操作系统的软件架构 | 283–290 | 302–309 |
| 10 | KVM 及虚拟机技术 | 291–308 | 310–327 |
| 11 | Linux 容器技术 | 309–353 | 328–372 |
| 12 | Linux 系统安全相关技术 | 354–末页 | 373–414 |

章节末页范围以后一章起始页反推；第12章目录列“本章实验”起于书内394页，是否覆盖末页需实际读取。索引是定位工具，不是已完成阅读的证明。

与现有第二周实验有关的定位：§2.2 x86 汇编基础（书内35页起）、§2.2.5 函数调用堆栈框架（53页起）、§2.3 ARM64 汇编（58页起）、§2.5 精简操作系统内核（75页起）。仅在相应任务下阅读和使用。

## 第六周已完成实验的连续性线索

- 第五、六周选择的同一个系统调用是 `write`；i386 ABI 的调用号为4。下一周若要求延续前次选择，可先从现有报告核对，不必重新询问。
- 第六周在课程预置的32位 Linux 3.18.6 中调试。工作目录为 `~/LinuxKernel`，MenuOS 源目录为 `menu/`；这些是定位线索，不保证未来新环境的文件布局完全相同。
- 原 MenuOS 的一次 `help` 输出在 `sys_write` 返回到 `sysenter_after_call`，未命中 `system_call`；本次在 `test.c` 新增 `write80`，通过 `int $0x80` 写入14字节的 `Hello syscall\n`。
- 用户程序编译为 `menu/init-week6`，独立镜像为 `rootfs-week6.img`。全新环境需要重新准备，不能声称这些材料已经存在。
- 实测返回标志为 `0x8`，进入 `schedule()` 后再经 `irq_return` 的 `iret` 回到用户态，`eax=14`。该标志、函数地址、用户地址和栈位置都是本次观察值，不作未来实验固定常量。条件调试方法见 [系统调用调试要点](system-call-debugging.md)。
- 本周 MD 和同名 PDF 位于 `Linux作业/第六周作业/`；2026-10-31导出 PDF 共22页、18张内嵌图片，PNG/SVG 流程图保存在该目录 `assets/`。

## 工具命令

本 skill 提供工具，不依赖 Typora 手工导出。下列命令中的 `node`／`python` 应为实际存在的运行时。课程根目录是工作目录。

```powershell
# 从本地归档只提取第六周作业，默认滤去 ARM 实践和豆列关注条目
python .\skills\linux-weekly-homework\scripts\read_week_assignment.py '.\《Linux内核原理与分析》CSDN博客.mhtml' --week 6

# 从 MD 自动生成同目录同名 PDF
node .\skills\linux-weekly-homework\scripts\md_to_pdf.mjs 'Linux作业\第四周作业\20262819《Linux内核原理与分析》第四周作业.md'

# 仅在用户明确要求核对原文时：渲染书内 pp.90–97（PDF pp.109–116）
python .\skills\linux-weekly-homework\scripts\render_book.py '.\庖丁解牛Linux操作系统分析.pdf' --start 90 --end 97 --printed --out '.\tmp\reading\week-4'

# 同步可维护源版本到 Codex 技能目录
powershell -NoProfile -ExecutionPolicy Bypass -File .\skills\linux-weekly-homework\scripts\install_skill.ps1
```

`render_book.py` 保留用于用户明确要求的原文核对，默认章节总结不调用它；它依赖 Poppler 的 `pdftoppm` 与 `pdfinfo`，只使用 Python 标准库，可用 `--poppler-dir` 指定。需要核对时，渲染不等于阅读，应实际查看相关图片。打印工具依赖 `marked`、`playwright`，可通过 `--modules-dir` 或 `LINUX_SKILL_NODE_MODULES` 指定包目录；浏览器通过 `--browser` 指定，否则按本地 Edge／Chrome／Playwright Chromium 查找。外部网络图片默认报错，应先核验并保存本地；不能默默丢图。

本机已检测运行时：

```text
Node: C:/Users/sevenlsw7/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe
Node 模块: C:/Users/sevenlsw7/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules
Python: C:/Users/sevenlsw7/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe
Poppler: C:/Users/sevenlsw7/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/Library/bin
浏览器: C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe
```

运行时路径是本机提示，不保证其他电脑相同。新版 Codex 可先调用 `load_workspace_dependencies` 获取实际路径。PDF 浏览器转换仅处理生成的本地文档，不操作学生已有浏览器会话。
