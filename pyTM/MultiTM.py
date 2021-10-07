
L, S, R = 'L', 'S', 'R'
F = '#'
ANY = "ANY"
I = "SAME"

class MultiTM:
    def __init__(self, k):
        self.tapes = [[""]]*k
        self.k = k
        self._headpos = None
        self._state = None
        self._map = None
        self._init_state = None
        self._endstates = None

    def _r(self):
        return [self.tapes[i][self._headpos[i]] for i in range(self.k)]
    
    def _w(self,symbols):
        # print("write:",symbols)
        for i in range(1,self.k):
            self.tapes[i][self._headpos[i]] = symbols[i-1]
        
    def _mov(self,where):
        for i in range(0,self.k):
            if where[i] == L:
                if self._headpos[i] == 0:
                    self.tapes[i] = [F] + self.tapes[i]
                else: 
                    self._headpos[i] -= 1
            elif where[i] == S:
                pass
            elif where[i] == R:
                if self._headpos[i] == len(self.tapes[i])-1:
                    self.tapes[i] = self.tapes[i] + [F]
                self._headpos[i] += 1
                
    def _step(self):
        s_in = self._r()
        
        found = False
        if self._state not in self._map:
            print(f"no state: {self._state}")
            return False
        for s, (q_new, s_out, mov) in self._map[self._state].items():
            found = True
            for i in range(0,self.k):
                if s[i] != ANY and s[i] != s_in[i]:
                    found = False
                    break
            if found:
                w = []
                for i in range(1,self.k):
                    if s_out[i-1] == I:
                        # leave that symbol
                        w.append(s[i])
                    elif isinstance(s_out[i-1], str):
                        w.append(s_out[i-1])
                    else:
                        w.append(s_out[i-1](s_in))
                self._w(w)
                self._mov(mov)
                self._state = q_new
                break
        return found
        
    def run(self, inpt, debug=True, timeout=1000):
        self.tapes = [[F]]*self.k
        if not not inpt:
            self.tapes[0] = list(inpt)
        self._state = self._init_state
        self._headpos = [0]*self.k
        step = 0
        ok = True
        while ok and not (self._state in self._endstates):
            if debug:
                print(f"========[state {self._state}]=========")
                for i in range(self.k):
                    prefix = "".join(self.tapes[i][:self._headpos[i]])
                    s = self.tapes[i][self._headpos[i]]
                    postfix =  "".join(self.tapes[i][self._headpos[i]+1:])
                    print(f"{prefix}{s}{postfix}")
                    print(f"{len(prefix)*' '}^")
                print("====================")
            if step > timeout:
                print("Timeout.")
                return self.tapes[-1].strip(F), -1
            ok = self._step()
            step += 1
        ans = "".join(self.tapes[-1]).strip(F)
        if debug:
            print(f"Finished in {step} steps. \n  [{ans}]")
        return ans, step
        

class MultiTMFactory:
    def __init__(self,k):
        self.map = {}
        self.k = k
    
    # def parse(file):
    #     tmf = MultiTMFactory()
    #     i = 0
    #     for line in file.readlines():
    #         line = line.strip()
    #         if not line or line[0] == ';' or line.isspace(): continue
    #         tok = line.split()
            
    #         if i == 0:
    #             init = tok[0]
    #             i += 1
    #         elif i == 1: 
    #             ends = tok
    #             i += 1
            
    #         tmf.add_rule(tok[0], tok[1], tok[2], tok[3], tok[4])
    #     return tmf.build(init, ends)
    
    def add_state(self,new_state):
        if not (new_state in self.map):
            self.map[new_state] = {}
        return self
            
    def add_rule(self, q_in, s_in, q_out, s_out, mov):
        self.add_state(q_in)
        self.map[q_in][s_in] = (q_out, s_out, mov) # dict preserve insertion order
        return self
        
    def build(self,init_state, end_states):
        machine = MultiTM(self.k)
        machine._init_state = init_state
        machine._endstates = end_states
        machine._map = self.map
        return machine
