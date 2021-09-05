
L, S, R = 'L', 'S', 'R'
F = '#'
ANY = "ANY"
I = "SAME"

class TM:
    def __init__(self):
        self.tape = ""
        self._headpos = None
        self._state = None
        self._map = None
        self._init_state = None
        self._endstates = None

    def _r(self):
        return self.tape[self._headpos]
    
    def _w(self,symbol):
        self.tape[self._headpos] = symbol
        
    def _mov(self,where):
        if where == L:
            if self._headpos == 0:
                self.tape = [F] + self.tape
            else: 
                self._headpos -= 1
        elif where == S:
            pass
        elif where == R:
            if self._headpos == len(self.tape)-1:
                self.tape = self.tape + [F]
            self._headpos += 1
                
    def _step(self):
        s_in = self._r()
        
        found = False
        for s, (q_new, s_out, mov) in self._map[self._state].items():
            if s == ANY:
                # s_new is a function of s_in
                if s_out == I:
                    # leave that symbol
                    pass
                elif isinstance(s_out, str):
                    self._w(s_out)
                else:
                    self._w(s_out(s_in))
                self._mov(mov)
                self._state = q_new
                found = True
                break
            elif s == s_in:
                # s_out is a const
                self._w(s_out)
                self._mov(mov)
                self._state = q_new
                found = True
                break
        return found
        
    def run(self, inpt, debug=True, timeout=1000):
        if not inpt:
            self.tape = [F]
        else:
            self.tape = list(inpt)
        self._state = self._init_state
        self._headpos = 0
        i = 0
        ok = True
        while ok and not (self._state in self._endstates):
            if debug:
                prefix = "".join(self.tape[:self._headpos])
                s = self.tape[self._headpos]
                postfix =  "".join(self.tape[self._headpos+1:])
                print(f"{prefix}{s}{postfix} : step {i}")
                print(f"{len(prefix)*' '}^ ({self._state})")
            if i > timeout:
                print("Timeout.")
                return -1
            ok = self._step()
            i += 1
        self.tape = "".join(self.tape)
        print(f"Finished in {i} steps. \n  [{self.tape.strip(F)}]")
        

class TMFactory:
    def __init__(self):
        self.map = {}
    
    def parse(file):
        tmf = TMFactory()
        i = 0
        for line in file.readlines():
            line = line.strip()
            if not line or line[0] == ';' or line.isspace(): continue
            tok = line.split()
            
            if i == 0:
                init = tok[0]
                i += 1
            elif i == 1: 
                ends = tok
                i += 1
            
            tmf.add_rule(tok[0], tok[1], tok[2], tok[3], tok[4])
        return tmf.build(init, ends)
    
    def add_state(self,new_state):
        if not (new_state in self.map):
            self.map[new_state] = {}
        return self
            
    def add_rule(self, q_in, s_in, q_out, s_out, mov):
        self.add_state(q_in)
        self.map[q_in][s_in] = (q_out, s_out, mov) # dict preserve insertion order
        return self
    
    def add_any_rule(self,q_in, q_out, s_out_function, mov):
        self.add_state(q_in)
        self.map[q_in][ANY] = (q_out, s_out_function, mov) # dict preserve insertion order
        return self
        
    def build(self,init_state, end_states):
        machine = TM()
        machine._init_state = init_state
        machine._endstates = end_states
        machine._map = self.map
        return machine
