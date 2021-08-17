def daxpy(myCPU, d, p, WORD_SIZE):
    a = list(range(0, d*WORD_SIZE, WORD_SIZE))
    b = list(range(d*WORD_SIZE, 2*d*WORD_SIZE, WORD_SIZE))
    c = list(range(2*d*WORD_SIZE, 3*d*WORD_SIZE, WORD_SIZE))

    for i in range(d):
        myCPU.storeDouble(a[i], i)
        myCPU.storeDouble(b[i], 2*i)
        myCPU.storeDouble(c[i], 0)

    register0 = 3

    for i in range(d):
        register1 = myCPU.loadDouble(a[i])
        register2 = myCPU.multDouble(register0, register1)
        register3 = myCPU.loadDouble(b[i])
        register4 = myCPU.addDouble(register2, register3)
        myCPU.storeDouble(c[i], register4)
    
    result = []
    v1 = []
    v2 = []
    for i in range(d):
        v1.append(myCPU.loadDouble(a[i]))
        v2.append(myCPU.loadDouble(b[i]))
        result.append(myCPU.loadDouble(c[i]))
    if p:
        print(f'vector 1: {v1}')
        print(f'vector 2: {v2}')
        print(f'result vector: {result}')
    myCPU.print()