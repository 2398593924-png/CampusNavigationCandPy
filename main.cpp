#include "GetAdjMatrix.h"
#include "Dijkstra.h"

char transform(int num){
    return (char)(num + 65);
}

int main(){
    char sss[] = "graph_data.json";
    cJSON* root = GetJsonPtr(sss);
    double** data = GetAdjMatrix(root);
    int start, end;
    int len = GetLength(root);
    printf("TABLE\n");
    for (int i = 0; i < len; i++){
        printf("%d <-> %c\n", i, transform(i));
    }
    printf("================\n");
    printf("Input the starting point:");
    scanf("%d", &start);
    printf("Input the destination:");
    scanf("%d", &end);


    double** res = Dijkstra(data, len, start, end);
    if (isinf(res[end][1]) || isinf(res[end][2])){
        printf("Not connected!");
        return -1;
    }

    double distance = res[end][1];

    int path[len];
    int path_len = 0;
    int current = end;
    while(current != start){
        path[path_len++] = current;
        current = (int)res[current][2];
    }
    path[path_len++] = start;

    printf("\nShortest distance between %d and %d is: %lf px", start, end, distance);
    printf("\nPath: ");
    for (int i = path_len - 1; i >= 0; i--){
        printf("%c", transform(path[i]));
        if (i != 0){
            printf("->");
        }
    }
    //对接python
    FILE* file = fopen("temp.bin", "wb");
    if (file == NULL){
        printf("[ERROR]Docking Failed!");
        return -1;
    }

    fwrite(&path_len, sizeof(int), 1, file);
    fwrite(path, sizeof(int), path_len, file);
    fclose(file);

    system("py ShowPath.py");

    return 0;
}