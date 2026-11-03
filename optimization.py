def derivative(f, h=0.0001):
    def df(x):
        return (f(x + h) - f(x - h)) / (2 * h)

    return df


def best_worst_points(f, points: list):
    if len(points) < 2:
        raise ValueError("Not enough points!")

    best_point, best_val = None, float('inf')
    worst_point, worst_val = None, float('-inf')

    for point in points:
        val = f(*point)
        
        if val < best_val:
            best_point, best_val = point, val
        if val > worst_val:
            worst_point, worst_val = point, val

    return best_point, best_val, worst_point, worst_val


def reflection(f, points: list):
    best_point, best_val, worst_point, worst_val = best_worst_points(f, points)

    other_points = list(points)
    other_points.remove(worst_point)
    average = [sum(group)/len(other_points) for group in zip(*other_points)] # M

    updated_worst = [2 * m_el - a_el for m_el, a_el in zip(average, worst_point)] # A'
    if f(*updated_worst) < best_val: # f(A') < f(A) 
        expanded_updated_worst = [3 * m_el - 2 * a_el for m_el, a_el in zip(average, worst_point)]
        if f(*expanded_updated_worst) < f(*updated_worst):
            other_points.append(expanded_updated_worst) # A''
        else:
            other_points.append(updated_worst) # A'
    elif f(*updated_worst) > worst_val: # f(A') > f(A)
        other_points.append([(m_el + a_el) / 2 for m_el, a_el in zip(average, worst_point)]) # (A + M)/2
    else:
        other_points.append(updated_worst)

    return other_points


def gradient(f, h=0.0001):
    
    def grad(*args):
        result = []

        for i in range(len(args)):
            x = list(args)

            x[i] += h
            forward = f(*x)

            x[i] -= 2 * h
            backward = f(*x)

            result.append((forward - backward) / (2 * h))

        return result

    return grad


def hessian(f, h=0.0001):
    
    grad = gradient(f, h)

    def H(*args):
        n = len(args)
        result = []

        for i in range(n):
            row = []
            x = list(args)

            x[i] += h
            forward = grad(*x)

            x[i] -= 2 * h
            backward = grad(*x)

            for j in range(n):
                row.append((forward[j] - backward[j]) / (2 * h))

            result.append(row)

        return result

    return H


def inverse_matrix(matrix):
    n = len(matrix)

    A = [row[:] + [1 if i == j else 0 for j in range(n)]
         for i, row in enumerate(matrix)]

    for i in range(n):

        pivot = max(range(i, n), key=lambda r: abs(A[r][i]))

        if abs(A[pivot][i]) < 1e-12: # ~0
            raise ValueError("Matrix is singular!")

        A[i], A[pivot] = A[pivot], A[i]

        divisor = A[i][i]
        A[i] = [x / divisor for x in A[i]]

        for j in range(n):
            if i != j:
                factor = A[j][i]
                A[j] = [
                    A[j][k] - factor * A[i][k]
                    for k in range(2 * n)
                ]

    return [row[n:] for row in A]


def matrix_multiply(H1, H2):

    rows_1 = len(H1)
    cols_1 = len(H1[0])
    rows_2 = len(H2)
    cols_2 = len(H2[0])

    if cols_1 != rows_2:
        raise ValueError("Matrices cannot be multiplied")
    
    result = [[0 for _ in range(cols_2)] for _ in range(rows_1)]

    for i in range(rows_1):
        for j in range(cols_2):
            for k in range(cols_1):
                result[i][j] += H1[i][k] * H2[k][j]

    return result


def matrix_transposition(H):

    rows = len(H)
    cols = len(H[0])

    H_t = [[0 for _ in range(rows)] for _ in range(cols)]

    for i in range(cols):
        for j in range(rows):
            H_t[i][j] += H[j][i]

    return H_t