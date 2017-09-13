import config

class RecSet(frozenset):
    def __init__(self, elems, final=False):
        self.final = final
        elems = map(lambda e: e.upper() if isinstance(e, str) else e, elems)
        super(RecSet, self).__init__(elems)

    def __new__(cls, elems, final=False):
        elems = map(lambda e: e.upper() if isinstance(e, str) else e, elems)
        return super(RecSet, cls).__new__(cls, elems)

    def __contains__(self, item):
        if isinstance(item, str): item = item.upper()
        if super(RecSet, self).__contains__(item):
            return True
        elif not self.final:
            return any(map(lambda e: isinstance(e, frozenset) and item in e, self))
        return False

class Container(object):
    def __init__(self, content):
        self.content = content
    def __repr__(self):
        return repr(self.content)
    def __str__(self):
        return str(self.content)

class File(object):
    def __init__(self, name, stripped, fformat, is32):
        self.name = name
        self.stripped = stripped
        self.format = fformat
        self.is32bit = is32

class Func(object):
    def __init__(self, name, begin, end, is_lib):
        self.func_name = name
        self.func_begin_addr = begin
        self.func_end_addr = end
        self.is_lib = is_lib

class Section(object):
    def __init__(self, name, begin, size):
        self.sec_name = name
        self.sec_begin_addr = begin
        self.sec_size = size

class Loc(object):
    def __init__(self, label, addr, visible):
        self.loc_label = label
        self.loc_addr = addr
        self.loc_visible = visible

class Bblock(object):
    def __init__(self, bf_name, bblock_name, bblock_begin_loc, bblock_end_loc, bblock_head_instr):
        self.bf_name = bf_name
        self.bblock_name = bblock_name
        self.bblock_begin_loc = bblock_begin_loc
        self.bblock_end_loc = bblock_end_loc
        self.bblock_head_instr = bblock_head_instr


if config.arch == config.ARCH_X86:
    ###################################################
    ############## X86 DEFINITIONS ####################
    ###################################################

    CommonReg = RecSet([
        'RAX', 'RBX', 'RCX', 'RDX', 'RDI', 'RSI',
        'EAX', 'EBX', 'ECX', 'EDX', 'EDI', 'ESI',
        'AX', 'BX', 'CX', 'DX',
        'AL', 'BL', 'CL', 'DL',
        'AH', 'BH', 'CH', 'DH'
    ], True)
    SpecialReg = RecSet([
        'R8',  'R9',  'R10',  'R11',  'R12',  'R13',  'R14',  'R15',
        'R8D', 'R9D', 'R10D', 'R11D', 'R12D', 'R13D', 'R14D', 'R15D',
        'R8W', 'R9W', 'R10W', 'R11W', 'R12W', 'R13W', 'R14W', 'R15W',
        'R8B', 'R9B', 'R10B', 'R11B', 'R12B', 'R13B', 'R14B', 'R15B',
        'XMM0', 'XMM1', 'XMM2', 'XMM3', 'XMM4', 'XMM5', 'XMM6', 'XMM7'
        'ST0', 'ST1', 'ST2', 'ST3', 'ST4', 'ST5', 'ST6', 'ST7'
    ], True)
    StackReg = RecSet(['RBP', 'RSP', 'ESP', 'EBP'], True)
    PCReg = RecSet(['EIP', 'RIP'], True)
    OtherReg = RecSet(['EIZ'], True)
    PtrType = RecSet(['QWORD', 'DWORD', 'WORD', 'TBYTE', 'BYTE'], True)
    MathOp = RecSet(['MATHADD'], True)
    Seg = RecSet(['FS', 'GS', 'CS', 'SS', 'DS', 'ES'], True)
    Reg = RecSet([CommonReg, SpecialReg, StackReg, PCReg, OtherReg])

    StackOp = RecSet(['PUSH', 'POP', 'PUSHL', 'POPL', 'PUSHF', 'POPF'], True)
    SystemOp = RecSet(['INT', 'IN', 'OUT'], True)
    ArithmOp = RecSet(['ADC', 'ADD', 'XADD', 'SUB', 'ADDL', 'ADDQ', 'SUBL', 'SUBQ',
                       'MUL', 'IMUL', 'MULB', 'MULSD', 'DIV', 'IDIV', 'DIVL', 'ADCL',
                       'IDIVL', 'DIVSD', 'IVSS', 'MULSS', 'DIVQ', 'IDIVQ', 'PMULUDQ',
                       'INC', 'INCQ', 'INCL', 'INCW', 'DEC', 'NEG', 'SBB', 'FADD',
                       'NEGL', 'FMUL', 'FXCH', 'FUCOMIP', 'FUCOMI', 'FCOMPP',
                       'FCOMPL', 'BSR', 'MULL', 'FMULL', 'UCOMISD', 'UCOMISS', 'SUBSS',
                       'ADDW', 'ADDSD', 'ADDSS', 'FMULP', 'FMULS', 'FADDS', 'FADDP', 'FADDL',
                       'SUBW', 'SUBSD', 'IMULL', 'BSWAP', 'DECL', 'DECB', 'DECD', 'DECW',
                       'FDIV', 'FDIVL', 'ADDB', 'SUBB', 'SBBL', 'FDIVR', 'FABS', 'FSQRT',
                       'FDIVRS', 'CBTW', 'FRNDINT', 'FDIVRL', 'FPREM', 'CVTSI2SD',
                       'CVTSI2SDL', 'CVTSI2SSL', 'CVTSS2SD', 'CVTDQ2PS', 'CVTSI2SS',
                       'CVTTSD2SI', 'CVTTSS2SI', 'CVTSI2SDQ', 'CVTPS2PD',
                       'MAXSD', 'NEGQ', 'UNPCKLPS', 'UNPCKLPD', 'CVTPD2PS', 'CVTSD2SS',
                       'SQRTSS', 'MAXSS', 'MINSD', 'SQRTSD', 'MINSS', 'CVTTPS2DQ',
                       'DECQ', 'SUBPD', 'ADDPD', 'PADDQ', 'IMULQ', 'PADDD', 'PADDB',
                       'PSUBD', 'PSUBW', 'PSUBB', 'MULPD', 'UNPCKHPD', 'ADDPS', 'MULPS',
                       'DIVPD', 'DIVPS', 'CQTO', 'INCB', 'PSUBUSW'
    ], True)
    LogicOp = RecSet(['AND', 'ANDB', 'OR', 'XOR', 'PXOR', 'NOT', 'ANDL', 'NOTL', 'ORW',
                      'XORB', 'XORL', 'SAHF', 'ANDW', 'NOTB', 'NOTW', 'XORPD', 'XORPS',
                      'ANDQ', 'XORQ', 'ANDPS', 'ANDNPS', 'ORPS', 'ANDPD', 'NOTQ', 'ANDNPD',
                      'ORPD', 'PAND', 'POR', 'PANDN'
    ], True)
    RolOp = RecSet(['ROL', 'SHL', 'SHR', 'SHLD |SHRD', 'SHRL', 'ROR', 'RORL',
                    'SAL', 'SAR', 'SHLL', 'ROLL', 'SHRB', 'SHLB', 'SARL', 'ROLW', 'SHLW',
                    'SARW', 'SHRW', 'SHLQ', 'SHRQ', 'PSHUFD', 'SHUFPS', 'SHUFPD',
                    'PSLLW', 'PSLLD', 'PSLLQ', 'PSRAW', 'PSRAD', 'PSLLDQ', 'PSRLDQ',
                    'PSRLD', 'PSHUFLW'
    ], True)
    AssignOp = RecSet(['MOV', 'XCHG', 'LEA', 'MOVSX', 'MOVSD', 'MOVL', 'FLDL', 'MOVZBL', 'MOVZBW',
                       'MOVSW', 'MOVAPD', 'MOVSLQ', 'MOVQ', 'MOVABS', 'MOVSBQ',
                       'MOVW', 'MOVZX', 'MOVAPS', 'FLD', 'FSTP', 'CMOVAE', 'CMOVE', 'CMOVNE', 'MOVSS',
                       'CMOVBE', 'CMOVB', 'CMOVS', 'CMOVA', 'CMOVNS', 'MOVB',
                       'MOVZWL', 'MOVSWL', 'MOVSBL', 'MOVSBW', 'FLDT', 'FSTPT', 'ORL', 'ORB', 'MOVSB',
                       'FNSTCW', 'FLDCW', 'FLDZ', 'REPZ', 'REPE', 'FSTPL', 'REPNZ',
                       'REP', 'FNSTSW', 'CMOVLE', 'CMOVG', 'CMOVL', 'FILDLL',
                       'FLDS', 'FILDL', 'FLD1', 'FDIVP', 'FSTL', 'FISTPL', 'FILD',
                       'FSUB', 'FDIVS', 'FISTPLL', 'FDIVRP', 'CMOVGE', 'FCMOVBE',
                       'FSUBP', 'FISTL', 'FSUBRP', 'FSUBRL', 'CWTL', 'FSUBRS', 'FSTPS',
                       'FSUBS', 'FSUBR', 'FSTS', 'FSUBL', 'FCMOVNBE', 'FCMOVE', 'FCMOVNE',
                       'FCMOVB', 'FISTP', 'FCMOVNB', 'CMOVNP', 'STOS', 'STOSB', 'STOSW', 'STOSD',
                       'FIST', 'FFREE', 'MOVSWQ', 'ORQ', 'MOVDQU', 'MOVDQA',
                       'MOVUPS', 'MOVD', 'MOVHLPS', 'MOVLHPS', 'MOVUPD',
                       'PUNPCKHQDQ', 'PUNPCKLDQ', 'PUNPCKLBW', 'PINSRW', 'PEXTRW',
                       'PUNPCKLQDQ', 'PUNPCKLWD', 'MOVHPD', 'MOVLPD', 'LAHF', 'SAHF'
    ], True)
    CompareOp = RecSet(['CMP', 'CMPQ', 'TEST', 'CMPL', 'CMPB', 'CMPW', 'TESTB', 'TESTL', 'CMPSB',
                        'BT', 'TESTW', 'CMPNLESS', 'CMPLTSS', 'CMPNLTSS', 'TESTQ', 'CMPNLTSD',
                        'PCMPGTD', 'PCMPGTB', 'PCMPEQD', 'CMPLTSD', 'PCMPEQW', 'CMPEQSS'
    ], True)
    SetOp = RecSet(['SETA', 'SETAE', 'SETB', 'SETBE', 'SETC',
                    'SETNBE', 'SETNC', 'SETNG', 'SETNE',
                    'SETE', 'SETNP', 'SETGE', 'SETG', 'SETLE',
                    'SETL', 'SETP', 'SETNS', 'SETS'
    ], True)
    OtherOp = RecSet(['NOP', 'HLT', 'NOPW', 'NOPL', 'UD2'], True)
    JumpOp = RecSet(['JMP', 'JNE', 'JE', 'JB', 'JNAE', 'JNP',
                     'JC', 'JNB', 'JAE', 'JNC', 'JBE', 'JNA',
                     'JA', 'JNBE', 'JL', 'JNGE', 'JGE', 'JNL', 'JLE',
                     'JNG', 'JG', 'JNLE', 'JS', 'JNS', 'JP', 'JMPQ'
    ], True)
    LoopOp = RecSet(['LOOP', 'LOOPE', 'LOOPNE'], True)
    FlagOp = RecSet(['CLD', 'CLTD', 'CLTQ'], True)
    AssistOp = RecSet(['SCAS', 'MOVSL', 'MOVSB', 'CMPSW', 'CMPSB', 'MOVSQ', 'POP', 'STOS'], True)
    ControlOp = RecSet([JumpOp, LoopOp, FlagOp,
                        'CALL', 'CALLQ',
                        'LEAVE', 'LEAVEQ',
                        'RET', 'RETN', 'RETQ',
                        'FXAM', 'FCHS'
    ])
    CommonOp = RecSet([ArithmOp, LogicOp, RolOp, AssignOp, CompareOp, SetOp, OtherOp])
    ErrorOp = RecSet(['(bad)'])
    Op = RecSet([CommonOp, StackOp, ControlOp, SystemOp, ErrorOp])

elif config.arch == config.ARCH_ARMT:
    ###################################################
    ############## ARM DEFINITIONS ####################
    ###################################################

    CommonReg = RecSet(['R0',  'R1',  'R2',  'R3',  'R4',  'R5',  'R6',
                        'R7',  'R8',  'R9', 'R10', 'R11', 'R12'], True)
    SpecialReg = RecSet([ 'D0',  'D1',  'D2',  'D3',  'D4',  'D5',  'D6',  'D7',
                          'D8',  'D9', 'D10', 'D11', 'D12', 'D13', 'D14', 'D15',
                          'S0',  'S1',  'S2',  'S3',  'S4',  'S5',  'S6',  'S7',
                          'S8',  'S9', 'S10', 'S11', 'S12', 'S13', 'S14', 'S15',
                         'S16', 'S17', 'S18', 'S19', 'S20', 'S21', 'S22', 'S23',
                         'S24', 'S25', 'S26', 'S27', 'S28', 'S29', 'S30', 'S31'
    ], True)
    StackReg = RecSet(['R13', 'SP'], True)
    LinkReg = RecSet(['R14', 'LR'], True)
    PCReg = RecSet(['R15', 'PC'], True)
    Reg = RecSet([CommonReg, SpecialReg, StackReg, PCReg, LinkReg])

    StackOp = RecSet(['POP', 'PUSH'], True)
    SystemOp = RecSet(['BKPT', 'CLREX', 'CPS', 'CPSIE', 'CPSID', 'DBG', 'DMB',
                       'DSB', 'ISB', 'PLD', 'PLI', 'RFE', 'SEV', 'SMC', 'SRS',
                       'SVC', 'WFE', 'WFI', 'YIELD'], True)
    ArithmOp = RecSet(['ADC', 'ADCS', 'ADD', 'ADDS', 'ADDW', 'ADR', 'AND', 'ANDS',
                       'CLZ', 'MLA', 'MLS', 'MUL', 'NEG', 'QADD', 'QADD16', 'QADD8',
                       'QASX', 'QDADD', 'QDSUB', 'QSAX', 'QSUB', 'QSUB16', 'QSUB8',
                       'RSB', 'RSBS', 'SADD16', 'SADD8', 'SASX', 'SBC', 'SBCS',
                       'SDIV', 'SHADD16', 'SHADD8', 'SHASX', 'SHSAX', 'SHSUB16',
                       'SHSUB8', 'SMLABB', 'SMLABT', 'SMLATB', 'SMLATT', 'SMLAD',
                       'SMLADX', 'SMLAL', 'SMLALBB', 'SMLALBT', 'SMLALTB', 'SMLALTT',
                       'SMLALD', 'SMLALDX', 'SMLAWB', 'SMLAWT', 'SMLSD', 'SMLSDX',
                       'SMLSLD', 'SMLSLDX', 'SMMLA', 'SMMLAR', 'SMMLS', 'SMMLSR',
                       'SMMUL', 'SMMULR', 'SMUAD', 'SMUADX', 'SMULBB', 'SMULBT',
                       'SMULTB', 'SMULTT', 'SMULL', 'SMULWB', 'SMULWT', 'SMUSD',
                       'SMUSDX', 'SSAT', 'SSAT16', 'SSAX', 'SSUB16', 'SSUB8',
                       'SUB', 'SUBS', 'SUBW', 'SXTAB', 'SXTAB16', 'SXTAH', 'SXTB',
                       'SXTB16', 'SXTH', 'UADD16', 'UADD8', 'UASX', 'UDIV', 'UHADD16',
                       'UHADD8', 'UHASX', 'UHSAX', 'UHSUB16', 'UHSUB8', 'UMAAL',
                       'UMLAL', 'UMULL', 'UQADD16', 'UQADD8', 'UQASX', 'UQSAX',
                       'UQSUB16', 'UQSUB8', 'USAD8', 'USADA8', 'USAT', 'USAT16',
                       'USAX', 'USUB16', 'USUB8', 'UXTAB', 'UXTAB16', 'UXTAH',
                       'UXTB', 'UXTB16', 'UXTH', 'VMUL', 'VNMUL', 'VMLA', 'VMLS',
                       'VNMLS', 'VNMLA', 'VADD', 'VSUB', 'VDIV', 'VABS', 'VNEG',
                       'VSQRT'
    ], True)
    LogicOp = RecSet(['BIC', 'BICS', 'EOR', 'EORS', 'ORN', 'ORNS', 'ORR', 'ORRS',
                      'PKHBT', 'PKHTB', 'RBIT', 'REV', 'REV16', 'REVSH', 'SBFX',
                      'UBFX'], True)
    RolOp = RecSet(['ASR', 'ASRS', 'LSL', 'LSLS', 'LSR', 'LSRS', 'ROR', 'RORS',
                    'RRX', 'RRXS'], True)
    AssignOp = RecSet(['BFC', 'BFI', 'CPY', 'LDMDB', 'LDMEA', 'LDMIA', 'LDMFD',
                       'LDR', 'LDRB', 'LDRBT', 'LDRD', 'LDREX', 'LDREXB', 'LDREXD',
                       'LDREXH', 'LDRH', 'LDRHT', 'LDRSB', 'LDRSBT', 'LDRSH', 'LDRSHT',
                       'LDRT', 'MOV', 'MOVS', 'MOVW', 'MOVT', 'MRS', 'MSR', 'MVN', 'MVNS'
                       'SEL', 'STMDB', 'STMFD', 'STMIA', 'STMEA', 'STR', 'STRB', 'STRBT',
                       'STRD', 'STREX', 'STREXB', 'STREXD', 'STREXH', 'STRH', 'STRHT',
                       'STRT', 'VCVT', 'VCVTT', 'VCVTR', 'VCVTB', 'VMOV', 'VMSR',
                       'VSTR', 'VSTM', 'VSTMDB', 'VPUSH', 'VLDR', 'VLDM', 'VLDMDB'
                       'VPOP'
    ], True)
    CompareOp = RecSet(['CMN', 'CMP', 'IT', 'TEQ', 'TST', 'VCMP', 'VCMPE'], True)
    OtherOp = RecSet(['CDP', 'CDP2', 'LDC', 'LDCL', 'LDC2', 'LDC2L', 'MCR', 'MCR2',
                      'MCRR', 'MCRR2', 'MRC', 'MRC2', 'MRRC', 'MRRC2', 'NOP', 'SETEND',
                      'STC', 'STC2', 'STCL', 'STC2L'], True)
    ControlOp = RecSet(['B', 'BL', 'BLX', 'BX', 'BXJ', 'CBNZ', 'CBZ', 'SUBS', 'TBB', 'TBH'], True)
    CondSuff = RecSet(['EQ', 'NE', 'CS', 'CC', 'MI', 'PL', 'VS', 'VC',
                       'HI', 'LS', 'GE', 'LT', 'GT', 'LE', 'AL'], True)
    OpQualifier = RecSet(['W', 'N', 'F32', 'F64'])
    CommonOp = RecSet([ArithmOp, LogicOp, RolOp, AssignOp, CompareOp])
    Op = RecSet([CommonOp, StackOp, ControlOp, SystemOp, OtherOp])


class Symbol(object): pass
class Exp(object): pass
class SegClass(str): pass
class RegClass(str, Exp):
    def __init__(self, reg):
        if reg not in Reg: raise Exception('Not a register')
        super(RegClass, self).__init__(reg)
class AssistOpClass(str, Exp):
    def __init__(self, op):
        if op not in AssistOp: raise Exception('No assist op')
        super(AssistOpClass, self).__init__(op)
class Ptr(Exp): pass
class Label(str, Exp): pass

class JumpDes(int, Symbol): pass
class CallDes(Func, Symbol):
    def __init__(self, func):
        super(CallDes, self).__init__(func.func_name,
            func.func_begin_addr, func.func_end_addr, func.is_lib)
class StarDes(Exp, Symbol, Container): pass
class Const(long, Exp): pass
class Point(Const): pass
class Normal(Const): pass

class UnOP(RegClass, Ptr): pass
class BinOP_PLUS(tuple, Ptr): pass
class BinOP_PLUS_S(tuple, Ptr): pass
class BinOP_MINUS(tuple, Ptr): pass
class BinOP_MINUS_S(tuple, Ptr): pass
class ThreeOP(tuple, Ptr): pass
class FourOP_PLUS(tuple, Ptr): pass
class FourOP_MINUS(tuple, Ptr): pass
class FourOP_PLUS_S(tuple, Ptr): pass
class FourOP_MINUS_S(tuple, Ptr): pass
class JmpTable_PLUS(tuple, Ptr): pass
class JmpTable_MINUS(tuple, Ptr): pass
class JmpTable_PLUS_S(tuple, Ptr): pass
class JmpTable_MINUS_S(tuple, Ptr): pass
class SegRef(tuple, Ptr): pass

class control(object): pass
class J(control): pass
class F(control): pass

class Instr(tuple): pass
class SingleInstr(Instr):
    def __init__(self, items):
        if len(items) != 3: raise Exception('Invalid single')
        super(SingleInstr, self).__init__(items)
class DoubleInstr(Instr):
    def __init__(self, items):
        if len(items) != 4: raise Exception('Invalid double')
        super(DoubleInstr, self).__init__(items)
class TripleInstr(Instr):
    def __init__(self, items):
        if len(items) != 5: raise Exception('Invalid triple')
        super(TripleInstr, self).__init__(items)
class FourInstr(Instr):
    def __init__(self, items):
        if len(items) != 6: raise Exception('Invalid quad')
        super(FourInstr, self).__init__(items)