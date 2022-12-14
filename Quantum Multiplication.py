'''Importing necessary files from Qiskit'''

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile, Aer, execute, IBMQ
from math import pi
#----------------------------------------------------------------------------------------------------------------------

'''Main function that will carry out all the necessary calculations. This contains some internal functions as well.''' 
#Although the same variables could have been used throughout this function but for better readability, different variables
#have been used wherever necessary
def multiplication(multiplicand_string, multiplier_string ):
    #This message is placed to let the user know that the program is running (useful when calculations may take long time)
    print("Processing....")
    
    #Conversion of basis of numbers from decimal to binary
    multiplicand_string = bin(int(multiplicand_string))
    multiplier_string = bin(int(multiplier_string))

    #The in-built binary conversion function used above has string "0b" in the beginning to indicate 
    #binary basis. This would however interfere with program's working so these characters are deleted
    multiplicand_string = multiplicand_string.replace('0b','')
    multiplier_string = multiplier_string.replace('0b', '')

    #finding lengths of the two numbers to determine limits of loops
    n1 = len(multiplicand_string)
    n2 = len(multiplier_string)
    n = n1 + n2

    #To reduce the number of iterations and optimize the circuit better, longer string (higher number) is taken as multiplicand.
    #The shorter string(smaller number) is assigned as multiplier to determine the number of iterations
    if (n2 > n1):
        multiplier_string, multiplicand_string = multiplicand_string, multiplier_string
        n2, n1 = n1, n2
    
    #----------------------------------------------------------------------------------------------------------------------    
    '''This function operates on a quantum register and converts it from Computational to Fourier Basis for further processing.'''

    def QFT(circuit, quantum_register, n):
        qc.h(quantum_register[n])
        for j in range (0,n):
            circuit.cp(pi/float(2**(j+1)), quantum_register[n - (j+1)], quantum_register[n])
    #----------------------------------------------------------------------------------------------------------------------

    '''This function performs Inverse Fourier Transform on the quantum register and converts it back to computational basis'''

    def Inverse_QFT(circuit,quantum_register, n):
        for j in range(0, n):
            circuit.cp(-1 * pi / float(2**(n - j)), quantum_register[j], quantum_register[n])
        circuit.h(quantum_register[n])
    #---------------------------------------------------------------------------------------------------------------------

    '''This function applies Fourier Transform on the combined state of register_x and register_y. Here register_y acts as 
    controller for phase rotations on register_x'''

    def QFT_adder(circuit, register_x, register_y, n, factor):
        l = len(register_y)
        for j in range (0, n+1):
            #This condition is for enabling program to work with registers of different sizes
            if (n - j ) > l - 1:
                pass
            else:
                circuit.cp(factor*pi /  float(2**(j)),register_y[n - j], register_x[n])
    #---------------------------------------------------------------------------------------------------------------------

    '''This function is to call all the above functions and add the two registers (x and y) bit by bit. Here the variable
    'factor' is used to tell the program whether to add or to subrtract. It performs addition for factor = 1 and subtraction 
    for factor = -1'''

    def summation(register_x, register_y, qc, factor):
        n = len(register_x) - 1
    
        for i in range(0, n+1):
            QFT(qc, register_x, n-i)
    
        for i in range(0, n+1):
            QFT_adder(qc, register_x, register_y, n-i, factor)
    
        for i in range(0, n+1):
            Inverse_QFT(qc, register_x, i)
    #--------------------------------------------------------------------------------------------------------------------
    
    
    #This quantum register will store the values of repeated summation of multiplicand until multiplier is zero
    adder = QuantumRegister(n)
    #This quantum register will decrease the value of multiplier by 1 after every iteration
    decrementer = QuantumRegister(1)

    #Quantum registers to store multiplicand and multiplier
    multiplicand = QuantumRegister(n1)
    multiplier = QuantumRegister(n2)

    c_reg = ClassicalRegister(n)

    qc = QuantumCircuit(adder, multiplier, multiplicand, decrementer, c_reg, name = "circuit")

    #Setting the decrementer to state |1>
    qc.x(decrementer)

    #Storing numbers in the multiplicand and multiplier registers according to user input
    for i in range(n1):
        if (multiplicand_string[i] == '1'):
            #The index here is written so as take care of the different ordering in classical
            #and quantum programming (particularly Qiskit)
            qc.x(multiplicand[n1-i-1])
    
    for i in range(n2):
        if (multiplier_string[i] == '1'):
            qc.x(multiplier[n2-i-1])

    #This is initially set to 1. Once the multiplier string goes to zero, this will switch to zero as well and stop the loop
    #The need for this arises because of absence of a controlled gate that tells the program to stop doing iterations
    multiplier_stopper = '1'

    #This loop adds the multiplicand multiple times and decreases the multiplier with each iteration till the multiplier is zero
    #Results of the calculations are stored in the "counts" variable duting the processing
    while(int(multiplier_stopper) != 0):
        #This function call is to add multiplicand to adder repeatedly using QFT and the sum is stored in adder
        summation(adder, multiplicand, qc, 1)
    
        #This function call is to decrease the value of multiplier by 1
        summation(multiplier, decrementer, qc, -1)
    
        #This patch of code gets result of the operations done above (via measurement) and makes the multiplier string zero when
        #its value goes to 0 after consecutive decrement by 1. At this point the loop terminates and addition is stopped. 
        for i in range(len(multiplier)):
            qc.measure(multiplier[i], c_reg[i])
        job = execute(qc, backend = Aer.get_backend('qasm_simulator'), shots = 2)
        counts = job.result().get_counts(qc)
        multiplier_stopper = list(counts.keys())[0]

    #Making final measurement and getting the results
    qc.measure(adder, c_reg)

    job = execute(qc, backend = Aer.get_backend('qasm_simulator'), shots = 2)
    counts = job.result().get_counts(qc)

    print("")
    #The counts variable is in dictionary form which doesn't suit purpose of this program so usual output form is used
    product = int(next(iter(counts)),2)   
        
    return(product)
