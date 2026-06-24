def test_func():
    for i in range(2):
        if i == 0:
            last_raw_tool_res = "test"
            print("Set last_raw_tool_res")
        if i == 1:
            break
    if 'last_raw_tool_res' in locals():
        print("YES in locals")
    else:
        print("NO in locals")

test_func()
