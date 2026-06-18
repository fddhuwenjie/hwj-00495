// Example 8: Functions and Arrays - demonstrates array operations with functions
int sum(int arr[10], int len) {
    int total = 0;
    for (int i = 0; i < len; i = i + 1) {
        total = total + arr[i];
    }
    return total;
}

float average(int arr[10], int len) {
    int s = sum(arr, len);
    float avg = s / 2.0;
    return avg;
}

void reverse(int arr[10], int len) {
    for (int i = 0; i < len / 2; i = i + 1) {
        int temp = arr[i];
        arr[i] = arr[len - i - 1];
        arr[len - i - 1] = temp;
    }
}

int find_max(int arr[10], int len) {
    int max_val = arr[0];
    for (int i = 1; i < len; i = i + 1) {
        if (arr[i] > max_val) {
            max_val = arr[i];
        }
    }
    return max_val;
}

void main() {
    int data[10];
    for (int i = 0; i < 10; i = i + 1) {
        data[i] = i * 10;
    }

    int total = sum(data, 10);
    print(total);

    float avg = average(data, 10);
    print(avg);

    int max_val = find_max(data, 10);
    print(max_val);

    reverse(data, 10);
    for (int j = 0; j < 10; j = j + 1) {
        print(data[j]);
    }
}
