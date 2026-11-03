from optimization import * 
from visualization import visualize_path



# Nelder–Mead method

def nelder_mead_method_by_points(f, points: list, iterations: int):
    for i in range(iterations):
        points = reflection(f, points)
        print(points)

    b, b_val, w, w_val = best_worst_points(f, points)
    
    return b, b_val


def nelder_mead_method(f, points: list, iterations: int):
    print(1234567890)
    path = [best_worst_points(f, points)[0]]
    simplices = []

    for i in range(iterations):
        points = reflection(f, points)
        path.append(best_worst_points(f, points)[0])
        simplices.append(points)

    b, b_val, w, w_val = best_worst_points(f, points)
    visualize_path(f, path, print_items=simplices)
    return b, b_val



# Gradient descent

def gradient_descent_method_by_points(f, point: list, iterations: int, alpha: int):
    grad_func = gradient(f)

    for i in range(iterations):
        print(point)
        grad = grad_func(*point)
        point = [p - alpha*g for p, g in zip(point, grad)]

    return point, f(*point)


def gradient_descent_method(f, point: list, iterations: int, alpha: float):
    grad_func = gradient(f)
    path = [point]

    for i in range(iterations):
        grad = grad_func(*point)
        point = [p - alpha * g for p, g in zip(point, grad)]
        path.append(point)

    visualize_path(f, path)
    return point, f(*point)



# Newton's method

def newtons_method_by_points(f, point: list, iterations: int):
    grad_func = gradient(f)
    H = hessian(f)

    for i in range(iterations):
        print(point)
        grad = grad_func(*point)
        hess_inv = inverse_matrix(H(*point))

        first_addend = matrix_transposition([point])
        second_addend = matrix_multiply(hess_inv, matrix_transposition([grad]))
        
        result = [
            [a[0] - b[0]]
            for a, b in zip(first_addend, second_addend)
        ]

        point = matrix_transposition(result)[0]

    return point, f(*point)


def newtons_method(f, point: list, iterations: int):
    grad_func = gradient(f)
    H = hessian(f)
    path = [point]

    for i in range(iterations):
        grad = grad_func(*point)
        hess_inv = inverse_matrix(H(*point))

        first_addend = matrix_transposition([point])
        second_addend = matrix_multiply(hess_inv, matrix_transposition([grad]))
        result = [
            [a[0] - b[0]]
            for a, b in zip(first_addend, second_addend)
        ]

        point = matrix_transposition(result)[0]
        path.append(point)

    visualize_path(f, path)
    return point, f(*point)