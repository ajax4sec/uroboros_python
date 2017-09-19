import re
import capstone
from struct import unpack
from elfesteem import elf, elf_init

def load_size(op, exp):
    # Return byte size of the memory load
    op = op.lower()
    if op.startswith('vldr'):
        return 4 if exp.startswith('s') else 8
    if op.startswith('ldr'):
        if len(op) < 4 or op[3] == '.': return 4
        if op[3] == 'd': return 8
        if op[3] == 'h' or (op[3] == 's' and op[4] == 'h'): return 2
        return 1
    return 4

def tb_process(offsize, pc, buf, filehandle):
    if offsize > 2:
        # ldr jumptable
        # TODO: stub
        pass
    else:
        # tb[hb] jumptable
        # TODO: this is not super clean and must be fixed, things will get broken
        # if new instructions are inserted since offsets won't be valid anymore.
        # A solution could be transforming it to a ldr jumptable but the value
        # of the register acting as table index would be modified.
        i = 0
        unpacker = '<H' if offsize == 2 else '<B'
        datatype = ('.short' if offsize == 2 else '.byte').ljust(7)
        while i < len(buf):
            val = unpack(unpacker, buf[i:i+offsize])[0]
            filehandle.write(('%x' % (pc+i)).rjust(8) + ':\t' + datatype + ' 0x%X\n' % val)
            i += offsize

def eval_tb_size(op, last_cmp, reg):
    if reg != last_cmp[0]: raise Exception('Unhandled jumptable case')
    offsize = 4 if op.startswith('ldr') else (2 if op[-1] == 'h' else 1)
    tablesize = (int(last_cmp[1].strip()[1:], 16) + 1) * offsize
    tablesize += (tablesize & 1) # For 2 byte alignment
    return (offsize, tablesize)

def arm_process(filename):
    # Disassemble the binary processing PC relative loads
    #     ldr.w   ip, [pc, #16]
    # library function invokations
    #     blx     #0x10a40 <strcmp@plt>
    # inline jump tables
    #     tbh     [pc, r3, lsl #1]
    #      .short  0x0123
    #       ...
    #  or
    #     addr    r2, pc, #4
    #     ldr     pc, [r2, r3, lsl #2]
    #      .word   0x00010545
    #      ...

    with open(filename, 'rb') as f:
        raw = f.read()
    info = elf_init.ELF(raw)

    voffset = filter(lambda h: elf.constants['PT'].get(h.ph.type, '') == 'LOAD' and h.ph.offset == 0, info.ph.phlist)
    voffset = voffset[0].ph.vaddr
    textsec = info.getsectionbyname('.text')
    textraw = raw[textsec.addr - voffset : textsec.addr + textsec.size - voffset]
    with open('plts.info') as f:
        plts = {int(l.split()[0],16): ' ' + l.split()[1].rstrip(':') for l in f}

    dis = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
    dis.syntax = capstone.CS_OPT_SYNTAX_ATT

    inlinedata = {}
    last_cmp = ('', '')
    pcrelre = re.compile('\[pc,\s*\#0x([0-9a-f]+)\]', re.I)
    pcreltblre = re.compile('\[pc,\s*(r[0-9]+)(,\s*lsl \#1)?\]|pc,\s*\[r[0-9],\s*(r[0-9]),\s*lsl\s*\#2\]', re.I)
    calls = set(('bl', 'blx'))
    offtableop = set(('tbb', 'tbh'))
    f = open('instrs.info', 'w')
    curr_off = 0
    while curr_off < textsec.size:
        for e in dis.disasm_lite(textraw[curr_off:], textsec.addr + curr_off):
            curr_off += e[1]
            if e[2] == 'cmp': last_cmp = tuple(e[3].split(','))
            instr = ('%x' % e[0]).rjust(8) + ':\t' + e[2].ljust(7) + ' ' + e[3].replace(', ', ',').replace(' ', '|')
            m = pcrelre.search(instr)
            if m:
                # Insert label for PC relative loads
                dest = (e[0] & 0xFFFFFFFC) + int(m.group(1), 16) + 4
                inlinedata[dest] = load_size(e[2], e[3])
                instr = pcrelre.sub('0x%X' % dest, instr)
            elif e[2] in calls and e[3].startswith('#'):
                # Insert plt symbol
                instr += plts.get(int(e[3][1:], 16), '')
            f.write(instr + '\n')
            if e[2] in offtableop or e[2].startswith('ldr'):
                # Process inline jumptable
                m = pcreltblre.search(e[3])
                if m:
                    offsize, tablesize = eval_tb_size(e[2], last_cmp, m.group(0))
                    tb_process(offsize, curr_off + textsec.addr, textraw[curr_off:curr_off + tablesize], f)
                    curr_off += tablesize
                    break
            if curr_off + textsec.addr in inlinedata: break
        else:
            if curr_off < textsec.size: inlinedata[curr_off + textsec.addr] = 2
        while curr_off + textsec.addr in inlinedata:
            # Parse inline data
            pc = curr_off + textsec.addr
            size = inlinedata.pop(pc)
            if size == 1:
                vals = unpack('<BB', textraw[curr_off:curr_off+2])
                f.write(('%x' % pc).rjust(8) + ':\t.byte   0x%x\n' % vals[0])
                f.write(('%x' % (pc+1)).rjust(8) + ':\t.byte   0x%x\n' % vals[1])
                size = 2
            else:
                if size == 8:
                    inlinedata[pc+4] = 4
                    size = 4
                val = unpack('<H' if size == 2 else '<I', textraw[curr_off:curr_off+size])[0]
                f.write(('%x' % pc).rjust(8) + ':\t' + ('.short' if size == 2 else '.word').ljust(7) + ' 0x%x\n' % val)
            curr_off += size
    f.close()
