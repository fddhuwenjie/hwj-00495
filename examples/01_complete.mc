// Example 1: Complete program without errors
int global_var = 10;

int add(int a, int b) {
    return a + b;
}

float average(int x, int y) {
    float sum = add(x, y);
    return sum / 2.0;
}

void main() {
    int x = 5;
    int y = 10;
    int result = add(x, y);
    print(result);

    float avg = average(x, y);
    print(avg);

    bool flag = true;
    if (flag) {
        print(x);
    } else {
        print(y);
    }

    int i = 0;
    while (i < 5) {
        print(i);
        i = i + 1;
    }

    for (int j = 0; j < 3; j = j + 1) {
        print(j);
    }
}
