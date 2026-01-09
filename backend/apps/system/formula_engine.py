"""
公式计算引擎 - 安全的表达式求值

使用 simpleeval 库实现安全的数学和逻辑表达式计算。
支持基本数学运算、字符串操作和条件表达式。
"""

from decimal import Decimal, ROUND_HALF_UP
import re

try:
    from simpleeval import simple_eval, EvalWithCompoundTypes, InvalidExpression
    SIMPLEEVAL_AVAILABLE = True
except ImportError:
    SIMPLEEVAL_AVAILABLE = False


class FormulaEngine:
    """安全公式计算引擎"""
    
    # 允许的内置函数
    ALLOWED_FUNCTIONS = {
        # 数学函数
        'round': round,
        'abs': abs,
        'max': max,
        'min': min,
        'sum': sum,
        'pow': pow,
        
        # 类型转换
        'int': int,
        'float': float,
        'str': str,
        'bool': bool,
        
        # 字符串函数
        'len': len,
        'upper': lambda s: s.upper() if isinstance(s, str) else s,
        'lower': lambda s: s.lower() if isinstance(s, str) else s,
        'strip': lambda s: s.strip() if isinstance(s, str) else s,
        
        # 条件函数
        'if_else': lambda cond, true_val, false_val: true_val if cond else false_val,
        'is_empty': lambda x: x is None or x == '' or x == [],
        'default': lambda x, default: x if x is not None and x != '' else default,
    }
    
    # 允许的运算符 (simpleeval 默认支持)
    # +, -, *, /, //, %, **, ==, !=, <, >, <=, >=, and, or, not
    
    @classmethod
    def evaluate(cls, expression: str, context: dict, precision: int = None) -> any:
        """
        安全执行公式表达式
        
        Args:
            expression: 公式字符串，如 "price * quantity * (1 - discount)"
            context: 变量上下文，如 {"price": 100, "quantity": 2, "discount": 0.1}
            precision: 结果精度（小数位数），仅对数值结果有效
        
        Returns:
            计算结果
            
        Raises:
            FormulaError: 公式执行错误
        """
        if not SIMPLEEVAL_AVAILABLE:
            raise FormulaError("simpleeval 库未安装，请运行: pip install simpleeval")
        
        if not expression or not expression.strip():
            return None
        
        # 预处理上下文：处理 None 值
        safe_context = cls._prepare_context(context)
        
        try:
            evaluator = EvalWithCompoundTypes(
                names=safe_context,
                functions=cls.ALLOWED_FUNCTIONS
            )
            result = evaluator.eval(expression)
            
            # 应用精度
            if precision is not None and isinstance(result, (int, float, Decimal)):
                result = round(float(result), precision)
            
            return result
            
        except InvalidExpression as e:
            raise FormulaError(f"无效的公式表达式: {str(e)}")
        except Exception as e:
            raise FormulaError(f"公式计算错误: {str(e)}")
    
    @classmethod
    def _prepare_context(cls, context: dict) -> dict:
        """预处理上下文，将 None 转为 0 或空字符串"""
        result = {}
        for key, value in context.items():
            if value is None:
                result[key] = 0
            elif isinstance(value, Decimal):
                result[key] = float(value)
            else:
                result[key] = value
        return result
    
    @classmethod
    def validate_expression(cls, expression: str) -> tuple[bool, str]:
        """
        验证公式表达式是否有效
        
        Args:
            expression: 公式字符串
            
        Returns:
            (is_valid, error_message)
        """
        if not SIMPLEEVAL_AVAILABLE:
            return False, "simpleeval 库未安装"
        
        if not expression or not expression.strip():
            return False, "表达式不能为空"
        
        # 检查危险模式
        dangerous_patterns = [
            r'__\w+__',      # 双下划线属性
            r'import\s+',    # import 语句
            r'exec\s*\(',    # exec 函数
            r'eval\s*\(',    # eval 函数
            r'compile\s*\(', # compile 函数
            r'open\s*\(',    # open 函数
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, expression, re.IGNORECASE):
                return False, f"表达式包含不允许的模式: {pattern}"
        
        # 尝试用模拟数据执行一次
        try:
            # 提取变量名
            variables = cls.extract_variables(expression)
            mock_context = {var: 1 for var in variables}
            
            evaluator = EvalWithCompoundTypes(
                names=mock_context,
                functions=cls.ALLOWED_FUNCTIONS
            )
            evaluator.eval(expression)
            return True, ""
            
        except Exception as e:
            return False, f"表达式语法错误: {str(e)}"
    
    @classmethod
    def extract_variables(cls, expression: str) -> list:
        """
        从表达式中提取变量名
        
        Args:
            expression: 公式字符串
            
        Returns:
            变量名列表
        """
        # 移除字符串字面量
        cleaned = re.sub(r'"[^"]*"', '', expression)
        cleaned = re.sub(r"'[^']*'", '', cleaned)
        
        # 匹配变量名（排除函数名和数字）
        var_pattern = r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b'
        matches = re.findall(var_pattern, cleaned)
        
        # 排除函数名和关键字
        excluded = set(cls.ALLOWED_FUNCTIONS.keys()) | {'and', 'or', 'not', 'True', 'False', 'None'}
        
        return list(set(m for m in matches if m not in excluded))


class FormulaError(Exception):
    """公式计算错误"""
    pass
