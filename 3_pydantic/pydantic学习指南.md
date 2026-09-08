# Pydantic 学习指南（核心全面）

> 本指南系统讲解 **Pydantic** 的核心函数、特性应用、注意事项与应用场景。
> 每个知识点都配有可独立运行的示例文件（位于本目录），文中的输出均为**实际运行结果**。
> 环境：Python 3.10 · Pydantic 2.13.5 · pydantic-settings 2.13 · email-validator。
>
> Pydantic 是 FastAPI 的数据校验底座——[4_FastAPI/FastAPI学习指南.md](../4_FastAPI/FastAPI学习指南.md) 里所有「请求体校验、422 报错、响应模型」都靠它。读懂本指南，FastAPI 那部分就豁然开朗了。

---

## 目录

1. [引言：为什么需要 Pydantic](#1-引言为什么需要-pydantic)
2. [核心概念](#2-核心概念)
3. [核心函数与特性](#3-核心函数与特性)
4. [进阶特性应用](#4-进阶特性应用)
5. [注意事项](#5-注意事项)
6. [应用场景](#6-应用场景)
7. [总结与延伸](#7-总结与延伸)
8. [示例文件清单](#8-示例文件清单)

---

## 1. 引言：为什么需要 Pydantic

程序大量时间在处理**数据**——来自 JSON 接口、配置文件、数据库、用户输入。而 Python 是动态类型语言，数据进来时常常是一堆**没有校验的字典**：

```python
# 手写校验：又臭又长，还容易漏
data = {"name": "alice", "age": "20"}          # age 是字符串！
if not isinstance(data, dict):
    raise ValueError(...)
if not isinstance(data["name"], str):
    raise ValueError(...)
age = int(data["age"])                          # 自己手动转，转失败还要 try
if age < 0:
    raise ValueError(...)
```

Pydantic 的思路是：**用类型注解声明「数据长什么样」，校验和转换它全包了**。

```python
from pydantic import BaseModel, Field

class User(BaseModel):
    name: str
    age: int = Field(ge=0)      # 自动把 "20" 转成 20，再校验 >= 0

User(name="alice", age="20")    # 一行搞定：转换 + 校验
```

### 它解决的三件事

| 能力 | 说明 |
|------|------|
| **校验** | 类型、范围、长度、正则、邮箱、枚举……不合规就抛 `ValidationError` |
| **转换** | `"20"` → `20`、`"2024-01-15"` → `date`、`"123..."` → `UUID`，自动完成 |
| **序列化** | 对象 → 字典 / JSON / JSON Schema，一个 `model_dump()` 搞定 |

### 与相近方案对比

| 方案 | 校验 | 类型转换 | 序列化 | 说明 |
|------|------|----------|--------|------|
| 手写 `if` | ❌ 手写 | ❌ 手写 | ❌ 手写 | 容易漏、难维护 |
| `dataclass` | ❌ 无 | ❌ 无 | ❌ 无 | 只做字段存储，不做校验 |
| `attrs` | 部分 | 部分 | 部分 | 功能偏底层 |
| **Pydantic** | ✅ 声明式 | ✅ 自动 | ✅ 内置 | 类型注解驱动，生态最大（FastAPI 内置） |

> 一句话：Pydantic 让你**用类型注解声明数据结构**，校验、转换、序列化免费获得。

---

## 2. 核心概念

### 2.1 `BaseModel`：一切模型的基类

定义一个 Pydantic 模型，就是继承 `BaseModel` 并写上带类型注解的字段：

```python
class User(BaseModel):
    id: int
    name: str
    score: float
```

实例化时，Pydantic 会：

1. 按字段类型**校验**每个值
2. 必要时做**类型转换**（`"2"` → `2`）
3. 不合规就抛出 `ValidationError`

### 2.2 字段的三种形态

```python
class User(BaseModel):
    id: int                        # 必填：不传就报错
    is_active: bool = True         # 可选：有默认值
    nickname: str | None = None    # 可选且可为 None
```

- **无默认值** → 必填字段
- **有默认值** → 可选字段，不传用默认值
- `str | None` → 可为 `None`（Python 3.10+ 语法；老版本写 `Optional[str]`）

### 2.3 v2 的 Rust 内核

Pydantic v2 把校验引擎用 Rust 重写（`pydantic-core`），**比 v1 快 5~50 倍**。API 也做了调整（`dict()` → `model_dump()` 等），详见 [第 5 节注意事项](#5-注意事项)。

---

## 3. 核心函数与特性

> 每小节先讲用法，再给「实际运行输出」。完整可运行代码见对应的 `demo_*.py` 文件。

### 3.1 `BaseModel`：定义、转换、默认值

示例文件：[demo_basemodel.py](demo_basemodel.py)

```python
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str
    score: float
    is_active: bool = True          # 可选
    tags: list[str] = []            # 可变默认值，Pydantic 会复制一份，安全
    nickname: str | None = None     # 可选，可为 None

User(id=1, name="alice", score=98.5)          # 正常
User(id="2", name="bob", score="80")          # 字符串自动转 int/float
```

实际运行输出：

```
== 1. 正常实例化 ==
   id=1 name='alice' score=98.5 is_active=True tags=[] nickname=None
  字段访问: 1 alice 98.5

== 2. 类型自动转换 ==
   id=2 name='bob' score=80.0 is_active=True tags=[] nickname=None | score 类型: float

== 3. 默认值与可选字段 ==
  is_active: True | tags: [] | nickname: None

== 4. 非法输入 -> ValidationError ==
  错误数量: 1
    ('id',) -> Input should be a valid integer, unable to parse string as an integer
```

> 观察点：① `id="2"` 字符串自动转成了 `int 2`；② `tags=[]` 可变默认值安全（每个实例各自一份）；③ 非法 `id` 抛出 `ValidationError`，错误信息里 `('id',)` 指出了出错字段。

### 3.2 `Field` 约束与常用字段类型

`Field()` 给字段加约束（范围、长度、正则……），并配合各种类型做精准校验。示例文件：[demo_field.py](demo_field.py)

```python
from pydantic import BaseModel, Field, EmailStr
from enum import Enum
from typing import Literal
from datetime import date
from uuid import UUID

class Product(BaseModel):
    name: str = Field(min_length=2, max_length=20)
    price: float = Field(gt=0, le=10000)          # 0 < price <= 10000
    quantity: int = Field(ge=0)                    # >= 0
    sku: str = Field(pattern=r"^[A-Z]{2}-\d{4}$")  # 正则
    email: EmailStr                                # 邮箱（需安装 email-validator）
    role: Role = Role.user                         # 枚举
    level: Literal["low", "mid", "high"] = "low"   # 字面量
    released: date                                 # 日期
    uid: UUID                                      # UUID
    tags: list[str] = Field(default_factory=list)  # 可变默认值用 default_factory
```

常用 `Field` 约束速查：

| 约束 | 含义 |
|------|------|
| `gt` / `ge` / `lt` / `le` | 大于 / 大于等于 / 小于 / 小于等于 |
| `min_length` / `max_length` | 字符串或列表长度 |
| `pattern` | 正则匹配 |
| `default` / `default_factory` | 默认值 / 默认值工厂 |
| `description` | 字段描述（写入 JSON Schema，FastAPI 文档可见） |
| `alias` | 字段别名（见 4.3） |

实际运行输出：

```
== 1. 合法实例 ==
   name='钢笔' price=9.9 quantity=5 sku='AB-1234' email='a@b.com' role=<Role.admin: 'admin'> level='high' released=datetime.date(2024, 1, 15) uid=UUID('12345678-1234-5678-1234-567812345678') tags=[]
  uid 类型: UUID | released 类型: date

== 2. 各约束被破坏时的报错 ==
  拒绝: ('name',) -> String should have at least 2 characters
  拒绝: ('price',) -> Input should be greater than 0
  拒绝: ('sku',) -> String should match pattern '^[A-Z]{2}-\d{4}$'
  拒绝: ('email',) -> value is not a valid email address: An email address must have an @-sign.
```

> 观察点：① `"2024-01-15"` 自动转成 `date` 对象，UUID 字符串自动转成 `UUID` 对象；② 四种约束被破坏时，错误信息都精确指向字段和原因。

### 3.3 自定义校验器 `field_validator` / `model_validator`

内置约束不够用时，写自己的校验逻辑。示例文件：[demo_validators.py](demo_validators.py)

```python
from pydantic import BaseModel, field_validator, model_validator

class User(BaseModel):
    name: str
    age: int
    password: str
    password2: str

    @field_validator("name")          # 针对单个字段：清洗 + 校验
    @classmethod
    def name_strip(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("名字不能为空")
        return v

    @field_validator("age")
    @classmethod
    def age_check(cls, v):
        if v < 0:
            raise ValueError("年龄不能为负")
        return v

    @model_validator(mode="after")    # 针对整个模型：跨字段校验
    def check_passwords(self):
        if self.password != self.password2:
            raise ValueError("两次密码不一致")
        return self
```

- `field_validator`：校验**单个字段**，接收该字段值、返回处理后的值。
- `model_validator`：校验**整个模型**，能做「跨字段」校验（如两次密码一致）。`mode="before"` 在字段校验前拿原始输入，`mode="after"` 在字段校验后拿已构建的模型。

实际运行输出：

```
== 1. field_validator：清洗 + 校验 ==
  name 被 strip 后: 'alice'

== 2. field_validator 抛错 ==
   ('name',) -> Value error, 名字不能为空
   ('age',) -> Value error, 年龄不能为负

== 3. model_validator：跨字段校验 ==
   () -> Value error, 两次密码不一致

== 4. ValidationError 的完整结构 ==
  errors(): [{'type': 'int_parsing', 'loc': ('age',), 'msg': 'Input should be a valid integer, unable to parse string as an integer', 'input': 'not-int', 'url': 'https://errors.pydantic.dev/2.13/v/int_parsing'}]
  str(e):
1 validation error for User
age
  Input should be a valid integer, unable to parse string as an integer [type=int_parsing, input_value='not-int', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/int_parsing
```

> 观察点：① `"  alice  "` 被 validator 清洗成 `"alice"`——**校验的同时还能改值**；② 跨字段的「两次密码」用 `model_validator` 才能实现（`field_validator` 看不到别的字段）；③ `ValidationError.errors()` 返回结构化错误列表（`type`/`loc`/`msg`/`input`），机器可读。

### 3.4 序列化与反序列化

Pydantic 的核心能力是「对象 ↔ 字典/JSON」互转。示例文件：[demo_serialization.py](demo_serialization.py)

```python
from pydantic import BaseModel, Field

class Item(BaseModel):
    name: str
    price: float = Field(gt=0)
    secret: str = Field(exclude=True)   # 序列化时默认排除

item = Item(name="牙刷", price=9.9, secret="不要外传")

item.model_dump()                       # 对象 -> 字典
item.model_dump_json()                  # 对象 -> JSON 字符串
Item.model_validate({...})              # 字典 -> 对象
Item.model_validate_json('{...}')       # JSON 字符串 -> 对象
Item.model_json_schema()                # 导出 JSON Schema
```

实际运行输出：

```
== 1. model_dump 转字典 ==
   {'name': '牙刷', 'price': 9.9} | secret 被排除: True

== 2. model_dump_json 转 JSON 字符串 ==
   {"name":"牙刷","price":9.9} | 类型: str

== 3. model_validate 从字典构建 ==
   name='铅笔' price=2.5 secret='x'

== 4. model_validate_json 从 JSON 字符串构建 ==
   name='橡皮' price=1.5 secret='y'

== 5. model_json_schema 导出 JSON Schema ==
  字段: ['name', 'price', 'secret']
  price 约束: {'exclusiveMinimum': 0, 'title': 'Price', 'type': 'number'}
```

> 观察点：① `Field(exclude=True)` 让 `secret` 在序列化时**默认被排除**（`model_dump()` 和 `model_dump_json()` 都没有它），但对象本身仍保留该字段；② `model_json_schema()` 把字段约束翻译成标准 JSON Schema（`exclusiveMinimum: 0`），这就是 FastAPI 自动文档的数据来源。

### 3.5 `ValidationError` 与错误处理

所有校验失败都抛出 `ValidationError`。它有结构化的接口：

```python
try:
    User(id="abc", ...)
except ValidationError as e:
    e.error_count()     # 错误条数
    e.errors()          # 结构化错误列表：[{type, loc, msg, input}, ...]
    str(e)              # 人类可读的多行文本
```

`loc` 用元组表示出错位置：单字段是 `('field',)`，嵌套字段是 `('outer', 'inner', 0)`。

### 3.6 `model_config` 配置

用 `ConfigDict` 配置模型行为。示例文件：[demo_config.py](demo_config.py)

```python
from pydantic import BaseModel, ConfigDict

class M(BaseModel):
    model_config = ConfigDict(extra="forbid",          # 禁止额外字段
                              validate_assignment=True, # 赋值时也校验
                              str_strip_whitespace=True, # 字符串去首尾空格
                              str_to_lower=True,        # 字符串转小写
                              frozen=True,              # 不可变
                              from_attributes=True)     # 从属性对象读取
```

实际运行输出：

```
== 1. extra=forbid：拒绝额外字段 ==
  额外字段 b -> Extra inputs are not permitted

== 2. validate_assignment：赋值时校验 ==
  赋值 -1 -> Input should be greater than 0

== 3. 字符串归一化 ==
  name: 'alice'

== 4. frozen：不可变 ==
  修改被拒 -> ValidationError

== 5. from_attributes：从任意属性对象读取（ORM 模式）==
   id=1 name='alice'
```

常用 `ConfigDict` 项：

| 配置 | 含义 |
|------|------|
| `extra="forbid"` / `"ignore"` / `"allow"` | 额外字段：禁止 / 忽略 / 允许 |
| `validate_assignment=True` | 字段被重新赋值时也校验 |
| `str_strip_whitespace` / `str_to_lower` / `str_to_upper` | 字符串归一化 |
| `frozen=True` | 模型不可变（赋值抛错） |
| `from_attributes=True` | 允许从任意带属性对象（如 ORM 对象）读取 |
| `populate_by_name=True` | 同时接受字段名和别名填充 |
| `use_enum_values=True` | 枚举字段存值而非枚举对象 |

---

## 4. 进阶特性应用

示例文件：[demo_advanced.py](demo_advanced.py) 与 [demo_settings.py](demo_settings.py)

### 4.1 `computed_field` 计算字段

派生字段——由其它字段算出，不必存储、随模型一起序列化：

```python
class Rect(BaseModel):
    width: int
    height: int

    @computed_field
    @property
    def area(self) -> int:
        return self.width * self.height
```

实际运行输出：

```
== 1. computed_field 计算字段 ==
  area: 12 | dump: {'width': 3, 'height': 4, 'area': 12}
```

### 4.2 `Annotated` + `Field` 复用约束

把「类型 + 约束」打包成一个可复用类型：

```python
PositiveInt = Annotated[int, Field(gt=0)]

class Order(BaseModel):
    qty: PositiveInt
    price: PositiveInt
```

实际运行输出：

```
== 2. Annotated 复用约束 ==
   qty=2 price=10
  qty=0 -> ValidationError
```

### 4.3 `alias` 别名

JSON 字段名（如 `userName`）和 Python 变量名（如 `user_name`）不一致时用别名：

```python
class AliasModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    user_name: str = Field(alias="userName")

AliasModel(userName="alice")            # 用别名构建
a.user_name                             # 用字段名访问
a.model_dump(by_alias=True)             # 序列化时换回别名
```

实际运行输出：

```
== 3. alias 别名 ==
  从别名构建: user_name='alice' | 字段名访问: alice | dump(by_alias): {'userName': 'alice'}
```

### 4.4 泛型模型

`Generic[T]` 让模型可参数化，复用分页、响应包装等结构：

```python
T = TypeVar("T")
class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int

Page[Book](items=[...], total=2)
```

实际运行输出：

```
== 4. 泛型模型 ==
   {'items': [{'title': 'a'}, {'title': 'b'}], 'total': 2}
```

### 4.5 `TypeAdapter`：单个类型也能校验

不用 `BaseModel`，直接校验裸类型（`list[int]`、`dict[str, int]` 等）：

```python
from pydantic import TypeAdapter
ta = TypeAdapter(list[int])
ta.validate_python(["1", "2", "3"])    # -> [1, 2, 3]
```

实际运行输出：

```
== 5. TypeAdapter：单个类型也能校验 ==
  校验: [1, 2, 3]
  非法 -> ValidationError
```

### 4.6 `pydantic-settings` 配置管理

用 Pydantic 管理配置：从环境变量 / `.env` 文件读取并校验。示例文件：[demo_settings.py](demo_settings.py)

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="APP_", env_file=".env", extra="ignore")
    host: str = "localhost"
    port: int = 8000
    debug: bool = False
```

读取顺序（后者覆盖前者）：默认值 < `.env` 文件 < 环境变量。`APP_PORT="9000"` 会自动转成 `int 9000`，`APP_DEBUG="true"` 自动转成 `True`。

实际运行输出：

```
host : prod.example.com
port : 9000 | 类型: int
debug: True | 类型: bool
model_dump: {'host': 'prod.example.com', 'port': 9000, 'debug': True}
```

### 4.7 JSON Schema 导出

`model_json_schema()` 把模型转成标准 JSON Schema，可用于文档、代码生成、前端校验（见 3.4 输出）。

### 4.8 ORM 模式 `from_attributes`

`model_config = ConfigDict(from_attributes=True)` 后，`model_validate(orm_obj)` 可从任意带属性的对象读取，配合 SQLAlchemy 等 ORM 使用（见 3.6 输出）。

---

## 5. 注意事项

### 5.1 v1 → v2 差异（网上教程最大坑）

Pydantic v2 改了 API，网上大量 v1 教程照抄会报错：

| 操作 | v1（旧，已废弃） | v2（新） |
|------|------------------|----------|
| 对象转字典 | `item.dict()` | `item.model_dump()` |
| 对象转 JSON | `item.json()` | `item.model_dump_json()` |
| 字典构建对象 | `Model.parse_obj(d)` | `Model.model_validate(d)` |
| JSON 字符串构建 | `Model.parse_raw(s)` | `Model.model_validate_json(s)` |
| 单字段校验器 | `@validator` | `@field_validator` |
| 根校验器 | `@root_validator` | `@model_validator` |
| ORM 模式 | `class Config: orm_mode = True` | `model_config = ConfigDict(from_attributes=True)` |
| 模型配置 | 内部类 `class Config` | `model_config = ConfigDict(...)` |
| 复制模型 | `item.copy()` | `item.model_copy()` |
| 导出 Schema | `Model.schema()` | `Model.model_json_schema()` |

### 5.2 可变默认值：`[]` 安全，但仍推荐 `default_factory`

Pydantic 对 `list[str] = []` 会**自动复制**，不会出现共享引用的问题。但函数/字典等默认值最好用 `default_factory` 显式声明，语义更清晰：

```python
tags: list[str] = Field(default_factory=list)
```

### 5.3 校验发生在构造时，不在赋值时

默认**只在实例化（构造）时校验**。如果后面直接改字段值，不会触发校验：

```python
u = User(age=10)
u.age = -1        # ❌ 默认不校验，直接改成功
```

要赋值时也校验，加 `model_config = ConfigDict(validate_assignment=True)`（见 3.6）。

### 5.4 默认「忽略」额外字段

Pydantic 默认 `extra="ignore"`：传入模型没声明的字段会被**静默丢弃**，不会报错。这有时是坑——拼错字段名会悄悄丢数据。要严格可以用 `extra="forbid"`（见 3.6）。

### 5.5 `model_dump` 会丢失未声明字段、按规则过滤

- 未在模型里声明的额外字段，`model_dump()` 不会输出（构造时就被忽略了）。
- `Field(exclude=True)` 的字段默认不导出（见 3.4）。
- 想导出一部分字段用 `model_dump(include={"a", "b"})` 或 `model_dump(exclude={"c"})`。

### 5.6 性能：v2 很快，但别在热路径反复构造

Rust 内核让 v2 比 v1 快 5~50 倍，单次校验开销很小。但**大量重复构造模型**（如百万行数据逐行 `model_validate`）仍值得注意：批量场景可考虑 `TypeAdapter`（免去模型对象开销）或复用模型实例。

### 5.7 类型注解是「声明意图」，不是强制运行类型

`int` 字段传 `"20"` 会被**转换**成 `20`（宽松），传 `"abc"` 才报错。Pydantic 是「**先尽力转换，转不了才报错**」，不是 Python 运行时的 `isinstance` 检查。这既是便利（宽松），也意味着「看起来合法」的输入可能被悄悄改写。

### 5.8 `EmailStr` 需要额外安装 `email-validator`

```bash
pip install "pydantic[email]"   # 或单独 pip install email-validator
```

否则导入 `EmailStr` 时运行会报错提示缺依赖（本环境已安装）。

### 5.9 可变默认值校验时机（`default_factory` 每次调用）

`default_factory` 在**每次实例化**时调用，适合「默认值是新建对象」的场景（如 `default_factory=list`）。注意别写成 `Field(default_factory=[])`——`default_factory` 要传**可调用对象**，不是值。

### 5.10 Windows 控制台中文乱码

在 Windows 命令行直接 `python demo_xxx.py`，若中文输出乱码，是因为默认用 GBK 编码。加上环境变量即可：

```bash
PYTHONUTF8=1 python demo_basemodel.py
```

---

## 6. 应用场景

| 场景 | 说明 |
|------|------|
| **API 请求/响应校验** | FastAPI 的 `BaseModel` 请求体、`response_model`，自动 422 + 文档 |
| **配置文件管理** | `pydantic-settings` 从 `.env`/环境变量读取并校验，启动即发现配置错误 |
| **数据管道清洗** | 从 CSV/JSON/数据库读入脏数据，用模型清洗 + 校验 + 转类型 |
| **机器学习超参/特征校验** | 校验超参范围、特征类型，训练前拦截非法配置 |
| **消息队列载荷校验** | 消费 MQ 消息时 `model_validate_json` 校验 payload，防脏数据入库 |
| **ORM 数据转换** | `from_attributes=True` 把 ORM 对象转成响应模型 |
| **JSON Schema 文档** | `model_json_schema()` 生成 Schema，驱动前端表单/文档 |

**不适用**：需要极致性能的逐字段手写校验（可考虑 `pydantic-core` 或纯手写）、非声明式的动态 schema（字段运行时才确定）。

---

## 7. 总结与延伸

### 核心要点回顾

1. **声明即校验**：继承 `BaseModel` + 类型注解，校验/转换/序列化全自动。
2. **约束靠 `Field`**：`gt/ge/lt/le`、`min_length/max_length`、`pattern`、`default_factory`。
3. **自定义校验**：`@field_validator`（单字段）、`@model_validator`（跨字段/整个模型）。
4. **序列化四件套**：`model_dump` / `model_dump_json` / `model_validate` / `model_validate_json`。
5. **配置靠 `model_config`**：`extra`、`validate_assignment`、`frozen`、`from_attributes`、字符串归一化。
6. **进阶武器**：`computed_field`、`Annotated` 复用约束、`alias`、泛型、`TypeAdapter`、`pydantic-settings`。
7. **错误结构化**：`ValidationError.errors()` 返回 `type/loc/msg/input`，机器可读。

### 下一步延伸（本指南未展开）

- **与 FastAPI 结合** —— 见 [4_FastAPI/FastAPI学习指南.md](../4_FastAPI/FastAPI学习指南.md)，`BaseModel`/`Field`/`response_model` 无缝衔接。
- **SQLModel** —— FastAPI 作者出的 ORM，融合 SQLAlchemy + Pydantic，模型即表结构。
- **`pydantic-settings` 进阶** —— 嵌套配置、`SecretStr`（敏感信息不落日志）、多个 `.env` 合并。
- **自定义类型** —— `BeforeValidator` / `AfterValidator` / `WrapValidator` 实现自定义转换逻辑。
- **严格模式** —— `model_config = ConfigDict(strict=True)` 关闭宽松的类型转换。
- **序列化自定义** —— `@field_serializer` / `model_serializer` 定制输出格式。

---

## 8. 示例文件清单

| 文件 | 内容 |
|------|------|
| [demo_basemodel.py](demo_basemodel.py) | BaseModel 定义、类型转换、默认值、ValidationError |
| [demo_field.py](demo_field.py) | Field 约束与常用字段类型（EmailStr/枚举/Literal/date/UUID） |
| [demo_validators.py](demo_validators.py) | field_validator / model_validator、ValidationError 结构 |
| [demo_serialization.py](demo_serialization.py) | model_dump / model_validate / json_schema 序列化与反序列化 |
| [demo_config.py](demo_config.py) | model_config：extra / validate_assignment / frozen / from_attributes |
| [demo_advanced.py](demo_advanced.py) | computed_field / Annotated / alias / 泛型 / TypeAdapter |
| [demo_settings.py](demo_settings.py) | pydantic-settings 配置管理 |
