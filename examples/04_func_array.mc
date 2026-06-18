// Example 4: Functions and arrays
int sum_array(int arr[5], int size) {
    int total = 0;
    int i = 0;
    while (i < size) {
        total = total + arr[i];
        i = i + 1;
    }
    return total;
}

int max_value(int data[10], int len) {
    int max = data[0];
    int i = 1;
    while (i < len) {
        if (data[i] > max) {
            max = data[i];
        }
        i = i + 1;
    }
    return max;
}

void main() {
    int scores[5];
    scores[0] = 90;
    scores[1] = 85;
    scores[2] = 92;
    scores[3] = 78;
    scores[4] = 88;

    int total = sum_array(scores, 5);
    print(total);

    int highest = max_value(scores, 5);
    print(highest);

    int matrix[10];
    int k = 0;
    for (k = 0; k < 10; k = k + 1) {
        matrix[k] = k * 10;
    }
}
