# -*- coding: utf-8 -*-
"""
Created on Thu Oct 20 21:33:29 2022

@author: Manideep
"""

from numpy import asarray



ENERGY_LEVEL = [100, 113, 110, 85, 105, 102, 86, 63,
                81, 101, 94, 106, 101, 79, 94, 90, 97]


def find_significant_energy_increase_brute(A):
    mostSignificant=0
    start,end=0,0
    for i in range(len(A)-1):
        currentMax=0
        reachedMaxAt=i
        for j in range(i+1,len(A)):
            if A[j]-A[i]>currentMax:
                currentMax=A[j]-A[i]
                reachedMaxAt=j
                if currentMax>mostSignificant:
                    mostSignificant=currentMax
                    start=i
                    end=reachedMaxAt
                    return(start,end)

def find_significant_energy_increase_recursive(A):
    _, start, end = helper(A, 0, len(A)-1)
    return (start, end)
def helper(A, start, end):
    
    if end - start == 0:
        return 0, start, start
        if end - start == 1:
            return A[end] - A[start], start, end
    mid = (start + end)//2
    left_max, min_temp1, max_temp1 = helper(A, start, mid-1)
    right_max, min_temp2, max_temp2 = helper(A, mid, end)
    minTempIdx = start
    minTempVal = A[start]
    for k in range(start+1, mid):

      if A[k] < minTempVal:
        minTempVal = A[k]
        minTempIdx = k
        maxTempIdx = mid
        maxTempVal = A[mid]
    for k in range(mid+1, end+1):
      if A[k] > maxTempVal:
        maxTempVal = A[k]
        maxTempIdx = k
        maxCrossBorder = maxTempVal - minTempVal
      if right_max > left_max:
       if maxCrossBorder > right_max:
        return maxCrossBorder, minTempIdx, maxTempIdx
       else:
        return right_max, min_temp2, max_temp2
      else:
       if maxCrossBorder > left_max:
        return maxCrossBorder, minTempIdx, maxTempIdx
    else:
        return left_max, min_temp1, max_temp1

def find_significant_energy_increase_iterative(A):

    minSoFar = float("inf")
    maxProfit = float("-inf")
    start = 0
    end = 0
    for i, val in enumerate(A):
     if val < minSoFar:
        minSoFar = val
        start = i
     elif val - minSoFar > maxProfit:
        maxProfit = val - minSoFar
        end = i
    return (start, end)

def square_matrix_multiply_strassens(A, B):

    A = asarray(A)
    B = asarray(B)
    assert A.shape == B.shape
    assert A.shape == A.T.shape
    assert (len(A) & (len(A) - 1)) == 0, "A is not a power of 2"
    result = strassen(A, B)
    return result
def strassen(A, B):
    if len(A) == 1:
        return [[A[0][0] * B[0][0]]]
    a, b, c, d = split_matrix(A)
    e, f, g, h = split_matrix(B)
    p1 = strassen(a, sub_matrix(f, h))
    p2 = strassen(add_matrix(a, b), h)
    p3 = strassen(add_matrix(c, d), e)
    p4 = strassen(d, sub_matrix(g, e))
    p5 = strassen(add_matrix(a, d), add_matrix(e, h))
    p6 = strassen(sub_matrix(b, d), add_matrix(g, h))
    p7 = strassen(sub_matrix(a, c), add_matrix(e, f))
    top_left = add_matrix(sub_matrix(add_matrix(p5, p4), p2), p6)
    top_right = add_matrix(p1, p2)
    bot_left = add_matrix(p3, p4)
    bot_right = sub_matrix(sub_matrix(add_matrix(p1, p5), p3), p7)
    res = []
    for i in range(len(top_right)):
     res.append(top_left[i] + top_right[i])
    for i in range(len(bot_right)):
     res.append(bot_left[i] + bot_right[i])
    return res
def add_matrix(matrix_a, matrix_b):
    return [[matrix_a[row][col] + matrix_b[row][col]
    for col in range(len(matrix_a[row]))]
    for row in range(len(matrix_a))]
def sub_matrix(matrix_a, matrix_b):
    return [[matrix_a[row][col] - matrix_b[row][col]
for col in range(len(matrix_a[row]))]
for row in range(len(matrix_a))]
def split_matrix(matrix):
    matrix_length = len(matrix)
    mid = matrix_length // 2
    top_left = [[matrix[i][j] for j in range(mid)] for i in range(mid)]
    bottom_left = [[matrix[i][j] for j in range(mid)] for i in range(mid, matrix_length)]
    top_right = [[matrix[i][j] for j in range(mid, matrix_length)] for i in range(mid)]
    bottom_right = [[matrix[i][j] for j in range(mid, matrix_length)] for i in range(mid, matrix_length)]
    return top_left, top_right, bottom_left, bottom_right




def power_of_matrix_navie(A, k):
    if not validation(A, k):
        return "Input valid Parameters"
        result = A
    if k == 1:
     return A
    while k > 1:
     result = square_matrix_multiply_strassens(A, result)
     k -= 1
    return asarray(result, dtype=int)
def validation(A, k):
    if len(A) != len(A[0]):
        return False
    if k > 10 or k <= 0:
     return False
    if len(A) > 32:
     return False
    return True


def power_of_matrix_divide_and_conquer(A, k):
 if not validation(A, k):
        return "Input valid Parameters"
        _dict = {}
        result = calculate_power(A, k, _dict)
        return result
def calculate_power(A, k, _dict):
    if k in _dict:
        return _dict[k]
    if k == 1:
        return A
    else:
        mat_a = calculate_power(A, (k//2), _dict)
        mat_b = calculate_power(A, (k+1)//2, _dict)
        _dict[k] = square_matrix_multiply_strassens(mat_a, mat_b)
    return _dict[k]




