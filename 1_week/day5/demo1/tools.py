from schemas import CalculatorInput

def calculator(
        a:float,
        b:float,
        operation:str,
)->float:
    if operation == "add":
        return a + b
    elif operation == "subtract":
        return a - b
    elif operation == "multiply":
        return a * b
    elif operation == "divide":
        if b == 0:
            raise ValueError("除数不能为0")
        return a / b
    raise ValueError(f"{operation}不支持运算")

TOOL_REGISTRY={
    "calculator":{
        "function":calculator,
        "input_model":CalculatorInput,
        "description":"用于执行加减惩处的数学计算"
    }
}
