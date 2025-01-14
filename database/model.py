from sqlalchemy import String, Numeric, DateTime, func, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(unique=True)
    first_name: Mapped[str] = mapped_column(String(150), nullable=True)
    last_name: Mapped[str] = mapped_column(String(150), nullable=True)


class Expense(Base):
    __tablename__ = 'expense'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    description: Mapped[str] = mapped_column(String(150), nullable=True)
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())

    user_id: Mapped[int] = mapped_column(ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey('category_expense.id', ondelete='CASCADE'), nullable=False)

    category: Mapped['CategoryExpense'] = relationship(backref='expense')


class Income(Base):
    __tablename__ = 'income'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    description: Mapped[str] = mapped_column(String(150), nullable=True)
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())

    user_id: Mapped[int] = mapped_column(ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey('category_income.id', ondelete='CASCADE'), nullable=False)

    category: Mapped['CategoryIncome'] = relationship(backref='income')


class CategoryExpense(Base):
    __tablename__ = 'category_expense'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    limit: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    is_active: Mapped[bool] = mapped_column(default=True)

    user_id: Mapped[int] = mapped_column(ForeignKey('user.id', ondelete='CASCADE'), nullable=False)


class CategoryIncome(Base):
    __tablename__ = 'category_income'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)

    user_id: Mapped[int] = mapped_column(ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
