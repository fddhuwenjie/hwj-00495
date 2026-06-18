// Example 5: Nested scopes
int global_x = 100;

int compute(int a) {
    int result = a * 2;
    if (a > 10) {
        int temp = a + 5;
        result = temp;
        if (temp > 20) {
            int deep = temp - 10;
            result = deep;
        }
    }
    return result;
}

void main() {
    int x = 10;
    {
        int y = 20;
        {
            int z = 30;
            print(x + y + z);
        }
        int z = 50;
        print(y + z);
    }
    int result = compute(x);
    print(result);

    for (int i = 0; i < 3; i = i + 1) {
        int temp = i * 10;
        if (temp > 10) {
            int inner = temp + 1;
            print(inner);
        }
    }
}
