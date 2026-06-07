#ifndef DIJJJ_H
#define DIJJJ_H

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

bool IsAllTrue(bool* arr, int len){
    for (int i = 0; i < len; i++){
        if (arr[i] == false) return false;
    }
    return true;
}

double** Dijkstra(double** M, int len, int from, int to){
    //标记
    bool* flag = (bool*)calloc(len, sizeof(bool));
    if (!flag){
        printf("[ERROR]Oh God...There's something wrong :(");
        return NULL;
    }
    flag[from] = true;
    //状态矩阵, (len-1) * 3
    double** res = (double**)malloc(len * sizeof(double*));
    for (int i = 0; i < len; i++){
        res[i] = (double*)malloc(3 * sizeof(double));
        if (!res[i]){
            printf("[ERROR]Daisy, Daisy, give me your answer do...");
            return NULL;
        }
        res[i][0] = i;
        res[i][1] = M[from][i];
        if (!isinf(M[from][i])){
            res[i][2] = from;
        }else{
            res[i][2] = INFINITY;
        }
    }
    res[from][2] = from;
    //距离起始点的最短节点
    int ptr = 0;
    double length = M[from][ptr];
    for (int i = 1; i < len; i++){
        if (M[from][i] < length){
            length = M[from][i];
            ptr = i;
        }
    }
    flag[ptr] = true;
    //搜索
    while(!IsAllTrue(flag, len)){
        //首先更新数表
        for (int i = 0; i < len; i++){
            if (!flag[i]){
                if (M[ptr][i] + length < res[i][1]){
                    res[i][1] = M[ptr][i] + length;
                    res[i][2] = ptr;
                }
            }
        }
        //之后寻找最小距离点
        double tmp = INFINITY;
        for (int i = 0; i < len; i++){
            if (res[i][1] < tmp && !flag[i]){
                tmp = res[i][1];
                ptr = i;
            }
        }
        length = tmp;
        flag[ptr] = true;
        if (ptr == to || isinf(tmp)) break;
    }
    return res;
}

void ShowM(double** M, int r, int c){
    for (int i = 0; i < r; i++){
        for (int j = 0; j < c; j++){
            printf("%lf ", M[i][j]);
        }
        printf("\n");
    }
}

#endif