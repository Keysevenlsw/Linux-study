from pathlib import Path
from html import escape
from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent
W, H = 1500, 1820
im = Image.new('RGB', (W, H), 'white')
d = ImageDraw.Draw(im)
font_path = 'C:/Windows/Fonts/msyh.ttc'
fonts = {s: ImageFont.truetype(font_path, s) for s in [21, 23, 24, 27, 36]}
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">', '<rect width="100%" height="100%" fill="white"/>']
ink = '#20334a'
blue = '#235789'

def text(x, y, value, size=24, color=ink):
    lines = value.split('\n')
    line_h = size + 10
    first = y - (len(lines) - 1) * line_h / 2
    for i, line in enumerate(lines):
        cy = first + i * line_h
        d.text((x, cy), line, font=fonts[size], fill=color, anchor='mm')
        svg.append(f'<text x="{x}" y="{cy}" text-anchor="middle" dominant-baseline="central" font-family="Microsoft YaHei, sans-serif" font-size="{size}" fill="{color}">{escape(line)}</text>')

def box(x, y, label, w=640, h=88, optional=False):
    fill = '#f3f5f7' if optional else '#eef5fc'
    edge = '#7b8795' if optional else blue
    rect = (x-w/2, y-h/2, x+w/2, y+h/2)
    d.rounded_rectangle(rect, radius=14, fill=fill, outline=edge, width=3)
    svg.append(f'<rect x="{rect[0]}" y="{rect[1]}" width="{w}" height="{h}" rx="14" fill="{fill}" stroke="{edge}" stroke-width="3"/>')
    text(x, y, label, 23 if optional else 24)

def diamond(y, label):
    points = [(650, y-58), (930, y), (650, y+58), (370, y)]
    d.polygon(points, fill='#fff8e7', outline=blue, width=3)
    svg.append('<polygon points="'+' '.join(f'{x},{yy}' for x, yy in points)+f'" fill="#fff8e7" stroke="{blue}" stroke-width="3"/>')
    text(650, y, label)

def arrow(points, color=blue):
    d.line(points, fill=color, width=3)
    x, y = points[-1]
    px, py = points[-2]
    if x > px: tri = [(x,y),(x-12,y-6),(x-12,y+6)]
    elif x < px: tri = [(x,y),(x+12,y-6),(x+12,y+6)]
    elif y > py: tri = [(x,y),(x-6,y-12),(x+6,y-12)]
    else: tri = [(x,y),(x-6,y+12),(x+6,y+12)]
    d.polygon(tri, fill=color)
    svg.append('<polyline points="'+' '.join(f'{xx},{yy}' for xx,yy in points)+f'" fill="none" stroke="{color}" stroke-width="3"/>')
    svg.append('<polygon points="'+' '.join(f'{xx},{yy}' for xx,yy in tri)+f'" fill="{color}"/>')

text(750, 42, '32位 x86 系统调用处理流程', 36)
text(750, 90, 'Linux 3.18.6 · write 系统调用 · int 0x80 入口', 23, '#58677a')

box(650, 175, '用户态：准备调用号和参数，执行 int $0x80')
box(650, 310, 'CPU 切换到内核栈\n保存 EIP、CS、EFLAGS、用户 ESP 和 SS')
box(650, 445, 'system_call：保存原调用号、SAVE_ALL\n准备内核环境并取得线程信息')
diamond(580, '需要入口工作处理？')
box(1230, 580, 'syscall_trace_entry\n跟踪 / 审计等入口处理', 350, 94, True)
diamond(745, '系统调用号有效？')
box(150, 745, '无效调用号\n返回 -ENOSYS', 250, 94, True)
box(650, 900, 'syscall_call：调用 sys_call_table[eax]\n本次：SyS_write → 写入 → 返回14')
box(650, 1040, 'syscall_after_call\n将返回值保存到现场的 EAX 槽位')
diamond(1200, '还有返回前工作？')
box(1230, 1200, '处理退出跟踪、调度、\n信号和通知等工作\n本次实际调用 schedule()', 350, 126, True)
box(650, 1400, 'restore_all / restore_nocheck\n恢复寄存器，跳过原调用号等槽位')
box(650, 1540, 'irq_return：执行 iret\n恢复用户执行位置、标志及用户栈')
box(650, 1680, '用户态：从 int $0x80 后继续执行\n本次 EAX=14，返回 EIP=0x0804a04d')

for a,b in [(219,266),(354,401),(489,522),(638,687),(803,856),(944,996),(1084,1142),(1258,1356),(1444,1496),(1584,1636)]:
    arrow([(650,a),(650,b)])
text(610, 658, '否', 21)
text(610, 825, '是', 21)
text(610, 1300, '否', 21)
arrow([(930,580),(1055,580)], '#7b8795')
text(990,550,'是',21)
arrow([(1230,627),(1230,665),(650,665),(650,687)], '#7b8795')
arrow([(370,745),(275,745)], '#7b8795')
text(320,715,'否',21)
arrow([(150,792),(150,1040),(330,1040)], '#7b8795')
arrow([(930,1200),(1055,1200)], '#7b8795')
text(990,1170,'是',21)
arrow([(1230,1263),(1230,1320),(1020,1320),(1020,1110),(650,1110),(650,1142)], '#7b8795')
text(1200,1352,'处理后重新检查',21,'#58677a')
text(750, 1770, '灰色框为条件处理；本次进入重新调度分支。省略特殊段栈和异常修复细节。', 21, '#58677a')

svg.append('</svg>')
im.save(OUT / 'system_call流程图.png')
(OUT / 'system_call流程图.svg').write_text('\n'.join(svg), encoding='utf-8')
print('Created PNG and SVG flowchart')
