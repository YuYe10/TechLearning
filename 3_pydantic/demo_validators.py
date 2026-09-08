"""Pydantic 自定义校验：field_validator / model_validator 与 ValidationError 结构。"""
from pydantic import BaseModel, field_validator, model_validator, ValidationError


class User(BaseModel):
    name: str
    age: int
    password: str
    password2: str

    @field_validator("name")
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

    @model_validator(mode="after")
    def check_passwords(self):
        if self.password != self.password2:
            raise ValueError("两次密码不一致")
        return self


def main():
    print("== 1. field_validator：清洗 + 校验 ==")
    u = User(name="  alice  ", age=20, password="x", password2="x")
    print("  name 被 strip 后:", repr(u.name))

    print("\n== 2. field_validator 抛错 ==")
    for kw in [dict(name="", age=20, password="x", password2="x"),
               dict(name="bob", age=-1, password="x", password2="x")]:
        try:
            User(**kw)
        except ValidationError as e:
            print("  ", e.errors()[0]["loc"], "->", e.errors()[0]["msg"])

    print("\n== 3. model_validator：跨字段校验 ==")
    try:
        User(name="carol", age=20, password="a", password2="b")
    except ValidationError as e:
        print("  ", e.errors()[0]["loc"], "->", e.errors()[0]["msg"])

    print("\n== 4. ValidationError 的完整结构 ==")
    try:
        User(name="dave", age="not-int", password="x", password2="x")
    except ValidationError as e:
        print("  errors():", e.errors())
        print("  str(e):")
        print(e)


if __name__ == "__main__":
    main()
