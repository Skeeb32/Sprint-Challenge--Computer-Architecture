import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        pass
        self.pc = 0
        self.reg = [0] * 8
        self.ram = [0] * 256
        self.SP = 7
        self.reg[self.SP] = 0xF4
        self.flag = {}
        self.LDI = 0b10000010
        self.PRN = 0b01000111
        self.HLT = 0b00000001
        self.MUL = 0b10100010
        self.PUSH = 0b01000101
        self.POP = 0b01000110
        self.CALL = 0b01010000
        self.RET = 0b00010001
        self.ADD = 0b10100000
        self.CMP = 0b10100111
        self.JMP = 0b01010100
        self.JEQ = 0b01010101
        self.JNE = 0b01010110

    def load(self, filename):
        """Load a program into memory."""
        # print("Loading CPU...")
        address = 0

        # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010, # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111, # PRN R0
        #     0b00000000,
        #     0b00000001, # HLT
        # ]

        # for instruction in program:
        #     self.ram[address] = instruction
        #     address += 1
        try:
            address = 0
            #open the file
            with open(sys.argv[1]) as f:
                #read every line
                for line in f:
                    # Use strip to make sure no errors occur in spacing
                    comment_split = line.strip().split("#")
                    # Cast number string to int
                    value = comment_split[0].strip()
                    # Leave Strings empty
                    if value == "":
                        continue
                    instruction = int(value, 2)
                    # Populate memory array
                    self.ram[address] = instruction
                    address += 1

        except:
            print("cant find file")
            sys.exit(2)


    def ram_read(self, address):
        # Memory Address Register
        # The MAR contains the address that is being read or written to.
        return self.ram[address]

    def ram_write(self, address, value):
        # Memory Data Register
        # The MDR contains the data that was read or the data to write. 
        self.ram[address] = value


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""
        if op == self.ADD:
            self.reg[reg_a] += self.reg[reg_b]
        elif op == self.MUL:
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == self.CMP:
            if self.reg[reg_a] == self.reg[reg_b]:
                self.flag['E'] = 1
            else:
                self.flag['E'] = 0
            if self.reg[reg_a] < self.reg[reg_b]:
                self.flag['L'] = 1
            else:
                self.flag['L'] = 0
            if self.reg[reg_a] > self.reg[reg_b]:
                self.flag['G'] = 1
            else:
                self.flag['G'] = 0
        #elif op == "SUB": etc
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """
        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        halted = False
        while not halted:
            # IR = Instruction Register, contains a copy of the currently executing instruction
            IR = self.ram[self.pc]
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)
            # print(IR, self.pc, operand_a, operand_b)
            if IR == self.LDI:
                self.reg[operand_a] = operand_b
                # print(self.pc, self.reg, self.ram)
                self.pc += 3
            elif IR == self.PRN:
                print(self.reg[operand_a])
                self.pc += 2
            elif IR == self.MUL:
                self.alu(IR, operand_a, operand_b)
                self.pc += 3
            elif IR == self.PUSH:
                operand_a = self.ram_read(self.pc + 1) 
                self.ram_write(self.SP, self.reg[operand_a])
                self.pc += 2
                self.SP -= 1
            elif IR == self.POP:
                operand_a = self.ram_read(self.pc + 1)
                self.reg[operand_a] = self.ram_read(self.SP+1)
                self.SP += 1
                self.pc += 2
            elif IR == self.CALL:
                # print(operand_a)
                operand_a = self.ram_read(self.pc + 1)
                self.SP -= 1
                self.ram_write(self.SP, self.pc + 2)
                self.pc = self.reg[operand_a]
                # print(self.pc)
            elif IR == self.RET:
                self.pc = self.ram_read(self.SP)
                self.SP += 1
            elif IR == self.ADD:
                self.pc +=3
                self.alu(self.ADD, operand_a, operand_b)
            elif IR == self.CMP:
                self.alu(self.CMP, operand_a, operand_b)
                self.pc += 3
            # Jump to the address stored in the given register.
            # Set the PC to the address stored in the given register.
            elif IR == self.JMP:
                self.pc = self.reg[operand_a]
            # If equal flag is set (true), jump to the address stored in the given register.
            elif IR == self.JEQ:
                if self.flag['E'] == 1:
                    self.pc = self.reg[operand_a]
                else:
                    self.pc += 2
            # If E flag is clear (false, 0), jump to the address stored in the given register.
            elif IR == self.JNE:
                if self.flag['E'] == 0:
                    self.pc = self.reg[operand_a]
                else:
                    self.pc += 2
            elif IR == self.HLT:
                sys.exit(0)
            else:
                print(f"Did not work")
                sys.exit(1)