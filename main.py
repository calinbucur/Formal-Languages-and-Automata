# Tema3
# Bucur Calin-Andrei
# 332CB

import sys

class NFA():
	# Constructor
	def __init__(self, alphabet, states, finals, delta):
		self.states = states
		self.finals = finals
		self.delta = delta
		self.alphabet = alphabet

	# Converts the NFA/DFA into a string for printing
	def __str__(self):
		nfa_str = " "
		delta_str = ""
		for d in self.delta:
			delta_str = delta_str + (str(d[0]) + " " + d[1] + " " + nfa_str.join(map(str, self.delta[d])) + "\n")
		return str(self.states) + "\n" + nfa_str.join(map(str, self.finals)) + "\n" + delta_str

	# Generates the epsilon list
	# This list contains for each state the set of states reachable via epsilon transitions
	def compute_eps(self):
		epsilon = []
		for s in range(self.states):
			cl = {s}
			q = [s]
			# BFS on the epsilon transitions
			while q:
				crt = q.pop(0)
				if (crt, "eps") in self.delta:
					for x in self.delta[(crt, "eps")]:
						if x not in cl:
							q.append(x)
					cl = cl.union(set(self.delta[(crt, "eps")]))
			epsilon.append(cl)
		self.epsilon = epsilon

# Reads the regex from the input file
def read():
	input_file = open(sys.argv[1], "r")
	return input_file.readline()

# Prints the DFA to the dfa file
def print_dfa(dfa):
	output_file = open(sys.argv[3], "w")
	output_file.write(str(dfa))
	output_file.close()

#Prints the NFA to the nfa file
def print_nfa(nfa):
	output_file = open(sys.argv[2], "w")
	output_file.write(str(nfa))
	output_file.close()

# Converts the NFA to a DFA
# Returns the DFA as a NFA object
def NFA_to_DFA(nfa):
	# This list stores the states as sets
	# In the delta function the states are the indexes
	states = []
	# Starts from the initial state
	states.append(nfa.epsilon[0])
	q = [nfa.epsilon[0]]
	delta = {}
	# Once again something resembling a BFS
	# Searching for new states until no new ones are found
	while q:
		crt = q.pop(0)
		# For every symbol determine the set of next states
		for e in nfa.alphabet:
			# The next set of states
			nxt = set()
			for s in crt:
				if (s,e) in nfa.delta:
					aux = nfa.delta[(s,e)]
					for a in aux:
						# Keeping track of epsilon
						nxt = nxt.union(nfa.epsilon[a])
			if nxt:
				if nxt not in states:
					states.append(nxt)
					q.append(nxt)
				# Generating the transitions
				delta[(states.index(crt),e)] = [states.index(nxt)]
	# Finding the final states
	# All states containing the original finals are final themselves
	finals = set()
	for f in nfa.finals:
		for i in range(len(states)):
			if f in states[i]:
				finals.add(i)
	# Finally adding a sinkstate for the yet undefined transitions
	for e in nfa.alphabet:
		for i in range(len(states)):
			if (i, e) not in delta:
				delta[(i,e)] = [len(states)]
		delta[(len(states), e)] = [len(states)]
	return NFA(nfa.alphabet,len(states) + 1, list(finals), delta)

# Replaces the concatenation with dots
# This way I can convert it to postfix form
def dots(rx):
	op = "(|)*"
	res = ""
	res+=rx[0]
	for c in rx[1:]:
		if c not in op[1:] and res[len(res) - 1] not in op[:2]:
			res+="."
		res+=c
	return res

# Rewrites the regex in postfixed form
def postfix(rx):
	s = [] # Stack used for operators
	q = "" # Queue where the result postfix regex is stored
	op = "()|.*" # Possible operators
	# Their order COUNTS as it represents precedence
	# Go through the regex
	for c in rx:
		# If it's a character add it to the final expression
		if c not in op:
			q += c
		else:
			# If it's "(" push it to the stack
			if c == "(":
				s.append(c)
			else:
				# If it's a ")" pop and add to the queue
				# until we find a ")"
				if c == ")":
					while s[len(s) - 1] != "(":
						q += s.pop()
					s.pop()
				# Pop and add to the queue until we find an operator
				# with lower precedence then push the current operator
				else:
					while len(s) > 0 and op.index(s[len(s) - 1]) >= op.index(c):
						q += s.pop()
					s.append(c)
	# If there are operators left in the stack
	# pop them and add them to the queue
	while len(s) != 0:
		q += s.pop()
	return q

# Get the alphabet of the language
def getAlphabet(rx):
	alpha = []
	op = "|*.$"
	for c in rx:
		if c not in op and c not in alpha:
			alpha.append(c)
	return alpha

# NFA concatenation
def concat(b, a):
	# Sets the alphabet
	alpha = a.alphabet
	# Sets the new number of states
	states = a.states + b.states
	# The new final state is the final state of B
	# but offset with A's number of states (like all of B's states)
	finals = list(map(lambda x: x + a.states, b.finals))
	# Delta has all of A's transitions
	delta = a.delta
	# Add an epsilon transition from A's final state to B's initial
	if (a.finals[0], "eps") not in delta:
		delta[(a.finals[0], "eps")] = [a.states]
	else:
		delta[(a.finals[0], "eps")] += [a.states]
	# Also add B's transitions but offset with A's number of states
	for t in b.delta:
		delta[(t[0] + a.states, t[1])] = list(map(lambda x: x + a.states, b.delta[t]))
	# Build and return the NFA
	return NFA(alpha, states, finals, delta)

# NFA union
def union(a, b):
	# Sets the alphabet
	alpha = a.alphabet
	# Set the new number of states
	# (one new final state and one new initial state)
	states = a.states + b.states + 2
	# The final state is a new one
	finals = list(map(lambda x: x + a.states + 2, b.finals))
	delta = {}
	# Add A's transitions to delta offset with 1 (the initial state)
	for t in a.delta:
		delta[(t[0] + 1, t[1])] = list(map(lambda x: x + 1, a.delta[t]))
	# Add a transition from the new initial state to A's initial state
	delta[(0, "eps")] = [1, a.states + 1]
	# And from A's final state to the new final state
	if (a.finals[0] + 1, "eps") not in delta:
		delta[(a.finals[0] + 1, "eps")] = [states - 1]
	else:
		delta[(a.finals[0] + 1, "eps")] += [states - 1]
	# Do the same for B but it's also offset by A's number of states
	for t in b.delta:
		delta[(t[0] + a.states + 1, t[1])] = list(map(lambda x: x + a.states + 1, b.delta[t]))	
	if (b.finals[0] + a.states + 1, "eps") not in delta:
		delta[(b.finals[0] + a.states + 1, "eps")] = [states - 1]
	else:
		delta[(b.finals[0] + a.states + 1, "eps")] += [states - 1]

	# Build and return the NFA
	return NFA(alpha, states, finals, delta)

# NFA Kleene star
def kleene(a):
	delta = {}
	# Add A's transitions to delta but offset with 1
	for t in a.delta:
		delta[(t[0] + 1, t[1])] = list(map(lambda x: x + 1, a.delta[t]))
	# Add transitions from the new initial state to A's initial state
	# and to the new final state
	delta[(0, "eps")] = [1, a.states + 1]
	# Add transition from the new final state to the new initial state
	delta[(a.states + 1, "eps")] = [0]
	# Add transition from A's final state to the new final state
	if (a.finals[0] + 1, "eps") not in delta:
		delta[(a.finals[0] + 1, "eps")] = [a.states + 1]
	else:
		delta[(a.finals[0] + 1, "eps")] += [a.states + 1]
	# Build and return the NFA
	return NFA(a.alphabet, a.states + 2, [a.finals[0] + 2], delta)

# Converts the regex to a NFA
def regexToNFA(rx):
	s = [] # Stack for "partial" NFAs
	op = ".|*" # Possible operators
	alpha = getAlphabet(rx)
	# Go through the regex
	for c in rx:
		# If it's a character or epsilon
		if c not in op:
			# Build the simple NFA and push it into the stack
			if c == "$":
				s.append(NFA(alpha, 1, [0], {}))
			else:
				s.append(NFA(alpha, 2, [1], {(0, c):[1]}))
		# If it's concatenation
		if c == ".":
			# Pop 2 NFAs from the stack and apply concatenation
			# Push the resulting NFA into the stack
			s.append(concat(s.pop(), s.pop()))
		# If it's union
		if c == "|":
			# Pop 2 NFAs from the stack and apply union
			# Push the resulting NFA into the stack
			s.append(union(s.pop(), s.pop()))
		# If it's kleene star
		if c == "*":
			# Pop a NFA from the stack and apply kleene star
			# Push the resulting NFA into the stack
			s.append(kleene(s.pop()))

	# The only NFA left in the stack will be the final one
	# Pop and return it
	return s.pop()


rx = read().replace("eps", "$") # Read regex and encode epsilon
rx = dots(rx) # Add dots for concatenation
rx = postfix(rx) # Convert to postfix form
nfa = regexToNFA(rx) # Convert to nfa
nfa.compute_eps() # Get the epsilon closure
print_nfa(nfa) # Print the NFA
print_dfa(NFA_to_DFA(nfa)) # Convert the NFA to DFA and print it