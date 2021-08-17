def mxm(myCPU, d, p, WORD_SIZE):
    a = [[(j*WORD_SIZE)+d*i*WORD_SIZE for j in range(d)] for i in range(d)]
    b = [[(j*WORD_SIZE)+d*i*WORD_SIZE for j in range(d)] for i in range(d, 2*d)]
    c = [[(j*WORD_SIZE)+d*i*WORD_SIZE for j in range(d)] for i in range(2*d, 3*d)]


    for i in range(d):
        for j in range(d):
            myCPU.storeDouble(a[i][j], j+d*i)
            myCPU.storeDouble(b[i][j], 2*(j+d*i))
            myCPU.storeDouble(c[i][j], 0)


    for i in range(d):
        for j in range(d):
            register0 = 0
            for k in range(d):
                register1 = myCPU.loadDouble(a[i][k])
                register2 = myCPU.loadDouble(b[k][j])
                register3 = myCPU.multDouble(register1, register2)
                register0 = myCPU.addDouble(register3, register0)
            myCPU.storeDouble(c[i][j], register0)
    
    result = []
    m1 = []
    m2 = []
    for i in range(d):
        result_row = []
        row1 = []
        row2 = []
        for j in range(d):
            row1.append(myCPU.loadDouble(a[i][j]))
            row2.append(myCPU.loadDouble(b[i][j]))
            result_row.append(myCPU.loadDouble(c[i][j]))
        m1.append(row1)
        m2.append(row2)
        result.append(result_row)
    if p:
        print(f'matrix 1: {m1}')
        print(f'matrix 2: {m2}')
        print(f'result matrix: {result}')

    myCPU.print()
    
