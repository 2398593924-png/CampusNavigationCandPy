// Made By Henry, 7 Jun, 2026

#ifndef GAMM_H
#define GAMM_H

#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <math.h>
#include "cJSON.h"

cJSON* GetJsonPtr(char* path){
    //读取JSON文件并获取指针
    FILE* f = fopen(path, "rb");
    if (!f){
        printf("[ERROR]I can't find the file...");
        exit(1);
        return NULL;
    }
    fseek(f, 0, SEEK_END);
    long len = ftell(f);
    fseek(f, 0, SEEK_SET);
    char* data = (char*)malloc(len + 1);
    fread(data, 1, len, f);
    data[len] = '\0';
    fclose(f);

    cJSON* root = cJSON_Parse(data);
    if (!root){
        printf("[ERROR]Oops!There's something wrong...");
        exit(1);
        return NULL;
    }

    free(data);
    return root;
}

double** GetAdjMatrix(cJSON* root){
    //获取邻接矩阵
    cJSON* nodes = cJSON_GetObjectItem(root, "nodes");
    int len = cJSON_GetArraySize(nodes);
    //空矩阵构建
    double** data = (double**)malloc(len * sizeof(double*));
    if (!data){
        printf("[ERROR]Oops!There's something wrong...");
        exit(1);
    }
    for (int i = 0; i < len; i++){
        data[i] = (double*)malloc(len * sizeof(double));
        if (!data[i]){
            printf("[ERROR]Oops!There's something wrong...");
            exit(1);
        }
        for (int j = 0; j < len; j++){
            if (i == j){
                data[i][j] = 0;
                continue;
            }
            data[i][j] = INFINITY;
        }
    }

    //填值
    cJSON* edges = cJSON_GetObjectItem(root, "edges");
    int len_edge = cJSON_GetArraySize(edges);
    for (int i = 0; i < len_edge; i++){
        cJSON* temp = cJSON_GetArrayItem(edges, i);
        cJSON* from = cJSON_GetObjectItem(temp, "from");
        cJSON* to = cJSON_GetObjectItem(temp, "to");
        cJSON* distanace = cJSON_GetObjectItem(temp, "distance");
        int v1 = from->valueint;
        int v2 = to->valueint;
        double dis = distanace->valuedouble;

        data[v1][v2] = dis;
        data[v2][v1] = dis;
    }
    return data;
}

int GetLength(cJSON* root){
    cJSON* temp = cJSON_GetObjectItem(root, "nodes");
    int len = cJSON_GetArraySize(temp);
    
    return len;
}

#endif